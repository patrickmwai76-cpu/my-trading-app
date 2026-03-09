import streamlit as st
import pandas as pd
import pandas_ta as ta
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# --- 1. CLOUD-SAFE AUDIO ---
WINDOWS_AUDIO = False
if os.name == 'nt':
    try:
        import winsound
        WINDOWS_AUDIO = True
    except: pass

# --- 2. THE ERROR-PROOF DATA ENGINE ---
def get_market_data(ticker, tf="1m"):
    try:
        # Download and force a simple format
        df = yf.download(ticker, period="5d", interval=tf, progress=False, auto_adjust=True)
        if df.empty: return pd.DataFrame()
        
        # FIX: Flatten MultiIndex if it exists
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        df.index = pd.to_datetime(df.index)
        return df
    except Exception as e:
        st.error(f"Data Error: {e}")
        return pd.DataFrame()

# --- 3. UI SETUP ---
st.set_page_config(page_title="PATRO AI PRO V11.6", layout="wide")
st.markdown("<style>.stApp { background: #050505; color: white; }</style>", unsafe_allow_html=True)

with st.sidebar:
    st.title("🌌 PATRO V11.6")
    assets = {"GOLD": "GC=F", "GBPUSD": "GBPUSD=X", "US30": "^DJI"}
    choice = st.selectbox("Asset", list(assets.keys()))
    ticker = assets[choice]
    main_tf = st.radio("Timeframe", ["1m", "5m", "15m"], index=1, horizontal=True)
    matrix_spot = st.empty()

# --- 4. CORE ENGINE ---
@st.fragment(run_every="7s")
def start_patro():
    # 4a. Trend Matrix (Multi-Timeframe)
    matrix_data = []
    for tf in ["1m", "5m", "15m"]:
        m_df = get_market_data(ticker, tf=tf)
        if not m_df.empty and len(m_df) > 2:
            # DIRECT VALUE PASSING (Avoids Column Name Errors)
            vwap_vals = ta.vwap(high=m_df['High'], low=m_df['Low'], close=m_df['Close'], volume=m_df['Volume'])
            if vwap_vals is not None:
                bias = "🟢" if m_df['Close'].iloc[-1] > vwap_vals.iloc[-1] else "🔴"
                matrix_data.append({"TF": tf, "Trend": bias})
    
    with matrix_spot.container():
        st.table(pd.DataFrame(matrix_data))

    # 4b. Main Analysis & Charting
    df = get_market_data(ticker, tf=main_tf)
    if not df.empty and len(df) > 20:
        # Calculate VWAP using Direct Arguments
        df['VWAP'] = ta.vwap(high=df['High'], low=df['Low'], close=df['Close'], volume=df['Volume'])
        df['RSI'] = ta.rsi(df['Close'], length=14)
        
        last_price = df['Close'].iloc[-1]
        last_vwap = df['VWAP'].iloc[-1]
        
        # UI Header
        c1, c2 = st.columns(2)
        with c1:
            color = "#00FF88" if last_price > last_vwap else "#FF3366"
            st.markdown(f"### BIAS: <span style='color:{color}'>{'BULL' if last_price > last_vwap else 'BEAR'}</span>", unsafe_allow_html=True)
        with c2:
            st.metric("RSI (14)", int(df['RSI'].iloc[-1]))

        # Pro Charting
        fig = make_subplots(rows=1, cols=1)
        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"))
        fig.add_trace(go.Scatter(x=df.index, y=df['VWAP'], line=dict(color='orange', width=2), name="VWAP"))
        fig.update_layout(height=600, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True, key=f"p_{choice}")

        # Local Audio Alert
        if WINDOWS_AUDIO and df['Volume'].iloc[-1] > (df['Volume'].mean() * 3):
            winsound.Beep(1000, 200)

start_patro()
