import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from streamlit_autorefresh import st_autorefresh
from plotly.subplots import make_subplots

# 1. SETUP & SESSION
st.set_page_config(page_title="PATRO AI PRO V8.0", layout="wide")
if 'auth' not in st.session_state: st.session_state['auth'] = False
if 'trade_lock' not in st.session_state: st.session_state.trade_lock = None

# 2. SECURITY
if not st.session_state['auth']:
    st.title("🛡️ PATRO AI PRO | SECURE ACCESS")
    u, p = st.text_input("User"), st.text_input("Pass", type="password")
    if st.button("Unlock"):
        if u == "PATRO_ADMIN" and p == "patro666@":
            st.session_state['auth'] = True
            st.rerun()
    st.stop()

# 3. SIDEBAR: INSTITUTIONAL SOP & CONTROLS
with st.sidebar:
    st.title("🎮 PATRO CONTROL")
    st.divider()
    
    st.subheader("📋 INSTITUTIONAL SOP")
    sop_trend = st.checkbox("Trend Matrix Confluence", value=True)
    sop_vwap = st.checkbox("Price Action near VWAP", value=True)
    sop_vol = st.checkbox("Volume Confirmation", value=True)
    
    st.divider()
    st.subheader("⚙️ SETTINGS")
    asset_choice = st.selectbox("Asset", ["XAUUSD (GOLD)", "US30 (DOW JONES)"])
    tf = st.radio("Timeframe", ["1m", "5m", "15m"], index=0, horizontal=True)
    
    if st.button("♻️ RESET SIGNAL LOCK", use_container_width=True):
        st.session_state.trade_lock = None
        st.rerun()

# 4. DATA ENGINE
ticker = "GC=F" if asset_choice == "XAUUSD (GOLD)" else "^DJI"
st_autorefresh(interval=10000, key="v8_sop_pulse")

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

        # 5. SIGNAL LOGIC
        if st.session_state.trade_lock is None and sop_trend and sop_vwap and sop_vol:
            if last_p < last_v and last_p < last_s and last_r < 45:
                st.session_state.trade_lock = {"type": "SELL", "en": last_p, "sl": last_p + (atr_val*1.5), "tp": last_p - (atr_val*3), "time": df.index[-1]}
                st.toast("🚨 SOP CONFIRMED: SELL SIGNAL")
            elif last_p > last_v and last_p > last_s and last_r > 55:
                st.session_state.trade_lock = {"type": "BUY", "en": last_p, "sl": last_p - (atr_val*1.5), "tp": last_p + (atr_val*3), "time": df.index[-1]}
                st.toast("💰 SOP CONFIRMED: BUY SIGNAL")

        # 6. CHARTING WITH SUBPLOTS (PRICE & VOLUME)
        st.header(f"📊 {asset_choice} Terminal")
        
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.7, 0.3])

        # --- ROW 1: CANDLES, VWAP, SMA ---
        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Market"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['VWAP'], line=dict(color='cyan', width=2), name='VWAP'), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['SMA'], line=dict(color='orange', width=1.5), name='SMA 20'), row=1, col=1)

        # --- ROW 2: VOLUME ---
        vol_colors = ['#ff4b4b' if row['Open'] > row['Close'] else '#00ff00' for _, row in df.iterrows()]
        fig.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color=vol_colors, name="Volume"), row=2, col=1)

        # --- SIGNAL MARKERS & LINES ---
        if st.session_state.trade_lock:
            t = st.session_state.trade_lock
            color = "#ff4b4b" if t['type'] == "SELL" else "#00ff00"
            symbol = "triangle-down" if t['type'] == "SELL" else "triangle-up"
            
            # Locked Price Lines
            fig.add_hline(y=t['en'], line_dash="dot", line_color="white", annotation_text="ENTRY", row=1, col=1)
            fig.add_hline(y=t['sl'], line_dash="dash", line_color="red", row=1, col=1)
            fig.add_hline(y=t['tp'], line_dash="dash", line_color="lime", row=1, col=1)
            
            # Triangle Marker on the specific Candle
            fig.add_trace(go.Scatter(x=[t['time']], y=[t['en']], mode="markers", 
                                     marker=dict(symbol=symbol, size=15, color=color), name="Entry Marker"), row=1, col=1)
            
            st.error(f"LOCKED {t['type']} | Entry: {t['en']:.2f} | SL: {t['sl']:.2f} | TP: {t['tp']:.2f}")
        else:
            st.info("🔍 SCANNING: Confirm Trend, VWAP, and Volume in Sidebar to enable signals.")

        fig.update_layout(template="plotly_dark", height=750, xaxis_rangeslider_visible=False, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Syncing Data... {e}")
