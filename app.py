import streamlit as st
import pandas as pd
import pandas_ta as ta
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import logging
import os

# --- 1. SYSTEM INITIALIZATION ---
logging.getLogger('yfinance').setLevel(logging.CRITICAL)

# Cloud-Safe Audio
WINDOWS_AUDIO = False
if os.name == 'nt':
    try:
        import winsound
        WINDOWS_AUDIO = True
    except: pass

# Local MT5 Check
try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except:
    MT5_AVAILABLE = False

# --- 2. PREMIUM CSS ---
st.set_page_config(page_title="PATRO AI PRO V11.6", layout="wide")
st.markdown("""
    <style>
    .stApp { background: #050505; color: white; }
    .glass-card {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px; padding: 15px; text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. THE "STAY ALIVE" UTILITIES ---
def get_clean_data(ticker, period="3d", interval="1m"):
    """Downloads and flattens MultiIndex to prevent AttributeErrors"""
    try:
        # Use multi_level_index=False to try and get a clean DF directly
        df = yf.download(ticker, period=period, interval=interval, progress=False, multi_level_index=False)
        if df.empty: return pd.DataFrame()
        
        # Double-check flattening for safety
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        # Ensure the index is Datetime (Required by pandas_ta)
        df.index = pd.to_datetime(df.index)
        return df
    except:
        return pd.DataFrame()

def safe_vwap(df):
    """Calculates VWAP and handles 'None' returns safely"""
    try:
        res = ta.vwap(df['High'], df['Low'], df['Close'], df['Volume'])
        if res is not None and not res.empty:
            return res
        return pd.Series([0] * len(df), index=df.index) # Fallback to zero
    except:
        return pd.Series([0] * len(df), index=df.index)

# --- 4. SIDEBAR & ASSETS ---
assets = {"GOLD": "GC=F", "GBPUSD": "GBPUSD=X", "US30": "^DJI"}
with st.sidebar:
    st.title("PATRO V11.6")
    choice = st.selectbox("Asset", list(assets.keys()))
    ticker = assets[choice]
    tf_choice = st.radio("TF", ["1m", "5m", "15m"], index=0, horizontal=True)
    
    st.divider()
    s1 = st.checkbox("MTF Align", value=True)
    s2 = st.checkbox("VWAP Check", value=True)
    sop = sum([s1, s2])
    matrix_spot = st.empty()

# --- 5. MAIN ENGINE ---
@st.fragment(run_every="7s")
def main_loop():
    # Matrix Check (Side)
    matrix_res = []
    for m in ["1m", "5m", "15m"]:
        m_df = get_clean_data(ticker, interval=m)
        if not m_df.empty:
            m_vwap_ser = safe_vwap(m_df)
            m_bias = "🟢" if m_df['Close'].iloc[-1] > m_vwap_ser.iloc[-1] else "🔴"
            matrix_res.append({"TF": m, "Trend": m_bias})
    matrix_spot.table(pd.DataFrame(matrix_res))

    # Main Chart Logic
    df = get_clean_data(ticker, interval=tf_choice)
    if not df.empty:
        df['VWAP'] = safe_vwap(df)
        df['ADX'] = ta.adx(df['High'], df['Low'], df['Close'])['ADX_14']
        
        last = df.iloc[-1]
        
        # UI Metrics
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f'<div class="glass-card">VWAP BIAS<br><h1>{"BULL" if last["Close"] > last["VWAP"] else "BEAR"}</h1></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="glass-card">ADX STRENGTH<br><h1>{int(last["ADX"])}</h1></div>', unsafe_allow_html=True)

        # Chart
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.8, 0.2])
        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close']), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['VWAP'], line=dict(color='orange')), row=1, col=1)
        fig.add_trace(go.Bar(x=df.index, y=df['Volume']), row=2, col=1)
        fig.update_layout(height=600, template="plotly_dark", xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

main_loop()
