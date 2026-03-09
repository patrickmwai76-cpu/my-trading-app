import streamlit as st
import pandas as pd
import pandas_ta as ta
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# --- 1. SYSTEM INITIALIZATION ---
WINDOWS_AUDIO = False
if os.name == 'nt':
    try:
        import winsound
        WINDOWS_AUDIO = True
    except: pass

# --- 2. ERROR-PROOF DATA ENGINE ---
def get_clean_data(ticker, interval="1m"):
    try:
        df = yf.download(ticker, period="5d", interval=interval, progress=False, auto_adjust=True)
        if df.empty: return pd.DataFrame()
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df.index = pd.to_datetime(df.index)
        return df
    except: return pd.DataFrame()

# --- 3. PREMIUM UI ---
st.set_page_config(page_title="PATRO AI PRO V11.6", layout="wide")
st.markdown("""
    <style>
    .stApp { background: #050505; color: white; }
    .score-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px; padding: 20px; text-align: center;
    }
    .action-banner {
        font-size: 42px; font-weight: 900; padding: 10px; border-radius: 10px; margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. SIDEBAR COMMANDS ---
assets = {"GOLD": "GC=F", "GBPUSD": "GBPUSD=X", "US30": "^DJI"}
with st.sidebar:
    st.title("🌌 PATRO V11.6")
    choice = st.selectbox("Asset", list(assets.keys()))
    ticker = assets[choice]
    
    st.divider()
    st.markdown("### 📋 INSTITUTIONAL SOP")
    s1 = st.checkbox("MTF Confluence", value=True)
    s2 = st.checkbox("VWAP Proximity", value=True)
    s3 = st.checkbox("Volume Confirmation", value=True)
    s4 = st.checkbox("FVG / Liquidity Sweep", value=True)
    sop_count = sum([s1, s2, s3, s4])
    
    matrix_spot = st.empty()

# --- 5. CORE CONFLUENCE ENGINE ---
@st.fragment(run_every="7s")
def start_engine():
    # 5a. Multi-Timeframe Matrix
    matrix_data = []
    trends = {}
    for tf in ["1m", "5m", "15m"]:
        m_df = get_clean_data(ticker, interval=tf)
        if not m_df.empty:
            m_vwap = ta.vwap(high=m_df['High'], low=m_df['Low'], close=m_df['Close'], volume=m_df['Volume']).iloc[-1]
            bias = "BULL" if m_df['Close'].iloc[-1] > m_vwap else "BEAR"
            matrix_data.append({"TF": tf, "Trend": "🟢 BULL" if bias == "BULL" else "🔴 BEAR"})
            trends[tf] = bias
    
    with matrix_spot.container():
        st.table(pd.DataFrame(matrix_data))

    # 5b. Main Analysis (1m)
    df = get_clean_data(ticker, interval="1m")
    if not df.empty and len(df) > 50:
        df['VWAP'] = ta.vwap(high=df['High'], low=df['Low'], close=df['Close'], volume=df['Volume'])
        df['ADX'] = ta.adx(df['High'], df['Low'], df['Close'])['ADX_14']
        df['RSI'] = ta.rsi(df['Close'], length=14)
        
        last = df.iloc[-1]
        
        # --- AI SCORE CALCULATION ---
        # 1. MTF Alignment (40%)
        all_match = len(set(trends.values())) == 1
        mtf_score = 40 if all_match else (20 if trends.get("1m") == trends.get("5m") else 0)
        
        # 2. SOP Compliance (40%)
        sop_score = (sop_count / 4) * 40
        
        # 3. Trend Strength (20%)
        adx_score = 20 if last['ADX'] > 25 else (last['ADX'] / 25) * 20
        
        final_conf = int(mtf_score + sop_score + adx_score)
        
        # --- ACTION LOGIC ---
        current_trend = trends.get("1m")
        if all_match and final_conf >= 90:
            action = f"🚀 STRONG {current_trend}"
            act_clr = "#00FF88" if current_trend == "BULL" else "#FF3366"
        elif all_match:
            action = f"✅ {current_trend} CONFIRMED"
            act_clr = "#00FF88" if current_trend == "BULL" else "#FF3366"
        else:
            action = "⌛ WAITING FOR ALIGNMENT"
            act_clr = "#777"

        # --- TOP DISPLAY ---
        st.markdown(f"""
            <div class="score-card">
                <span style="font-size: 20px; color: #aaa;">AI CONFLUENCE SCORE</span><br>
                <span style="font-size: 64px; font-weight: 900; color: {act_clr};">{final_conf}%</span>
                <div class="action-banner" style="background: {act_clr}22; color: {act_clr}; border: 2px solid {act_clr};">
                    {action}
                </div>
            </div>
        """, unsafe_allow_html=True)

        # --- CHARTING ---
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True, row_heights=[0.5, 0.2, 0.3], vertical_spacing=0.03)
        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['VWAP'], line=dict(color='orange', width=2), name="VWAP"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], line=dict(color='#00FF88'), name="RSI"), row=2, col=1)
        fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name="Volume"), row=3, col=1)
        fig.update_layout(height=800, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=10,b=0))
        st.plotly_chart(fig, use_container_width=True, key=f"p_{choice}")

        if WINDOWS_AUDIO and final_conf >= 95:
            winsound.Beep(1200, 500)

start_engine()
