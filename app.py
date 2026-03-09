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

# Windows Audio Fix (Prevents Cloud Crash)
WINDOWS_AUDIO = False
if os.name == 'nt':
    try:
        import winsound
        WINDOWS_AUDIO = True
    except: pass

# --- 2. PREMIUM CSS & INTERFACE ---
st.set_page_config(page_title="PATRO AI PRO V11.6", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .stApp { background-color: #050505; color: white; }
    header, footer, #MainMenu {visibility: hidden;}
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px; padding: 15px; text-align: center; margin-bottom: 10px;
    }
    .metric-val { font-size: 24px; font-weight: 800; color: #00FF88; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATA CLEANING UTILITY ---
def get_clean_data(ticker, period="3d", interval="1m"):
    try:
        df = yf.download(ticker, period=period, interval=interval, progress=False, auto_adjust=True)
        if df.empty: return pd.DataFrame()
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df.index = pd.to_datetime(df.index)
        return df
    except: return pd.DataFrame()

# --- 4. SIDEBAR: THE COMMAND CENTER ---
asset_map = {"GOLD": "GC=F", "GBPUSD": "GBPUSD=X", "US30": "^DJI"}

with st.sidebar:
    st.title("🌌 PATRO V11.6")
    asset_choice = st.selectbox("Market Asset", list(asset_map.keys()))
    ticker = asset_map[asset_choice]
    
    st.divider()
    st.markdown("### 📋 INSTITUTIONAL SOP")
    s1 = st.checkbox("MTF Confluence", value=True)
    s2 = st.checkbox("VWAP Proximity", value=True)
    s3 = st.checkbox("Volume Confirmation", value=True)
    sop_score = sum([s1, s2, s3])

    st.divider()
    tf_main = st.radio("Main Chart TF", ["1m", "5m", "15m"], index=1, horizontal=True)
    
    # Placeholder for the Live Matrix
    matrix_spot = st.empty()

# --- 5. THE LIVE ENGINE ---
@st.fragment(run_every="7s")
def dashboard_engine():
    # 5a. Trend Matrix Calculation (Restored)
    matrix_results = []
    for mtf in ["1m", "5m", "15m"]:
        m_df = get_clean_data(ticker, interval=mtf)
        if not m_df.empty:
            vwap_m = ta.vwap(m_df['High'], m_df['Low'], m_df['Close'], m_df['Volume']).iloc[-1]
            bias = "🟢 BULL" if m_df['Close'].iloc[-1] > vwap_m else "🔴 BEAR"
            matrix_results.append({"TF": mtf, "Trend": bias})
    
    with matrix_spot.container():
        st.markdown("### 📊 TREND MATRIX")
        st.table(pd.DataFrame(matrix_results))

    # 5b. Main Data & Indicators
    df = get_clean_data(ticker, interval=tf_main)
    if not df.empty and len(df) > 30:
        # Indicators
        df['VWAP'] = ta.vwap(df['High'], df['Low'], df['Close'], df['Volume'])
        df['RSI'] = ta.rsi(df['Close'], length=14)
        df['VOL_SMA'] = df['Volume'].rolling(20).mean()
        
        last = df.iloc[-1]
        
        # Volume Spike & Audio Alert
        is_spike = last['Volume'] > (last['VOL_SMA'] * 2.5)
        if is_spike and WINDOWS_AUDIO:
            try: winsound.Beep(1000, 300)
            except: pass

        # AI Confidence Scoring
        current_bias = "🟢 BULL" if last['Close'] > last['VWAP'] else "🔴 BEAR"
        matches = sum(1 for x in matrix_results if x['Trend'] == current_bias)
        final_score = int(((matches / 3) * 50) + ((sop_score / 3) * 50))

        # UI Metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f'<div class="glass-card">AI SCORE<br><span class="metric-val">{final_score}%</span></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="glass-card">RSI (14)<br><span class="metric-val">{int(last["RSI"])}</span></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="glass-card">VOLUME<br><span class="metric-val">{"SPIKE" if is_spike else "NORMAL"}</span></div>', unsafe_allow_html=True)

        # 5c. Professional Multi-Pane Chart (Restored)
        fig = make_subplots(
            rows=3, cols=1, 
            shared_xaxes=True, 
            vertical_spacing=0.02, 
            row_heights=[0.5, 0.2, 0.3],
            subplot_titles=("PRICE & VWAP", "RSI MOMENTUM", "VOLUME DATA")
        )

        # Pane 1: Price & VWAP
        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['VWAP'], line=dict(color='orange', width=2), name="VWAP"), row=1, col=1)

        # Pane 2: RSI Line
        fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], line=dict(color='#00FF88', width=2), name="RSI"), row=2, col=1)
        fig.add_hline(y=70, line_dash="dot", line_color="red", row=2, col=1)
        fig.add_hline(y=30, line_dash="dot", line_color="red", row=2, col=1)

        # Pane 3: Volume Histogram
        v_colors = ['#FFFF00' if v > (df['VOL_SMA'].iloc[i] * 2.5) else '#333' for i, v in enumerate(df['Volume'])]
        fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name="Volume", marker_color=v_colors), row=3, col=1)

        fig.update_layout(height=800, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=10,r=10,t=10,b=10))
        st.plotly_chart(fig, use_container_width=True, key=f"chart_{asset_choice}")

dashboard_engine()
