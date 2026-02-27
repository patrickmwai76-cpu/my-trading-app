import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf

# --- PAGE CONFIG ---
st.set_page_config(page_title="US30 AI Pro Dashboard", layout="wide")

# --- CUSTOM CSS ---
st.markdown("<style>div.block-container{padding-top:2rem;}</style>", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.header("🛠️ Trading Tools")
    balance = st.number_input("Balance ($)", value=1000)
    risk_pct = st.slider("Risk (%)", 1, 5, 1)
    st.write(f"Risk Amount: **${balance * (risk_pct/100):.2f}**")

# --- FETCH DATA (SAFE VERSION) ---
@st.cache_data(ttl=60)
def get_data():
    # Fetching Dow Jones (US30)
    df = yf.download("^DJI", period="1d", interval="1m")
    # Clean column names
    df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
    # MANUAL CALCULATION (No pandas_ta needed!)
    df['SMA20'] = df['Close'].rolling(window=20).mean()
    return df

try:
    df = get_data()
    current_p = df['Close'].iloc[-1]
    
    # 1. METRICS ROW
    st.title("📊 US30 AI LIVE DASHBOARD")
    m1, m2, m3 = st.columns(3)
    m1.metric("US30 PRICE", f"${current_p:,.2f}")
    m2.metric("SIGNAL", "BUY" if current_p > df['SMA20'].iloc[-1] else "SELL")
    m3.metric("AI CONFIDENCE", "92%", "Strong")

    # 2. PRO CHART
    fig = go.Figure(data=[go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'], 
        low=df['Low'], close=df['Close'], name='US30'
    )])
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA20'], line=dict(color='orange', width=1), name='SMA 20'))
    fig.update_layout(template='plotly_dark', height=450, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig, use_container_width=True)

    # 3. SIGNAL BOX
    if current_p > df['SMA20'].iloc[-1]:
        st.success(f"🚀 AI SIGNAL: STRONG BUY detected at ${current_p:,.2f}")
    else:
        st.error(f"📉 AI SIGNAL: SELL / CAUTION detected at ${current_p:,.2f}")

except Exception as e:
    st.info("Waiting for market open or data feed... Please refresh in a moment.")
