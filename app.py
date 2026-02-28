import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import hmac
from datetime import datetime
import pytz

# --- 1. SECURITY (MUST BE FIRST) ---
def check_password():
    def credentials_entered():
        if (st.session_state["username"] == st.secrets["username"] and 
            hmac.compare_digest(st.session_state["password"], st.secrets["password"])):
            st.session_state["password_correct"] = True
            del st.session_state["password"]
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False
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

# --- 2. MARKET STATUS ENGINE ---
def get_market_status():
    ny_tz = pytz.timezone('US/Eastern')
    ny_now = datetime.now(ny_tz)
    # Check if Weekend (5=Sat, 6=Sun)
    if ny_now.weekday() >= 5:
        return "🔴 MARKET CLOSED (WEEKEND)", "#ff4b4b"
    # Check if outside 9:30 AM - 4:00 PM
    if ny_now.hour < 9 or (ny_now.hour == 9 and ny_now.minute < 30) or ny_now.hour >= 16:
        return "🟠 MARKET CLOSED (AFTER HOURS)", "#ffa500"
    return "🟢 MARKET LIVE (NEW YORK)", "#00ff00"

# --- 3. DATA ENGINE ---
@st.cache_data(ttl=60)
def get_data():
    df = yf.download("^DJI", period="1d", interval="1m")
    df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
    df['SMA20'] = df['Close'].rolling(window=20).mean()
    # RSI Logic
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    df['RSI'] = 100 - (100 / (1 + (gain / loss)))
    # Signals
    df['Trend'] = 0
    df.loc[df['Close'] > df['SMA20'], 'Trend'] = 1
    df.loc[df['Close'] < df['SMA20'], 'Trend'] = -1
    df['Entry'] = df['Trend'].diff()
    return df

# --- 4. THE UI ---
status_text, status_color = get_market_status()
df = get_data()
curr_p = df['Close'].iloc[-1]
sig = "BUY" if df['Trend'].iloc[-1] == 1 else "SELL"
sig_c = "#00ff00" if sig == "BUY" else "#ff4b4b"

# HEADER BLOCK
t1, t2 = st.columns([3, 1])
with t1:
    st.markdown(f"<h1 style='color:{sig_c}; margin:0;'>🛡️ PATRO AI PRO: {sig}</h1>", unsafe_allow_html=True)
with t2:
    st.markdown(f"<div style='border:2px solid {status_color}; color:{status_color}; padding:10px; border-radius:10px; text-align:center; font-weight:bold; margin-top:10px;'>{status_text}</div>", unsafe_allow_html=True)

# SIDEBAR
with st.sidebar:
    st.markdown(f"<h3 style='color:#00ff00;'>🛠️ TERMINAL CONTROLS</h3>", unsafe_allow_html=True)
    if st.button("🔄 REFRESH SYSTEM"): st.rerun()
    st.divider()
    bal = st.number_input("Balance ($)", value=1000)
    risk = st.slider("Risk (%)", 0.5, 5.0, 1.0)
    st.error(f"Trade Risk: ${bal * (risk/100):.2f}")

# METRICS
st.divider()
m1, m2, m3 = st.columns(3)
m1.metric("US30 PRICE", f"${curr_p:,.2f}")
m2.metric("SIGNAL", sig)
m3.metric("RSI (14)", f"{df['RSI'].iloc[-1]:.2f}")

# CHART
fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3], vertical_spacing=0.05)
fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='US30'), row=1, col=1)
fig.add_trace(go.Scatter(x=df.index, y=df['SMA20'], name='Trend', line=dict(color='orange')), row=1, col=1)

# Add Buy/Sell boxes
for i in range(1, len(df)):
    if df['Entry'].iloc[i] == 2:
        fig.add_annotation(x=df.index[i], y=df['Low'].iloc[i], text="BUY", bgcolor="green", font=dict(color="white"), row=1, col=1)
    elif df['Entry'].iloc[i] == -2:
        fig.add_annotation(x=df.index[i], y=df['High'].iloc[i], text="SELL", bgcolor="red", font=dict(color="white"), row=1, col=1)

fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name='RSI', line=dict(color='purple')), row=2, col=1)
fig.update_layout(template='plotly_dark', height=700, xaxis_rangeslider_visible=False)
st.plotly_chart(fig, use_container_width=True)

with st.expander("📖 VIEW OPERATIONAL MANUAL"):
    st.write("1. Check Price vs Orange Line. 2. Confirm RSI > 50 for Buy. 3. Manage Risk in Sidebar.")
