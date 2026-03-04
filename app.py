import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from streamlit_autorefresh import st_autorefresh
from plotly.subplots import make_subplots
from datetime import datetime

# 1. SETUP & SESSION
st.set_page_config(page_title="PATRO AI PRO V8.7", layout="wide")
if 'auth' not in st.session_state: st.session_state['auth'] = False
if 'trade_lock' not in st.session_state: st.session_state.trade_lock = None

# 2. SECURITY
if not st.session_state['auth']:
    st.title("🛡️ PATRO AI PRO | SECURE ACCESS")
    u, p = st.text_input("User"), st.text_input("Pass", type="password")
    if st.button("Unlock"):
        if u == "PATRO_ADMIN" and p == "patro666@":
            st.session_state['auth'] = True
            st.rerun()
    st.stop()

# 3. SIDEBAR: INSTITUTIONAL SOP & CONTROLS
with st.sidebar:
    st.title("🎮 PATRO CONTROL")
    
    # --- UPDATED BUTTONS (NO DEPRECATION WARNINGS) ---
    if st.button("🔄 FORCE DATA SYNC", width="stretch" if 'width' in dir(st) else None):
        st.cache_data.clear()
        st.rerun()
    
    st.divider()
    
    # --- NEWS BLOCK (March 4, 2026) ---
    st.subheader("🗓️ TODAY'S RISK EVENTS")
    events = [
        {"Time": "08:15", "Name": "ADP Jobs Report", "Impact": "HIGH"},
        {"Time": "10:00", "Name": "ISM Services PMI", "Impact": "HIGH"},
        {"Time": "14:00", "Name": "Fed Beige Book", "Impact": "MED"}
    ]
    for e in events:
        color = "🔴" if e['Impact'] == "HIGH" else "🟡"
        st.caption(f"{color} {e['Time']} ET - {e['Name']}")
    
    st.divider()
    st.subheader("📋 CONFLUENCE GATES")
    sop_trend = st.checkbox("Trend Matrix (SMA)", value=True)
    sop_vwap = st.checkbox("Price Location (VWAP)", value=True)
    sop_vol = st.checkbox("Volume Confirmation", value=True)
    sop_macd_gate = st.checkbox("MACD Momentum Guard", value=True)
    
    st.divider()
    asset_choice = st.selectbox("Asset", ["XAUUSD (GOLD)", "US30 (DOW JONES)"])
    tf = st.radio("Timeframe", ["1m", "5m", "15m"], index=0, horizontal=True)
    
    if st.button("♻️ RESET SIGNAL LOCK", width="stretch" if 'width' in dir(st) else None):
        st.session_state.trade_lock = None
        st.rerun()

# 4. DATA ENGINE (ERROR-PROOF)
ticker = "GC=F" if asset_choice == "XAUUSD (GOLD)" else "^DJI"
st_autorefresh(interval=10000, key="v8_sop_pulse")

try:
    # Use 5d period to ensure ADX (14-period) has enough data to calculate
    df = yf.download(ticker, period="5d", interval=tf)
    
    if df.empty or len(df) < 30:
        st.warning("📡 SYNCING... Market data is currently heavy. Use 'FORCE DATA SYNC' if stuck.")
        st.stop()

    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    df = df.ffill().dropna() 

    # --- INDICATORS ---
    df['VWAP'] = (((df['High'] + df['Low'] + df['Close']) / 3) * df['Volume']).cumsum() / (df['Volume'].cumsum() + 1e-9)
    df['SMA'] = df['Close'].rolling(20).mean()
    
    exp1 = df['Close'].ewm(span=12, adjust=False).mean()
    exp2 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp1 - exp2
    df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['Hist'] = df['MACD'] - df['Signal']
    
    # ADX Safety Math
    plus_dm = df['High'].diff().clip(lower=0)
    minus_dm = (-df['Low'].diff()).clip(lower=0)
    tr = pd.concat([df['High']-df['Low'], abs(df['High']-df['Close'].shift(1)), abs(df['Low']-df['Close'].shift(1))], axis=1).max(axis=1)
    atr = tr.rolling(14).mean().replace(0, np.nan)
    
    df['ADX'] = (abs((100*(plus_dm.rolling(14).mean()/atr)) - (100*(minus_dm.rolling(14).mean()/atr))) / 
                ((100*(plus_dm.rolling(14).mean()/atr)) + (100*(minus_dm.rolling(14).mean()/atr)) + 1e-9) * 100).rolling(14).mean()
    df['ATR'] = (df['High'] - df['Low']).rolling(14).mean()

    last = df.iloc[-1]
    prev = df.iloc[-2]
    atr_val = last['ATR'] if not pd.isna(last['ATR']) else 1.5

    # --- SAFE POWER METER (NaN & BOUNDARY FIX) ---
    with st.sidebar:
        st.divider()
        adx_val = float(last['ADX']) if not pd.isna(last['ADX']) else 0.0
        prev_adx_val = float(prev['ADX']) if not pd.isna(prev['ADX']) else 0.0
        
        arrow = "▲" if adx_val > prev_adx_val else "▼"
        color = "green" if adx_val > prev_adx_val else "red"
        
        st.markdown(f"### ⚡ POWER: {adx_val:.1f}% :{color}[{arrow}]")
        
        # FIX: Clamping progress between 0.0 and 1.0 to prevent crash
        safe_progress = min(max(adx_val / 100.0, 0.0), 1.0)
        st.progress(safe_progress)

    # 5. SIGNAL LOGIC
    if st.session_state.trade_lock is None and sop_trend and sop_vwap and sop_vol and sop_macd_gate:
        if last['Close'] < last['VWAP'] and last['Close'] < last['SMA'] and last['Hist'] < 0:
            st.session_state.trade_lock = {"type": "SELL", "en": last['Close'], "sl": last['Close'] + (atr_val*1.5), "tp": last['Close'] - (atr_val*3)}
            st.toast("🚨 SOP SELL CONFIRMED")
        elif last['Close'] > last['VWAP'] and last['Close'] > last['SMA'] and last['Hist'] > 0:
            st.session_state.trade_lock = {"type": "BUY", "en": last['Close'], "sl": last['Close'] - (atr_val*1.5), "tp": last['Close'] + (atr_val*3)}
            st.toast("💰 SOP BUY CONFIRMED")

    # 6. CHARTING
    st.header(f"📊 {asset_choice} Terminal")
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.5, 0.2, 0.3])
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['VWAP'], line=dict(color='cyan', width=2), name='VWAP'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA'], line=dict(color='orange', width=1.5), name='SMA 20'), row=1, col=1)
    
    vol_colors = ['#ff4b4b' if r['Open'] > r['Close'] else '#00ff00' for _, r in df.iterrows()]
    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color=vol_colors, name="Volume"), row=2, col=1)
    
    fig.add_trace(go.Scatter(x=df.index, y=df['MACD'], line=dict(color='#00E676', width=1), name='MACD'), row=3, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['Signal'], line=dict(color='#FF5252', width=1), name='Signal'), row=3, col=1)
    h_colors = ['#00E676' if x > 0 else '#FF5252' for x in df['Hist']]
    fig.add_trace(go.Bar(x=df.index, y=df['Hist'], marker_color=h_colors, name='Hist'), row=3, col=1)

    if st.session_state.trade_lock:
        t = st.session_state.trade_lock
        fig.add_hline(y=t['en'], line_dash="dot", line_color="white", row=1, col=1)
        st.error(f"LOCKED {t['type']} | Entry: {t['en']:.2f} | SL: {t['sl']:.2f}")

    fig.update_layout(template="plotly_dark", height=800, xaxis_rangeslider_visible=False, showlegend=False)
    
    # FIX: Replaced use_container_width=True with width="stretch"
    st.plotly_chart(fig, width="stretch")

except Exception as e:
    st.error(f"📡 Syncing System... {e}")
