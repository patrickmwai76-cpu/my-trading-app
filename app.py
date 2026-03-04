import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
import pandas_ta as ta

# --- 1. SETUP & THEME ---
st.set_page_config(page_title="PATRO AI PRO V8.7", layout="wide")

# --- 2. SIDEBAR ---
with st.sidebar:
    st.title("🛡️ PATRO AI PRO")
    
    # News Guard Toggle
    news_mode = st.toggle("ACTIVATE NEWS GUARD", value=True)
    if news_mode:
        st.warning("⚠️ STRICT: Red Arrow blocks entry")

    # Asset & Timeframe
    asset_choice = st.selectbox("SELECT ASSET", ["XAUUSD (GOLD)", "US30 (DOW JONES)"])
    tf = st.selectbox("TIMEFRAME", ["1m", "5m", "15m", "1h"], index=0)
    
    # Sync Button
    if st.button("🔄 FORCE DATA SYNC"):
        st.cache_data.clear()
        st.rerun()

# --- 3. DATA ENGINE ---
ticker = "GC=F" if asset_choice == "XAUUSD (GOLD)" else "^DJI"
st_autorefresh(interval=10000, key="v8_sop_pulse")

try:
    df = yf.download(ticker, period="2d", interval=tf)
    
    if df.empty or len(df) < 20:
        st.error("⚠️ DATA HEAVY. CLICK FORCE SYNC.")
        st.stop()

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # --- 4. INDICATORS ---
    df['SMA'] = ta.sma(df['Close'], length=20)
    df['VWAP'] = (df['Close'] * df['Volume']).cumsum() / df['Volume'].cumsum()
    
    macd = ta.macd(df['Close'])
    df = pd.concat([df, macd], axis=1)
    
    adx_df = ta.adx(df['High'], df['Low'], df['Close'])
    df['ADX'] = adx_df['ADX_14']
    
    last = df.iloc[-1]
    prev = df.iloc[-2]

    # --- 5. POWER METER (SIDEBAR) ---
    adx_val = last['ADX'] if not pd.isna(last['ADX']) else 0.0
    prev_adx = prev['ADX'] if not pd.isna(prev['ADX']) else 0.0
    
    arrow = "▲" if adx_val > prev_adx else "▼"
    color = "green" if adx_val > prev_adx else "red"
    
    with st.sidebar:
        st.divider()
        st.markdown(f"### ⚡ POWER: {adx_val:.1f}% :{color}[{arrow}]")
        st.progress(min(max(adx_val / 100, 0.0), 1.0))

    # --- 6. SIGNAL LOGIC ---
    entry_allowed = True
    if news_mode and arrow == "▼":
        entry_allowed = False

    if entry_allowed:
        if last['Close'] < last['VWAP'] and last['MACD_12_26_9'] < 0:
            st.success("🎯 INSTITUTIONAL SELL READY")
        elif last['Close'] > last['VWAP'] and last['MACD_12_26_9'] > 0:
            st.success("🎯 INSTITUTIONAL BUY READY")
    else:
        st.info("🕒 WAITING FOR GREEN MOMENTUM ARROW...")

    # --- 7. CHARTING (FIXED LINE) ---
    fig = go.Figure(data=[go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"
    )])
    
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA'], name="SMA", line=dict(color='orange')))
    fig.add_trace(go.Scatter(x=df.index, y=df['VWAP'], name="VWAP", line=dict(color='cyan')))

    fig.update_layout(xaxis_rangeslider_visible=False, template="plotly_dark", height=600)
    
    # This line is restored to work with your Streamlit version
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.info("📡 CONNECTING TO EXCHANGE FEED...")
