import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from streamlit_autorefresh import st_autorefresh
from plotly.subplots import make_subplots

# 1. SETUP & SESSION
st.set_page_config(page_title="PATRO AI PRO V8.5", layout="wide")
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
    sop_macd_gate = st.checkbox("MACD Momentum Guard", value=True) # MACD GATE
    
    st.divider()
    st.subheader("⚙️ VISUALS")
    show_macd_row = st.toggle("Show MACD Analysis Row", value=True) # MACD TOGGLE
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
        
        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        df['RSI'] = 100 - (100 / (1 + (gain / (loss + 1e-9))))
        
        # MACD ENGINE
        exp1 = df['Close'].ewm(span=12, adjust=False).mean()
        exp2 = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = exp1 - exp2
        df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        df['Hist'] = df['MACD'] - df['Signal']
        
        # ADX (TREND STRENGTH)
        plus_dm = df['High'].diff().clip(lower=0)
        minus_dm = (-df['Low'].diff()).clip(lower=0)
        tr = pd.concat([df['High']-df['Low'], abs(df['High']-df['Close'].shift(1)), abs(df['Low']-df['Close'].shift(1))], axis=1).max(axis=1)
        atr = tr.rolling(14).mean()
        df['ADX'] = (abs((100 * (plus_dm.rolling(14).mean()/atr)) - (100 * (minus_dm.rolling(14).mean()/atr))) / 
                    ((100 * (plus_dm.rolling(14).mean()/atr)) + (100 * (minus_dm.rolling(14).mean()/atr))) * 100).rolling(14).mean()

        df['ATR'] = (df['High'] - df['Low']).rolling(14).mean()

        last = df.iloc[-1]
        atr_val = last['ATR'] if not pd.isna(last['ATR']) else 1.5

        # TREND STRENGTH METER IN SIDEBAR
        with st.sidebar:
            st.divider()
            st.subheader(f"⚡ TREND POWER: {last['ADX']:.1f}%")
            st.progress(min(last['ADX']/100, 1.0))

        # 5. SIGNAL LOGIC (ALL 4 GATES)
        if st.session_state.trade_lock is None and sop_trend and sop_vwap and sop_vol and sop_macd_gate:
            # SELL Logic: Below lines + Negative RSI + Negative MACD Histogram
            if last['Close'] < last['VWAP'] and last['Close'] < last['SMA'] and last['RSI'] < 45 and last['Hist'] < 0:
                st.session_state.trade_lock = {"type": "SELL", "en": last['Close'], "sl": last['Close'] + (atr_val*1.5), "tp": last['Close'] - (atr_val*3), "time": df.index[-1]}
                st.toast("🚨 4-GATE SELL CONFIRMED")
            # BUY Logic: Above lines + Positive RSI + Positive MACD Histogram
            elif last['Close'] > last['VWAP'] and last['Close'] > last['SMA'] and last['RSI'] > 55 and last['Hist'] > 0:
                st.session_state.trade_lock = {"type": "BUY", "en": last['Close'], "sl": last['Close'] - (atr_val*1.5), "tp": last['Close'] + (atr_val*3), "time": df.index[-1]}
                st.toast("💰 4-GATE BUY CONFIRMED")

        # 6. CHARTING WITH SUBPLOTS
        st.header(f"📊 {asset_choice} Terminal")
        
        n_rows = 3 if show_macd_row else 2
        r_heights = [0.5, 0.2, 0.3] if show_macd_row else [0.7, 0.3]
        
        fig = make_subplots(rows=n_rows, cols=1, shared_xaxes=True, vertical_spacing=0.04, row_heights=r_heights)

        # ROW 1: CANDLES, VWAP, SMA
        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['VWAP'], line=dict(color='cyan', width=2), name='VWAP'), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['SMA'], line=dict(color='orange', width=1.5), name='SMA 20'), row=1, col=1)

        # ROW 2: VOLUME
        vol_colors = ['#ff4b4b' if r['Open'] > r['Close'] else '#00ff00' for _, r in df.iterrows()]
        fig.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color=vol_colors, name="Volume"), row=2, col=1)

        # ROW 3: MACD (ONLY IF TOGGLED)
        if show_macd_row:
            fig.add_trace(go.Scatter(x=df.index, y=df['MACD'], line=dict(color='#00E676', width=1), name='MACD'), row=3, col=1)
            fig.add_trace(go.Scatter(x=df.index, y=df['Signal'], line=dict(color='#FF5252', width=1), name='Signal'), row=3, col=1)
            h_colors = ['#00E676' if x > 0 else '#FF5252' for x in df['Hist']]
            fig.add_trace(go.Bar(x=df.index, y=df['Hist'], marker_color=h_colors, name='Hist'), row=3, col=1)

        # SIGNAL MARKERS & LINES
        if st.session_state.trade_lock:
            t = st.session_state.trade_lock
            color = "#ff4b4b" if t['type'] == "SELL" else "#00ff00"
            symbol = "triangle-down" if t['type'] == "SELL" else "triangle-up"
            
            fig.add_hline(y=t['en'], line_dash="dot", line_color="white", annotation_text="ENTRY", row=1, col=1)
            fig.add_hline(y=t['sl'], line_dash="dash", line_color="red", row=1, col=1)
            fig.add_hline(y=t['tp'], line_dash="dash", line_color="lime", row=1, col=1)
            
            fig.add_trace(go.Scatter(x=[t['time']], y=[t['en']], mode="markers", 
                         marker=dict(symbol=symbol, size=18, color=color, line=dict(width=1, color="white"))), row=1, col=1)
            
            st.error(f"LOCKED {t['type']} | Entry: {t['en']:.2f} | SL: {t['sl']:.2f} | TP: {t['tp']:.2f}")
        else:
            st.info("🔍 SCANNING: Confluence Gates Active.")

        fig.update_layout(template="plotly_dark", height=800, xaxis_rangeslider_visible=False, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Syncing Data... {e}")
