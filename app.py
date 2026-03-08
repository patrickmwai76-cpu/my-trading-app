import streamlit as st
import pandas as pd
import pandas_ta as ta
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import logging
import os

# --- 1. SYSTEM CHECKS & CLOUD COMPATIBILITY ---
logging.getLogger('yfinance').setLevel(logging.CRITICAL)

# Check for Windows Audio (Prevents Streamlit Cloud Crash)
WINDOWS_AUDIO = False
if os.name == 'nt':
    try:
        import winsound
        WINDOWS_AUDIO = True
    except ImportError:
        pass

# Check for MetaTrader 5 (Only available on local Windows)
try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False

# --- 2. PREMIUM UI CONFIGURATION ---
st.set_page_config(page_title="PATRO AI PRO V11.6", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .stApp { background-color: #050505; color: white; }
    header, footer, #MainMenu {visibility: hidden;}
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 15px; text-align: center; margin-bottom: 10px;
    }
    div.stButton > button {
        border-radius: 10px !important; font-weight: 800 !important;
        height: 3em !important; width: 100% !important;
    }
    button[key="buy_btn"] { background: linear-gradient(135deg, #00FF88 0%, #008DFF 100%) !important; color: black !important; }
    button[key="sell_btn"] { background: linear-gradient(135deg, #FF3366 0%, #FF8A00 100%) !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. EXECUTION ENGINE (LOCAL ONLY) ---
def execute_trade(symbol, order_type, volume=0.01):
    if not MT5_AVAILABLE:
        st.error("⚠️ Trade Execution requires local Windows MT5.")
        return
    if not mt5.initialize(): return
    # Symbol mapping for JustMarkets/Exness
    s_name = "XAUUSD.m" if "GC=F" in symbol else f"{symbol}.m"
    mt5.symbol_select(s_name, True)
    tick = mt5.symbol_info_tick(s_name)
    if tick:
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": s_name,
            "volume": float(volume),
            "type": order_type,
            "price": tick.ask if order_type == 0 else tick.bid,
            "magic": 1162026,
            "comment": "PATRO AI V11.6",
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        mt5.order_send(request)
        st.toast(f"Order Sent: {s_name}")

# --- 4. SIDEBAR SETTINGS ---
asset_dict = {"XAUUSD": "GC=F", "GBPUSD": "GBPUSD=X", "US30": "^DJI"}

with st.sidebar:
    st.title("🌌 PATRO V11.6")
    asset_choice = st.selectbox("Market Asset", list(asset_dict.keys()))
    ticker = asset_dict[asset_choice]
    
    st.divider()
    st.markdown("### 📋 INSTITUTIONAL SOP")
    s1 = st.checkbox("MTF Confluence", value=True)
    s2 = st.checkbox("VWAP Proximity", value=True)
    s3 = st.checkbox("Volume Confirmation", value=True)
    sop_score = sum([s1, s2, s3])

    st.divider()
    risk_pct = st.slider("Risk %", 0.5, 5.0, 1.0)
    lots = st.number_input("Lot Size", value=0.01, step=0.01)
    
    st.divider()
    tf = st.radio("Chart Timeframe", ["1m", "5m", "15m"], index=1, horizontal=True)
    matrix_spot = st.empty()

# --- 5. DATA CLEANING UTILITY ---
def clean_data(df):
    """Flattens MultiIndex columns from yfinance 2025/2026 updates"""
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df.index = pd.to_datetime(df.index)
    return df

# --- 6. THE LIVE DASHBOARD ---
@st.fragment(run_every="7s")
def run_patro_engine():
    # 6a. Trend Matrix Logic
    matrix_results = []
    for m in ["1m", "5m", "15m"]:
        m_data = yf.download(ticker, period="1d", interval=m, progress=False)
        if not m_data.empty:
            m_data = clean_data(m_data)
            vwap = ta.vwap(m_data['High'], m_data['Low'], m_data['Close'], m_data['Volume'])
            if vwap is not None and not vwap.empty:
                bias = "🟢 BULL" if m_data['Close'].iloc[-1] > vwap.iloc[-1] else "🔴 BEAR"
                matrix_results.append({"TF": m, "Trend": bias})
    
    with matrix_spot.container():
        st.markdown("### 📊 TREND MATRIX")
        st.table(pd.DataFrame(matrix_results))

    # 6b. Main Analysis
    main_df = yf.download(ticker, period="2d", interval=tf, progress=False)
    if not main_df.empty:
        main_df = clean_data(main_df)
        
        # Indicators
        main_df['VWAP'] = ta.vwap(main_df['High'], main_df['Low'], main_df['Close'], main_df['Volume'])
        main_df['ADX'] = ta.adx(main_df['High'], main_df['Low'], main_df['Close'])['ADX_14']
        macd = ta.macd(main_df['Close'])
        main_df['MACD_H'] = macd['MACDh_12_26_9']
        
        # Volume Spike Logic
        vol_avg = main_df['Volume'].rolling(20).mean()
        is_spike = main_df['Volume'].iloc[-1] > (vol_avg.iloc[-1] * 2.5)
        
        if is_spike and WINDOWS_AUDIO:
            try: winsound.Beep(800, 300)
            except: pass

        # Score Calculation
        last = main_df.iloc[-1]
        tech_score = 0
        current_side = "🟢 BULL" if last['Close'] > last['VWAP'] else "🔴 BEAR"
        
        # Calculate matrix match
        matches = sum(1 for x in matrix_results if x['Trend'] == current_side)
        final_conf = int(((matches / 3) * 50) + ((sop_score / 3) * 30) + (20 if last['ADX'] > 25 else 0))

        # UI Header
        h1, h2 = st.columns(2)
        with h1:
            st.markdown(f'<div class="glass-card">CONFIDENCE<br><h1 style="color:#00FF88;">{final_conf}%</h1></div>', unsafe_allow_html=True)
        with h2:
            st.markdown(f'<div class="glass-card">ADX STRENGTH<br><h1>{int(last["ADX"])}</h1></div>', unsafe_allow_html=True)

        # Execution Buttons
        b1, b2 = st.columns(2)
        with b1:
            if st.button("🚀 BUY", key="buy_btn"): execute_trade(ticker, 0, lots)
        with b2:
            if st.button("📉 SELL", key="sell_btn"): execute_trade(ticker, 1, lots)

        # Main Chart
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3], vertical_spacing=0.05)
        fig.add_trace(go.Candlestick(x=main_df.index, open=main_df['Open'], high=main_df['High'], low=main_df['Low'], close=main_df['Close'], name="Price"), row=1, col=1)
        fig.add_trace(go.Scatter(x=main_df.index, y=main_df['VWAP'], line=dict(color='orange', width=1.5), name="VWAP"), row=1, col=1)
        fig.add_trace(go.Bar(x=main_df.index, y=main_df['Volume'], name="Volume", marker_color="#333"), row=2, col=1)
        
        fig.update_layout(height=600, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=10,r=10,t=10,b=10))
        st.plotly_chart(fig, use_container_width=True, key=f"chart_{asset_choice}")

run_patro_engine()
