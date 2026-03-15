import streamlit as st
import pandas as pd
import pandas_ta as ta
import yfinance as yf
import plotly.graph_objects as go

# --- 1. CORE CONFIG ---
st.set_page_config(page_title="PATRO AI PRO V12.1.7", layout="wide")
st.markdown("<style>.stApp { background: #010101; color: #ffffff; }</style>", unsafe_allow_html=True)

# --- 2. SESSION STATE ---
if "locked" not in st.session_state:
    st.session_state.update({
        "locked": False, "l_entry": 0.0, "l_tp": 0.0, "l_sl": 0.0, "l_sig": "WAIT"
    })

# --- 3. DATA ENGINE ---
def get_market_data(ticker, interval="5m"):
    try:
        df = yf.download(ticker, period="2d", interval=interval, progress=False, auto_adjust=True)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        df['VWAP'] = ta.vwap(df.High, df.Low, df.Close, df.Volume)
        df['ATR'] = ta.atr(df.High, df.Low, df.Close, length=14)
        # FVG Detection
        df['FVG_Up'] = (df['Low'].shift(-1) > df['High'].shift(1)) 
        df['FVG_Down'] = (df['High'].shift(-1) < df['Low'].shift(1))
        return df
    except: return None

# --- 4. SIDEBAR ---
with st.sidebar:
    st.header("🏢 SMC COMMAND")
    asset = st.selectbox("Target", ["GOLD", "GBPUSD", "US30"])
    ticker_map = {"GOLD":"GC=F", "GBPUSD":"GBPUSD=X", "US30":"^DJI"}
    target_ticker = ticker_map[asset]
    
    if st.button("🔒 LOCK SIGNAL"): st.session_state.locked = True
    if st.button("🔓 UNLOCK"): st.session_state.locked = False

# --- 5. LIVE DASHBOARD ---
@st.fragment(run_every="15s")
def render_app():
    df = get_market_data(target_ticker, "5m")
    if df is None: return

    cp, vwap_curr = df.Close.iloc[-1], df.VWAP.iloc[-1]
    curr_sig = "BUY" if cp > vwap_curr else "SELL"
    
    if not st.session_state.locked:
        atr = df.ATR.iloc[-1]
        st.session_state.l_entry, st.session_state.l_sig = vwap_curr, curr_sig
        st.session_state.l_tp = cp + (atr * 3) if curr_sig == "BUY" else cp - (atr * 3)
        st.session_state.l_sl = cp - (atr * 1.5) if curr_sig == "BUY" else cp + (atr * 1.5)

    col = "#00FF88" if st.session_state.l_sig == "BUY" else "#FF3366"
    st.markdown(f"<div style='border:2px solid {col}; padding:10px; border-radius:10px; text-align:center;'><h2 style='color:{col};'>🏦 BANK {st.session_state.l_sig} | {cp:,.2f}</h2></div>", unsafe_allow_html=True)

    # --- THE CHART ---
    fig = go.Figure()
    
    # 1. Background Zones (TikTok Style)
    for i in range(len(df)-1):
        x0, x1 = df.index[i], df.index[i+1]
        fill = "rgba(0, 255, 136, 0.04)" if df.Close.iloc[i] > df.VWAP.iloc[i] else "rgba(255, 51, 102, 0.04)"
        fig.add_shape(type="rect", x0=x0, x1=x1, y0=df.Low.min(), y1=df.High.max(), fillcolor=fill, line_width=0, layer="below")

    # 2. Candlesticks
    fig.add_trace(go.Candlestick(x=df.index, open=df.Open, high=df.High, low=df.Low, close=df.Close, name="Price"))
    
    # 3. Floating BUY/SELL Label (Visual Signal)
    label_y = df.Low.iloc[-1] if st.session_state.l_sig == "BUY" else df.High.iloc[-1]
    fig.add_annotation(x=df.index[-1], y=label_y, text=f"<b>{st.session_state.l_sig}</b>", bgcolor=col, font=dict(color="black", size=18), showarrow=True, arrowhead=2, arrowcolor=col)

    # 4. FVG Liquidity Boxes
    for i in range(len(df)-30, len(df)-1):
        if df['FVG_Up'].iloc[i]:
            fig.add_shape(type="rect", x0=df.index[i-1], x1=df.index[i+1], y0=df['High'].iloc[i-1], y1=df['Low'].iloc[i+1], fillcolor="rgba(0, 255, 136, 0.2)", line_width=0)
        if df['FVG_Down'].iloc[i]:
            fig.add_shape(type="rect", x0=df.index[i-1], x1=df.index[i+1], y0=df['Low'].iloc[i-1], y1=df['High'].iloc[i+1], fillcolor="rgba(255, 51, 102, 0.2)", line_width=0)

    # 5. Trading Lines
    fig.add_hline(y=st.session_state.l_entry, line_color="white", annotation_text="ENTRY")
    fig.add_hline(y=st.session_state.l_tp, line_color="#00FF88", line_dash="dash", annotation_text="TP")
    fig.add_hline(y=st.session_state.l_sl, line_color="#FF3366", line_dash="dash", annotation_text="SL")

    fig.update_layout(height=650, template="plotly_dark", paper_bgcolor="#010101", plot_bgcolor="#010101", xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True, key="smc_final_v12")

render_app()
