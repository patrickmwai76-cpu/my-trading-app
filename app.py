import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import hmac

# --- 1. SECURITY & BRANDING ---
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

# --- 2. THE ENGINE ---
@st.cache_data(ttl=60)
def get_pro_data():
    df = yf.download("^DJI", period="1d", interval="1m", progress=False)
    df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
    # Trend Math
    df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
    df['Signal'] = 0
    df.loc[df['Close'] > df['EMA20'], 'Signal'] = 1
    df.loc[df['Close'] < df['EMA20'], 'Signal'] = -1
    # Detect the "Cross" for clean labels
    df['Entry'] = df['Signal'].diff()
    return df

df = get_pro_data()

# --- 3. PRO DASHBOARD HEADER ---
st.markdown("<h1 style='text-align:center; color:#00ff00; letter-spacing: 2px;'>PATRO AI PRO</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:gray;'>Advanced US30 Scalping System</p>", unsafe_allow_html=True)

m1, m2, m3 = st.columns(3)
curr_sig = "BUY" if df['Signal'].iloc[-1] == 1 else "SELL"
sig_color = "#00ff00" if curr_sig == "BUY" else "#ff4b4b"

m1.metric("US30 PRICE", f"${df['Close'].iloc[-1]:,.2f}")
m2.metric("CURRENT SIGNAL", curr_sig)
m3.metric("SYSTEM STATUS", "ONLINE", delta="LIVE")

# --- 4. THE CHART (GainzAlgo Visuals) ---
fig = go.Figure()

# Candlesticks
fig.add_trace(go.Candlestick(
    x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
    name='US30', increasing_line_color='#00ff00', decreasing_line_color='#ff4b4b'
))

# Trend Line
fig.add_trace(go.Scatter(x=df.index, y=df['EMA20'], name='Trend', line=dict(color='orange', width=1.5, dash='dot')))

# GREEN BUY LABELS
buys = df[df['Entry'] == 2]
fig.add_trace(go.Scatter(
    x=buys.index, y=buys['Low'] * 0.9997,
    mode='markers+text', text="BUY", textposition="bottom center",
    marker=dict(color='#00ff00', size=14, symbol='triangle-up'),
    name='Buy Alert'
))

# RED SELL LABELS
sells = df[df['Entry'] == -2]
fig.add_trace(go.Scatter(
    x=sells.index, y=sells['High'] * 1.0003,
    mode='markers+text', text="SELL", textposition="top center",
    marker=dict(color='#ff4b4b', size=14, symbol='triangle-down'),
    name='Sell Alert'
))

fig.update_layout(
    template='plotly_dark', height=750, 
    xaxis_rangeslider_visible=False,
    showlegend=False,
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)'
)
st.plotly_chart(fig, use_container_width=True)

# --- 5. SIDEBAR CONTROLS ---
with st.sidebar:
    st.markdown("<h2 style='color:#00ff00;'>CONTROL PANEL</h2>", unsafe_allow_html=True)
    if st.button("🔄 REBOOT SYSTEM"):
        st.cache_data.clear()
        st.rerun()
    
    st.divider()
    bal = st.number_input("Account Balance ($)", value=1000)
    risk = st.slider("Risk per Trade (%)", 0.5, 10.0, 1.0)
    st.error(f"Stop Loss Protection: ${bal * (risk/100):.2f}")
