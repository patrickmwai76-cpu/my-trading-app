import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import hmac
from datetime import datetime
import pytz

# --- 1. SECURITY & CONFIG ---
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

# Fetching
t1, t5, t15 = get_mtf_trend("^DJI", "1m"), get_mtf_trend("^DJI", "5m"), get_mtf_trend("^DJI", "15m")
df = get_main_data()

# --- 3. TOP HERO SECTION (THE IMAGE) ---
st.image("https://files.oaiusercontent.com/file-SbeHnO8vO6PzX2YVp6vPjWRA?se=2024-05-23T20%3A58%3A37Z&sp=r&sv=2021-08-06&sr=b&rscc=max-age%3D31536000%2C%20private%2C%20immutable&rscd=attachment%3B%20filename%3D0f31952e-c5e8-4672-9844-48606c483250.webp&sig=A37R%2BNI7lU9V0eWw%2BtL5W7f0R5lW%2By8t3R9lW%2By8t3R%2BNI7lU9V0eWw%2BtL5W7f0R5lW%2By8t3R9lW%2By8t3R%2B", use_column_width=True)

st.markdown("<h1 style='text-align:center; color:#00ff00; letter-spacing: 10px; margin-top:-50px; text-shadow: 2px 2px 10px #000;'>PATRO AI PRO</h1>", unsafe_allow_html=True)
st.divider()

# --- 4. SIDEBAR: TREND MATRIX ---
with st.sidebar:
    st.markdown("<h2 style='color:#00ff00;'>📊 TREND MATRIX</h2>", unsafe_allow_html=True)
    for label, val in [("1 MIN", t1), ("5 MIN", t5), ("15 MIN", t15)]:
        c = "#00ff00" if val == "UP" else "#ff4b4b"
        st.markdown(f"<div style='border:1px solid {c}; padding:10px; border-radius:5px; margin-bottom:5px; background-color:rgba(0,0,0,0.3);'><h4 style='margin:0; color:{c};'>{label}: {val}</h4></div>", unsafe_allow_html=True)
    
    st.divider()
    if st.button("🔄 REFRESH SYSTEM"):
        st.cache_data.clear()
        st.rerun()
    st.info(f"NY Time: {datetime.now(pytz.timezone('US/Eastern')).strftime('%H:%M:%S')}")

# --- 5. MAIN DASHBOARD ---
m1, m2, m3 = st.columns(3)
curr_sig = "BUY" if df['Close'].iloc[-1] > df['EMA20'].iloc[-1] else "SELL"
m1.metric("US30 PRICE", f"${df['Close'].iloc[-1]:,.2f}")
m2.metric("CURRENT SIGNAL", curr_sig)
m3.metric("EMA STATUS", "BULLISH" if curr_sig == "BUY" else "BEARISH")

# --- 6. CHART & VOLUME ---
fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.75, 0.25])
fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='US30'), row=1, col=1)
fig.add_trace(go.Scatter(x=df.index, y=df['EMA20'], name='EMA 20', line=dict(color='orange', width=1.5, dash='dot')), row=1, col=1)

# Volume Bars
v_colors = ['#00ff00' if df['Close'].iloc[i] > df['Open'].iloc[i] else '#ff4b4b' for i in range(len(df))]
fig.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color=v_colors, name='Volume Surge'), row=2, col=1)

fig.update_layout(template='plotly_dark', height=800, xaxis_rangeslider_visible=False, showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
st.plotly_chart(fig, use_container_width=True)
