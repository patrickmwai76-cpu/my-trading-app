import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from streamlit_autorefresh import st_autorefresh
from plotly.subplots import make_subplots

# 1. Security Logic (Username: PATRO_ADMIN | Password: patro666@)
if 'auth' not in st.session_state:
    st.session_state['auth'] = False

if not st.session_state['auth']:
    st.title("🛡️ PATRO AI PRO | SECURE ACCESS")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Unlock Terminal"):
        if u == "PATRO_ADMIN" and p == "patro666@":
            st.session_state['auth'] = True
            st.rerun()
        else:
            st.error("Invalid Credentials")
    st.stop()

# 2. Page Configuration
st.set_page_config(page_title="PATRO AI PRO", layout="wide")
st_autorefresh(interval=30000, key="auto_update")

# 3. Sidebar - Institutional Layout
st.sidebar.title("🛡️ TERMINAL CONTROL")
tf = st.sidebar.radio("Timeframe", ["1m", "5m", "15m"], index=0, horizontal=True)

st.sidebar.divider()
st.sidebar.subheader("📋 OPERATOR SOP")
s1 = st.sidebar.checkbox("Trend Matrix Confluence?")
s2 = st.sidebar.checkbox("Price Action near VWAP?")
s3 = st.sidebar.checkbox("News Guard is CLEAR?")
s4 = st.sidebar.checkbox("Risk Management set?")

if all([s1, s2, s3, s4]):
    st.sidebar.success("✅ READY TO TRADE")
else:
    st.sidebar.warning("⚠️ STANDBY")

st.sidebar.divider()
st.sidebar.subheader("📉 RISK MGMT")
bal = st.sidebar.number_input("Wallet ($)", value=1000)
risk = st.sidebar.slider("Risk %", 1.0, 5.0, 1.0)
st.sidebar.info(f"Lot Size: {(bal * (risk/100)) / 50:.2f}")

st.sidebar.divider()
st.sidebar.subheader("📊 TREND MATRIX")
st.sidebar.success("1M: UP | 5M: UP | 15M: UP")

# 4. Main Header & News Guard
st.markdown("""
    <div style="background: linear-gradient(90deg, #00c853, #b2ff59); padding: 15px; border-radius: 10px; color: black; text-align: center; font-weight: bold;">
        🛡️ PATRO AI PRO | BUY MODE<br>Institutional Scalping Terminal v4.0
    </div>
""", unsafe_allow_html=True)

st.write("🛡️ **NEWS GUARD ACTIVE**")
c1, c2 = st.columns(2)
c1.info("Mon Mar 2 | ISM PMI (10:00 AM)")
c2.error("Fri Mar 6 | NFP Jobs (08:30 AM)")

# 5. Data Engine & Charting
df = yf.download("^DJI", period="1d", interval=tf)

if not df.empty:
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    # Technicals
    df['SMA'] = df['Close'].rolling(20).mean()
    change = df['Close'].diff()
    gain = change.mask(change < 0, 0).rolling(14).mean()
    loss = (-change.mask(change > 0, 0)).rolling(14).mean()
    rs = gain / (loss + 1e-9)
    df['RSI'] = 100 - (100 / (1 + rs))

    # Fix: Subplots with Correct Row References
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.02, row_heights=[0.6, 0.15, 0.25])

    # Layer 1: Candles & Trend
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='US30'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA'], line=dict(color='orange', width=1), name='Trend'), row=1, col=1)

    # FIXED: Real BUY/SELL Annotations with row=1, col=1 specified
    for i in range(len(df)-10, len(df)): 
        if df['Close'].iloc[i] > df['SMA'].iloc[i]:
            fig.add_annotation(x=df.index[i], y=df['Low'].iloc[i], text="BUY", bgcolor="green", font=dict(color="white"), row=1, col=1)
        else:
            fig.add_annotation(x=df.index[i], y=df['High'].iloc[i], text="SELL", bgcolor="red", font=dict(color="white"), row=1, col=1)

    # Layer 2: Volume
    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name='Volume', marker_color='gray'), row=2, col=1)

    # Layer 3: RSI Purple Line
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], line=dict(color='purple'), name='RSI'), row=3, col=1)

    fig.update_layout(template="plotly_dark", height=850, xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.error("Awaiting Market Data...")
