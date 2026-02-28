import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import hmac
from datetime import datetime
import pytz

# --- 1. SECURITY ---
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

# --- 2. TIME & SESSION ENGINE ---
def get_session_info():
    ny_tz = pytz.timezone('US/Eastern')
    now = datetime.now(ny_tz)
    time_str = now.strftime("%H:%M")
    if now.weekday() >= 5: return "WEEKEND", "🔴", "Market Closed"
    
    hour = now.hour
    minute = now.minute
    
    if hour == 9 and minute >= 30 or hour == 10: return "NY OPEN", "🔥", "Extreme Volatility"
    if 11 <= hour <= 13: return "MID-DAY", "🥪", "Choppy/Low Volume"
    if 14 <= hour <= 15: return "AFTERNOON", "📈", "Trend Continuation"
    if hour == 16: return "POWER HOUR", "⚡", "Big Reversals"
    return "OFF-HOURS", "🌙", "Slow Market"

session_name, session_icon, session_desc = get_session_info()

# --- 3. DATA ENGINES ---
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
    df['SMA20'] = df['Close'].rolling(window=20).mean()
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    df['RSI'] = 100 - (100 / (1 + (gain / loss)))
    df['Trend'] = 1 if df['Close'].iloc[-1] > df['SMA20'].iloc[-1] else -1
    return df

# --- 4. UI: THE HEADER ---
st.markdown(f"<h2 style='color:#00ff00;'>🛡️ {session_icon} {session_name} SESSION</h2>", unsafe_allow_html=True)
st.caption(f"Status: {session_desc} | New York Time: {datetime.now(pytz.timezone('US/Eastern')).strftime('%I:%M %p')}")

# --- 5. SIDEBAR: THE MATRIX ---
with st.sidebar:
    st.markdown("<h2 style='color:#00ff00;'>📊 TREND MATRIX</h2>", unsafe_allow_html=True)
    t1, t5, t15 = get_mtf_trend("^DJI", "1m"), get_mtf_trend("^DJI", "5m"), get_mtf_trend("^DJI", "15m")
    
    for label, val in [("1 MIN", t1), ("5 MIN", t5), ("15 MIN", t15)]:
        color = "#00ff00" if val == "UP" else "#ff4b4b"
        st.markdown(f"<div style='border:1px solid {color}; padding:10px; border-radius:5px; margin-bottom:5px; text-align:center;'><small>{label}</small><br><b style='color:{color};'>{val}</b></div>", unsafe_allow_html=True)
    
    st.divider()
    if st.button("🔄 REFRESH SYSTEM"): st.cache_data.clear(); st.rerun()
    bal = st.number_input("Balance ($)", value=1000)
    risk = st.slider("Risk (%)", 0.5, 5.0, 1.0)
    st.error(f"Max Risk: ${bal * (risk/100):.2f}")

# --- 6. MAIN CONTENT ---
df = get_main_data()
sig = "BUY" if df['Trend'].iloc[-1] == 1 else "SELL"
sig_c = "#00ff00" if sig == "BUY" else "#ff4b4b"

m1, m2, m3 = st.columns(3)
m1.metric("US30 PRICE", f"${df['Close'].iloc[-1]:,.2f}")
m2.metric("SIGNAL", sig, delta="Trending" if sig=="BUY" else "Falling")
m3.metric("RSI", f"{df['RSI'].iloc[-1]:.2f}")

# The Chart
fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3])
fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='US30'), row=1, col=1)
fig.add_trace(go.Scatter(x=df.index, y=df['SMA20'], name='EMA 20', line=dict(color='orange')), row=1, col=1)
fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name='RSI', line=dict(color='purple')), row=2, col=1)
fig.update_layout(template='plotly_dark', height=650, xaxis_rangeslider_visible=False)
st.plotly_chart(fig, use_container_width=True)
