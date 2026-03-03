import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from streamlit_autorefresh import st_autorefresh
from plotly.subplots import make_subplots
import datetime
import MetaTrader5 as mt5

# --- 1. SESSION & SECURITY ---
st.set_page_config(page_title="PATRO AI PRO V8.0", layout="wide")
if 'auth' not in st.session_state: st.session_state['auth'] = False
if 'trade_lock' not in st.session_state: st.session_state.trade_lock = None

if not st.session_state['auth']:
    st.title("🛡️ PATRO AI PRO | SECURE ACCESS")
    u, p = st.text_input("User"), st.text_input("Pass", type="password")
    if st.button("Unlock"):
        if u == "PATRO_ADMIN" and p == "patro666@":
            st.session_state['auth'] = True
            st.rerun()
    st.stop()

# --- 2. MT5 CONNECTIVITY ---
if not mt5.initialize():
    st.sidebar.error("❌ MT5 Offline")
else:
    st.sidebar.success("✅ MT5 Connected")

def execute_trade(symbol, action, lot, price, sl, tp):
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": mt5.ORDER_TYPE_BUY if action == "BUY" else mt5.ORDER_TYPE_SELL,
        "price": price, "sl": sl, "tp": tp,
        "magic": 123456, "comment": "Patro AI V8.0",
        "type_time": mt5.ORDER_TIME_GTC, "type_filling": mt5.ORDER_FILLING_IOC,
    }
    return mt5.order_send(request)

# --- 3. SIDEBAR & TOOLS ---
asset_choice = st.sidebar.selectbox("Select Asset", ["XAUUSD (GOLD)", "US30 (DOW JONES)"])
ticker = "GC=F" if asset_choice == "XAUUSD (GOLD)" else "^DJI"
tf = st.sidebar.radio("Timeframe", ["1m", "5m", "15m"], index=0, horizontal=True)

if st.sidebar.button("♻️ RESET SIGNAL LOCK"):
    st.session_state.trade_lock = None
    st.rerun()

st.sidebar.divider()
st.sidebar.subheader("📋 INSTITUTIONAL SOP")
st.sidebar.checkbox("Trend Matrix Confluence?", value=True)
st.sidebar.checkbox("Price Action near VWAP?", value=True)

# --- 4. NEWS GUARD ---
now_eat = datetime.datetime.now()
news_events = [{"name": "🇺🇸 ISM Manufacturing PMI", "time": datetime.time(18, 00)}]
for event in news_events:
    event_time = datetime.datetime.combine(datetime.date.today(), event['time'])
    time_diff = (event_time - now_eat).total_seconds() / 60
    if -30 < time_diff < 30:
        st.error(f"🚨 NEWS GUARD: {event['name']} is LIVE!")

# --- 5. DATA ENGINE ---
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

        last_p, last_v, last_s, last_r = df['Close'].iloc[-1], df['VWAP'].iloc[-1], df['SMA'].iloc[-1], df['RSI'].iloc[-1]
        atr_val = df['ATR'].iloc[-1] if not pd.isna(df['ATR'].iloc[-1]) else 1.5
        ping_url = "https://www.soundjay.com/buttons/sounds/button-3.mp3"

        # --- SIGNAL LOCKING LOGIC (NO MORE SLIDING) ---
        if st.session_state.trade_lock is None:
            if last_p < last_v and last_p < last_s and last_r < 45:
                st.session_state.trade_lock = {"type": "SELL", "en": last_p, "sl": last_p + (atr_val*1.5), "tp": last_p - (atr_val*3)}
                st.audio(ping_url, autoplay=True)
                execute_trade(ticker, "SELL", 0.01, last_p, st.session_state.trade_lock['sl'], st.session_state.trade_lock['tp'])
            elif last_p > last_v and last_p > last_s and last_r > 55:
                st.session_state.trade_lock = {"type": "BUY", "en": last_p, "sl": last_p - (atr_val*1.5), "tp": last_p + (atr_val*3)}
                st.audio(ping_url, autoplay=True)
                execute_trade(ticker, "BUY", 0.01, last_p, st.session_state.trade_lock['sl'], st.session_state.trade_lock['tp'])

        # --- CHARTING ENGINE (ALL INDICATORS + SIGNAL MARKERS) ---
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True, row_heights=[0.5, 0.2, 0.3], vertical_spacing=0.04)
        
        # Row 1: Candlesticks, VWAP, SMA
        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['VWAP'], line=dict(color='cyan', width=2), name='VWAP'), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['SMA'], line=dict(color='orange', width=1.5), name='SMA 20'), row=1, col=1)

        # Draw Signal Markers & Risk Lines if Locked
        if st.session_state.trade_lock:
            t = st.session_state.trade_lock
            m_y = df['Low'].iloc[-1]*0.999 if t['type']=="BUY" else df['High'].iloc[-1]*1.001
            m_sym = "triangle-up" if t['type']=="BUY" else "triangle-down"
            m_col = "lime" if t['type']=="BUY" else "red"
            
            fig.add_trace(go.Scatter(x=[df.index[-1]], y=[m_y], mode="markers", marker=dict(symbol=m_sym, size=20, color=m_col), name="LOCKED SIGNAL"), row=1, col=1)
            fig.add_hline(y=t['en'], line_dash="dot", line_color="white", annotation_text="LOCKED ENTRY", row=1, col=1)
            fig.add_hline(y=t['sl'], line_dash="dash", line_color="red", annotation_text="STOP LOSS", row=1, col=1)
            fig.add_hline(y=t['tp'], line_dash="dash", line_color="lime", annotation_text="TAKE PROFIT", row=1, col=1)
            st.toast(f"🚨 {t['type']} ACTIVE AT {t['en']:.2f}")

        # Row 2 & 3: Volume & RSI
        fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name='Volume', marker_color='#444444'), row=2, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], line=dict(color='purple', width=2), name='RSI'), row=3, col=1)

        fig.update_layout(template="plotly_dark", height=800, xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Engine Error: {e}")
