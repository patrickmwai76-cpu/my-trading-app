import streamlit as st
import pandas as pd
import pandas_ta as ta
import yfinance as yf
import plotly.graph_objects as go

# --- 1. CORE CONFIG ---
st.set_page_config(page_title="PATRO AI PRO V12.1.6", layout="wide")
st.markdown("<style>.stApp { background: #010101; color: #ffffff; }</style>", unsafe_allow_html=True)

# --- 2. SESSION STATE ---
if "locked" not in st.session_state:
    st.session_state.update({
        "locked": False, "l_entry": 0.0, "l_tp": 0.0, "l_sl": 0.0, "l_sig": "WAIT"
    })

# --- 3. DATA ENGINE (FLATTENED) ---
def get_market_data(ticker, interval="5m"):
    try:
        # Download data
        df = yf.download(ticker, period="2d", interval=interval, progress=False, auto_adjust=True)
        
        if df.empty: return None
        
        # --- CRITICAL FIX: FLATTEN MULTI-INDEX COLUMNS ---
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        # Ensure all necessary columns exist
        df = df[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
        
        # Calculate Indicators
        df['RSI'] = ta.rsi(df.Close, length=14)
        df['VWAP'] = ta.vwap(df.High, df.Low, df.Close, df.Volume)
        df['ATR'] = ta.atr(df.High, df.Low, df.Close, length=14)
        
        return df
    except Exception as e:
        st.sidebar.error(f"Data Error: {e}")
        return None

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("🌌 COMMAND CENTER")
    asset = st.selectbox("Market Target", ["GOLD", "GBPUSD", "US30"])
    ticker_map = {"GOLD":"GC=F", "GBPUSD":"GBPUSD=X", "US30":"^DJI"}
    target_ticker = ticker_map[asset]
    
    if st.button("🔄 MANUAL REFRESH"):
        st.rerun()

# --- 5. LIVE DASHBOARD ---
@st.fragment(run_every="15s")
def render_app():
    df = get_market_data(target_ticker, "5m")
    
    if df is None or len(df) < 10:
        st.warning("Waiting for Market Data... Check connection.")
        return

    cp = df.Close.iloc[-1]
    vwap_curr = df.VWAP.iloc[-1]
    curr_sig = "BUY" if cp > vwap_curr else "SELL"
    
    # Update state
    if not st.session_state.locked:
        atr = df.ATR.iloc[-1]
        st.session_state.l_entry, st.session_state.l_sig = vwap_curr, curr_sig
        st.session_state.l_tp = cp + (atr * 3) if curr_sig == "BUY" else cp - (atr * 3)
        st.session_state.l_sl = cp - (atr * 1.5) if curr_sig == "BUY" else cp + (atr * 1.5)

    col = "#00FF88" if st.session_state.l_sig == "BUY" else "#FF3366"
    
    # Top Metric
    st.markdown(f"<div style='border:2px solid {col}; padding:10px; border-radius:10px; text-align:center;'><h2 style='color:{col}; margin:0;'>🏦 BANK {st.session_state.l_sig} | PRICE: {cp:,.2f}</h2></div>", unsafe_allow_html=True)

    # --- THE CHART ---
    fig = go.Figure()
    
    # Candlesticks
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name="Market"
    ))
    
    # Visual Polish
    fig.add_hline(y=st.session_state.l_entry, line_color="white", annotation_text="ENTRY")
    fig.add_hline(y=st.session_state.l_tp, line_color="#00FF88", line_dash="dash")
    fig.add_hline(y=st.session_state.l_sl, line_color="#FF3366", line_dash="dash")

    # FORCE RENDERING SETTINGS
    fig.update_layout(
        height=600,
        template="plotly_dark",
        paper_bgcolor="#010101",
        plot_bgcolor="#010101",
        xaxis_rangeslider_visible=False,
        margin=dict(l=10, r=10, t=10, b=10)
    )
    
    # render_mode="webgl" ensures it uses the GPU for drawing
    st.plotly_chart(fig, use_container_width=True, key="gold_pro_v12")

render_app()
