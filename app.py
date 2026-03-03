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
        <h1 style="color: white; margin: 0;">PATRO AI PRO V8.0 <span style="font-size: 15px; color: #00ff00;">● SOP ACTIVE</span></h1>
        <p style="color: #bdc3c7; margin: 0;">Institutional Terminal | {asset_choice}</p>
    </div>
""", unsafe_allow_html=True)

tf = st.sidebar.radio("Timeframe", ["1m", "5m", "15m"], index=0, horizontal=True)

# SIDEBAR SOP CHECKLIST (Functional)
st.sidebar.subheader("📋 INSTITUTIONAL SOP")
sop_trend = st.sidebar.checkbox("Trend Matrix Confluence", value=True)
sop_vwap = st.sidebar.checkbox("Price near VWAP (Strike Zone)", value=True)
sop_vol = st.sidebar.checkbox("Volume Confirmation", value=True)

st_autorefresh(interval=10000, key="v8_master_pulse")

try:
    df = yf.download(ticker, period="1d", interval=tf)
    if not df.empty:
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        # --- CALCULATE INSTITUTIONAL INDICATORS ---
        df['VWAP'] = (((df['High'] + df['Low'] + df['Close']) / 3) * df['Volume']).cumsum() / df['Volume'].cumsum()
        df['SMA'] = df['Close'].rolling(20).mean()
        df['Vol_Avg'] = df['Volume'].rolling(10).mean()
        
        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        df['RSI'] = 100 - (100 / (1 + (gain / (loss + 1e-9))))
        
        # ATR for Dynamic Risk
        df['ATR'] = (df['High'] - df['Low']).rolling(14).mean()

        # --- SOP ENGINE LOGIC ---
        last = df.iloc[-1]
        vol_confirmed = last['Volume'] > last['Vol_Avg'] if sop_vol else True
        
        # Trend Matrix: Price must be on the same side of SMA and VWAP
        matrix_buy = last['Close'] > last['SMA'] and last['Close'] > last['VWAP']
        matrix_sell = last['Close'] < last['SMA'] and last['Close'] < last['VWAP']
        
        # VWAP Strike Zone: Price must be within 0.1% of VWAP to avoid overextension
        vwap_dist = abs(last['Close'] - last['VWAP']) / last['VWAP']
        near_vwap = vwap_dist < 0.002 if sop_vwap else True # 0.2% threshold

        signal_type = "NEUTRAL"
        if sop_trend:
            if matrix_buy and near_vwap and vol_confirmed and last['RSI'] > 50:
                signal_type = "BUY"
            elif matrix_sell and near_vwap and vol_confirmed and last['RSI'] < 50:
                signal_type = "SELL"

        # Display Signal
        if signal_type == "BUY":
            st.success(f"🚀 BUY SIGNAL: Confluence Met at {last['Close']:.2f}")
            sl, tp = last['Close'] - (last['ATR']*2), last['Close'] + (last['ATR']*4)
        elif signal_type == "SELL":
            st.error(f"📉 SELL SIGNAL: Confluence Met at {last['Close']:.2f}")
            sl, tp = last['Close'] + (last['ATR']*2), last['Close'] - (last['ATR']*4)
        else:
            st.info("🔎 SCANNING: Waiting for SOP Confluence...")

        # --- VISUALS ---
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.7, 0.3])
        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['VWAP'], line=dict(color='cyan', width=2), name='VWAP'), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['SMA'], line=dict(color='orange', width=1), name='SMA 20'), row=1, col=1)

        if signal_type != "NEUTRAL":
            color = "lime" if signal_type == "BUY" else "red"
            symbol = "triangle-up" if signal_type == "BUY" else "triangle-down"
            fig.add_trace(go.Scatter(x=[df.index[-1]], y=[last['Close']], mode="markers", marker=dict(symbol=symbol, size=20, color=color, line=dict(width=2, color="white"))), row=1, col=1)
            fig.add_hline(y=sl, line_dash="dash", line_color="red", annotation_text="SL", row=1, col=1)
            fig.add_hline(y=tp, line_dash="dash", line_color="lime", annotation_text="TP", row=1, col=1)

        fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name="Volume", marker_color="gray"), row=2, col=1)
        fig.update_layout(template="plotly_dark", height=800, xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Terminal Error: {e}")
