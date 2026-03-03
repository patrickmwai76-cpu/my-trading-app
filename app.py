import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from streamlit_autorefresh import st_autorefresh
from plotly.subplots import make_subplots
import datetime

# 1. SECURITY & CONFIG
st.set_page_config(page_title="PATRO AI PRO V8.0", layout="wide")
if 'auth' not in st.session_state: st.session_state['auth'] = False
if not st.session_state['auth']:
    st.title("🛡️ PATRO AI PRO | SECURE ACCESS")
    u, p = st.text_input("User"), st.text_input("Pass", type="password")
    if st.button("Unlock"):
        if u == "PATRO_ADMIN" and p == "patro666@":
            st.session_state['auth'] = True
            st.rerun()
    st.stop()

# 2. ASSET SELECTION & TICKER SETUP
asset_choice = st.sidebar.selectbox("Select Asset", ["XAUUSD (GOLD)", "US30 (DOW JONES)"])

# Define ticker and thresholds immediately to avoid NameError
if asset_choice == "XAUUSD (GOLD)":
    ticker = "GC=F"  # Gold Futures
    dist_threshold = 1.5
else:
    ticker = "^DJI"  # Dow Jones
    dist_threshold = 5.0

# 3. PROFESSIONAL HEADER
st.markdown(f"""
    <div style="background-color: #1e1e1e; padding: 20px; border-radius: 10px; border-bottom: 4px solid #f39c12;">
        <h1 style="color: white; margin: 0;">PATRO AI PRO V8.0 <span style="font-size: 15px; color: #00ff00;">● LIVE</span></h1>
        <p style="color: #bdc3c7; margin: 0;">Institutional Terminal | Asset: {asset_choice} | .m Account Sync</p>
    </div>
""", unsafe_allow_html=True)

tf = st.sidebar.radio("Timeframe", ["1m", "5m", "15m"], index=0, horizontal=True)
st.sidebar.divider()
st.sidebar.subheader("📋 INSTITUTIONAL SOP")
st.sidebar.checkbox("Trend Matrix Confluence?", value=True)
st.sidebar.checkbox("Price Action near VWAP?", value=True)
st.sidebar.checkbox("Volume Confirmation?", value=True)
bal = st.sidebar.number_input("Wallet ($)", value=1000)

# 4. DATA ENGINE (10s REFRESH)
st_autorefresh(interval=10000, key="v8_master_pulse")

try:
    df = yf.download(ticker, period="1d", interval=tf)
    
    if not df.empty:
        # Clean multi-index columns if they exist
        if isinstance(df.columns, pd.MultiIndex): 
            df.columns = df.columns.get_level_values(0)
        
        # INDICATORS
        df['VWAP'] = (((df['High'] + df['Low'] + df['Close']) / 3) * df['Volume']).cumsum() / df['Volume'].cumsum()
        df['SMA'] = df['Close'].rolling(20).mean()
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        df['RSI'] = 100 - (100 / (1 + (gain / (loss + 1e-9))))
        df['Vol_Avg'] = df['Volume'].rolling(20).mean()

        # 5. LIVE SIGNAL BOX (The logic you wanted back)
        last_price = df['Close'].iloc[-1]
        last_vwap = df['VWAP'].iloc[-1]
        
        if last_price > last_vwap:
            st.success(f"🚀 **SIGNAL: BUY** | Price is above Cyan VWAP (${last_price:.2f})")
        else:
            st.error(f"📉 **SIGNAL: SELL** | Price is below Cyan VWAP (${last_price:.2f})")

        # 6. CHARTING
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.04, row_heights=[0.5, 0.2, 0.3])
        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name=asset_choice), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['VWAP'], line=dict(color='cyan', width=2.5), name='VWAP (Cyan)'), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['SMA'], line=dict(color='orange', width=1.5), name='SMA (Orange)'), row=1, col=1)
        fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name='Volume', marker_color='#444444'), row=2, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], line=dict(color='purple', width=2), name='RSI'), row=3, col=1)

        # Labels on Chart
        for i in range(len(df)-10, len(df)):
            dist = abs(df['Close'].iloc[i] - df['VWAP'].iloc[i])
            if (df['Close'].iloc[i] > df['VWAP'].iloc[i] and df['RSI'].iloc[i] > 55 and dist > dist_threshold):
                if df['Close'].iloc[i-1] <= df['VWAP'].iloc[i-1]:
                    fig.add_annotation(x=df.index[i], y=df['Low'].iloc[i], text="BUY", bgcolor="green", font=dict(color="white"), row=1, col=1)
            elif (df['Close'].iloc[i] < df['VWAP'].iloc[i] and df['RSI'].iloc[i] < 45 and dist > dist_threshold):
                if df['Close'].iloc[i-1] >= df['VWAP'].iloc[i-1]:
                    fig.add_annotation(x=df.index[i], y=df['High'].iloc[i], text="SELL", bgcolor="red", font=dict(color="white"), row=1, col=1)

        fig.update_layout(template="plotly_dark", height=700, xaxis_rangeslider_visible=False, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("Searching for market data... please wait.")

except Exception as e:
    st.warning(f"Connecting to Market Feed... {e}")

st.info(f"🛡️ PATRO V8.0: Institutional Mode Active. Syncing with .m Gold accounts.")
