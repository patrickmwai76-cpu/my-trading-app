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

# --- 2. MARKET STATUS & NEWS GUARD ---
def get_market_status():
    ny_tz = pytz.timezone('US/Eastern')
    ny_now = datetime.now(ny_tz)
    if ny_now.weekday() >= 5: return "🔴 MARKET CLOSED (WEEKEND)", "#ff4b4b"
    if ny_now.hour < 9 or (ny_now.hour == 9 and ny_now.minute < 30) or ny_now.hour >= 16:
        return "🟠 MARKET CLOSED (AFTER HOURS)", "#ffa500"
    return "🟢 MARKET LIVE (NEW YORK)", "#00ff00"

# MARCH 2026 HIGH-IMPACT CALENDAR
news_alerts = [
    {"Day": "Mon Mar 2", "Time": "10:00 AM", "Event": "ISM Manufacturing PMI", "Level": "🔥 HIGH"},
    {"Day": "Wed Mar 4", "Time": "08:15 AM", "Event": "ADP Jobs Report", "Level": "🔥 HIGH"},
    {"Day": "Fri Mar 6", "Time": "08:30 AM", "Event": "Non-Farm Payrolls", "Level": "💣 CRITICAL"}
]

# --- 3. DATA ENGINE ---
@st.cache_data(ttl=60)
def get_data():
    df = yf.download("^DJI", period="1d", interval="1m")
    df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
    df['SMA20'] = df['Close'].rolling(window=20).mean()
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    df['RSI'] = 100 - (100 / (1 + (gain / loss)))
    df['Trend'] = 0
    df.loc[df['Close'] > df['SMA20'], 'Trend'] = 1
    df.loc[df['Close'] < df['SMA20'], 'Trend'] = -1
    df['Entry'] = df['Trend'].diff()
    return df

# --- 4. DASHBOARD UI ---
df = get_data()
status_text, status_color = get_market_status()
sig = "BUY" if df['Trend'].iloc[-1] == 1 else "SELL"
sig_c = "#00ff00" if sig == "BUY" else "#ff4b4b"

# Top Row
c1, c2 = st.columns([2, 1])
with c1:
    st.markdown(f"<h1 style='color:{sig_c};'>🛡️ PATRO AI PRO: {sig}</h1>", unsafe_allow_html=True)
with c2:
    st.markdown(f"<div style='border:2px solid {status_color}; color:{status_color}; padding:8px; border-radius:10px; text-align:center; font-weight:bold;'>{status_text}</div>", unsafe_allow_html=True)

st.divider()

# Sidebar
with st.sidebar:
    st.markdown("<h2 style='color:#00ff00;'>🛠️ CONTROL</h2>", unsafe_allow_html=True)
    if st.button("🔄 REFRESH SYSTEM"): st.rerun()
    st.divider()
    bal = st.number_input("Balance ($)", value=1000)
    risk = st.slider("Risk (%)", 0.5, 5.0, 1.0)
    st.error(f"Trade Risk: ${bal * (risk/100):.2f}")
    st.divider()
    st.subheader("⚠️ NEWS GUARD")
    for news in news_alerts:
        st.caption(f"**{news['Day']} @ {news['Time']}**")
        st.write(f"{news['Event']} ({news['Level']})")

# Main Content
m1, m2, m3 = st.columns(3)
m1.metric("US30 PRICE", f"${df['Close'].iloc[-1]:,.2f}")
m2.metric("CURRENT SIGNAL", sig)
m3.metric("RSI (14)", f"{df['RSI'].iloc[-1]:.2f}")

# Chart
fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3], vertical_spacing=0.05)
fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='US30'), row=1, col=1)
fig.add_trace(go.Scatter(x=df.index, y=df['SMA20'], name='Trend', line=dict(color='orange')), row=1, col=1)

for i in range(1, len(df)):
    if df['Entry'].iloc[i] == 2:
        fig.add_annotation(x=df.index[i], y=df['Low'].iloc[i], text="BUY", bgcolor="green", font=dict(color="white"), row=1, col=1)
    elif df['Entry'].iloc[i] == -2:
        fig.add_annotation(x=df.index[i], y=df['High'].iloc[i], text="SELL", bgcolor="red", font=dict(color="white"), row=1, col=1)

fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name='RSI', line=dict(color='purple')), row=2, col=1)
fig.update_layout(template='plotly_dark', height=750, xaxis_rangeslider_visible=False)
st.plotly_chart(fig, use_container_width=True)
