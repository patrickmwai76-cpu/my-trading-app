import streamlit as st
import pandas as pd
import pandas_ta as ta
import yfinance as yf
import plotly.graph_objects as go

# --- 1. CORE CONFIG ---
st.set_page_config(page_title="PATRO AI PRO V12.1.11", layout="wide")
st.markdown("<style>.stApp { background: #000; color: #fff; }</style>", unsafe_allow_html=True)

# --- 2. DATA ENGINE (The "No-Black-Screen" Logic) ---
def get_market_data(ticker):
    try:
        df = yf.download(ticker, period="2d", interval="5m", progress=False, auto_adjust=True)
        if df.empty: return None
        # Flatten Multi-Index Columns
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        # SMC Indicators
        df['VWAP'] = ta.vwap(df.High, df.Low, df.Close, df.Volume)
        df['ATR'] = ta.atr(df.High, df.Low, df.Close, length=14)
        df['RSI'] = ta.rsi(df.Close, length=14)
        
        # FVG Detection (The Boxes)
        df['FVG_Up'] = (df['Low'].shift(-1) > df['High'].shift(1)) 
        df['FVG_Down'] = (df['High'].shift(-1) < df['Low'].shift(1))
        return df.dropna()
    except: return None

# --- 3. SIDEBAR ---
with st.sidebar:
    st.header("🏢 SMC COMMAND")
    asset = st.selectbox("Market Target", ["GOLD", "GBPUSD", "US30"])
    ticker_map = {"GOLD":"GC=F", "GBPUSD":"GBPUSD=X", "US30":"^DJI"}
    target_ticker = ticker_map[asset]
    st.divider()
    st.info("ANTI-FAKE: Active")
    st.info("BOXES: Rendered In-Chart")

# --- 4. LIVE DASHBOARD ---
@st.fragment(run_every="15s")
def render_app():
    df = get_market_data(target_ticker)
    if df is None: return

    cp = df.Close.iloc[-1]
    vwap_curr = df.VWAP.iloc[-1]
    atr = df.ATR.iloc[-1]
    
    # --- ANTI-FAKE LOGIC ---
    # Only flip signal if price is at least 0.5 * ATR away from VWAP
    # This stops the "flickering" fake sells.
    buffer = atr * 0.5
    if cp > (vwap_curr + buffer):
        sig = "BUY"
    elif cp < (vwap_curr - buffer):
        sig = "SELL"
    else:
        sig = "WAIT" # Neutral zone to prevent fake signals

    col = "#00FF88" if sig == "BUY" else ("#FF3366" if sig == "SELL" else "#FFA500")

    # Header
    st.markdown(f"<div style='border:3px solid {col}; padding:10px; border-radius:10px; text-align:center; background:#111;'><h1 style='color:{col}; margin:0;'>🏦 {sig} ZONE | {cp:,.2f}</h1></div>", unsafe_allow_html=True)

    # --- THE CHART ---
    fig = go.Figure()

    # 1. Background Shading
    fig.add_vrect(x0=df.index[0], x1=df.index[-1], fillcolor=col, opacity=0.03, layer="below", line_width=0)

    # 2. Candlesticks
    fig.add_trace(go.Candlestick(x=df.index, open=df.Open, high=df.High, low=df.Low, close=df.Close, name="Price"))

    # 3. Floating BUY/SELL Label
    if sig != "WAIT":
        fig.add_annotation(x=df.index[-1], y=cp, text=f"<b>{sig}</b>", bgcolor=col, font=dict(color="black", size=16), showarrow=True, arrowhead=2)

    # 4. FVG LIQUIDITY BOXES (INSIDE CHART)
    for i in range(len(df)-20, len(df)-1):
        if df['FVG_Up'].iloc[i]:
            fig.add_shape(type="rect", x0=df.index[i-1], x1=df.index[i+1], y0=df['High'].iloc[i-1], y1=df['Low'].iloc[i+1], fillcolor="rgba(0, 255, 136, 0.15)", line_width=1, line_color="rgba(0, 255, 136, 0.3)")
        if df['FVG_Down'].iloc[i]:
            fig.add_shape(type="rect", x0=df.index[i-1], x1=df.index[i+1], y0=df['Low'].iloc[i-1], y1=df['High'].iloc[i+1], fillcolor="rgba(255, 51, 102, 0.15)", line_width=1, line_color="rgba(255, 51, 102, 0.3)")

    # 5. VWAP Line (Center of Truth)
    fig.add_trace(go.Scatter(x=df.index, y=df.VWAP, line=dict(color='white', width=1, dash='dot'), name="VWAP"))

    fig.update_layout(height=650, template="plotly_dark", paper_bgcolor="black", plot_bgcolor="black", xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
    
    # theme=None is the shield against the black screen
    st.plotly_chart(fig, use_container_width=True, theme=None, key="smc_final_v11")

render_app()
