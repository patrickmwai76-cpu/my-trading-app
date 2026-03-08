import streamlit as st
import pandas as pd
import pandas_ta as ta
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import logging
import os

# --- 1. CLOUD-SAFE SYSTEM INITIALIZATION ---
logging.getLogger('yfinance').setLevel(logging.CRITICAL)

# Windows Audio Fix (Prevents Cloud Crash)
WINDOWS_AUDIO = False
if os.name == 'nt':
    try:
        import winsound
        WINDOWS_AUDIO = True
    except: pass

# MetaTrader 5 Check (Local Execution)
try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except:
    MT5_AVAILABLE = False

# --- 2. THE "VIDEO LOOK" PREMIUM INTERFACE ---
st.set_page_config(page_title="PATRO AI PRO V11.6", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #050505 0%, #0a0a0e 100%); color: white; }
    [data-testid="stSidebar"] { background: #080808 !important; border-right: 1px solid #1a1a1a; }
    .glass-card {
        background: rgba(255, 255, 255, 0.02);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px; padding: 15px; text-align: center;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
    }
    .metric-val { font-size: 28px; font-weight: 800; color: #00FF88; }
    div.stButton > button {
        border-radius: 8px !important; font-weight: 900 !important;
        height: 3.5em !important; width: 100% !important; text-transform: uppercase;
    }
    button[key="buy"] { background: linear-gradient(90deg, #00FF88, #008DFF) !important; color: black !important; }
    button[key="sell"] { background: linear-gradient(90deg, #FF3366, #FF8A00) !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. EXECUTION ENGINE (JustMarkets Mapping) ---
def fire_order(symbol, o_type, lot_size=0.01):
    if not MT5_AVAILABLE:
        st.error("⚠️ Execution requires local Windows MT5.")
        return
    if not mt5.initialize(): return
    # JustMarkets Symbol Mapping
    jm_symbol = "XAUUSD.m" if "GC=F" in symbol else "GBPUSD.m" if "GBPUSD" in symbol else f"{symbol}.m"
    mt5.symbol_select(jm_symbol, True)
    tick = mt5.symbol_info_tick(jm_symbol)
    if tick:
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": jm_symbol,
            "volume": float(lot_size),
            "type": o_type,
            "price": tick.ask if o_type == 0 else tick.bid,
            "magic": 1162026,
            "comment": "PATRO AI V11.6",
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        res = mt5.order_send(request)
        if res.retcode == mt5.TRADE_RETCODE_DONE: st.toast("Trade Executed ✅")

# --- 4. DATA CLEANING UTILITY (MultiIndex Fix) ---
def get_clean_data(ticker, period="2d", interval="1m"):
    df = yf.download(ticker, period=period, interval=interval, progress=False)
    if not df.empty:
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df.index = pd.to_datetime(df.index)
    return df

# --- 5. SIDEBAR: INSTITUTIONAL DASHBOARD ---
asset_map = {"GOLD (XAUUSD)": "GC=F", "GBPUSD": "GBPUSD=X", "US30": "^DJI"}

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2544/2544111.png", width=60) # Scalper Icon
    st.title("PATRO V11.6")
    asset_label = st.selectbox("Market Asset", list(asset_map.keys()))
    ticker = asset_map[asset_label]
    
    st.divider()
    st.markdown("### 📋 INSTITUTIONAL SOP")
    c1 = st.checkbox("15m Trend Alignment", value=True)
    c2 = st.checkbox("FVG / Liquidity Sweep", value=True)
    c3 = st.checkbox("VWAP Bounce Confirmed", value=True)
    sop_score = sum([c1, c2, c3])
    
    st.divider()
    risk_val = st.number_input("Account Balance ($)", value=1000)
    risk_pct = st.slider("Risk Per Trade (%)", 0.5, 5.0, 1.0)
    lot_size = (risk_val * (risk_pct/100)) / 300 # Rough estimate
    st.success(f"Suggested Lots: **{max(0.01, round(lot_size, 2))}**")
    
    tf_main = st.radio("Main Chart TF", ["1m", "5m", "15m"], index=1, horizontal=True)
    matrix_spot = st.empty()

# --- 6. CORE INTELLIGENCE ENGINE ---
@st.fragment(run_every="7s")
def dashboard_loop():
    # 6a. Trend Matrix Calculation
    matrix_data = []
    for tf_check in ["1m", "5m", "15m"]:
        m_df = get_clean_data(ticker, period="1d", interval=tf_check)
        if not m_df.empty:
            m_vwap = ta.vwap(m_df['High'], m_df['Low'], m_df['Close'], m_df['Volume']).iloc[-1]
            bias = "🟢 BULL" if m_df['Close'].iloc[-1] > m_vwap else "🔴 BEAR"
            matrix_data.append({"TF": tf_check, "Trend": bias})
    
    with matrix_spot.container():
        st.markdown("### 📊 TREND MATRIX")
        st.table(pd.DataFrame(matrix_results))

    # 6b. Main Technical Analysis
    df = get_clean_data(ticker, period="3d", interval=tf_main)
    if not df.empty:
        # Indicators
        df['VWAP'] = ta.vwap(df['High'], df['Low'], df['Close'], df['Volume'])
        df['SMA200'] = ta.sma(df['Close'], length=200)
        df['RSI'] = ta.rsi(df['Close'], length=14)
        macd = ta.macd(df['Close'])
        df['MACD_H'] = macd['MACDh_12_26_9']
        
        # Audio Spike Alert
        vol_spike = df['Volume'].iloc[-1] > (df['Volume'].rolling(20).mean().iloc[-1] * 2.5)
        if vol_spike and WINDOWS_AUDIO:
            try: winsound.Beep(1200, 300)
            except: pass

        # 100% Confluence Logic
        last = df.iloc[-1]
        tech_bias = "🟢 BULL" if last['Close'] > last['VWAP'] and last['MACD_H'] > 0 else "🔴 BEAR" if last['Close'] < last['VWAP'] and last['MACD_H'] < 0 else None
        
        matrix_match = sum(1 for x in matrix_data if x['Trend'] == tech_bias) if tech_bias else 0
        ai_score = int(((matrix_match/3)*40) + ((sop_score/3)*40) + (20 if last['RSI'] > 50 else 0))

        # Metrics Row
        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(f'<div class="glass-card">AI CONFIDENCE<br><span class="metric-val" style="color:{"#00FF88" if ai_score > 70 else "#FFCC00"}">{ai_score}%</span></div>', unsafe_allow_html=True)
        with m2:
            st.markdown(f'<div class="glass-card">RSI (14)<br><span class="metric-val">{int(last["RSI"])}</span></div>', unsafe_allow_html=True)
        with m3:
            st.markdown(f'<div class="glass-card">VOLUME<br><span class="metric-val" style="color:{"#FFFF00" if vol_spike else "white"}">{"SPIKE" if vol_spike else "NORMAL"}</span></div>', unsafe_allow_html=True)

        # Execution Buttons
        bt1, bt2 = st.columns(2)
        with bt1:
            if st.button("🚀 EXECUTE BUY", key="buy"): fire_order(ticker, 0, lot_size)
        with bt2:
            if st.button("📉 EXECUTE SELL", key="sell"): fire_order(ticker, 1, lot_size)

        # Professional Charting
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.75, 0.25])
        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['VWAP'], line=dict(color='orange', width=1.5), name="VWAP"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['SMA200'], line=dict(color='white', width=1, dash='dot'), name="SMA200"), row=1, col=1)
        fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name="Volume", marker_color="#333"), row=2, col=1)
        
        fig.update_layout(height=700, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True, key=f"chart_{asset_label}")

dashboard_loop()
