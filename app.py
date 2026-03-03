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
dist_threshold = 1.5 if asset_choice == "XAUUSD (GOLD)" else 5.0

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
st.sidebar.checkbox("Price near VWAP (Strike Zone)?", value=True)
st.sidebar.checkbox("Volume Confirmation?", value=True)

# 4. NEWS GUARD ENGINE
now_eat = datetime.datetime.now()
news_events = [{"name": "🇺🇸 ISM Manufacturing PMI", "time": datetime.time(18, 00)}]
for event in news_events:
    event_time = datetime.datetime.combine(datetime.date.today(), event['time'])
    time_diff = (event_time - now_eat).total_seconds() / 60
    if -30 < time_diff < 30:
        st.error(f"🚨 NEWS GUARD: {event['name']} is LIVE! Extreme Volatility.")

# 5. DATA ENGINE (10s REFRESH)
st_autorefresh(interval=10000, key="v8_master_pulse")

try:
    df = yf.download(ticker, period="1d", interval=tf)
    if not df.empty:
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        # INDICATORS
        df['VWAP'] = (((df['High'] + df['Low'] + df['Close']) / 3) * df['Volume']).cumsum() / df['Volume'].cumsum()
        df['SMA'] = df['Close'].rolling(20).mean()
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        df['RSI'] = 100 - (100 / (1 + (gain / (loss + 1e-9))))
        df['ATR'] = (df['High'] - df['Low']).rolling(14).mean()

        # SIGNAL LOGIC
        last_p, last_v, last_s, last_r = df['Close'].iloc[-1], df['VWAP'].iloc[-1], df['SMA'].iloc[-1], df['RSI'].iloc[-1]
        atr_sl = df['ATR'].iloc[-1] * 1.5
        signal_type = "NEUTRAL"

        if last_p > last_v and last_p > last_s and last_r > 55:
            signal_type = "BUY"
            en, sl, tp = last_p, last_p - atr_sl, last_p + (atr_sl * 2)
            st.success(f"🚀 **INSTITUTIONAL BUY** | Entry: {en:.2f} | SL: {sl:.2f} | TP: {tp:.2f}")
        elif last_p < last_v and last_p < last_s and last_r < 45:
            signal_type = "SELL"
            en, sl, tp = last_p, last_p + atr_sl, last_p - (atr_sl * 2)
            st.error(f"📉 **INSTITUTIONAL SELL** | Entry: {en:.2f} | SL: {sl:.2f} | TP: {tp:.2f}")
        else:
            st.info("🔵 SCANNING: Waiting for SOP Confluence...")

        # 6. CHARTING (ALL FEATURES)
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.04, row_heights=[0.5, 0.2, 0.3])
        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['VWAP'], line=dict(color='cyan', width=2), name='VWAP'), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['SMA'], line=dict(color='orange', width=1.5), name='SMA 20'), row=1, col=1)

        if signal_type != "NEUTRAL":
            # Candle Markers
            m_y = df['Low'].iloc[-1] * 0.999 if signal_type == "BUY" else df['High'].iloc[-1] * 1.001
            m_sym = "triangle-up" if signal_type == "BUY" else "triangle-down"
            fig.add_trace(go.Scatter(x=[df.index[-1]], y=[m_y], mode="markers", marker=dict(symbol=m_sym, size=15, color="lime" if signal_type=="BUY" else "red"), name="SIGNAL"), row=1, col=1)
            # SL, TP, Entry Lines
            fig.add_hline(y=en, line_dash="dot", line_color="white", annotation_text="ENTRY", row=1, col=1)
            fig.add_hline(y=sl, line_dash="dash", line_color="red", annotation_text="STOP LOSS", row=1, col=1)
            fig.add_hline(y=tp, line_dash="dash", line_color="lime", annotation_text="TAKE PROFIT", row=1, col=1)

        fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name='Volume', marker_color='#444444'), row=2, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], line=dict(color='purple', width=2), name='RSI'), row=3, col=1)
        fig.update_layout(template="plotly_dark", height=750, xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
except Exception as e:
    st.warning(f"Connecting... {e}")
