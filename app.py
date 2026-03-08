import streamlit as st
import pandas as pd
import pandas_ta as ta
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# --- 1. SYSTEM CONFIG ---
WINDOWS_AUDIO = False
if os.name == 'nt':
    try:
        import winsound
        WINDOWS_AUDIO = True
    except: pass

# --- 2. THE "BULLETPROOF" DATA ENGINE ---
def force_flat_columns(df):
    """Guarantees columns are flat strings (e.g., 'Close') and not MultiIndex"""
    if df.empty:
        return df
    if isinstance(df.columns, pd.MultiIndex):
        # Keeps only the first level (e.g., 'Close' instead of ('Close', 'GC=F'))
        df.columns = df.columns.get_level_values(0)
    # Ensure index is datetime for indicators
    df.index = pd.to_datetime(df.index)
    return df

def get_market_data(ticker, tf="1m"):
    """Download and immediately clean data before any analysis"""
    try:
        # We download 5 days to ensure we have enough data for SMA200/indicators
        raw = yf.download(ticker, period="5d", interval=tf, progress=False, auto_adjust=True)
        return force_flat_columns(raw)
    except Exception as e:
        st.error(f"Data Download Error: {e}")
        return pd.DataFrame()

# --- 3. INTERFACE ---
st.set_page_config(page_title="PATRO AI PRO V11.6", layout="wide")
st.markdown("<style>.stApp { background: #050505; color: white; }</style>", unsafe_allow_html=True)

with st.sidebar:
    st.title("🌌 PATRO V11.6")
    asset_dict = {"GOLD": "GC=F", "GBPUSD": "GBPUSD=X", "US30": "^DJI"}
    choice = st.selectbox("Asset", list(asset_dict.keys()))
    ticker = asset_dict[choice]
    main_tf = st.radio("Timeframe", ["1m", "5m", "15m"], index=1, horizontal=True)
    st.divider()
    sop_check = st.checkbox("Institutional Alignment", value=True)
    matrix_spot = st.empty()

# --- 4. EXECUTION LOOP ---
@st.fragment(run_every="7s")
def run_app():
    # 4a. Trend Matrix
    matrix_results = []
    for tf in ["1m", "5m", "15m"]:
        m_df = get_market_data(ticker, tf=tf)
        if not m_df.empty:
            vwap_res = ta.vwap(m_df['High'], m_df['Low'], m_df['Close'], m_df['Volume'])
            if vwap_res is not None and not vwap_res.empty:
                current_v = vwap_res.iloc[-1]
                bias = "🟢" if m_df['Close'].iloc[-1] > current_v else "🔴"
                matrix_results.append({"TF": tf, "Trend": bias})
    
    with matrix_spot.container():
        st.table(pd.DataFrame(matrix_results))

    # 4b. Main Analysis
    df = get_market_data(ticker, tf=main_tf)
    if not df.empty and len(df) > 20:
        # Calculate Indicators with safety checks
        df['VWAP'] = ta.vwap(df['High'], df['Low'], df['Close'], df['Volume'])
        df['RSI'] = ta.rsi(df['Close'], length=14)
        
        # Prevent crash if VWAP is None
        last_close = df['Close'].iloc[-1]
        last_vwap = df['VWAP'].iloc[-1] if df['VWAP'].iloc[-1] != 0 else last_close
        
        # UI Metrics
        col1, col2 = st.columns(2)
        with col1:
            color = "#00FF88" if last_close > last_vwap else "#FF3366"
            st.markdown(f"### BIAS: <span style='color:{color}'>{'BULL' if last_close > last_vwap else 'BEAR'}</span>", unsafe_allow_html=True)
        with col2:
            st.metric("RSI (14)", int(df['RSI'].iloc[-1]))

        # Charting
        fig = make_subplots(rows=1, cols=1)
        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"))
        fig.add_trace(go.Scatter(x=df.index, y=df['VWAP'], line=dict(color='orange', width=2), name="VWAP"))
        fig.update_layout(height=600, template="plotly_dark", xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
        
        # Audio Spike logic
        if WINDOWS_AUDIO and df['Volume'].iloc[-1] > (df['Volume'].mean() * 3):
            winsound.Beep(1000, 200)

run_app()
