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

# 2. ASSET SELECTION
asset_choice = st.sidebar.selectbox("Select Asset", ["XAUUSD (GOLD)", "US30 (DOW JONES)"])
ticker = "GC=F" if asset_choice == "XAUUSD (GOLD)" else "^DJI"

# 3. HEADER
st.markdown(f"""
    <div style="background-color: #1e1e1e; padding: 20px; border-radius: 10px; border-bottom: 4px solid #f39c12;">
        <h1 style="color: white; margin: 0;">PATRO AI PRO V8.0 <span style="font-size: 15px; color: #00ff00;">● LIVE</span></h1>
        <p style="color: #bdc3c7; margin: 0;">Institutional Terminal | Asset: {asset_choice}</p>
    </div>
""", unsafe_allow_html=True)

tf = st.sidebar.radio("Timeframe", ["1m", "5m", "15m"], index=0, horizontal=True)
st_autorefresh(interval=10000, key="v8_master_pulse")

# 4. DATA ENGINE
try:
    df = yf.download(ticker, period="1d", interval=tf)
    if not df.empty:
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        # INDICATORS
        df['VWAP'] = (((df['High'] + df['Low'] + df['Close']) / 3) * df['Volume']).cumsum() / df['Volume'].cumsum()
        df['SMA'] = df['Close'].rolling(20).mean()
        
        # RSI & ATR
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        df['RSI'] = 100 - (100 / (1 + (gain / (loss + 1e-9))))
        df['ATR'] = (df['High'] - df['Low']).rolling(14).mean()

        # --- 5. SIGNAL & RISK CALCULATIONS ---
        last_p, last_v, last_s, last_r = df['Close'].iloc[-1], df['VWAP'].iloc[-1], df['SMA'].iloc[-1], df['RSI'].iloc[-1]
        atr_val = df['ATR'].iloc[-1] if not pd.isna(df['ATR'].iloc[-1]) else 1.5
        sl_dist = atr_val * 1.5
        
        # Initialize Variables to avoid NameError
        signal_type = "NEUTRAL"
        entry_price = last_p
        stop_loss = last_p
        take_profit = last_p

        # Institutional Confluence Check
        if last_p > last_v and last_p > last_s and last_r > 52:
            signal_type = "BUY"
            stop_loss = entry_price - sl_dist
            take_profit = entry_price + (sl_dist * 2)
            st.success(f"🚀 **INSTITUTIONAL BUY** | Entry: {entry_price:.2f} | SL: {stop_loss:.2f} | TP: {take_profit:.2f}")
        elif last_p < last_v and last_p < last_s and last_r < 48:
            signal_type = "SELL"
            stop_loss = entry_price + sl_dist
            take_profit = entry_price - (sl_dist * 2)
            st.error(f"📉 **INSTITUTIONAL SELL** | Entry: {entry_price:.2f} | SL: {stop_loss:.2f} | TP: {take_profit:.2f}")
        else:
            st.info("🔵 SCANNING: Waiting for SOP Confluence (Price must clear VWAP & SMA)...")

        # --- 6. CHARTING ENGINE ---
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.04, row_heights=[0.5, 0.2, 0.3])
        
        # Price, VWAP, SMA
        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['VWAP'], line=dict(color='cyan', width=2), name='Inst. VWAP'), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['SMA'], line=dict(color='orange', width=1.5), name='Trend SMA'), row=1, col=1)

        # FORCE MARKERS ON CANDLES
        if signal_type != "NEUTRAL":
            marker_y = df['Low'].iloc[-1] * 0.999 if signal_type == "BUY" else df['High'].iloc[-1] * 1.001
            marker_color = "lime" if signal_type == "BUY" else "red"
            marker_symbol = "triangle-up" if signal_type == "BUY" else "triangle-down"

            # 1. Triangle on Candle
            fig.add_trace(go.Scatter(x=[df.index[-1]], y=[marker_y], mode="markers", 
                                     marker=dict(symbol=marker_symbol, size=20, color=marker_color), 
                                     name=f"{signal_type} SIGNAL"), row=1, col=1)
            
            # 2. Risk Lines (Drawn across the chart)
            fig.add_hline(y=entry_price, line_dash="dot", line_color="white", annotation_text="ENTRY", row=1, col=1)
            fig.add_hline(y=stop_loss, line_dash="dash", line_color="red", annotation_text="STOP LOSS", row=1, col=1)
            fig.add_hline(y=take_profit, line_dash="dash", line_color="lime", annotation_text="TAKE PROFIT", row=1, col=1)

        # Volume & RSI
        fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name='Volume', marker_color='#444444'), row=2, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], line=dict(color='purple', width=2), name='RSI'), row=3, col=1)

        fig.update_layout(template="plotly_dark", height=800, xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.error("Market data feed interrupted. Reconnecting...")
except Exception as e:
    st.warning(f"Connecting to Market Feed... {e}")
