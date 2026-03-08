import streamlit as st
import pandas as pd
import pandas_ta as ta
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import logging
import time

# --- 1. SILENT & SAFE MT5 ENGINE ---
logging.getLogger('streamlit').setLevel(logging.CRITICAL)

try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False

# --- 2. PREMIUM UI SETUP ---
st.set_page_config(page_title="PATRO AI PRO V11.6", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .stApp { background-color: #050505; color: white; }
    header, footer, #MainMenu {visibility: hidden;}
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 20px; text-align: center; margin-bottom: 15px;
    }
    div.stButton > button {
        border-radius: 12px !important; font-weight: 900 !important;
        height: 3.5em !important; width: 100% !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. EXECUTION LOGIC ---
def place_justmarket_trade(symbol, order_type, volume=0.01):
    if not MT5_AVAILABLE:
        st.warning("⚠️ Local Windows MT5 required for execution.")
        return
    if not mt5.initialize(): return
    
    symbol_name = "XAUUSD.m" if "GC=F" in symbol else f"{symbol}.m"
    mt5.symbol_select(symbol_name, True)
    tick = mt5.symbol_info_tick(symbol_name)
    if tick:
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol_name,
            "volume": volume,
            "type": order_type,
            "price": tick.ask if order_type == mt5.ORDER_TYPE_BUY else tick.bid,
            "magic": 1162026,
            "comment": "PATRO AI V11.6",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        mt5.order_send(request)
        st.balloons()

# --- 4. SIDEBAR CONTROLS ---
with st.sidebar:
    st.title("🌌 PATRO V11.6")
    asset_dict = {"XAUUSD": "GC=F", "US30": "^DJI", "GBPUSD": "GBPUSD=X"}
    choice = st.selectbox("Market Asset", list(asset_dict.keys()))
    tf = st.radio("Timeframe", ["1m", "5m", "15m"], index=1, horizontal=True)
    
    st.divider()
    balance = st.number_input("Balance ($)", value=1000)
    risk_pct = st.slider("Risk %", 0.5, 5.0, 1.0)
    sl_pips = st.number_input("Stop Loss Pips", value=30)
    lots = (balance * (risk_pct/100)) / (sl_pips * 10) if sl_pips > 0 else 0.01
    st.success(f"Lot Size: **{lots:.2f}**")

# --- 5. THE AUTO-REFRESH FRAGMENT ---
# This decorator tells Streamlit to rerun this specific function every 10 seconds
@st.fragment(run_every=10)
def live_dashboard(ticker_key, timeframe):
    ticker = asset_dict[ticker_key]
    data = yf.download(ticker, period="2d", interval=timeframe, progress=False)
    
    if data.empty:
        st.error("Waiting for Market Data...")
        return

    if isinstance(data.columns, pd.MultiIndex): data.columns = data.columns.get_level_values(0)
    
    # Technicals
    data['VWAP'] = ta.vwap(data['High'], data['Low'], data['Close'], data['Volume'])
    macd = ta.macd(data['Close'])
    data['MACD_H'] = macd['MACDh_12_26_9']
    data['RSI'] = ta.rsi(data['Close'])
    last = data.iloc[-1]

    # AI Score
    score = 0
    if last['Close'] > last['VWAP']: score += 50
    if last['MACD_H'] > 0: score += 50
    clr = "#00FF88" if score > 50 else "#FF3366"

    # UI Display
    st.markdown(f"""
        <div class="glass-card" style="border-top: 4px solid {clr};">
            <p style="margin:0; font-size:12px; opacity:0.6;">AI LIVE CONFIDENCE</p>
            <h1 style="color:{clr}; font-size:50px; margin:10px 0;">{score}%</h1>
            <p style="font-size:10px;">AUTO-REFRESHING EVERY 10S</p>
        </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🚀 BUY", use_container_width=True): place_justmarket_trade(ticker_key, 0, lots)
    with c2:
        if st.button("📉 SELL", use_container_width=True): place_justmarket_trade(ticker_key, 1, lots)

    # Chart
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.7, 0.3])
    fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name="Price"), row=1, col=1)
    fig.add_trace(go.Scatter(x=data.index, y=data['VWAP'], line=dict(color='orange', width=2), name="VWAP"), row=1, col=1)
    
    h_clrs = ['#00FF88' if v >= 0 else '#FF3366' for v in data['MACD_H']]
    fig.add_trace(go.Bar(x=data.index, y=data['MACD_H'], marker_color=h_clrs, name="MACD"), row=2, col=1)
    
    fig.update_layout(height=600, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig, use_container_width=True)

# Call the fragment
live_dashboard(choice, tf)
