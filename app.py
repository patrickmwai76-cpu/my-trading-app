import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from streamlit_autorefresh import st_autorefresh
from plotly.subplots import make_subplots
import datetime

# 1. SECURITY & FAST PULSE
st.set_page_config(page_title="PATRO AI PRO", layout="wide")
st_autorefresh(interval=5000, key="mt5_fast_pulse") # 5-second live refresh

if 'auth' not in st.session_state: st.session_state['auth'] = False
if not st.session_state['auth']:
    st.title("🛡️ PATRO AI PRO | SECURE ACCESS")
    u, p = st.text_input("Username"), st.text_input("Password", type="password")
    if st.button("Unlock"):
        if u == "PATRO_ADMIN" and p == "patro666@":
            st.session_state['auth'] = True
            st.rerun()
    st.stop()

# 2. SIDEBAR - ALL FEATURES RESTORED
st.sidebar.title("🛡️ TERMINAL CONTROL")
tf = st.sidebar.radio("Timeframe", ["1m", "5m", "15m"], index=0, horizontal=True)

st.sidebar.divider()
st.sidebar.subheader("📋 OPERATOR SOP")
s1 = st.sidebar.checkbox("Trend Matrix Confluence?")
s2 = st.sidebar.checkbox("Price Action near VWAP?")
s3 = st.sidebar.checkbox("News Guard is CLEAR?")
s4 = st.sidebar.checkbox("Risk Management set?")

st.sidebar.divider()
st.sidebar.subheader("📉 RISK MGMT")
bal = st.sidebar.number_input("Wallet ($)", value=1000)
risk = st.sidebar.slider("Risk %", 0.5, 5.0, 1.0)
st.sidebar.info(f"Lot Size: {(bal * (risk/100)) / 50:.2f}")

# 3. HEADER & NEWS GUARD
st.markdown('<div style="background: linear-gradient(90deg, #00c853, #b2ff59); padding: 15px; border-radius: 10px; color: black; text-align: center; font-weight: bold; font-size: 20px;">🛡️ PATRO AI PRO | INSTITUTIONAL TERMINAL v4.0</div>', unsafe_allow_html=True)

st.write(f"🛡️ **NEWS GUARD ACTIVE** | Last Pulse: {datetime.datetime.now().strftime('%H:%M:%S')}")
c1, c2 = st.columns(2)
c1.info("Mon Mar 2 | ISM PMI (10:00 AM)")
c2.error("Fri Mar 6 | NFP Jobs (08:30 AM)")

# 4. DATA ENGINE (YM=F FOR LIVE MOTION)
df = yf.download("YM=F", period="1d", interval=tf, prepost=True)

if not df.empty:
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    
    # INDICATORS
    df['VWAP'] = (((df['High'] + df['Low'] + df['Close']) / 3) * df['Volume']).cumsum() / df['Volume'].cumsum()
    df['SMA'] = df['Close'].rolling(20).mean()
    change = df['Close'].diff()
    gain = (change.where(change > 0, 0)).rolling(14).mean()
    loss = (-change.where(change < 0, 0)).rolling(14).mean()
    df['RSI'] = 100 - (100 / (1 + (gain / (loss + 1e-9))))

    # 5. MULTI-LAYER CHART
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.02, row_heights=[0.6, 0.1, 0.3])
    
    # Layer 1: Candles + VWAP + SMA
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='US30'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['VWAP'], line=dict(color='cyan', width=2), name='VWAP'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA'], line=dict(color='orange', width=1), name='20 SMA'), row=1, col=1)

    # 6. SIGNAL LOGIC RESTORED (Cross-Detection)
    for i in range(15, len(df)):
        # BUY: Price crosses above SMA
        if df['Close'].iloc[i] > df['SMA'].iloc[i] and df['Close'].iloc[i-1] <= df['SMA'].iloc[i-1]:
            fig.add_annotation(x=df.index[i], y=df['Low'].iloc[i], text="BUY", bgcolor="green", font=dict(color="white"), row=1, col=1)
        # SELL: Price crosses below SMA
        elif df['Close'].iloc[i] < df['SMA'].iloc[i] and df['Close'].iloc[i-1] >= df['SMA'].iloc[i-1]:
            fig.add_annotation(x=df.index[i], y=df['High'].iloc[i], text="SELL", bgcolor="red", font=dict(color="white"), row=1, col=1)

    # Layer 2: Volume
    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name='Volume', marker_color='gray'), row=2, col=1)
    
    # Layer 3: RSI Purple Line
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], line=dict(color='purple', width=2), name='RSI'), row=3, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)

    fig.update_layout(template="plotly_dark", height=850, xaxis_rangeslider_visible=False, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)
else:
    st.error("Connecting to Liquidity Stream...")
