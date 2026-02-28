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
    df['SMA20'] = df['Close'].rolling(window=20).mean()
    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    df['RSI'] = 100 - (100 / (1 + (gain / loss)))
    return df

# PRE-LOAD FOR MATRIX
t1, t5, t15 = get_mtf_trend("^DJI", "1m"), get_mtf_trend("^DJI", "5m"), get_mtf_trend("^DJI", "15m")

# --- 3. UI: NEWS GUARD ---
news_alerts = [
    {"Day": "Mon Mar 2", "Time": "10:00 AM", "Event": "ISM PMI", "Lvl": "🔥 HIGH"},
    {"Day": "Fri Mar 6", "Time": "08:30 AM", "Event": "NFP Jobs", "Lvl": "💣 CRITICAL"}
]

with st.container():
    st.markdown("<h3 style='color:#00ff00;'>🛡️ NEWS GUARD</h3>", unsafe_allow_html=True)
    nc = st.columns(len(news_alerts))
    for i, n in enumerate(news_alerts):
        nc[i].info(f"**{n['Day']} @ {n['Time']}**\n\n{n['Event']}")

st.divider()

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='color:#00ff00;'>📊 TREND MATRIX</h2>", unsafe_allow_html=True)
    for label, val in [("1 MIN", t1), ("5 MIN", t5), ("15 MIN", t15)]:
        c = "#00ff00" if val == "UP" else "#ff4b4b"
        st.markdown(f"<div style='border:1px solid {c}; padding:10px; border-radius:5px; margin-bottom:5px;'><p style='margin:0; font-size:10px;'>{label}</p><h4 style='margin:0; color:{c};'>{val}</h4></div>", unsafe_allow_html=True)
    
    st.divider()
    if st.button("🔄 REFRESH SYSTEM"):
        st.cache_data.clear()
        st.rerun()
    bal = st.number_input("Balance ($)", value=1000)
    risk = st.slider("Risk (%)", 0.5, 5.0, 1.0)
    st.error(f"Risk: ${bal * (risk/100):.2f}")

# --- 5. MAIN CONTENT ---
df = get_main_data()
sig = "BUY" if df['Close'].iloc[-1] > df['SMA20'].iloc[-1] else "SELL"
sig_c = "#00ff00" if sig == "BUY" else "#ff4b4b"

# WEEKEND STATUS
st.markdown(f"<h1 style='text-align:center; color:#00ff00;'>🛡️ WEEKEND SESSION</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align:center;'>Market Closed | NY Time: {datetime.now(pytz.timezone('US/Eastern')).strftime('%H:%M')}</p>", unsafe_allow_html=True)

m1, m2, m3 = st.columns(3)
m1.metric("US30 PRICE", f"${df['Close'].iloc[-1]:,.2f}")
m2.metric("AI SIGNAL", sig)
m3.metric("RSI (14)", f"{df['RSI'].iloc[-1]:.2f}")

# CHART WITH VOLUME
fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.02, row_heights=[0.6, 0.2, 0.2])
# Main Candles
fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='US30'), row=1, col=1)
fig.add_trace(go.Scatter(x=df.index, y=df['SMA20'], name='EMA 20', line=dict(color='orange')), row=1, col=1)
# Volume
colors = ['green' if df['Close'].iloc[i] > df['Open'].iloc[i] else 'red' for i in range(len(df))]
fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name='Volume', marker_color=colors), row=2, col=1)
# RSI
fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name='RSI', line=dict(color='purple')), row=3, col=1)

fig.update_layout(template='plotly_dark', height=850, xaxis_rangeslider_visible=False, showlegend=False)
st.plotly_chart(fig, use_container_width=True)
