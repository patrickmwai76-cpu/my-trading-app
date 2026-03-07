import streamlit as st
import pandas as pd
import pandas_ta as ta
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- 1. PREMIUM CLOUD UI ---
st.set_page_config(page_title="PATRO AI PRO V11.6", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #050505; color: white; }
    header, footer, #MainMenu {visibility: hidden;}
    
    .signal-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 25px;
        text-align: center;
        margin-bottom: 20px;
    }
    .stButton > button {
        width: 100%; border-radius: 12px; height: 3em; font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA ENGINE (Cloud Stable) ---
@st.cache_data(ttl=15)
def get_cloud_data(ticker, interval):
    # Fetching 5 days to ensure SMA 200 calculates correctly
    df = yf.download(ticker, period="5d", interval=interval, auto_adjust=True, progress=False)
    if df.empty: return None
    
    # FIX: Flatten MultiIndex columns (crucial for Streamlit Cloud)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    # Technical Indicators
    df['VWAP'] = ta.vwap(df['High'], df['Low'], df['Close'], df['Volume'])
    df['SMA200'] = ta.sma(df['Close'], length=200)
    df['RSI'] = ta.rsi(df['Close'], length=14)
    df['ADX'] = ta.adx(df['High'], df['Low'], df['Close'])['ADX_14']
    
    # Logic: Filter for first trend change signal
    df['Raw'] = 0
    df.loc[(df['Close'] > df['VWAP']) & (df['ADX'] > 25), 'Raw'] = 1
    df.loc[(df['Close'] < df['VWAP']) & (df['ADX'] > 25), 'Raw'] = -1
    df['Entry'] = df['Raw'].diff().fillna(0)
    
    return df.dropna()

# --- 3. DASHBOARD ---
with st.sidebar:
    st.title("🌌 PATRO AI")
    asset = st.selectbox("Market", ["GC=F", "EURUSD=X", "GBPUSD=X"], format_func=lambda x: "GOLD (XAUUSD.m)" if x=="GC=F" else x)
    tf = st.selectbox("Timeframe", ["1m", "5m", "15m"], index=1)
    risk = st.slider("Risk %", 0.5, 5.0, 1.0)

data = get_cloud_data(asset, tf)

if data is not None:
    last = data.iloc[-1]
    status_clr = "#00FF88" if last['Raw'] == 1 else "#FF3366" if last['Raw'] == -1 else "#777"
    status_txt = "STRONG BUY" if last['Raw'] == 1 else "STRONG SELL" if last['Raw'] == -1 else "WAITING..."

    # Visual Signal Header
    st.markdown(f"""
        <div class="signal-card" style="border-top: 5px solid {status_clr};">
            <h1 style="color: {status_clr}; margin:0;">{status_txt}</h1>
            <p style="opacity:0.6;">JUSTMARKETS XAUUSD.m | ADX: {last['ADX']:.1f}</p>
        </div>
    """, unsafe_allow_html=True)

    # Manual Trade Buttons (For Visual Feedback)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🚀 PREPARE BUY"): st.toast("Signal Confirmed: Long Position")
    with c2:
        if st.button("📉 PREPARE SELL"): st.toast("Signal Confirmed: Short Position")

    # --- PROFESSIONAL CHARTING ---
    fig = make_subplots(rows=1, cols=1)
    fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name="Price"))
    
    # Add Signal Arrows
    buys = data[data['Entry'] == 1]
    sells = data[data['Entry'] == -1]
    fig.add_trace(go.Scatter(x=buys.index, y=buys['Low']*0.999, mode="markers", marker=dict(symbol="triangle-up", size=12, color="#00FF88"), name="Buy Signal"))
    fig.add_trace(go.Scatter(x=sells.index, y=sells['High']*1.001, mode="markers", marker=dict(symbol="triangle-down", size=12, color="#FF3366"), name="Sell Signal"))
    
    fig.add_trace(go.Scatter(x=data.index, y=data['VWAP'], line=dict(color='orange', width=1), name="VWAP"))
    fig.update_layout(height=600, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig, use_container_width=True)
