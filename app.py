import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import hmac
from datetime import datetime
import pytz

# --- 1. SECURITY & STYLE ---
def check_password():
    def credentials_entered():
        if (st.session_state["username"] == st.secrets["username"] and 
            hmac.compare_digest(st.session_state["password"], st.secrets["password"])):
            st.session_state["password_correct"] = True
            del st.session_state["password"]
            del st.session_state["username"]
        else: st.session_state["password_correct"] = False
    if st.session_state.get("password_correct", False): return True
    
    # Login Screen Styling
    st.markdown("""
        <style>
        .stApp { background-color: #0e1117; }
        .login-header { color: #00ff00; text-align: center; font-family: 'Courier New', Courier, monospace; }
        </style>
        <h1 class="login-header">🛡️ PATRO AI PRO INITIALIZATION</h1>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.text_input("User Identity", key="username")
        st.text_input("Command Key", type="password", key="password")
        st.button("BOOT SYSTEM", on_click=credentials_entered, use_container_width=True)
    return False

st.set_page_config(page_title="PATRO AI PRO", layout="wide")
if not check_password(): st.stop()

# --- 2. DATA ENGINES ---
@st.cache_data(ttl=60)
def get_mtf_trend(ticker, interval):
    try:
        data = yf.download(ticker, period="2d", interval=interval, progress=False)
        data.columns = [col[0] if isinstance(col, tuple) else col for col in data.columns]
        sma = data['Close'].rolling(window=20).mean()
        return "UP" if data['Close'].iloc[-1] > sma.iloc[-1] else "DOWN"
    except: return "N/A"

@st.cache_data(ttl=60)
def get_main_data():
    df = yf.download("^DJI", period="1d", interval="1m", progress=False)
    df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
    df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
    return df

# Fetching Data
t1, t5, t15 = get_mtf_trend("^DJI", "1m"), get_mtf_trend("^DJI", "5m"), get_mtf_trend("^DJI", "15m")
df = get_main_data()

# --- 3. STUDIO STYLE HEADER ---
st.markdown("""
    <div style="background: linear-gradient(90deg, #001a00 0%, #000000 50%, #001a00 100%); padding: 30px; border-radius: 15px; border: 1px solid #00ff00; text-align: center;">
        <h1 style="color: #00ff00; letter-spacing: 15px; font-family: 'Arial Black'; margin: 0; text-shadow: 0 0 20px #00ff00;">PATRO AI PRO</h1>
        <p style="color: #ffffff; font-size: 14px; opacity: 0.7;">INSTITUTIONAL GRADE TRADING TERMINAL v4.0</p>
    </div>
""", unsafe_allow_html=True)

st.divider()

# --- 4. SIDEBAR: TREND MATRIX ---
with st.sidebar:
    st.markdown("<h2 style='color:#00ff00; text-align:center;'>📊 TREND MATRIX</h2>", unsafe_allow_html=True)
    for label, val in [("1 MINUTE", t1), ("5 MINUTE", t5), ("15 MINUTE", t15)]:
        c = "#00ff00" if val == "UP" else "#ff4b4b"
        st.markdown(f"""
            <div style='border: 1px solid {c}; padding: 15px; border-radius: 8px; margin-bottom: 10px; text-align: center; background-color: rgba(0, 255, 0, 0.05);'>
                <span style='color: gray; font-size: 10px; display: block;'>{label}</span>
                <span style='color: {c}; font-size: 20px; font-weight: bold;'>{val}</span>
            </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    if st.button("🔄 REFRESH CORE"):
        st.cache_data.clear()
        st.rerun()

# --- 5. TOP METRICS ---
m1, m2, m3 = st.columns(3)
curr_sig = "BUY" if df['Close'].iloc[-1] > df['EMA20'].iloc[-1] else "SELL"
m1.metric("US30 PRICE", f"${df['Close'].iloc[-1]:,.2f}")
m2.metric("SIGNAL", curr_sig)
m3.metric("TIME (NY)", datetime.now(pytz.timezone('US/Eastern')).strftime('%H:%M:%S'))

# --- 6. PROFESSIONAL CHART ---
fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.75, 0.25])

# Candlesticks
fig.add_trace(go.Candlestick(
    x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
    name='US30', increasing_line_color='#00ff00', decreasing_line_color='#ff4b4b'
), row=1, col=1)

# EMA Line
fig.add_trace(go.Scatter(x=df.index, y=df['EMA20'], name='EMA 20', line=dict(color='orange', width=1.5)), row=1, col=1)

# Volume Bars
v_colors = ['#00ff00' if df['Close'].iloc[i] > df['Open'].
