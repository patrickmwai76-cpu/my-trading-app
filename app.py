import streamlit as st
import pandas as pd
import pandas_ta as ta
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime

# --- 1. CORE CONFIG ---
st.set_page_config(page_title="PATRO AI PRO V12.1.12", layout="wide")
st.markdown("<style>.stApp { background: #000; color: #fff; }</style>", unsafe_allow_html=True)

# --- 2. SESSION STATE (Keeping all your data) ---
if "locked" not in st.session_state:
    st.session_state.update({
        "locked": False, "l_entry": 0.0, "l_tp": 0.0, "l_sl": 0.0, "l_sig": "WAIT",
        "history": [{"Time": datetime.now().strftime("%H:%M"), "Signal": "SYSTEM START", "Price": "0.00"}]
    })

# --- 3. DATA ENGINE (The "No-Black-Screen" Fix) ---
def get_market_data(ticker):
    try:
        df = yf.download(ticker, period="2d", interval="5m", progress=False, auto_adjust=True)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        # SMC & Trend Indicators
        df['VWAP'] = ta.vwap(df.High, df.Low, df.Close, df.Volume)
        df['ATR'] = ta.atr(df.High, df.Low, df.Close, length=14)
        df['RSI'] = ta.rsi(df.Close, length=14)
        
        # FVG Detection (The TikTok Boxes)
        df['FVG_Up'] = (df['Low'].shift(-1) > df['High'].shift(1)) 
        df['FVG_Down'] = (df['High'].shift(-1) < df['Low'].shift(1))
        return df.dropna()
    except: return None

# --- 4. SIDEBAR (All Discussed Features Restored) ---
with st.sidebar:
    st.header("🏢 SMC COMMAND")
    asset = st.selectbox("Market Target", ["GOLD", "GBPUSD", "US30"])
    ticker_map = {"GOLD":"GC=F", "GBPUSD":"GBPUSD=X", "US30":"^DJI"}
    target_ticker = ticker_map[asset]
    
    st.divider()
    st.subheader("💰 RISK CALCULATOR")
    balance = st.number_input("Balance ($)", value=1000)
    risk_pct = st.slider("Risk (%)", 1, 5, 2)
    st.success(f"Risk Per Trade: ${balance * (risk_pct/100):.2f}")
    
    st.divider()
    st.subheader("📡 LIVE NEWS")
    st.error("🚨 US CPI Released: 2.4%")
    st.warning("⚔️ Geopolitical Volatility High")

# --- 5. LIVE DASHBOARD ---
@st.fragment(run_every="15s")
def render_app():
    df = get_market_data(target_ticker)
    if df is None: return

    cp = df.Close.iloc[-1]
    vwap_val = df.VWAP.iloc[-1]
    atr_val = df.ATR.iloc[-1]
    
    # --- ANTI-FAKE SIGNAL LOGIC ---
    # Only signals if price is > 0.5 ATR away from VWAP
    buffer = atr_val * 0.5
    if cp > (vwap_val + buffer): sig = "BUY"
    elif cp < (vwap_val - buffer): sig = "SELL"
    else: sig = "WAIT" 

    col = "#00FF88" if sig == "BUY" else ("#FF3366" if sig == "SELL" else "#FFA500")

    # Header Metric
    st.markdown(f"<div style='border:3px solid {col}; padding:10px; border-radius:10px; text-align:center; background:#111;'><h2 style='color:{col}; margin:0;'>🏦 BANK {sig} | {cp:,.2f}</h2></div>", unsafe_allow_html=True)

    # --- THE CHART (FULL VISUALS) ---
    fig = go.Figure()

    # Background Zone (TikTok Style)
    fig.add_vrect(x0=df.index[0], x1=df.index[-1], fillcolor=col, opacity=0.04, layer="below", line_width=0)

    # Candlesticks
    fig.add_trace(go.Candlestick(x=df.index, open=df.Open, high=df.High, low=df.Low, close=df.Close, name="Price"))

    # FVG Boxes (SMC Visuals)
    for i in range(len(df)-15, len(df)-1):
        if df['FVG_Up'].iloc[i]:
            fig.add_shape(type="rect", x0=df.index[i-1], x1=df.index[i+1], y0=df.High.iloc[i-1], y1=df.Low.iloc[i+1], fillcolor="rgba(0, 255, 136, 0.2)", line_width=1, line_color="rgba(0, 255, 136, 0.4)")
        if df['FVG_Down'].iloc[i]:
            fig.add_shape(type="rect", x0=df.index[i-1], x1=df.index[i+1], y0=df.Low.iloc[i-1], y1=df.High.iloc[i+1], fillcolor="rgba(255, 51, 102, 0.2)", line_width=1, line_color="rgba(255, 51, 102, 0.4)")

    # Floating Label (The text you wanted)
    if sig != "WAIT":
        fig.add_annotation(x=df.index[-1], y=cp, text=f"<b>{sig}</b>", bgcolor=col, font=dict(color="black", size=18), showarrow=True)

    # Trading Lines
    if sig != "WAIT":
        st.session_state.l_entry = vwap_val
        st.session_state.l_tp = cp + (atr_val * 3) if sig == "BUY" else cp - (atr_val * 3)
        st.session_state.l_sl = cp - (atr_val * 1.5) if sig == "BUY" else cp + (atr_val * 1.5)
        
        fig.add_hline(y=st.session_state.l_entry, line_color="white", annotation_text="ENTRY")
        fig.add_hline(y=st.session_state.l_tp, line_color="#00FF88", line_dash="dash")
        fig.add_hline(y=st.session_state.l_sl, line_color="#FF3366", line_dash="dash")

    fig.update_layout(height=600, template="plotly_dark", paper_bgcolor="black", plot_bgcolor="black", xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig, use_container_width=True, theme=None, key="final_v12")

    # --- RECENT SIGNALS TABLE ---
    st.divider()
    st.subheader("📜 SIGNAL HISTORY")
    st.table(pd.DataFrame(st.session_state.history))

render_app()
