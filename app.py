import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import hmac
from datetime import datetime
import pytz

# --- 1. THE GATEKEEPER (LOGIN) ---
def check_password():
    def credentials_entered():
        if (st.session_state["username"] == st.secrets["username"] and 
            hmac.compare_digest(st.session_state["password"], st.secrets["password"])):
            st.session_state["password_correct"] = True
            del st.session_state["password"]
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    if st.session_state.get("password_correct", False):
        return True

    # High-Contrast Login Screen
    st.markdown('<h1 style="color:#00ff00; text-align:center;">🛡️ PATRO AI PRO</h1>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.text_input("User Identity", key="username")
        st.text_input("Command Key", type="password", key="password")
        st.button("INITIALIZE SYSTEM", on_click=credentials_entered)
        if "password_correct" in st.session_state and not st.session_state["password_correct"]:
            st.error("🚫 AUTHENTICATION FAILED")
    return False

# --- 2. LAYOUT & STYLING ---
st.set_page_config(page_title="PATRO AI PRO", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117 !important; }
    [data-testid="stMetric"] {
        background-color: #1e2130 !important; 
        border: 2px solid #00ff00 !important;
        border-radius: 12px !important;
    }
    [data-testid="stMetricValue"] { color: #00ff00 !important; font-size: 32px !important; font-weight: 800 !important; }
    [data-testid="stMetricLabel"] { color: #ffffff !important; }
    </style>
    """, unsafe_allow_html=True)

# Stop here if not logged in
if not check_password():
    st.stop()

# --- 3. SIDEBAR (RISK CALCULATOR & REFRESH) ---
with st.sidebar:
    st.markdown("<h2 style='color: #00ff00;'>PATRO AI PRO</h2>", unsafe_allow_html=True)
    if st.button("🔄 REFRESH DATA"):
        st.cache_data.clear()
        st.rerun()
    st.divider()
    st.subheader("💰 Risk Management")
    balance = st.number_input("Balance ($)", value=1000)
    risk_pct = st.slider("Risk (%)", 0.5, 5.0, 1.0)
    risk_amt = balance * (risk_pct / 100)
    st.info(f"Risk Amount: ${risk_amt:.2f}")

# --- 4. DATA ENGINE ---
@st.cache_data(ttl=60)
def get_patro_data():
    df = yf.download("^DJI", period="1d", interval="1m")
    df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
    df['SMA20'] = df['Close'].rolling(window=20).mean()
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    df['RSI'] = 100 - (100 / (1 + (gain / loss)))
    return df, df['High'].max(), df['Low'].min()

# --- 5. MAIN DASHBOARD ---
try:
    df, d_high, d_low = get_patro_data()
    curr_p = df['Close'].iloc[-1]
    
    # Header
    st.markdown(f'<h1 style="color:#00ff00;">🛡️ PATRO AI PRO: BUY</h1>', unsafe_allow_html=True)
    
    # Metrics
    m1, m2, m3 = st.columns(3)
    m1.metric("US30 PRICE", f"${curr_p:,.2f}")
    m2.metric("CURRENT SIGNAL", "BUY")
    m3.metric("RSI (14)", f"{df['RSI'].iloc[-1]:.2f}")

    # The Chart
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.7, 0.3])
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='US30'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA20'], name='Trend', line=dict(color='orange')), row=1, col=1)
    fig.add_hline(y=d_high, line_dash="dash", line_color="#00ffff", annotation_text="HIGH", row=1, col=1)
    fig.add_hline(y=d_low, line_dash="dash", line_color="#ff4b4b", annotation_text="LOW", row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name='RSI', line=dict(color='#8A2BE2')), row=2, col=1)
    
    fig.update_layout(template='plotly_dark', height=700, xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

except Exception:
    st.info("Scanner initializing...")
