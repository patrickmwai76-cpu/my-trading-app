import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from streamlit_autorefresh import st_autorefresh
from plotly.subplots import make_subplots
import datetime
import numpy as np

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

if asset_choice == "XAUUSD (GOLD)":
    ticker = "GC=F"  
    dist_threshold = 1.5
else:
    ticker = "^DJI"  
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
        if isinstance(df.columns, pd.MultiIndex): 
            df.columns = df.columns.get_level_values(0)
        
        # --- INDICATORS ---
        df['VWAP'] = (((df['High'] + df['Low'] + df['Close']) / 3) * df['Volume']).cumsum() / df['Volume'].cumsum()
        df['SMA'] = df['Close'].rolling(20).mean()
        
        # RSI Calculation
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        df['RSI'] = 100 - (100 / (1 + (gain / (loss + 1e-9))))
        
        # ATR Calculation for Dynamic Stop Loss
        high_low = df['High'] - df['Low']
        high_cp = np.abs(df['High'] - df['Close'].shift(1))
        low_cp = np.abs(df['Low'] - df['Close'].shift(1))
        df['TR'] = pd.concat([high_low, high_cp, low_cp], axis=1).max(axis=1)
        df['ATR'] = df['TR'].rolling(window=14).mean()

        # --- 5. LIVE SIGNAL LOGIC ---
        last_price = df['Close'].iloc[-1]
        last_vwap = df['VWAP'].iloc[-1]
        last_rsi = df['RSI'].iloc[-1]
        # Multiplier: 1.5 for Gold, 2.0 for US30
        sl_mult = 1.5 if asset_choice == "XAUUSD (GOLD)" else 2.0
        atr_sl = df['ATR'].iloc[-1] * sl_mult

        signal_type = "NEUTRAL"
        if last_price > last_vwap and last_rsi > 55:
            signal_type = "BUY"
            entry_price = last_price
            stop_loss = entry_price - atr_sl
            st.success(f"🚀 **SIGNAL: BUY** | Price: ${last_price:.2f} | SL: ${stop_loss:.2f}")
        elif last_price < last_vwap and last_rsi < 45:
            signal_type = "SELL"
            entry_price = last_price
            stop_loss = entry_price + atr_sl
            st.error(f"📉 **SIGNAL: SELL** | Price: ${last_price:.2f} | SL: ${stop_loss:.2f}")
        else:
            st.warning("⚖️ **STATUS: CONSOLIDATION** | Waiting for Confluence")

        # --- 6. CHARTING ENGINE ---
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.04, row_heights=[0.5, 0.2, 0.3])
        
        # Candlestick
        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name=asset_choice), row=1, col=1)
        
        # VWAP & SMA
        fig.add_trace(go.Scatter(x=df.index, y=df['VWAP'], line=dict(color='cyan', width=2.5), name='VWAP'), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['SMA'], line=dict(color='orange', width=1.5), name='SMA'), row=1, col=1)
        
        # Visual Signal Markers & Risk Lines
        if signal_type == "BUY":
            fig.add_trace(go.Scatter(x=[df.index[-1]], y=[df['Low'].iloc[-1]*0.999], mode="markers", marker=dict(symbol="triangle-up", size=15, color="lime"), name="BUY TRIGGER"), row=1, col=1)
            fig.add_hline(y=entry_price, line_dash="dot", line_color="white", annotation_text="ENTRY", row=1, col=1)
            fig.add_hline(y=stop_loss, line_dash="dash", line_color="red", annotation_text="STOP LOSS", row=1, col=1)
        elif signal_type == "SELL":
            fig.add_trace(go.Scatter(x=[df.index[-1]], y=[df['High'].iloc[-1]*1.001], mode="markers", marker=dict(symbol="triangle-down", size=15, color="red"), name="SELL TRIGGER"), row=1, col=1)
            fig.add_hline(y=entry_price, line_dash="dot", line_color="white", annotation_text="ENTRY", row=1, col=1)
            fig.add_hline(y=stop_loss, line_dash="dash", line_color="red", annotation_text="STOP LOSS", row=1, col=1)

        # Volume & RSI
        fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name='Volume', marker_color='#444444'), row=2, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], line=dict(color='purple', width=2), name='RSI'), row=3, col=1)

        fig.update_layout(template="plotly_dark", height=750, xaxis_rangeslider_visible=False, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.error("Searching for market data... please wait.")

except Exception as e:
    st.warning(f"Connecting to Market Feed... {e}")

st.info(f"🛡️ PATRO V8.0: Institutional Mode Active. Syncing with .m Gold accounts.")
