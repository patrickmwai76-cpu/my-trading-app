Import streamlit as st
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
        if data.empty: return "N/A"
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

# --- 3. PRE-LOAD TRENDS (THIS FIXES THE ERROR) ---
t1 = get_mtf_trend("^DJI", "1m")
t5 = get_mtf_trend("^DJI", "5m")
t15 = get_mtf_trend("^DJI", "15m")

# --- 4. UI: NEWS GUARD TOP ---
news_alerts = [
    {"Day": "Mon Mar 2", "Time": "10:00 AM", "Event": "ISM PMI", "Lvl": "🔥 HIGH"},
    {"Day": "Fri Mar 6", "Time": "08:30 AM", "Event": "NFP Jobs", "Lvl": "💣 CRITICAL"}
]

with st.container():
    st.markdown("<h3 style='color:#00ff00;'>🛡️ NEWS GUARD ALERTS</h3>", unsafe_allow_html=True)
    cols = st.columns(len(news_alerts))
    for i, n in enumerate(news_alerts):
        cols[i].warning(f"**{n['Day']} @ {n['Time']}**\n\n{n['Event']} ({n['Lvl']})")

st.divider()

# --- 5. SIDEBAR: THE MATRIX ---
with st.sidebar:
    st.markdown("<h2 style='color:#00ff00;'>📊 TREND MATRIX</h2>", unsafe_allow_html=True)
    
    # Stylish Indicator Function
    def draw_indicator(label, trend):
        color = "#00ff00" if trend == "UP" else "#ff4b4b"
        st.markdown(f"""
            <div style="border:1px solid {color}; padding:10px; border-radius:5px; margin-bottom:10px;">
                <p style="margin:0; color:white; font-size:12px;">{label}</p>
                <h3 style="margin:0; color:{color};">{trend}</h3>
            </div>
        """, unsafe_allow_html=True)

    draw_indicator("1 MINUTE", t1)
    draw_indicator("5 MINUTE", t5)
    draw_indicator("15 MINUTE", t15)
    
    st.divider()
    if st.button("🔄 REFRESH AI"): 
        st.cache_data.clear()
        st.rerun()
    bal = st.number_input("Balance ($)", value=1000)
    risk = st.slider("Risk (%)", 0.5, 5.0, 1.0)
    st.error(f"Trade Risk: ${bal * (risk/100):.2f}")

# --- 6. MAIN CHART ---
df = get_main_data()
sig = "BUY" if df['Trend'].iloc[-1] == 1 else "SELL"
sig_c = "#00ff00" if sig == "BUY" else "#ff4b4b"

m1, m2, m3 = st.columns(3)
m1.metric("US30 PRICE", f"${df['Close'].iloc[-1]:,.2f}")
m2.metric("CURRENT SIGNAL", sig)
m3.metric("RSI (14)", f"{df['RSI'].iloc[-1]:.2f}")

fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3], vertical_spacing=0.05)
fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='US30'), row=1, col=1)
fig.add_trace(go.Scatter(x=df.index, y=df['SMA20'], name='EMA 20', line=dict(color='orange')), row=1, col=1)
fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name='RSI', line=dict(color='purple')), row=2, col=1)
fig.update_layout(template='plotly_dark', height=700, xaxis_rangeslider_visible=False)
st.plotly_chart(fig, use_container_width=True)
