import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import hmac

# --- 1. SECURITY & BRANDING ---
def check_password():
    def credentials_entered():
        if (st.session_state["username"] == st.secrets["username"] and 
            hmac.compare_digest(st.session_state["password"], st.secrets["password"])):
            st.session_state["password_correct"] = True
            del st.session_state["password"]
            del st.session_state["username"]
        else: st.session_state["password_correct"] = False
    if st.session_state.get("password_correct", False): return True
    st.markdown('<h1 style="color:#00ff00; text-align:center;">🛡️ PATRO AI PRO</h1>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.text_input("User Identity", key="username")
        st.text_input("Command Key", type="password", key="password")
        st.button("INITIALIZE SYSTEM", on_click=credentials_entered, use_container_width=True)
    return False

st.set_page_config(page_title="PATRO AI PRO", layout="wide")
if not check_password(): st.stop()

# --- 2. DATA ENGINE ---
@st.cache_data(ttl=60)
def get_master_data():
    df = yf.download("^DJI", period="1d", interval="1m", progress=False)
    df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
    # Technical Indicators
    df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
    return df

df = get_master_data()

# --- 3. PRO DASHBOARD HEADER ---
st.markdown("<h1 style='text-align:center; color:#00ff00; letter-spacing: 5px; margin-bottom:0;'>PATRO AI PRO</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:gray; font-size:14px;'>Institutional Grade US30 Analysis</p>", unsafe_allow_html=True)

h1, h2, h3 = st.columns(3)
curr_price = df['Close'].iloc[-1]
ema_val = df['EMA20'].iloc[-1]
sig = "BUY" if curr_price > ema_val else "SELL"
sig_color = "#00ff00" if sig == "BUY" else "#ff4b4b"

h1.metric("US30 PRICE", f"${curr_price:,.2f}")
h2.metric("CURRENT SIGNAL", sig)
h3.metric("VOLUME SURGE", f"{df['Volume'].iloc[-1]:,.0f}")

# --- 4. THE CLEAN TERMINAL CHART ---
# Row 1: Price | Row 2: Volume
fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.8, 0.2])

# Main Candlesticks
fig.add_trace(go.Candlestick(
    x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
    name='Price'
), row=1, col=1)

# EMA Trend Line
fig.add_trace(go.Scatter(
    x=df.index, y=df['EMA20'], 
    name='Trend', 
    line=dict(color='orange', width=1.5)
), row=1, col=1)

# Volume Bars (Restored)
colors = ['#00ff00' if df['Close'].iloc[i] > df['Open'].iloc[i] else '#ff4b4b' for i in range(len(df))]
fig.add_trace(go.Bar(
    x=df.index, y=df['Volume'], 
    marker_color=colors, 
    name='Volume'
), row=2, col=1)

fig.update_layout(
    template='plotly_dark', 
    height=800, 
    xaxis_rangeslider_visible=False, 
    showlegend=False,
    margin=dict(t=10, b=10)
)
st.plotly_chart(fig, use_container_width=True)

# --- 5. SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='color:#00ff00;'>PATRO AI CONTROLS</h2>", unsafe_allow_html=True)
    if st.button("🔄 REFRESH SYSTEM"):
        st.cache_data.clear()
        st.rerun()
    st.divider()
    bal = st.number_input("Account Balance ($)", value=1000)
    risk = st.slider("Risk Management (%)", 0.5, 5.0, 1.0)
    st.error(f"Potential Loss: ${bal * (risk/100):.2f}")
    st.divider()
    st.caption("PATRO AI PRO v2.0 - Weekend Watch Active")
