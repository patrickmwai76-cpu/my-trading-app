import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from streamlit_autorefresh import st_autorefresh
from plotly.subplots import make_subplots

# 1. SETUP & SESSION
st.set_page_config(page_title="PATRO AI PRO V8.6", layout="wide")
if 'auth' not in st.session_state: st.session_state['auth'] = False
if 'trade_lock' not in st.session_state: st.session_state.trade_lock = None

# 2. SECURITY (UNTOUCHED)
if not st.session_state['auth']:
    st.title("🛡️ PATRO AI PRO | SECURE ACCESS")
    u, p = st.text_input("User"), st.text_input("Pass", type="password")
    if st.button("Unlock"):
        if u == "PATRO_ADMIN" and p == "patro666@":
            st.session_state['auth'] = True
            st.rerun()
    st.stop()

# 3. SIDEBAR: NEWS GUARD & CONTROLS
with st.sidebar:
    st.title("🎮 PATRO CONTROL")
    st.divider()
    
    # --- NEWS GUARD (MARCH 4, 2026) ---
    st.error("🚨 NEWS GUARD: HIGH IMPACT")
    st.caption("Active Sessions: March 4, 2026")
    st.markdown("""
    * **08:15 AM:** ADP Employment Change
    * **10:00 AM:** ISM Services PMI
    * **02:00 PM:** Fed Beige Book
    """)
    st.warning("⚠️ High Volatility Expected")
    st.divider()

    st.subheader("📋 INSTITUTIONAL SOP")
    sop_trend = st.checkbox("Trend Matrix Confluence", value=True)
    sop_vwap = st.checkbox("Price Action near VWAP", value=True)
    sop_vol = st.checkbox("Volume Confirmation", value=True)
    sop_macd_gate = st.checkbox("MACD Momentum Guard", value=True)
    
    st.divider()
    st.subheader("⚙️ SETTINGS")
    asset_choice = st.selectbox("Asset", ["XAUUSD (GOLD)", "US30 (DOW JONES)"])
    tf = st.sidebar.radio("Timeframe", ["1m", "5m", "15m"], index=0, horizontal=True)
    
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
        
        # MACD
        exp1 = df['Close'].ewm(span=12, adjust=False).mean()
        exp2 = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = exp1 - exp2
        df['Sig'] = df['MACD'].ewm(span=9, adjust=False).mean()
        df['Hist'] = df['MACD'] - df['Sig']
        
        # ADX (TREND POWER)
        plus_dm = df['High'].diff().clip(lower=0)
        minus_dm = (-df['Low'].diff()).clip(lower=0)
        tr = pd.concat([df['High']-df['Low'], abs(df['High']-df['Close'].shift(1)), abs(df['Low']-df['Close'].shift(1))], axis=1).max(axis=1)
        atr_adx = tr.rolling(14).mean()
        df['ADX'] = (abs((100 * (plus_dm.rolling(14).mean()/atr_adx)) - (100 * (minus_dm.rolling(14).mean()/atr_adx))) / 
                    ((100 * (plus_dm.rolling(14).mean()/atr_adx)) + (100 * (minus_dm.rolling(14).mean()/atr_adx))) * 100).rolling(14).mean()
        
        df['ATR'] = (df['High'] - df['Low']).rolling(14).mean()

        last = df.iloc[-1]
        prev = df.iloc[-2]
        atr_val = last['ATR'] if not pd.isna(last['ATR']) else 1.5

        # ADX TREND ARROW LOGIC
        arrow = "▲" if last['ADX'] > prev['ADX'] else "▼"
        arrow_color = "green" if arrow == "▲" else "red"

        with st.sidebar:
            st.divider()
            st.subheader(f"⚡ TREND POWER: {last['ADX']:.1f}%")
            st.markdown(f"**Momentum:** :{arrow_color}[{arrow} {'ACCELERATING' if arrow=='▲' else 'FADING'}]")
            st.progress(min(last['ADX']/100, 1.0))

        # 5. SIGNAL LOGIC
        if st.session_state.trade_lock is None and sop_trend and sop_vwap and sop_vol and sop_macd_gate:
            if last['Close'] < last['VWAP'] and last['Close'] < last['SMA'] and last['Hist'] < 0:
                st.session_state.trade_lock = {"type": "SELL", "en": last['Close'], "sl": last['Close'] + (atr_val*1.5), "tp": last['Close'] - (atr_val*3), "time": df.index[-1]}
                st.toast("🚨 SELL SIGNAL")
            elif last['Close'] > last['VWAP'] and last['Close'] > last['SMA'] and last['Hist'] > 0:
                st.session_state.trade_lock = {"type": "BUY", "en": last['Close'], "sl": last['Close'] - (atr_val*1.5), "tp": last['Close'] + (atr_val*3), "time": df.index[-1]}
                st.toast("💰 BUY SIGNAL")

        # 6. CHARTING (VOLUME PRESERVED ON MAIN ROW)
        st.header(f"📊 {asset_choice} Terminal")
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.7, 0.3],
                            specs=[[{"secondary_y": True}], [{"secondary_y": False}]])

        # PRICE & INDICATORS
        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"), row=1, col=1, secondary_y=True)
        fig.add_trace(go.Scatter(x=df.index, y=df['VWAP'], line=dict(color='cyan', width=2), name='VWAP'), row=1, col=1, secondary_y=True)
        fig.add_trace(go.Scatter(x=df.index, y=df['SMA'], line=dict(color='orange', width=1.5), name='SMA 20'), row=1, col=1, secondary_y=True)

        # VOLUME BARS (Exactly as before, on Row 1)
        v_colors = ['#00ff00' if df['Close'][i] >= df['Open'][i] else '#ff4b4b' for i in range(len(df))]
        fig.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color=v_colors, opacity=0.3, name="Volume"), row=1, col=1, secondary_y=False)

        # MACD ROW
        h_colors = ['#00ff00' if x > 0 else '#ff4b4b' for x in df['Hist']]
        fig.add_trace(go.Bar(x=df.index, y=df['Hist'], marker_color=h_colors, name="MACD"), row=2, col=1)

        fig.update_layout(template="plotly_dark", height=800, xaxis_rangeslider_visible=False, showlegend=False)
        fig.update_yaxes(showgrid=False, secondary_y=False, row=1, col=1) # Hide volume grid
        st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Syncing... {e}")
