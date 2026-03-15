import streamlit as st
import pandas as pd
import pandas_ta as ta
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime

# --- 1. CORE CONFIG ---
st.set_page_config(page_title="PATRO AI PRO V12.1.5", layout="wide")
st.markdown("<style>.stApp { background: #010101; color: #ffffff; }</style>", unsafe_allow_html=True)

# --- 2. SESSION STATE ---
if "locked" not in st.session_state:
    st.session_state.update({
        "locked": False, "l_entry": 0.0, "l_tp": 0.0, "l_sl": 0.0, "l_sig": "WAIT",
        "history": [{"Time": "03:30 PM", "Signal": "NEWS VOL", "Entry": "5188.00", "Result": "🔄 ACTIVE"}]
    })

# --- 3. DATA ENGINE ---
def get_market_data(ticker, interval="5m"):
    try:
        df = yf.download(ticker, period="2d", interval=interval, progress=False, auto_adjust=True, multi_level_index=False)
        if df.empty: return None
        df['RSI'] = ta.rsi(df.Close, length=14)
        df['VWAP'] = ta.vwap(df.High, df.Low, df.Close, df.Volume)
        df['ATR'] = ta.atr(df.High, df.Low, df.Close, length=14)
        df['FVG_Up'] = (df['Low'].shift(-1) > df['High'].shift(1)) 
        df['FVG_Down'] = (df['High'].shift(-1) < df['Low'].shift(1))
        return df
    except: return None

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("🌌 COMMAND CENTER")
    asset = st.selectbox("Market Target", ["GOLD", "GBPUSD", "US30"])
    ticker_map = {"GOLD":"GC=F", "GBPUSD":"GBPUSD=X", "US30":"^DJI"}
    target_ticker = ticker_map[asset]
    
    if not st.session_state.locked:
        if st.button("🔒 LOCK SIGNAL"): st.session_state.locked = True
    else:
        st.info("⚠️ SIGNAL LOCKED")
        if st.button("🔓 UNLOCK"): 
            st.session_state.locked = False
            st.rerun()

# --- 5. LIVE DASHBOARD ---
@st.fragment(run_every="15s")
def render_app():
    df_5m = get_market_data(target_ticker, "5m")
    df_1h = get_market_data(target_ticker, "1h")
    if df_5m is None: return

    cp, vwap_curr = df_5m.Close.iloc[-1], df_5m.VWAP.iloc[-1]
    curr_sig = "BUY" if cp > vwap_curr else "SELL"
    
    if not st.session_state.locked:
        atr = df_5m.ATR.iloc[-1]
        st.session_state.l_entry, st.session_state.l_sig = vwap_curr, curr_sig
        st.session_state.l_tp = cp + (atr * 3) if curr_sig == "BUY" else cp - (atr * 3)
        st.session_state.l_sl = cp - (atr * 1.5) if curr_sig == "BUY" else cp + (atr * 1.5)

    dist = abs(cp - st.session_state.l_entry)
    is_too_late = dist > 2.5
    col = "#FFA500" if is_too_late else ("#00FF88" if st.session_state.l_sig == "BUY" else "#FF3366")
    
    m1, m2 = st.columns([2, 1])
    m1.markdown(f"<div style='border:2px solid {col}; padding:10px; border-radius:10px; text-align:center;'><h2 style='color:{col};'>{'⌛ WAIT' if is_too_late else '🏦 BANK ' + st.session_state.l_sig}</h2></div>", unsafe_allow_html=True)
    m2.metric("PRICE", f"{cp:,.2f}")

    # --- THE CHART (FIXED) ---
    fig = go.Figure()
    
    # Background boxes
    for i in range(len(df_5m)-1):
        x0, x1 = df_5m.index[i], df_5m.index[i+1]
        fill = "rgba(0, 255, 136, 0.05)" if df_5m.Close.iloc[i] > df_5m.VWAP.iloc[i] else "rgba(255, 51, 102, 0.05)"
        fig.add_shape(type="rect", x0=x0, x1=x1, y0=df_5m.Low.min(), y1=df_5m.High.max(), fillcolor=fill, line_width=0, layer="below")

    # Fixed Candlesticks (Using df.index)
    fig.add_trace(go.Candlestick(x=df_5m.index, open=df_5m.Open, high=df_5m.High, low=df_5m.Low, close=df_5m.Close, name="Market"))
    
    # Floating Label (BUY/SELL)
    label_y = df_5m.Low.iloc[-1] if st.session_state.l_sig == "BUY" else df_5m.High.iloc[-1]
    fig.add_annotation(x=df_5m.index[-1], y=label_y, text=f"<b>{st.session_state.l_sig}</b>", bgcolor=col, font=dict(color="black", size=16), showarrow=True)

    # Entry/TP/SL Lines
    fig.add_hline(y=st.session_state.l_entry, line_color="white", annotation_text="ENTRY")
    fig.add_hline(y=st.session_state.l_tp, line_color="#00FF88", line_dash="dash")
    fig.add_hline(y=st.session_state.l_sl, line_color="#FF3366", line_dash="dash")

    # FORCE TEMPLATE TO PREVENT BLACK SCREEN
    fig.update_layout(height=600, template="plotly_dark", paper_bgcolor="#010101", plot_bgcolor="#010101", xaxis_rangeslider_visible=False)
    
    # Use a unique KEY to prevent rendering errors
    st.plotly_chart(fig, use_container_width=True, key="main_chart_gold")

render_app()
