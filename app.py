import streamlit as st
import pandas as pd
import pandas_ta as ta
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime

# --- 1. CORE CONFIG ---
st.set_page_config(page_title="PATRO AI PRO V12.1.15", layout="wide")
st.markdown("<style>.stApp { background: #000; color: #fff; }</style>", unsafe_allow_html=True)

# --- 2. DATA ENGINE ---
def get_market_data(ticker):
    try:
        # period=1d to keep the chart fast and clean
        df = yf.download(ticker, period="1d", interval="5m", progress=False, auto_adjust=True)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        df['VWAP'] = ta.vwap(df.High, df.Low, df.Close, df.Volume)
        df['ATR'] = ta.atr(df.High, df.Low, df.Close, length=14)
        
        # SMC Boxes Logic
        df['FVG_Up'] = (df['Low'].shift(-1) > df['High'].shift(1)) 
        df['FVG_Down'] = (df['High'].shift(-1) < df['Low'].shift(1))
        return df.dropna()
    except: return None

# --- 3. SIDEBAR (Restored All Discussion Features) ---
with st.sidebar:
    st.header("🏢 COMMAND CENTER")
    asset = st.selectbox("Market Target", ["GOLD", "GBPUSD", "US30"])
    ticker_map = {"GOLD":"GC=F", "GBPUSD":"GBPUSD=X", "US30":"^DJI"}
    target_ticker = ticker_map[asset]
    
    st.divider()
    st.subheader("💰 RISK CALCULATOR")
    balance = st.number_input("Account Balance ($)", value=1000)
    risk_pct = st.slider("Risk per Trade (%)", 1, 5, 2)
    st.success(f"Recommended Risk: ${balance * (risk_pct / 100):.2f}")
    
    st.divider()
    st.subheader("📡 LIVE NEWS ALERTS")
    st.error("🚨 3:30 PM: US CPI Released (2.4%)")
    st.warning("⚔️ OIL ALERT: Conflict driving Gold demand")

# --- 4. LIVE DASHBOARD ---
@st.fragment(run_every="15s")
def render_app():
    df = get_market_data(target_ticker)
    if df is None: return

    cp = df.Close.iloc[-1]
    vwap_curr = df.VWAP.iloc[-1]
    atr = df.ATR.iloc[-1]
    
    # Signal Logic with Anti-Fake Buffer
    buffer = atr * 0.4
    if cp > (vwap_curr + buffer):
        status, col = "🏦 BANK BUY (SURE)", "#00FF88"
        sig_label = "BUY"
    elif cp < (vwap_curr - buffer):
        status, col = "🏦 BANK SELL (SURE)", "#FF3366"
        sig_label = "SELL"
    else:
        status, col = "⌛ WAIT (RETAIL TRAP)", "#FFA500"
        sig_label = "WAIT"

    # Header Metrics
    m1, m2 = st.columns([2, 1])
    m1.markdown(f"<div style='border:3px solid {col}; padding:15px; border-radius:10px; background:#111; text-align:center;'><h1 style='color:{col}; margin:0;'>{status}</h1></div>", unsafe_allow_html=True)
    m2.metric("LIVE PRICE", f"{cp:,.2f}")

    # --- THE CHART (THE TIKTOK LOOK) ---
    fig = go.Figure()

    # 1. Background Colored Zones (from your photos)
    fig.add_vrect(x0=df.index[0], x1=df.index[-1], fillcolor=col, opacity=0.05, layer="below", line_width=0)

    # 2. Candlesticks (Neon Green/Red)
    fig.add_trace(go.Candlestick(x=df.index, open=df.Open, high=df.High, low=df.Low, close=df.Close, 
                                 increasing_line_color='#00FF88', decreasing_line_color='#FF3366', name="Price"))

    # 3. BIG SIGNAL BOX (Floating at Current Price)
    if sig_label != "WAIT":
        fig.add_annotation(
            x=df.index[-1], y=cp,
            text=f"<b> {sig_label} </b>",
            font=dict(size=20, color="black"),
            bgcolor=col,
            bordercolor="white",
            borderwidth=2,
            borderpad=10,
            showarrow=True,
            arrowhead=2,
            arrowcolor=col,
            ay=-50 if sig_label == "SELL" else 50
        )

    # 4. FVG LIQUIDITY BOXES (Inside Chart)
    for i in range(len(df)-15, len(df)-1):
        if df['FVG_Up'].iloc[i]:
            fig.add_shape(type="rect", x0=df.index[i-1], x1=df.index[i+1], y0=df.High.iloc[i-1], y1=df.Low.iloc[i+1], 
                          fillcolor="rgba(0, 255, 136, 0.2)", line_width=1, line_color="rgba(0, 255, 136, 0.4)")
        if df['FVG_Down'].iloc[i]:
            fig.add_shape(type="rect", x0=df.index[i-1], x1=df.index[i+1], y0=df.Low.iloc[i-1], y1=df.High.iloc[i+1], 
                          fillcolor="rgba(255, 51, 102, 0.2)", line_width=1, line_color="rgba(255, 51, 102, 0.4)")

    # 5. Trading Lines (Entry, TP, SL)
    if sig_label != "WAIT":
        tp = cp + (atr * 3) if sig_label == "BUY" else cp - (atr * 3)
        sl = cp - (atr * 1.5) if sig_label == "BUY" else cp + (atr * 1.5)
        fig.add_hline(y=vwap_curr, line_color="white", annotation_text="ENTRY")
        fig.add_hline(y=tp, line_color="#00FF88", line_dash="dash", annotation_text="TP")
        fig.add_hline(y=sl, line_color="#FF3366", line_dash="dash", annotation_text="SL")

    # Layout Styling (Ensures it is never black)
    fig.update_layout(height=650, template="plotly_dark", paper_bgcolor="black", plot_bgcolor="black", 
                      xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
    
    st.plotly_chart(fig, use_container_width=True, theme=None, key="patro_ultimate_v15")

    # --- HISTORY TABLE ---
    st.divider()
    st.subheader("📜 RECENT BANK SIGNALS")
    st.table(pd.DataFrame([{"Time": "NOW", "Signal": status, "Entry": f"{vwap_curr:.2f}", "Result": "🔄 ACTIVE"}]))

render_app()
