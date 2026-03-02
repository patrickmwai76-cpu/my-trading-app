import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from streamlit_autorefresh import st_autorefresh
from plotly.subplots import make_subplots

# 1. Security & Mobile Layout
if 'auth' not in st.session_state: st.session_state['auth'] = False
if not st.session_state['auth']:
    st.title("🛡️ PATRO AI PRO | MOBILE ACCESS")
    u, p = st.text_input("User"), st.text_input("Pass", type="password")
    if st.button("Unlock Terminal"):
        if u == "PATRO_ADMIN" and p == "patro666@":
            st.session_state['auth'] = True
            st.rerun()
    st.stop()

st.set_page_config(page_title="PATRO AI PRO", layout="wide")
st_autorefresh(interval=30000, key="f5_mobile") # Refreshes every 30s

# 2. Sidebar
st.sidebar.title("🛡️ CONTROL")
tf = st.sidebar.radio("Timeframe", ["1m", "5m", "15m"], index=0, horizontal=True)
st.sidebar.divider()
st.sidebar.success("MARKET: OPEN (FUTURES)")

# 3. Main Header
st.markdown('<div style="background: linear-gradient(90deg, #00c853, #b2ff59); padding: 10px; border-radius: 8px; color: black; text-align: center; font-weight: bold; font-size: 20px;">🛡️ PATRO AI PRO v4.0</div>', unsafe_allow_html=True)

# 4. Live Data Engine (YM=F for 24/5 Motion)
ticker = "YM=F" 
df = yf.download(ticker, period="1d", interval=tf, prepost=True)

if not df.empty:
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    
    # Technical Confluence Logic
    # VWAP Calculation
    df['VWAP'] = ( ((df['High'] + df['Low'] + df['Close']) / 3) * df['Volume'] ).cumsum() / df['Volume'].cumsum()
    df['SMA'] = df['Close'].rolling(20).mean()
    
    # RSI Calculation
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    df['RSI'] = 100 - (100 / (1 + (gain / (loss + 1e-9))))

    # 5. Mobile-Optimized Charting
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.6, 0.1, 0.3])
    
    # Main Layer: Price + VWAP + SMA
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='US30'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['VWAP'], line=dict(color='cyan', width=2), name='VWAP'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA'], line=dict(color='orange', width=1), name='20 SMA'), row=1, col=1)

    # 6. CONFLUENCE SIGNALS (RSI + VWAP + SMA)
    for i in range(15, len(df)):
        # Institutional Buy: Price > SMA AND Price > VWAP AND RSI > 50
        if (df['Close'].iloc[i] > df['SMA'].iloc[i] and df['Close'].iloc[i] > df['VWAP'].iloc[i] and df['RSI'].iloc[i] > 55):
            if df['Close'].iloc[i-1] <= df['SMA'].iloc[i-1]:
                fig.add_annotation(x=df.index[i], y=df['Low'].iloc[i], text="BUY", bgcolor="green", font=dict(color="white", size=10), row=1, col=1)
        
        # Institutional Sell: Price < SMA AND Price < VWAP AND RSI < 45
        elif (df['Close'].iloc[i] < df['SMA'].iloc[i] and df['Close'].iloc[i] < df['VWAP'].iloc[i] and df['RSI'].iloc[i] < 45):
            if df['Close'].iloc[i-1] >= df['SMA'].iloc[i-1]:
                fig.add_annotation(x=df.index[i], y=df['High'].iloc[i], text="SELL", bgcolor="red", font=dict(color="white", size=10), row=1, col=1)

    # Oscillator Layers
    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name='Vol', marker_color='gray'), row=2, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], line=dict(color='purple'), name='RSI'), row=3, col=1)

    fig.update_layout(template="plotly_dark", height=700, margin=dict(l=10, r=10, t=10, b=10), xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.error("Connecting to Liquidity Provider... (Check Ticker)")
