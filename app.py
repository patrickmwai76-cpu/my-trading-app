import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from streamlit_autorefresh import st_autorefresh
from plotly.subplots import make_subplots
import datetime

# 1. Page & Security Configuration
st.set_page_config(page_title="PATRO AI PRO", layout="wide")

if 'auth' not in st.session_state:
    st.session_state['auth'] = False

def login_screen():
    st.title("🛡️ PATRO AI PRO | SECURE LOGIN")
    u = st.text_input("Username (PATRO_ADMIN)")
    p = st.text_input("Password", type="password")
    if st.button("Unlock Terminal"):
        if u == "PATRO_ADMIN" and p == "patro666@":
            st.session_state['auth'] = True
            st.rerun()
        else:
            st.error("Access Denied")

if not st.session_state['auth']:
    login_screen()
    st.stop()

# --- IF AUTHENTICATED, LOAD TERMINAL ---

# 2. Sidebar - Institutional Layout
st.sidebar.title("🛡️ TERMINAL CONTROL")
tf = st.sidebar.radio("Timeframe", ["1m", "5m", "15m"], index=0, horizontal=True)

st.sidebar.divider()
st.sidebar.subheader("📋 OPERATOR SOP")
c1 = st.sidebar.checkbox("Trend Matrix Confluence?")
c2 = st.sidebar.checkbox("Price Action near VWAP?")
c3 = st.sidebar.checkbox("News Guard is CLEAR?")
c4 = st.sidebar.checkbox("Risk Management set?")
if c1 and c2 and c3 and c4:
    st.sidebar.success("✅ READY TO TRADE")
else:
    st.sidebar.warning("⚠️ STANDBY")

st.sidebar.divider()
st.sidebar.subheader("📉 RISK MGMT")
balance = st.sidebar.number_input("Wallet ($)", value=1000)
risk_p = st.sidebar.slider("Risk %", 0.5, 5.0, 1.0)
st.sidebar.info(f"Lot Size: {(balance * (risk_p/100)) / 50:.2f}")

st.sidebar.divider()
st.sidebar.subheader("📊 TREND MATRIX")
st.sidebar.code("1M: UP\n5M: UP\n15M: UP")

if st.sidebar.button("🔒 Logout"):
    st.session_state['auth'] = False
    st.rerun()

# 3. Header & News Guard
st.markdown('<div style="background: linear-gradient(90deg, #00c853, #b2ff59); padding: 15px; border-radius: 10px; color: black; text-align: center; font-weight: bold; font-size: 22px;">🛡️ PATRO AI PRO | INSTITUTIONAL TERMINAL v4.0</div>', unsafe_allow_html=True)

st.write(f"🛡️ **NEWS GUARD ACTIVE** | Last Pulse: {datetime.datetime.now().strftime('%H:%M:%S')}")
n1, n2 = st.columns(2)
n1.info("Mon Mar 2 | ISM PMI (10:00 AM)")
n2.error("Fri Mar 6 | NFP Jobs (08:30 AM)")

# 4. Data Engine - Force Refresh
st_autorefresh(interval=30000, key="live_refresh")
# Using YM=F (Futures) to ensure movement 24/5
df = yf.download("YM=F", period="1d", interval=tf, prepost=True)

if not df.empty:
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    # CALCULATE INSTITUTIONAL INDICATORS
    # VWAP
    df['VWAP'] = ( ((df['High'] + df['Low'] + df['Close']) / 3) * df['Volume'] ).cumsum() / df['Volume'].cumsum()
    # SMA 20
    df['SMA'] = df['Close'].rolling(window=20).mean()
    # RSI
    change = df['Close'].diff()
    gain = (change.where(change > 0, 0)).rolling(14).mean()
    loss = (-change.where(change < 0, 0)).rolling(14).mean()
    df['RSI'] = 100 - (100 / (1 + (gain / (loss + 1e-9))))

    # 5. Multi-Layer Chart
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.02, row_heights=[0.6, 0.1, 0.3])
    
    # Row 1: Price + VWAP + SMA
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='US30'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['VWAP'], line=dict(color='cyan', width=2), name='VWAP'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA'], line=dict(color='orange', width=1), name='20 SMA'), row=1, col=1)

    # 6. TRIPLE-FILTER SIGNALS
    for i in range(20, len(df)):
        # BUY: Price > SMA AND Price > VWAP AND RSI > 55
        if (df['Close'].iloc[i] > df['SMA'].iloc[i] and df['Close'].iloc[i] > df['VWAP'].iloc[i] and df['RSI'].iloc[i] > 55):
            if df['Close'].iloc[i-1] <= df['SMA'].iloc[i-1]: # Trigger at the cross
                fig.add_annotation(x=df.index[i], y=df['Low'].iloc[i], text="BUY", bgcolor="#00FF00", font=dict(color="black", size=10), row=1, col=1)
        
        # SELL: Price < SMA AND Price < VWAP AND RSI < 45
        elif (df['Close'].iloc[i] < df['SMA'].iloc[i] and df['Close'].iloc[i] < df['VWAP'].iloc[i] and df['RSI'].iloc[i] < 45):
            if df['Close'].iloc[i-1] >= df['SMA'].iloc[i-1]:
                fig.add_annotation(x=df.index[i], y=df['High'].iloc[i], text="SELL", bgcolor="#FF0000", font=dict(color="white", size=10), row=1, col=1)

    # Row 2: Volume
    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name='Vol', marker_color='gray'), row=2, col=1)
    
    # Row 3: RSI
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], line=dict(color='#a020f0', width=2), name='RSI'), row=3, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)

    fig.update_layout(template="plotly_dark", height=850, xaxis_rangeslider_visible=False, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)
else:
    st.error("⚠️ DATA STREAM OFFLINE | Refreshing...")
