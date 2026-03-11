import streamlit as st
import pandas as pd
import pandas_ta as ta
import yfinance as yf
import plotly.graph_objects as go

# --- 1. CORE CONFIG ---
st.set_page_config(page_title="PATRO AI PRO V12.1.0", layout="wide")
st.markdown("<style>.stApp { background: #010101; color: #ffffff; }</style>", unsafe_allow_html=True)

# --- 2. SESSION STATE (Signal Locking) ---
if "locked" not in st.session_state:
    st.session_state.update({"locked": False, "l_entry": 0.0, "l_tp": 0.0, "l_sl": 0.0, "l_sig": "WAIT"})

# --- 3. DATA ENGINE ---
def get_market_data(ticker, interval="5m"):
    try:
        df = yf.download(ticker, period="5d", interval=interval, progress=False, auto_adjust=True)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        df['RSI'] = ta.rsi(df.Close, length=14)
        df['VWAP'] = ta.vwap(df.High, df.Low, df.Close, df.Volume)
        df['ATR'] = ta.atr(df.High, df.Low, df.Close, length=14)
        df['FVG_Up'] = (df['Low'].shift(-1) > df['High'].shift(1)) 
        df['FVG_Down'] = (df['High'].shift(-1) < df['Low'].shift(1))
        return df
    except: return None

# --- 4. SIDEBAR (Command & Risk) ---
with st.sidebar:
    st.header("🏢 COMMAND CENTER")
    asset = st.selectbox("Market Target", ["GOLD", "GBPUSD", "US30"])
    ticker_map = {"GOLD":"GC=F", "GBPUSD":"GBPUSD=X", "US30":"^DJI"}
    
    st.divider()
    # LOCK SYSTEM
    if not st.session_state.locked:
        if st.button("🔒 LOCK CURRENT SIGNAL"):
            st.session_state.locked = True
    else:
        st.info("⚠️ SIGNAL IS LOCKED")
        if st.button("🔓 UNLOCK / REFRESH"):
            st.session_state.locked = False
            st.rerun()

    st.divider()
    st.subheader("💰 RISK CALCULATOR")
    balance = st.number_input("Account Balance ($)", value=1000, step=100)
    risk_pct = st.slider("Risk per Trade (%)", 1, 5, 2)
    
    # Calculate Lot Size (Estimates for Gold 0.01 = $1/10 pips)
    risk_dollars = balance * (risk_pct / 100)
    suggested_lot = max(0.01, round(risk_dollars / 50, 2)) # Simple estimate
    st.success(f"Risk: ${risk_dollars} | Lot Size: {suggested_lot}")

# --- 5. LIVE DASHBOARD ---
@st.fragment(run_every="15s")
def render_app():
    df = get_market_data(ticker_map[asset])
    if df is None: return
    
    cp = df.Close.iloc[-1]
    vwap_curr = df.VWAP.iloc[-1]
    curr_sig = "BUY" if cp > vwap_curr else "SELL"
    
    # Update values ONLY if not locked
    if not st.session_state.locked:
        atr = df.ATR.iloc[-1]
        st.session_state.l_entry = vwap_curr
        st.session_state.l_tp = cp + (atr * 3.5) if curr_sig == "BUY" else cp - (atr * 3.5)
        st.session_state.l_sl = cp - (atr * 1.5) if curr_sig == "BUY" else cp + (atr * 1.5)
        st.session_state.l_sig = curr_sig

    # UI Logic
    dist = abs(cp - st.session_state.l_entry)
    is_late = dist > 2.5
    col = "#FFA500" if is_late else ("#00FF88" if st.session_state.l_sig == "BUY" else "#FF3366")
    status = "⌛ TOO LATE (WAIT)" if is_late else f"🏦 BANK {st.session_state.l_sig}"

    # Header Metrics
    st.title(f"🌌 PATRO AI PRO V12.1.0")
    m1, m2, m3 = st.columns([2, 1, 1])
    m1.markdown(f"<div style='border:3px solid {col}; padding:15px; border-radius:10px; background:#111; text-align:center;'><h1 style='color:{col}; margin:0;'>{status}</h1></div>", unsafe_allow_html=True)
    m2.metric("PRICE", f"{cp:,.2f}")
    m3.metric("LOCKED", "YES" if st.session_state.locked else "NO")

    # Chart
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df.index, open=df.Open, high=df.High, low=df.Low, close=df.Close, name="Price"))
    fig.add_hline(y=st.session_state.l_entry, line_color="white", annotation_text=f"ENTRY: {st.session_state.l_entry:.2f}")
    fig.add_hline(y=st.session_state.l_tp, line_dash="dash", line_color="#00FF88", annotation_text=f"TP: {st.session_state.l_tp:.2f}")
    fig.add_hline(y=st.session_state.l_sl, line_dash="dash", line_color="#FF3366", annotation_text=f"SL: {st.session_state.l_sl:.2f}")
    
    # BOXES (FVG)
    for i in range(len(df)-20, len(df)-1):
        if df['FVG_Up'].iloc[i]:
            fig.add_shape(type="rect", x0=df.index[i-1], x1=df.index[i+1], y0=df['High'].iloc[i-1], y1=df['Low'].iloc[i+1], fillcolor="rgba(0, 255, 136, 0.2)", line=dict(width=0))
        if df['FVG_Down'].iloc[i]:
            fig.add_shape(type="rect", x0=df.index[i-1], x1=df.index[i+1], y0=df['Low'].iloc[i-1], y1=df['High'].iloc[i+1], fillcolor="rgba(255, 51, 102, 0.2)", line=dict(width=0))

    fig.update_layout(height=500, template="plotly_dark", xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

render_app()
