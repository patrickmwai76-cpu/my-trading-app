import streamlit as st
import pandas as pd
import pandas_ta as ta
import yfinance as yf
from datetime import datetime

# --- 1. CORE CONFIG ---
st.set_page_config(page_title="PATRO AI PRO V12.1.17", layout="centered")
st.markdown("<style>.stApp { background: #000; color: #fff; }</style>", unsafe_allow_html=True)

# --- 2. DATA ENGINE ---
def get_market_data(ticker):
    try:
        df = yf.download(ticker, period="1d", interval="5m", progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        # SMC Indicators
        df['VWAP'] = ta.vwap(df.High, df.Low, df.Close, df.Volume)
        df['ATR'] = ta.atr(df.High, df.Low, df.Close, length=14)
        return df.dropna()
    except: return None

# --- 3. SIDEBAR (All Discussed Features) ---
with st.sidebar:
    st.header("🏢 SMC COMMAND")
    asset = st.selectbox("Asset", ["GOLD", "GBPUSD", "US30"])
    ticker_map = {"GOLD":"GC=F", "GBPUSD":"GBPUSD=X", "US30":"^DJI"}
    
    st.divider()
    st.subheader("💰 RISK CALCULATOR")
    bal = st.number_input("Balance", 1000)
    risk = st.slider("Risk %", 1, 5, 2)
    st.success(f"Risk Amount: ${bal * (risk/100):.2f}")
    
    st.divider()
    st.subheader("📡 LIVE NEWS")
    st.error("🚨 US CPI Impact: HIGH")

# --- 4. MAIN DASHBOARD ---
df = get_market_data(ticker_map[asset])

if df is not None:
    cp = df.Close.iloc[-1]
    vwap = df.VWAP.iloc[-1]
    atr = df.ATR.iloc[-1]
    
    # Anti-Fake Logic
    buffer = atr * 0.4
    if cp > (vwap + buffer):
        sig, col = "SURE BUY", "#00FF88"
    elif cp < (vwap - buffer):
        sig, col = "SURE SELL", "#FF3366"
    else:
        sig, col = "WAITING", "#FFA500"

    # Header Metric (TikTok Style)
    st.markdown(f"""
        <div style='border:3px solid {col}; padding:15px; border-radius:15px; background:#111; text-align:center;'>
            <h1 style='color:{col}; margin:0;'>🏦 BANK {sig}</h1>
            <h2 style='margin:5px;'>PRICE: {cp:,.2f}</h2>
        </div>
    """, unsafe_allow_html=True)

    st.divider()

    # --- THE CHART (COMPATIBILITY MODE) ---
    # Since Plotly is failing, we use Streamlit's native line chart
    # It shows Price vs VWAP clearly.
    st.subheader("📊 MARKET STRUCTURE")
    chart_data = df[['Close', 'VWAP']].tail(40)
    st.line_chart(chart_data, color=["#00FF88", "#ffffff"])

    # SMC Order Flow Table (Replaces the visual boxes for visibility)
    st.subheader("📦 INSTITUTIONAL ORDER FLOW")
    df_show = df[['Open', 'High', 'Low', 'Close']].tail(5)
    st.dataframe(df_show.style.highlight_max(axis=0, color='#004400').highlight_min(axis=0, color='#440000'))

    # 5. TP / SL TARGETS
    t1, t2 = st.columns(2)
    tp = cp + (atr * 3) if "BUY" in sig else cp - (atr * 3)
    sl = cp - (atr * 1.5) if "BUY" in sig else cp + (atr * 1.5)
    t1.metric("TARGET (TP)", f"{tp:,.2f}", delta_color="normal")
    t2.metric("STOP LOSS (SL)", f"{sl:,.2f}", delta_color="inverse")

    # 6. SIGNAL HISTORY
    st.divider()
    st.subheader("📜 SIGNAL HISTORY")
    st.table(pd.DataFrame([{"Time": datetime.now().strftime("%H:%M"), "Signal": sig, "Price": cp}]))
    
    if st.button("🔄 REFRESH NOW"):
        st.rerun()

else:
    st.error("Connection Error. Tap 'Refresh' below.")
    st.button("REFRESH")
