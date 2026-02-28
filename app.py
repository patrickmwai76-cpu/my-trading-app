import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import hmac
from datetime import datetime
import pytz

# --- 1. BOOT & SECURITY ---
st.set_page_config(page_title="PATRO AI PRO", layout="wide")

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

if not check_password(): st.stop()

# --- 2. TIMEFRAME & DATA CONTROL ---
with st.sidebar:
    st.markdown("<h2 style='color:#00ff00;'>⚙️ COMMAND CENTER</h2>", unsafe_allow_html=True)
    # TIMEFRAME SELECTOR
    tf = st.selectbox("CHART TIMEFRAME", ["1m", "5m", "15m", "30m", "1h"], index=0)
    st.divider()

@st.cache_data(ttl=60)
def get_custom_data(interval):
    df = yf.download("^DJI", period="2d", interval=interval, progress=False)
    df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
    df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    df['RSI'] = 100 - (100 / (1 + (gain / loss)))
    # Signal
    df['Trend'] = 0
    df.loc[df['Close'] > df['EMA20'], 'Trend'] = 1
    df.loc[df['Close'] < df['EMA20'], 'Trend'] = -1
    df['Entry'] = df['Trend'].diff()
    return df

df = get_custom_data(tf)

# --- 3. NEWS SESSION MONITOR ---
ny_tz = pytz.timezone('US/Eastern')
ny_now = datetime.now(ny_tz)

st.markdown(f"### 🌐 SESSION: {'NEW YORK' if 9 <= ny_now.hour < 17 else 'AFTER HOURS'}")
n_col1, n_col2 = st.columns(2)
with n_col1:
    st.warning("**COMING UP:** ISM Manufacturing PMI\n\n🕒 Monday 10:00 AM NY Time")
with n_col2:
    st.error("**CRITICAL:** Non-Farm Payrolls (NFP)\n\n🕒 Friday 08:30 AM NY Time")

st.divider()

# --- 4. MAIN CHART ---
last_sig = "BUY" if df['Trend'].iloc[-1] == 1 else "SELL"
sig_color = "#00ff00" if last_sig == "BUY" else "#ff4b4b"

m1, m2, m3 = st.columns(3)
m1.metric(f"US30 ({tf})", f"${df['Close'].iloc[-1]:,.2f}")
m2.markdown(f"<p style='color:grey;margin:0;'>AI SIGNAL</p><h2 style='color:{sig_color};margin:0;'>{last_sig}</h2>", unsafe_allow_html=True)
m3.metric("RSI", f"{df['RSI'].iloc[-1]:.2f}")

fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.8, 0.2], vertical_spacing=0.03)
# Candles
fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='US30'), row=1, col=1)
# Tags
buys = df[df['Entry'] == 2]
fig.add_trace(go.Scatter(x=buys.index, y=buys['Low']*0.9998, mode='markers+text', text="BUY", textposition="bottom center", marker=dict(color='#00ff00', size=10, symbol='triangle-up')), row=1, col=1)
sells = df[df['Entry'] == -2]
fig.add_trace(go.Scatter(x=sells.index, y=sells['High']*1.0002, mode='markers+text', text="SELL", textposition="top center", marker=dict(color='#ff4b4b', size=10, symbol='triangle-down')), row=1, col=1)
# Volume
fig.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color='grey', opacity=0.3, name='Volume'), row=2, col=1)

fig.update_layout(template='plotly_dark', height=800, xaxis_rangeslider_visible=False, showlegend=False)
st.plotly_chart(fig, use_container_width=True)
