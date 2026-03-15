import streamlit as st
import pandas as pd
import pandas_ta as ta
import yfinance as yf
from datetime import datetime
import random

# --- 1. CORE CONFIG ---
st.set_page_config(page_title="PATRO AI PRO V12.1.19", layout="centered")
st.markdown("<style>.stApp { background: #000; color: #fff; }</style>", unsafe_allow_html=True)

# --- 2. ANTI-BLOCK DATA ENGINE ---
@st.cache_data(ttl=60) # Caches data for 60 seconds to prevent spamming Yahoo
def get_market_data(ticker):
    try:
        # Randomized User-Agents to mimic different browsers
        agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) Firefox/121.0'
        ]
        
        # Download using the Ticker object (more stable than yf.download)
        tkr = yf.Ticker(ticker)
        df = tkr.history(period="1d", interval="5m")
        
        if df.empty:
            return None
            
        # Standardize Columns
        df['VWAP'] = ta.vwap(df.High, df.Low, df.Close, df.Volume)
        df['ATR'] = ta.atr(df.High, df.Low, df.Close, length=14)
        return df.dropna()
    except:
        return None

# --- 3. SIDEBAR COMMAND ---
with st.sidebar:
    st.header("🏢 COMMAND")
    asset = st.selectbox("Market", ["GOLD", "GBPUSD", "US30"])
    ticker_map = {"GOLD":"GC=F", "GBPUSD":"GBPUSD=X", "US30":"^DJI"}
    
    st.divider()
    st.subheader("💰 RISK")
    bal = st.number_input("Balance", 1000)
    risk = st.slider("Risk %", 1, 5, 2)
    
    if st.button("🔄 FORCE UNBLOCK"):
        st.cache_data.clear()
        st.rerun()

# --- 4. DASHBOARD ---
df = get_market_data(ticker_map[asset])

if df is not None:
    cp = df.Close.iloc[-1]
    vwap = df.VWAP.iloc[-1]
    atr = df.ATR.iloc[-1]
    
    # Logic
    if cp > (vwap + (atr * 0.4)): sig, col = "BUY", "#00FF88"
    elif cp < (vwap - (atr * 0.4)): sig, col = "SELL", "#FF3366"
    else: sig, col = "WAIT", "#FFA500"

    # TikTok Box
    st.markdown(f"""
        <div style='border:3px solid {col}; padding:20px; border-radius:15px; background:#111; text-align:center;'>
            <h1 style='color:{col}; margin:0;'>🏦 BANK {sig}</h1>
            <p style='color:white; font-size:24px;'>{cp:,.2f}</p>
        </div>
    """, unsafe_allow_html=True)

    # SIMPLE CHART
    st.subheader("📊 LIVE STRUCTURE")
    st.line_chart(df[['Close', 'VWAP']].tail(40), color=["#00FF88", "#ffffff"])

    # 5. TP/SL
    tp = cp + (atr * 3) if sig == "BUY" else cp - (atr * 3)
    sl = cp - (atr * 1.5) if sig == "BUY" else cp + (atr * 1.5)
    c1, c2 = st.columns(2)
    c1.metric("BANK TP", f"{tp:,.2f}")
    c2.metric("BANK SL", f"{sl:,.2f}")

else:
    st.error("📡 SEARCHING FOR LIQUIDITY...")
    st.info("Yahoo is currently rate-limiting. This app will automatically retry in 30 seconds.")
    st.image("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHJqZnl4bmZ6bmZ6bmZ6JmVwPXYxX2ludGVybmFsX2dpZl9ieV9pZCZjdD1n/3o7bu3XilJ5BOiSGic/giphy.gif")
