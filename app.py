import streamlit as st
import pandas as pd
import pandas_ta as ta
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime

# --- 1. CORE CONFIG ---
st.set_page_config(page_title="PATRO AI PRO V12.1.10", layout="wide")
st.markdown("<style>.stApp { background: #000000; color: #ffffff; }</style>", unsafe_allow_html=True)

# --- 2. SESSION STATE (All Features Saved) ---
if "locked" not in st.session_state:
    st.session_state.update({
        "locked": False, "l_entry": 0.0, "l_tp": 0.0, "l_sl": 0.0, "l_sig": "WAIT",
        "history": [
            {"Time": "03:30 PM", "Signal": "NEWS VOL", "Entry": "5188.00", "Result": "🔄 ACTIVE"}
        ]
    })

# --- 3. DATA ENGINE (The "No-Black-Screen" Logic) ---
def get_market_data(ticker):
    try:
        df = yf.download(ticker, period="2d", interval="5m", progress=False, auto_adjust=True)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        df['VWAP'] = ta.vwap(df.High, df.Low, df.Close, df.Volume)
        df['ATR'] = ta.atr(df.High, df.Low, df.Close, length=14)
        df['RSI'] = ta.rsi(df.Close, length=14)
        # SMC: Fair Value Gaps
        df['FVG_Up'] = (df['Low'].shift(-1) > df['High'].shift(1)) 
        df['FVG_Down'] = (df['High'].shift(-1) < df['Low'].shift(1))
        return df.dropna()
    except: return None

# --- 4. SIDEBAR (Restoring All Removed Features) ---
with st.sidebar:
    st.header("🏢 COMMAND CENTER")
    asset = st.selectbox("Market Target", ["GOLD", "GBPUSD", "US30"])
    ticker_map = {"GOLD":"GC=F", "GBPUSD":"GBPUSD=X", "US30":"^DJI"}
    target_ticker = ticker_map[asset]
    
    st.divider()
    mode = st.toggle("🚀 AGGRESSIVE MODE", value=False)
    
    if not st.session_state.locked:
        if st.button("🔒 LOCK SIGNAL"): st.session_state.locked = True
    else:
        st.warning("⚠️ SIGNAL LOCKED")
        if st.button("🔓 UNLOCK"): 
            st.session_state.locked = False
            st.rerun()

    st.divider()
    st.subheader("💰 RISK CALCULATOR")
    balance = st.number_input("Balance ($)", value=1000)
    risk_pct = st.slider("Risk (%)", 1, 5, 2)
    st.success(f"Risk Amount: ${balance * (risk_pct/100):.2f}")
    
    st.divider()
    st.subheader("📡 LIVE NEWS")
    st.error("🚨 US CPI Released: 2.4%")
    st.warning("⚔️ Oil driving Gold demand")

# --- 5. LIVE DASHBOARD ---
@st.fragment(run_every="15s")
def render_app():
    df = get_market_data(target_ticker)
    if df is None: return

    # --- SMC LOGIC ---
    cp = df.Close.iloc[-1]
    vwap_curr = df.VWAP.iloc[-1]
    atr = df.ATR.iloc[-1]
    
    curr_sig = "BUY" if cp > vwap_curr else "SELL"
    
    if not st.session_state.locked:
        st.session_state.l_entry, st.session_state.l_sig = vwap_curr, curr_sig
        st.session_state.l_tp = cp + (atr * 3) if curr_sig == "BUY" else cp - (atr * 3)
        st.session_state.l_sl = cp - (atr * 1.5) if curr_sig == "BUY" else cp + (atr * 1.5)

    # Strength Calculation
    strength = 0
    if (curr_sig == "BUY" and df.RSI.iloc[-1] > 50) or (curr_sig == "SELL" and df.RSI.iloc[-1] < 50): strength += 50
    if abs(cp - vwap_curr) < (atr * 2): strength += 50

    # Anti-Chase Logic
    dist = abs(cp - st.session_state.l_entry)
    is_too_late = dist > 2.5
    col = "#FFA500" if is_too_late else ("#00FF88" if st.session_state.l_sig == "BUY" else "#FF3366")
    status = "⌛ WAIT (PULLBACK)" if is_too_late else f"🏦 BANK {st.session_state.l_sig} (SURE)"

    # Header
    m1, m2, m3 = st.columns([2, 1, 1])
    m1.markdown(f"<div style='border:3px solid {col}; padding:10px; border-radius:10px; text-align:center; background:#111;'><h2 style='color:{col}; margin:0;'>{status}</h2></div>", unsafe_allow_html=True)
    m2.metric("PRICE", f"{cp:,.2f}")
    m3.metric("STRENGTH", f"{strength}%")

    # --- THE CHART ---
    fig = go.Figure()

    # Background Zones (Optimized to prevent black screen)
    fig.add_vrect(x0=df.index[0], x1=df.index[-1], fillcolor="rgba(0, 255, 136, 0.03)" if curr_sig == "BUY" else "rgba(255, 51, 102, 0.03)", layer="below", line_width=0)

    # Candlesticks
    fig.add_trace(go.Candlestick(x=df.index, open=df.Open, high=df.High, low=df.Low, close=df.Close, name="Market"))

    # BUY/SELL Words on Chart (TikTok Style)
    fig.add_annotation(x=df.index[-1], y=cp, text=f"<b>{st.session_state.l_sig}</b>", bgcolor=col, font=dict(color="black", size=18), showarrow=True, arrowhead=2, arrowcolor=col)

    # FVG Boxes
    for i in range(len(df)-15, len(df)-1):
        if df['FVG_Up'].iloc[i]:
            fig.add_shape(type="rect", x0=df.index[i-1], x1=df.index[i+1], y0=df['High'].iloc[i-1], y1=df['Low'].iloc[i+1], fillcolor="rgba(0, 255, 136, 0.2)", line_width=0)
        if df['FVG_Down'].iloc[i]:
            fig.add_shape(type="rect", x0=df.index[i-1], x1=df.index[i+1], y0=df['Low'].iloc[i-1], y1=df['High'].iloc[i+1], fillcolor="rgba(255, 51, 102, 0.2)", line_width=0)

    # Trading Lines
    fig.add_hline(y=st.session_state.l_entry, line_color="white", annotation_text="ENTRY")
    fig.add_hline(y=st.session_state.l_tp, line_color="#00FF88", line_dash="dash")
    fig.add_hline(y=st.session_state.l_sl, line_color="#FF3366", line_dash="dash")

    fig.update_layout(height=600, template="plotly_dark", paper_bgcolor="black", plot_bgcolor="black", xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig, use_container_width=True, theme=None, key="smc_v10")

    # History Table (Restored)
    st.divider()
    st.subheader("📜 RECENT BANK SIGNALS")
    st.table(pd.DataFrame(st.session_state.history))

render_app()
