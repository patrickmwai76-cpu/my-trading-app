import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from streamlit_autorefresh import st_autorefresh
from plotly.subplots import make_subplots
import datetime

# 1. Page Config
st.set_page_config(page_title="PATRO AI PRO", layout="wide")

# 2. FAST PULSE (Refreshes every 5 seconds for MT5 feel)
st_autorefresh(interval=5000, key="mt5_pulse")

if 'auth' not in st.session_state: st.session_state['auth'] = False
if not st.session_state['auth']:
    st.title("🛡️ PATRO AI PRO | SECURE ACCESS")
    u, p = st.text_input("User"), st.text_input("Pass", type="password")
    if st.button("Unlock"):
        if u == "PATRO_ADMIN" and p == "patro666@":
            st.session_state['auth'] = True
            st.rerun()
    st.stop()

# 3. Sidebar Features
st.sidebar.title("🛡️ CONTROL")
tf = st.sidebar.radio("Timeframe", ["1m", "5m", "15m"], index=0, horizontal=True)
st.sidebar.divider()
st.sidebar.subheader("📋 OPERATOR SOP")
s1 = st.sidebar.checkbox("Trend Matrix?")
s2 = st.sidebar.checkbox("VWAP Alignment?")

# 4. Data Engine (Using YM=F for LIVE Pre-Market Motion)
df = yf.download("YM=F", period="1d", interval=tf, prepost=True)

if not df.empty:
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    
    # INDICATORS
    df['VWAP'] = (((df['High'] + df['Low'] + df['Close']) / 3) * df['Volume']).cumsum() / df['Volume'].cumsum()
    df['SMA'] = df['Close'].rolling(20).mean()
    
    # RSI Calculation
    change = df['Close'].diff()
    gain = (change.where(change > 0, 0)).rolling(14).mean()
    loss = (-change.where(change < 0, 0)).rolling(14).mean()
    df['RSI'] = 100 - (100 / (1 + (gain / (loss + 1e-9))))

    # 5. HEADER
    st.markdown('<div style="background: #00c853; padding: 10px; border-radius: 5px; color: black; text-align: center; font-weight: bold;">🛡️ US30 LIVE STREAM ACTIVE</div>', unsafe_allow_html=True)
    st.write(f"📊 **Price:** {df['Close'].iloc[-1]:.2f} | **Last Update:** {datetime.datetime.now().strftime('%H:%M:%S')}")

    # 6. CHARTING
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.7, 0.3])
    
    # Candles
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='US30'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['VWAP'], line=dict(color='cyan', width=2), name='VWAP'), row=1, col=1)

    # 7. FIXED SIGNAL LOGIC (Relaxed for Pre-Market)
    for i in range(10, len(df)):
        # BUY: Price is above SMA and crossing up
        if df['Close'].iloc[i] > df['SMA'].iloc[i] and df['Close'].iloc[i-1] <= df['SMA'].iloc[i-1]:
            fig.add_annotation(x=df.index[i], y=df['Low'].iloc[i], text="BUY", bgcolor="green", font=dict(color="white"), row=1, col=1)
        
        # SELL: Price is below SMA and crossing down
        elif df['Close'].iloc[i] < df['SMA'].iloc[i] and df['Close'].iloc[i-1] >= df['SMA'].iloc[i-1]:
            fig.add_annotation(x=df.index[i], y=df['High'].iloc[i], text="SELL", bgcolor="red", font=dict(color="white"), row=1, col=1)

    # RSI Layer
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], line=dict(color='purple'), name='RSI'), row=2, col=1)
    
    fig.update_layout(template="plotly_dark", height=700, xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)
