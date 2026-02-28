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
    # Trend for Signals
    df['Trend'] = 0
    df.loc[df['Close'] > df['SMA20'], 'Trend'] = 1
    df.loc[df['Close'] < df['SMA20'], 'Trend'] = -1
    df['Entry'] = df['Trend'].diff()
    return df

t1, t5, t15 = get_mtf_trend("^DJI", "1m"), get_mtf_trend("^DJI", "5m"), get_mtf_trend("^DJI", "15m")

# --- 3. UI: NEWS GUARD ---
st.markdown("<h3 style='color:#00ff00;'>🛡️ NEWS GUARD</h3>", unsafe_allow_html=True)
c_news = st.columns(2)
c_news[0].info("**Mon Mar 2 @ 10:00 AM**\n\nISM PMI (High Volatility)")
c_news[1].info("**Fri Mar 6 @ 08:30 AM**\n\nNFP Jobs (Critical)")

st.divider()

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='color:#00ff00;'>📊 TREND MATRIX</h2>", unsafe_allow_html=True)
    for label, val in [("1 MIN", t1), ("5 MIN", t5), ("15 MIN", t15)]:
        col_c = "#00ff00" if val == "UP" else "#ff4b4b"
        st.markdown(f"<div style='border:1px solid {col_c}; padding:10px; border-radius:5px; margin-bottom:5px; color:{col_c};'><b>{label}: {val}</b></div>", unsafe_allow_html=True)
    st.divider()
    if st.button("🔄 REFRESH"): st.rerun()

# --- 5. CHART ENGINE ---
df = get_main_data()
curr_p = df['Close'].iloc[-1]

# Setup Subplots (Price Top, Volume Bottom)
fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.8, 0.2])

# Traces
fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='Price'), row=1, col=1)
fig.add_trace(go.Scatter(x=df.index, y=df['SMA20'], name='Trend', line=dict(color='orange', width=2)), row=1, col=1)

# FORCE VOLUME BARS
v_colors = ['green' if df['Close'].iloc[i] > df['Open'].iloc[i] else 'red' for i in range(len(df))]
fig.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color=v_colors, name='Volume'), row=2, col=1)

# FORCE SIGNALS ONTO CANDLES
for i in range(len(df)):
    if df['Entry'].iloc[i] == 2: # BUY
        fig.add_annotation(x=df.index[i], y=df['Low'].iloc[i], text="BUY", font=dict(color="white", size=12), bgcolor="green", showarrow=True, arrowhead=1, ax=0, ay=25, row=1, col=1)
    elif df['Entry'].iloc[i] == -2: # SELL
        fig.add_annotation(x=df.index[i], y=df['High'].iloc[i], text="SELL", font=dict(color="white", size=12), bgcolor="red", showarrow=True, arrowhead=1, ax=0, ay=-25, row=1, col=1)

fig.update_layout(template='plotly_dark', height=800, xaxis_rangeslider_visible=False)
st.plotly_chart(fig, use_container_width=True)
