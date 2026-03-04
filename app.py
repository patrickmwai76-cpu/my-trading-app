import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from streamlit_autorefresh import st_autorefresh
from plotly.subplots import make_subplots

# 1. SETUP
st.set_page_config(page_title="PATRO AI PRO V8.8", layout="wide")
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

# 3. SIDEBAR & NEWS GUARD
with st.sidebar:
    st.title("🎮 CONTROL")
    news_mode = st.toggle("ACTIVATE NEWS GUARD", value=True)
    if st.button("🔄 FORCE DATA SYNC"):
        st.cache_data.clear()
        st.rerun()
    
    st.divider()
    asset_choice = st.selectbox("Asset", ["XAUUSD (GOLD)", "US30 (DOW JONES)"])
    tf = st.radio("Timeframe", ["1m", "5m", "15m"], index=0, horizontal=True)

# 4. DATA ENGINE
ticker = "GC=F" if asset_choice == "XAUUSD (GOLD)" else "^DJI"
st_autorefresh(interval=10000, key="v8_sop_pulse")

try:
    df = yf.download(ticker, period="2d", interval=tf)
    if df.empty or len(df) < 30:
        st.error("⚠️ MARKET DATA HEAVY. Waiting for server...")
        st.stop()

    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    df = df.ffill().dropna()

    # INDICATORS
    df['VWAP'] = (((df['High'] + df['Low'] + df['Close']) / 3) * df['Volume']).cumsum() / (df['Volume'].cumsum() + 1e-9)
    df['SMA'] = df['Close'].rolling(20).mean()
    
    # ADX MATH (Safe Version)
    plus_dm = df['High'].diff().clip(lower=0)
    minus_dm = (-df['Low'].diff()).clip(lower=0)
    tr = pd.concat([df['High']-df['Low'], abs(df['High']-df['Close'].shift(1)), abs(df['Low']-df['Close'].shift(1))], axis=1).max(axis=1)
    atr = tr.rolling(14).mean().replace(0, np.nan)
    df['ADX'] = (abs((100*(plus_dm.rolling(14).mean()/atr)) - (100*(minus_dm.rolling(14).mean()/atr))) / 
                ((100*(plus_dm.rolling(14).mean()/atr)) + (100*(minus_dm.rolling(14).mean()/atr)) + 1e-9) * 100).rolling(14).mean()
    
    last = df.iloc[-1]
    prev = df.iloc[-2]
    
    # 5. SAFE POWER METER (No NaN Errors)
    with st.sidebar:
        adx_val = last['ADX'] if not pd.isna(last['ADX']) else 0.0
        prev_adx = prev['ADX'] if not pd.isna(prev['ADX']) else 0.0
        arrow = "▲" if adx_val > prev_adx else "▼"
        color = "green" if adx_val > prev_adx else "red"
        st.markdown(f"### ⚡ POWER: {adx_val:.1f}% :{color}[{arrow}]")
        st.progress(min(max(adx_val/100, 0.0), 1.0))

    # 6. SIGNAL LOGIC (News Mode Filter)
    arrow_ok = True if (not news_mode or adx_val > prev_adx) else False

    if st.session_state.trade_lock is None and arrow_ok:
        if last['Close'] < last['VWAP'] and last['Close'] < last['SMA']:
            st.session_state.trade_lock = {"type": "SELL", "en": last['Close']}
        elif last['Close'] > last['VWAP'] and last['Close'] > last['SMA']:
            st.session_state.trade_lock = {"type": "BUY", "en": last['Close']}

    # 7. CHARTING (Legacy Fix)
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3])
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close']), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['VWAP'], line=dict(color='cyan')), row=1, col=1)
    fig.update_layout(template="plotly_dark", height=600, xaxis_rangeslider_visible=False)
    
    # Final Chart Display - Fixed for your version
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.info("📡 Syncing Feed...")
