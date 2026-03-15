import streamlit as st
import pandas as pd
import pandas_ta as ta
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime

# --- 1. CORE CONFIG ---
st.set_page_config(page_title="PATRO AI PRO V12.1.13", layout="wide")
st.markdown("<style>.stApp { background: #000; color: #fff; }</style>", unsafe_allow_html=True)

# --- 2. SESSION STATE ---
if "locked" not in st.session_state:
    st.session_state.update({
        "locked": False, "l_entry": 0.0, "l_tp": 0.0, "l_sl": 0.0, "l_sig": "WAIT",
        "history": [{"Time": "03:30 PM", "Signal": "BANK SELL", "Entry": "5213.50", "Result": "✅ HIT TP"}]
    })

# --- 3. SMC DATA ENGINE ---
def get_market_data(ticker):
    try:
        df = yf.download(ticker, period="2d", interval="5m", progress=False, auto_adjust=True)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        # Indicators for SMC Logic
        df['VWAP'] = ta.vwap(df.High, df.Low, df.Close, df.Volume)
        df['ATR'] = ta.atr(df.High, df.Low, df.Close, length=14)
        
        # SMC: Market Structure (Fractal Highs/Lows)
        df['High_Sweep'] = (df['High'] > df['High'].shift(1)) & (df['High'] > df['High'].shift(-1))
        df['Low_Sweep'] = (df['Low'] < df['Low'].shift(1)) & (df['Low'] < df['Low'].shift(-1))
        
        # SMC: Fair Value Gaps (Order Blocks)
        df['FVG_Up'] = (df['Low'].shift(-1) > df['High'].shift(1)) 
        df['FVG_Down'] = (df['High'].shift(-1) < df['Low'].shift(1))
        return df.dropna()
    except: return None

# --- 4. SIDEBAR (Full Discussion Features) ---
with st.sidebar:
    st.header("🏢 SMC COMMAND")
    asset = st.selectbox("Market Target", ["GOLD", "GBPUSD", "US30"])
    ticker_map = {"GOLD":"GC=F", "GBPUSD":"GBPUSD=X", "US30":"^DJI"}
    target_ticker = ticker_map[asset]
    
    st.divider()
    st.subheader("💰 RISK CALCULATOR")
    bal = st.number_input("Balance", 1000)
    risk = st.slider("Risk %", 1, 5, 2)
    st.info(f"Lot Size Est: {round((bal * (risk/100)) / 40, 2)}")
    
    st.divider()
    st.subheader("📡 LIVE NEWS")
    st.error("🚨 US CPI: 2.4% (Neutral-Bullish Gold)")
    if st.button("🔓 UNLOCK SYSTEM"): st.session_state.locked = False

# --- 5. LIVE DASHBOARD ---
@st.fragment(run_every="15s")
def render_app():
    df = get_market_data(target_ticker)
    if df is None: return

    cp = df.Close.iloc[-1]
    vwap_val = df.VWAP.iloc[-1]
    atr = df.ATR.iloc[-1]
    
    # Logic: Only Signal if clear of the 'Retail Trap' (VWAP Buffer)
    buffer = atr * 0.4
    if cp > (vwap_val + buffer): sig = "BUY"
    elif cp < (vwap_val - buffer): sig = "SELL"
    else: sig = "WAIT"

    col = "#00FF88" if sig == "BUY" else ("#FF3366" if sig == "SELL" else "#FFA500")

    # Metrics Header
    m1, m2, m3 = st.columns([2,1,1])
    m1.markdown(f"<div style='border:2px solid {col}; padding:10px; border-radius:10px; background:#111; text-align:center;'><h2 style='color:{col}; margin:0;'>🏦 {sig} ZONE</h2></div>", unsafe_allow_html=True)
    m2.metric("PRICE", f"{cp:,.2f}")
    m3.metric("MODE", "SMC PRO")

    # --- THE CHART (FULL SMC VISUALS) ---
    fig = go.Figure()

    # 1. Background Logic Shading
    fig.add_vrect(x0=df.index[0], x1=df.index[-1], fillcolor=col, opacity=0.04, layer="below", line_width=0)

    # 2. Candlesticks (Premium Colors)
    fig.add_trace(go.Candlestick(x=df.index, open=df.Open, high=df.High, low=df.Low, close=df.Close, 
                                 increasing_line_color='#00FF88', decreasing_line_color='#FF3366', name="SMC Price"))

    # 3. Floating BUY/SELL Label (TikTok Icon Style)
    if sig != "WAIT":
        fig.add_annotation(x=df.index[-1], y=cp, text=f"<b>{sig}</b>", bgcolor=col, font=dict(color="black", size=18), 
                           showarrow=True, arrowhead=2, arrowcolor=col, ax=0, ay=-40 if sig=="SELL" else 40)

    # 4. Market Structure Labels (CHoCH / BOS)
    for i in range(len(df)-10, len(df)):
        if df['High_Sweep'].iloc[i]:
            fig.add_annotation(x=df.index[i], y=df.High.iloc[i], text="<b style='color:#FF3366'>CHoCH</b>", showarrow=False, yshift=15)
        if df['Low_Sweep'].iloc[i]:
            fig.add_annotation(x=df.index[i], y=df.Low.iloc[i], text="<b style='color:#00FF88'>BOS</b>", showarrow=False, yshift=-15)

    # 5. Order Blocks / FVG Boxes (The "TikTok Boxes")
    for i in range(len(df)-20, len(df)-1):
        if df['FVG_Up'].iloc[i]:
            fig.add_shape(type="rect", x0=df.index[i-1], x1=df.index[i+1], y0=df.High.iloc[i-1], y1=df.Low.iloc[i+1], 
                          fillcolor="rgba(0, 255, 136, 0.15)", line_width=1, line_color="rgba(0, 255, 136, 0.3)")
        if df['FVG_Down'].iloc[i]:
            fig.add_shape(type="rect", x0=df.index[i-1], x1=df.index[i+1], y0=df.Low.iloc[i-1], y1=df.High.iloc[i+1], 
                          fillcolor="rgba(255, 51, 102, 0.15)", line_width=1, line_color="rgba(255, 51, 102, 0.3)")

    # 6. Entry/TP/SL Lines
    if sig != "WAIT":
        entry = vwap_val
        tp = cp + (atr * 3) if sig == "BUY" else cp - (atr * 3)
        sl = cp - (atr * 1.5) if sig == "BUY" else cp + (atr * 1.5)
        fig.add_hline(y=entry, line_color="white", annotation_text="ENTRY")
        fig.add_hline(y=tp, line_color="#00FF88", line_dash="dash", annotation_text="TP")
        fig.add_hline(y=sl, line_color="#FF3366", line_dash="dash", annotation_text="SL")

    fig.update_layout(height=650, template="plotly_dark", paper_bgcolor="black", plot_bgcolor="black", 
                      xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
    
    st.plotly_chart(fig, use_container_width=True, theme=None, key="smc_pro_ultimate")

    # --- HISTORY & JOURNALS ---
    st.divider()
    st.subheader("📜 SIGNAL JOURNAL")
    st.table(pd.DataFrame(st.session_state.history))

render_app()
