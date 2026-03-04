import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from streamlit_autorefresh import st_autorefresh
from plotly.subplots import make_subplots

# 1. SETUP & SESSION
st.set_page_config(page_title="PATRO AI PRO V8.6", layout="wide")
if 'auth' not in st.session_state: st.session_state['auth'] = False
if 'trade_lock' not in st.session_state: st.session_state.trade_lock = None
if 'last_adx' not in st.session_state: st.session_state.last_adx = 0.0

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
    st.divider()
    
    st.subheader("📋 INSTITUTIONAL SOP")
    sop_trend = st.checkbox("Trend Matrix Confluence", value=True)
    sop_vwap = st.checkbox("Price Action near VWAP", value=True)
    sop_vol = st.checkbox("Volume Confirmation", value=True)
    sop_macd_gate = st.checkbox("MACD Momentum Guard", value=True)
    
    st.divider()
    st.subheader("⚙️ VISUALS")
    show_macd_row = st.toggle("Show MACD Row", value=True)
    asset_choice = st.selectbox("Asset", ["XAUUSD (GOLD)", "US30 (DOW JONES)"])
    tf = st.radio("Timeframe", ["1m", "5m", "15m"], index=0, horizontal=True)
    
    if st.button("♻️ RESET SIGNAL LOCK", use_container_width=True):
        st.session_state.trade_lock = None
        st.rerun()

# 4. DATA ENGINE
ticker = "GC=F" if asset_choice == "XAUUSD (GOLD)" else "^DJI"
st_autorefresh(interval=10000, key="v8_sop_pulse")

try:
    df = yf.download(ticker, period="1d", interval=tf)
    if not df.empty:
        # Fix yfinance MultiIndex columns for 2026 compatibility
        if isinstance(df.columns, pd.MultiIndex): 
            df.columns = df.columns.get_level_values(0)
        
        # --- INDICATORS ---
        # VWAP
        df['VWAP'] = (((df['High'] + df['Low'] + df['Close']) / 3) * df['Volume']).cumsum() / df['Volume'].cumsum()
        # SMA 20
        df['SMA'] = df['Close'].rolling(20).mean()
        # ATR (for SL/TP)
        df['ATR'] = (df['High'] - df['Low']).rolling(14).mean()
        
        # RSI Engine
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        df['RSI'] = 100 - (100 / (1 + (gain / (loss + 1e-9))))
        
        # MACD Engine
        exp1 = df['Close'].ewm(span=12, adjust=False).mean()
        exp2 = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = exp1 - exp2
        df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        df['Hist'] = df['MACD'] - df['Signal']
        
        # ADX (Trend Strength)
        plus_dm = df['High'].diff().clip(lower=0)
        minus_dm = (-df['Low'].diff()).clip(lower=0)
        tr = pd.concat([df['High']-df['Low'], abs(df['High']-df['Close'].shift(1)), abs(df['Low']-df['Close'].shift(1))], axis=1).max(axis=1)
        atr = tr.rolling(14).mean()
        df['ADX'] = (abs((100 * (plus_dm.rolling(14).mean()/atr)) - (100 * (minus_dm.rolling(14).mean()/atr))) / 
                    ((100 * (plus_dm.rolling(14).mean()/atr)) + (100 * (minus_dm.rolling(14).mean()/atr))) * 100).rolling(14).mean()

        last = df.iloc[-1]
        atr_val = last['ATR'] if not pd.isna(last['ATR']) else 1.5
        
        # Directional Arrow Logic
        adx_arrow = "▲" if last['ADX'] > st.session_state.last_adx else "▼"
        st.session_state.last_adx = last['ADX']

        # SIDEBAR METER
        with st.sidebar:
            st.divider()
            st.subheader(f"⚡ TREND POWER: {last['ADX']:.1f}% {adx_arrow}")
            st.progress(min(last['ADX']/100, 1.0))

        # 5. SIGNAL LOGIC
        if st.session_state.trade_lock is None and sop_trend and sop_vwap and sop_vol and sop_macd_gate:
            # SELL Logic
            if last['Close'] < last['VWAP'] and last['Close'] < last['SMA'] and last['Hist'] < 0:
                st.session_state.trade_lock = {"type": "SELL", "en": last['Close'], "sl": last['Close'] + (atr_val*1.5), "tp": last['Close'] - (atr_val*3), "time": df.index[-1]}
                st.toast("🚨 SELL SIGNAL LOCKED")
            # BUY Logic
            elif last['Close'] > last['VWAP'] and last['Close'] > last['SMA'] and last['Hist'] > 0:
                st.session_state.trade_lock = {"type": "BUY", "en": last['Close'], "sl": last['Close'] - (atr_val*1.5), "tp": last['Close'] + (atr_val*3), "time": df.index[-1]}
                st.toast("💰 BUY SIGNAL LOCKED")

        # 6. CHARTING
        st.header(f"📊 {asset_choice} Terminal")
        n_rows = 3 if show_macd_row else 2
        r_heights = [0.5, 0.2, 0.3] if show_macd_row else [0.7, 0.3]
        
        fig = make_subplots(rows=n_rows, cols=1, shared_xaxes=True, vertical_spacing=0.04, row_heights=r_heights)

        # ROW 1
        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Market"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['VWAP'], line=dict(color='cyan', width=2), name='VWAP'), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['SMA'], line=dict(color='orange', width=1.5), name='SMA'), row=1, col=1)

        # ROW 2
        vol_colors = ['#ff4b4b' if r['Open'] > r['Close'] else '#00ff00' for _, r in df.iterrows()]
        fig.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color=vol_colors, name="Volume"), row=2, col=1)

        # ROW 3
        if show_macd_row:
            fig.add_trace(go.Scatter(x=df.index, y=df['MACD'], line=dict(color='#00E676', width=1), name='MACD'), row=3, col=1)
            fig.add_trace(go.Scatter(x=df.index, y=df['Signal'], line=dict(color='#FF5252', width=1), name='Signal'), row=3, col=1)
            h_colors = ['#00E676' if x > 0 else '#FF5252' for x in df['Hist']]
            fig.add_trace(go.Bar(x=df.index, y=df['Hist'], marker_color=h_colors, name='Hist'), row=3, col=1)

        # TRADE MARKERS
        if st.session_state.trade_lock:
            t = st.session_state.trade_lock
            fig.add_hline(y=t['en'], line_dash="dot", line_color="white", row=1, col=1)
            st.error(f"ACTIVE {t['type']} | Entry: {t['en']:.2f} | SL: {t['sl']:.2f} | TP: {t['tp']:.2f}")

        fig.update_layout(template="plotly_dark", height=800, xaxis_rangeslider_visible=False, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Screen Refreshing... If error persists, check Asset selection. Error: {e}")
