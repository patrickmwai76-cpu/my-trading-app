import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import hmac

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

# --- 2. DATA ENGINE ---
@st.cache_data(ttl=60)
def get_pro_data():
    df = yf.download("^DJI", period="1d", interval="1m", progress=False)
    df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
    # Trend Logic
    df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
    df['Signal'] = 0
    df.loc[df['Close'] > df['EMA20'], 'Signal'] = 1
    df.loc[df['Close'] < df['EMA20'], 'Signal'] = -1
    # Find the "Cross" where trend flips
    df['Entry'] = df['Signal'].diff()
    return df

df = get_pro_data()

# --- 3. TOP METRICS ---
st.markdown("<h2 style='color:#00ff00; text-align:center;'>🚀 US30 SCALPER TERMINAL</h2>", unsafe_allow_html=True)
m1, m2, m3 = st.columns(3)
curr_sig = "BUY" if df['Signal'].iloc[-1] == 1 else "SELL"
m1.metric("US30 PRICE", f"${df['Close'].iloc[-1]:,.2f}")
m2.metric("CURRENT SIGNAL", curr_sig)
m3.metric("EMA STATUS", "BULLISH" if curr_sig == "BUY" else "BEARISH")

# --- 4. THE CHART (GainzAlgo Style) ---
fig = go.Figure()

# Candlesticks
fig.add_trace(go.Candlestick(
    x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
    name='Market', increasing_line_color='#00ff00', decreasing_line_color='#ff4b4b'
))

# EMA Line
fig.add_trace(go.Scatter(x=df.index, y=df['EMA20'], name='Trend', line=dict(color='orange', width=1)))

# ADD "BUY" LABELS (Where Entry == 2)
buys = df[df['Entry'] == 2]
fig.add_trace(go.Scatter(
    x=buys.index, y=buys['Low'] * 0.9995,
    mode='markers+text', text="BUY", textposition="bottom center",
    marker=dict(color='#00ff00', size=12, symbol='triangle-up'),
    name='Buy Entry'
))

# ADD "SELL" LABELS (Where Entry == -2)
sells = df[df['Entry'] == -2]
fig.add_trace(go.Scatter(
    x=sells.index, y=sells['High'] * 1.0005,
    mode='markers+text', text="SELL", textposition="top center",
    marker=dict(color='#ff4b4b', size=12, symbol='triangle-down'),
    name='Sell Entry'
))

fig.update_layout(template='plotly_dark', height=700, xaxis_rangeslider_visible=False, showlegend=False)
st.plotly_chart(fig, use_container_width=True)

# --- 5. SIDEBAR ---
with st.sidebar:
    st.markdown("### 📊 RISK CONTROL")
    bal = st.number_input("Balance ($)", value=1000)
    risk = st.slider("Risk (%)", 0.5, 5.0, 1.0)
    st.error(f"Max Loss per Trade: ${bal * (risk/100):.2f}")
    if st.button("🔄 REFRESH SYSTEM"):
        st.cache_data.clear()
        st.rerun()
