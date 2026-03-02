import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from streamlit_autorefresh import st_autorefresh
from plotly.subplots import make_subplots
import datetime

# 1. SECURITY & CONFIG
st.set_page_config(page_title="PATRO AI PRO", layout="wide")
if 'auth' not in st.session_state: st.session_state['auth'] = False
if not st.session_state['auth']:
    st.title("🛡️ PATRO AI PRO | SECURE ACCESS")
    u, p = st.text_input("User"), st.text_input("Pass", type="password")
    if st.button("Unlock"):
        if u == "PATRO_ADMIN" and p == "patro666@":
            st.session_state['auth'] = True
            st.rerun()
    st.stop()

# 2. SIDEBAR
st.sidebar.title("🛡️ CONTROL")
tf = st.sidebar.radio("Timeframe", ["1m", "5m", "15m"], index=0, horizontal=True)
st.sidebar.divider()
st.sidebar.subheader("📋 OPERATOR SOP")
s1 = st.sidebar.checkbox("Trend Matrix Confluence?")
s2 = st.sidebar.checkbox("Price Action near VWAP?")
s3 = st.sidebar.checkbox("Risk Management set?")

# 3. HEADER & NEWS
st.markdown('<div style="background: linear-gradient(90deg, #00c853, #b2ff59); padding: 10px; border-radius: 8px; color: black; text-align: center; font-weight: bold; font-size: 20px;">🛡️ PATRO AI PRO | MON MAR 2 SESSION</div>', unsafe_allow_html=True)
st.info("📊 **MARKET STATUS:** PRE-MARKET VOLATILITY (FUTURES ACTIVE)")

# 4. DATA ENGINE (10s REFRESH)
st_autorefresh(interval=10000, key="monday_pulse")
df = yf.download("YM=F", period="1d", interval=tf, prepost=True)

if not df.empty:
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    
    # CALCULATE INDICATORS
    df['VWAP'] = (((df['High'] + df['Low'] + df['Close']) / 3) * df['Volume']).cumsum() / df['Volume'].cumsum()
    df['SMA'] = df['Close'].rolling(20).mean()
    change = df['Close'].diff()
    gain = (change.where(change > 0, 0)).rolling(14).mean()
    loss = (-change.where(change < 0, 0)).rolling(14).mean()
    df['RSI'] = 100 - (100 / (1 + (gain / (loss + 1e-9))))

    # 5. CHARTING
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.7, 0.3])
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='US30'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['VWAP'], line=dict(color='cyan', width=2), name='VWAP'), row=1, col=1)

    # 6. TODAY'S SIGNAL RESET
    # This loop ONLY looks at today's data to avoid old Friday signals
    today = datetime.date.today()
    for i in range(20, len(df)):
        # Check if the candle belongs to TODAY
        if df.index[i].date() == today:
            # BUY: Above VWAP + RSI > 55
            if (df['Close'].iloc[i] > df['VWAP'].iloc[i] and df['RSI'].iloc[i] > 55):
                if df['Close'].iloc[i-1] <= df['VWAP'].iloc[i-1]:
                    fig.add_annotation(x=df.index[i], y=df['Low'].iloc[i], text="BUY", bgcolor="green", font=dict(color="white"), row=1, col=1)
            # SELL: Below VWAP + RSI < 45
            elif (df['Close'].iloc[i] < df['VWAP'].iloc[i] and df['RSI'].iloc[i] < 45):
                if df['Close'].iloc[i-1] >= df['VWAP'].iloc[i-1]:
                    fig.add_annotation(x=df.index[i], y=df['High'].iloc[i], text="SELL", bgcolor="red", font=dict(color="white"), row=1, col=1)

    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], line=dict(color='purple'), name='RSI'), row=2, col=1)
    fig.update_layout(template="plotly_dark", height=700, xaxis_rangeslider_visible=False)
    
    st.write(f"⏱️ **Last Price Tick:** {df.index[-1].strftime('%H:%M:%S')} (Waiting for Institutional Confluence...)")
    st.plotly_chart(fig, use_container_width=True)
