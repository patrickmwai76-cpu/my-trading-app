import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import pytz
import hmac

# --- 1. SETUP & THEME ---
st.set_page_config(page_title="PATRO AI PRO | US30", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117 !important; }
    [data-testid="stMetric"] {
        background-color: #1e2130 !important; 
        border: 2px solid #00ff00 !important;
        border-radius: 12px !important;
        padding: 20px !important;
    }
    [data-testid="stMetricValue"] { color: #00ff00 !important; font-size: 32px !important; font-weight: 800 !important; }
    [data-testid="stMetricLabel"] { color: #ffffff !important; font-size: 18px !important; }
    .status-live { color: #00ff00; font-weight: bold; border: 1px solid #00ff00; padding: 5px 10px; border-radius: 5px; }
    .status-closed { color: #ff4b4b; font-weight: bold; border: 1px solid #ff4b4b; padding: 5px 10px; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SECURITY (GATEKEEPER) ---
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

    st.markdown('<h1 style="color:#00ff00; text-align:center;">🛡️ PATRO AI PRO</h1>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.text_input("User Identity", key="username", placeholder="Enter Username")
        st.text_input("Command Key", type="password", key="password", placeholder="Enter Password")
        st.button("INITIALIZE SYSTEM", on_click=credentials_entered)
        if "password_correct" in st.session_state and not st.session_state["password_correct"]:
            st.error("🚫 AUTHENTICATION FAILED")
    return False

if not check_password():
    st.stop()

# --- 3. DATA ENGINE ---
@st.cache_data(ttl=60)
def get_patro_data():
    # Fetching Dow Jones (US30)
    df = yf.download("^DJI", period="1d", interval="1m")
    df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
    
    # Technical Indicators
    df['SMA20'] = df['Close'].rolling(window=20).mean()
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    df['RSI'] = 100 - (100 / (1 + (gain / loss)))
    
    return df, df['High'].max(), df['Low'].min()

# --- 4. MAIN TERMINAL UI ---
try:
    df, d_high, d_low = get_patro_data()
    
    # Market Status Logic
    now_ny = datetime.now(pytz.utc).astimezone(pytz.timezone('US/Eastern'))
    # Weekend or after-hours check
    is_open = now_ny.weekday() < 5 and 9 <= now_ny.hour < 16
    status_html = '<span class="status-live">🟢 MARKET LIVE</span>' if is_open else '<span class="status-closed">🔴 MARKET CLOSED</span>'

    # Header
    col_t1, col_t2 = st.columns([2, 1])
    col_t1.markdown(f'<h1 style="color:#00ff00; margin:0;">🛡️ PATRO AI PRO</h1>', unsafe_allow_html=True)
    col_t2.markdown(f'<div style="text-align:right; margin-top:20px;">{status_html}</div>', unsafe_allow_html=True)
    st.divider()

    # Live Metrics
    curr_p = df['Close'].iloc[-1]
    last_sma = df['SMA20'].iloc[-1]
    last_rsi = df['RSI'].iloc[-1]
    
    # Simple Signal Logic
    signal = "BUY" if curr_p > last_sma else "SELL"
    
    m1, m2, m3 = st.columns(3)
    m1.metric("US30 PRICE", f"${curr_p:,.2f}")
    m2.metric("CURRENT SIGNAL", signal)
    m3.metric("RSI (14)", f"{last_rsi:.2f}")

    # Charts
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.7, 0.3])
    
    # Candlesticks
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='Price'), row=1, col=1)
    # SMA Line
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA20'], name='Trend (SMA 20)', line=dict(color='orange', width=2)), row=1, col=1)
    # High/Low Lines
    fig.add_hline(y=d_high, line_dash="dash", line_color="#00ffff", annotation_text="DAY HIGH", row=1, col=1)
    fig.add_hline(y=d_low, line_dash="dash", line_color="#ff4b4b", annotation_text="DAY LOW", row=1, col=1)
    
    # RSI Chart
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name='RSI', line=dict(color='#8A2BE2')), row=2, col=1)
    fig.add_hline(y=70, line_dash="dot", line_color="red", row=2, col=1)
    fig.add_hline(y=30, line_dash="dot", line_color="green", row=2, col=1)

    fig.update_layout(template='plotly_dark', height=650, xaxis_rangeslider_visible=False, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)

    # --- 5. THE PATRO RULE OF CONFLUENCE ---
    st.divider()
    st.markdown("<h2 style='color: #00ff00; text-align: center;'>🛡️ THE PATRO RULE OF CONFLUENCE</h2>", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        <div style="background-color: #1e2130; padding: 20px; border-radius: 10px; border-left: 5px solid #00ff00;">
            <h3 style="color: #00ff00;">🟢 STRONG BUY SETUP</h3>
            <p style="color: white;">1. <b>Trend:</b> Price is ABOVE Orange SMA 20.</p>
            <p style="color: white;">2. <b>Momentum:</b> RSI is pointing UP and > 50.</p>
            <p style="color: white;">3. <b>Entry:</b> Terminal flashes <b>BUY</b> label.</p>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div style="background-color: #1e2130; padding: 20px; border-radius: 10px; border-left: 5px solid #ff4b4b;">
            <h3 style="color: #ff4b4b;">🔴 STRONG SELL SETUP</h3>
            <p style="color: white;">1. <b>Trend:</b> Price is BELOW Orange SMA 20.</p>
            <p style="color: white;">2. <b>Momentum:</b> RSI is pointing DOWN and < 50.</p>
            <p style="color: white;">3. <b>Entry:</b> Terminal flashes <b>SELL</b> label.</p>
        </div>
        """, unsafe_allow_html=True)

except Exception as e:
    st.info("System initializing... Waiting for Market Data.")
