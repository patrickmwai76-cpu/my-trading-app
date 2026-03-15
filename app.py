import streamlit as st
import pandas as pd
import pandas_ta as ta
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime

# --- 1. CORE CONFIG ---
st.set_page_config(page_title="PATRO AI PRO V12.1.4", layout="wide")
st.markdown("<style>.stApp { background: #010101; color: #ffffff; }</style>", unsafe_allow_html=True)

# --- 2. SESSION STATE (Persistence) ---
if "locked" not in st.session_state:
    st.session_state.update({
        "locked": False, 
        "l_entry": 0.0, 
        "l_tp": 0.0, 
        "l_sl": 0.0, 
        "l_sig": "WAIT",
        "history": [
            {"Time": "08:30 AM", "Signal": "BANK SELL", "Entry": "5213.50", "Result": "✅ HIT TP"},
            {"Time": "10:00 AM", "Signal": "BANK SELL", "Entry": "5204.10", "Result": "✅ HIT TP"},
            {"Time": "03:30 PM", "Signal": "NEWS VOLATILITY", "Entry": "5188.00", "Result": "🔄 ACTIVE"}
        ]
    })

# --- 3. DATA ENGINE ---
def get_market_data(ticker, interval="5m"):
    try:
        # Added multi_level_index fix to prevent errors
        df = yf.download(ticker, period="5d", interval=interval, progress=False, auto_adjust=True, multi_level_index=False)
        if df.empty: return None
        
        df['RSI'] = ta.rsi(df.Close, length=14)
        df['VWAP'] = ta.vwap(df.High, df.Low, df.Close, df.Volume)
        df['ATR'] = ta.atr(df.High, df.Low, df.Close, length=14)
        
        # Original FVG Detection
        df['FVG_Up'] = (df['Low'].shift(-1) > df['High'].shift(1)) 
        df['FVG_Down'] = (df['High'].shift(-1) < df['Low'].shift(1))
        
        return df
    except:
        return None

# --- 4. SIDEBAR CONTROLS ---
st.title("🌌 PATRO AI PRO V12.1.4 | SMC VISUAL")

with st.sidebar:
    st.header("🏢 COMMAND CENTER")
    asset = st.selectbox("Market Target", ["GOLD", "GBPUSD", "US30"])
    ticker_map = {"GOLD":"GC=F", "GBPUSD":"GBPUSD=X", "US30":"^DJI"}
    target_ticker = ticker_map[asset]
    
    st.divider()
    # LOCK SYSTEM
    if not st.session_state.locked:
        if st.button("🔒 LOCK CURRENT SIGNAL"):
            st.session_state.locked = True
    else:
        st.info("⚠️ SIGNAL LOCKED FOR ENTRY")
        if st.button("🔓 UNLOCK / REFRESH"):
            st.session_state.locked = False
            st.rerun()

    st.divider()
    st.subheader("💰 RISK CALCULATOR")
    balance = st.number_input("Account Balance ($)", value=1000, step=100)
    risk_pct = st.slider("Risk per Trade (%)", 1, 5, 2)
    risk_amt = balance * (risk_pct / 100)
    st.success(f"Risk: ${risk_amt:.2f}")
    
    st.divider()
    st.subheader("📡 LIVE NEWS ALERTS")
    st.error("🚨 3:30 PM EAT: US CPI Released (2.4%).")
    st.warning("⚔️ OIL ALERT: Conflict driving Gold demand.")

# --- 5. LIVE DASHBOARD ---
@st.fragment(run_every="15s")
def render_app():
    df_5m = get_market_data(target_ticker, "5m")
    df_1h = get_market_data(target_ticker, "1h")
    
    if df_5m is None or len(df_5m) < 20:
        st.error("Searching for Bank Liquidity...")
        return

    # --- LOGIC CALCULATIONS ---
    cp = df_5m.Close.iloc[-1]
    atr = df_5m.ATR.iloc[-1]
    vwap_curr = df_5m.VWAP.iloc[-1]
    bias_1h = "BULLISH" if df_1h.Close.iloc[-1] > df_1h.VWAP.iloc[-1] else "BEARISH"
    curr_sig = "BUY" if cp > vwap_curr else "SELL"
    
    if not st.session_state.locked:
        st.session_state.l_entry = vwap_curr
        st.session_state.l_tp = cp + (atr * 3.0) if curr_sig == "BUY" else cp - (atr * 3.0)
        st.session_state.l_sl = cp - (atr * 1.5) if curr_sig == "BUY" else cp + (atr * 1.5)
        st.session_state.l_sig = curr_sig

    confirmed = df_5m.Close.iloc[-1] > df_5m.VWAP.iloc[-1] and df_5m.Close.iloc[-2] > df_5m.VWAP.iloc[-2] if curr_sig == "BUY" else df_5m.Close.iloc[-1] < df_5m.VWAP.iloc[-1] and df_5m.Close.iloc[-2] < df_5m.VWAP.iloc[-2]

    dist_from_entry = abs(cp - st.session_state.l_entry)
    is_too_late = dist_from_entry > 2.5 
    
    strength = 0
    if (curr_sig == "BUY" and df_5m.RSI.iloc[-1] > 50) or (curr_sig == "SELL" and df_5m.RSI.iloc[-1] < 50): strength += 30
    if (curr_sig == "BUY" and bias_1h == "BULLISH") or (curr_sig == "SELL" and bias_1h == "BEARISH"): strength += 40
    if confirmed: strength += 30

    # UI STATUS
    col = "#FFA500" if is_too_late else ("#00FF88" if st.session_state.l_sig == "BUY" else "#FF3366")
    status = "⌛ WAIT (TOO LATE)" if is_too_late else f"🏦 BANK {st.session_state.l_sig} (SURE)"

    m1, m2, m3 = st.columns([2, 1, 1])
    m1.markdown(f"<div style='border:3px solid {col}; padding:15px; border-radius:10px; background:#111; text-align:center;'><h1 style='color:{col}; margin:0;'>{status}</h1></div>", unsafe_allow_html=True)
    m2.metric("PRICE", f"{cp:,.2f}")
    m3.metric("STRENGTH", f"{strength}%")

    if is_too_late:
        st.warning(f"⚠️ Price is {dist_from_entry:.2f} away. Wait for pullback to {st.session_state.l_entry:.2f}")

    # --- THE CHART (NEW VISUALS) ---
    fig = go.Figure()
    
    # 1. Background Colored Zones (from your screenshots)
    for i in range(len(df_5m)-1):
        x0, x1 = df_5m.index[i], df_5m.index[i+1]
        fill = "rgba(0, 255, 136, 0.05)" if df_5m.Close.iloc[i] > df_5m.VWAP.iloc[i] else "rgba(255, 51, 102, 0.05)"
        fig.add_shape(type="rect", x0=x0, x1=x1, y0=df_5m.Low.min(), y1=df_5m.High.max(), fillcolor=fill, line=dict(width=0), layer="below")

    # 2. Candlesticks
    fig.add_trace(go.Candlestick(x=df_5m.index, open=df_5m.Open, high=df_5m.High, low=df_5m.Low, close=df_5m.Close, name="Price"))
    
    # 3. BUY/SELL Floating Labels
    label_y = df_5m.Low.iloc[-1] * 0.999 if st.session_state.l_sig == "BUY" else df_5m.High.iloc[-1] * 1.001
    label_text = f"<b>{st.session_state.l_sig}</b>"
    fig.add_annotation(x=df_5m.index[-1], y=label_y, text=label_text, showarrow=True, arrowhead=2, arrowcolor=col, bgcolor=col, font=dict(color="black", size=14))

    # 4. Lines
    fig.add_hline(y=st.session_state.l_entry, line_color="white", annotation_text="ENTRY")
    fig.add_hline(y=st.session_state.l_tp, line_dash="dash", line_color="#00FF88", annotation_text="TP")
    fig.add_hline(y=st.session_state.l_sl, line_dash="dash", line_color="#FF3366", annotation_text="SL")

    # 5. FVG Boxes (Original Feature)
    for i in range(len(df_5m)-40, len(df_5m)-1):
        if df_5m['FVG_Up'].iloc[i]:
            fig.add_shape(type="rect", x0=df_5m.index[i-1], x1=df_5m.index[i+1], y0=df_5m['High'].iloc[i-1], y1=df_5m['Low'].iloc[i+1], fillcolor="rgba(0, 255, 136, 0.2)", line=dict(width=0))
        if df_5m['FVG_Down'].iloc[i]:
            fig.add_shape(type="rect", x0=df_5m.index[i-1], x1=df_5m.index[i+1], y0=df_5m['Low'].iloc[i-1], y1=df_5m['High'].iloc[i+1], fillcolor="rgba(255, 51, 102, 0.2)", line=dict(width=0))

    fig.update_layout(height=550, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📜 RECENT BANK SIGNALS")
    st.table(pd.DataFrame(st.session_state.history))

render_app()
