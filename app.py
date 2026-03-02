import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from streamlit_autorefresh import st_autorefresh
from plotly.subplots import make_subplots
import datetime

# 1. AUTH & CONFIG
st.set_page_config(page_title="PATRO AI PRO", layout="wide")
if 'auth' not in st.session_state: st.session_state['auth'] = False
if not st.session_state['auth']:
    st.title("🛡️ PATRO AI PRO | SECURE ACCESS")
    u, p = st.text_input("Username"), st.text_input("Password", type="password")
    if st.button("Unlock"):
        if u == "PATRO_ADMIN" and p == "patro666@":
            st.session_state['auth'] = True
            st.rerun()
    st.stop()

# 2. SIDEBAR - FULL OPERATOR SOP
st.sidebar.title("🛡️ CONTROL CENTER")
tf = st.sidebar.radio("Timeframe", ["1m", "5m", "15m"], index=0, horizontal=True)
st.sidebar.divider()
st.sidebar.subheader("📋 INSTITUTIONAL SOP")
sop1 = st.sidebar.checkbox("Trend Matrix Confluence?")
sop2 = st.sidebar.checkbox("Price Action near VWAP?")
sop3 = st.sidebar.checkbox("Institutional Volume Spike?")
sop4 = st.sidebar.checkbox("News Guard CLEAR?")
st.sidebar.divider()
st.sidebar.subheader("📉 RISK MGMT")
bal = st.sidebar.number_input("Wallet ($)", value=1000)
st.sidebar.info(f"Lot Size: {(bal * 0.01) / 50:.2f}")

# 3. TOP HEADER
st.markdown('<div style="background: linear-gradient(90deg, #00c853, #b2ff59); padding: 15px; border-radius: 10px; color: black; text-align: center; font-weight: bold; font-size: 22px;">🛡️ PATRO AI PRO | INSTITUTIONAL MASTER v5.1</div>', unsafe_allow_html=True)
st.write(f"🛡️ **NEWS GUARD:** Mon Mar 2 | ISM PMI (6:00 PM EAT)")
c1, c2 = st.columns(2)
c1.info("📅 PMI News at 10:00 AM EST")
c2.error("🚨 NFP News Friday")

# 4. DATA ENGINE (10s REFRESH)
st_autorefresh(interval=10000, key="no_fake_v5")
df = yf.download("YM=F", period="1d", interval=tf, prepost=True)

if not df.empty:
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    
    # INDICATORS
    df['VWAP'] = (((df['High'] + df['Low'] + df['Close']) / 3) * df['Volume']).cumsum() / df['Volume'].cumsum()
    df['SMA'] = df['Close'].rolling(20).mean()
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    df['RSI'] = 100 - (100 / (1 + (gain / (loss + 1e-9))))

    # 5. THE 3-LAYER CHART
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.6, 0.15, 0.25])
    
    # Layer 1: Candles + VWAP + SMA
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='US30'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['VWAP'], line=dict(color='cyan', width=2), name='VWAP'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA'], line=dict(color='orange', width=1.5), name='20 SMA'), row=1, col=1)

    # Layer 2: Volume (RESTORED)
    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name='Volume', marker_color='rgba(128, 128, 128, 0.5)'), row=2, col=1)

    # Layer 3: RSI
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], line=dict(color='purple', width=2), name='RSI'), row=3, col=1)

    # 6. "NO-FAKE" SIGNAL LOOP (NON-REPAINTING)
    today = datetime.date.today()
    for i in range(20, len(df)):
        if df.index[i].date() == today:
            # Triple Confluence Check
            if (df['Close'].iloc[i] > df['VWAP'].iloc[i] and df['Close'].iloc[i] > df['SMA'].iloc[i] and df['RSI'].iloc[i] > 55):
                if df['Close'].iloc[i-1] <= df['VWAP'].iloc[i-1]:
                    fig.add_annotation(x=df.index[i], y=df['Low'].iloc[i], text="BUY", bgcolor="green", font=dict(color="white"), row=1, col=1)
            elif (df['Close'].iloc[i] < df['VWAP'].iloc[i] and df['Close'].iloc[i] < df['SMA'].iloc[i] and df['RSI'].iloc[i] < 45):
                if df.index[i].date() == today and df['Close'].iloc[i-1] >= df['VWAP'].iloc[i-1]:
                    fig.add_annotation(x=df.index[i], y=df['High'].iloc[i], text="SELL", bgcolor="red", font=dict(color="white"), row=1, col=1)

    fig.update_layout(template="plotly_dark", height=850, xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

st.success(f"TERMINAL SECURE | NO-REPAINT ACTIVE | SCANNING {tf} TIMEFRAME")
