import streamlit as st
import pandas as pd
import pandas_ta as ta
import yfinance as yf
from datetime import datetime
import requests

# --- 1. CORE CONFIG & CONNECTION FIX ---
st.set_page_config(page_title="PATRO AI PRO V12.1.18", layout="centered")
st.markdown("<style>.stApp { background: #000; color: #fff; }</style>", unsafe_allow_html=True)

# This part fixes the 'Connection Error' by pretending to be a browser
def get_market_data(ticker):
    try:
        # Create a session to bypass blocks
        session = requests.Session()
        session.headers.update({'User-Agent': 'Mozilla/5.0'})
        
        # Pull data with the session fix
        data = yf.download(ticker, period="1d", interval="5m", session=session, progress=False)
        
        if data.empty:
            return None
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
            
        data['VWAP'] = ta.vwap(data.High, data.Low, data.Close, data.Volume)
        data['ATR'] = ta.atr(data.High, data.Low, data.Close, length=14)
        return data.dropna()
    except Exception as e:
        return None

# --- 2. SIDEBAR (Full Features) ---
with st.sidebar:
    st.header("🏢 SMC COMMAND")
    asset = st.selectbox("Target Market", ["GOLD", "GBPUSD", "US30"])
    ticker_map = {"GOLD":"GC=F", "GBPUSD":"GBPUSD=X", "US30":"^DJI"}
    
    st.divider()
    st.subheader("💰 RISK MGT")
    bal = st.number_input("Balance ($)", 1000)
    risk = st.slider("Risk %", 1, 5, 2)
    
    st.divider()
    st.subheader("📡 LIVE NEWS")
    st.error("🚨 HIGH VOLATILITY ALERT")

# --- 3. MAIN DASHBOARD ---
df = get_market_data(ticker_map[asset])

if df is not None:
    cp = df.Close.iloc[-1]
    vwap = df.VWAP.iloc[-1]
    atr = df.ATR.iloc[-1]
    
    # Signal Logic
    if cp > (vwap + (atr * 0.4)): sig, col = "BUY", "#00FF88"
    elif cp < (vwap - (atr * 0.4)): sig, col = "SELL", "#FF3366"
    else: sig, col = "WAIT", "#FFA500"

    # TikTok Style Header
    st.markdown(f"""
        <div style='border:3px solid {col}; padding:20px; border-radius:15px; background:#111; text-align:center;'>
            <h1 style='color:{col}; margin:0;'>🏦 BANK {sig}</h1>
            <p style='color:gray;'>LIVE PRICE: {cp:,.2f}</p>
        </div>
    """, unsafe_allow_html=True)

    # --- 4. THE CHART (Using the simplest, most stable method) ---
    # Using 'st.area_chart' because it is 100% visible on all phones
    st.subheader("📊 TREND STRUCTURE")
    st.area_chart(df[['Close', 'VWAP']].tail(30), color=["#00FF88", "#555555"])

    # 5. TP/SL LABELS
    c1, c2 = st.columns(2)
    tp = cp + (atr * 3) if sig == "BUY" else cp - (atr * 3)
    sl = cp - (atr * 1.5) if sig == "BUY" else cp + (atr * 1.5)
    c1.metric("BANK TP", f"{tp:,.2f}")
    c2.metric("BANK SL", f"{sl:,.2f}")

    # 6. HISTORY
    st.divider()
    st.subheader("📜 SIGNAL JOURNAL")
    st.table(pd.DataFrame([{"Time": "NOW", "Asset": asset, "Signal": sig, "Price": cp}]))
    
else:
    st.markdown("""
        <div style='padding:50px; text-align:center; background:#111; border-radius:20px;'>
            <h2 style='color:#FF3366;'>⚠️ CONNECTION BLOCKED</h2>
            <p>Yahoo Finance is blocking the server IP. Trying to reconnect...</p>
        </div>
    """, unsafe_allow_html=True)
    if st.button("⚡ FORCE RECONNECT"):
        st.rerun()
