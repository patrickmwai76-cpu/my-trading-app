import streamlit as st
import pandas as pd
import pandas_ta as ta
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import logging
import os

# --- 1. SYSTEM CHECKS & CONDITIONAL IMPORTS ---
logging.getLogger('yfinance').setLevel(logging.CRITICAL)

# Check for Windows Audio (Prevents Cloud Crash)
WINDOWS_AUDIO = False
if os.name == 'nt':
    try:
        import winsound
        WINDOWS_AUDIO = True
    except ImportError:
        pass

# MetaTrader 5 Check
try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False

# --- 2. PREMIUM INTERFACE SETUP ---
st.set_page_config(page_title="PATRO AI PRO V11.6", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .stApp { background-color: #050505; color: white; }
    header, footer, #MainMenu {visibility: hidden;}
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 20px; text-align: center; margin-bottom: 20px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.8);
    }
    div.stButton > button {
        border-radius: 12px !important; font-weight: 900 !important;
        height: 3.5em !important; width: 100% !important;
        text-transform: uppercase; transition: 0.3s;
    }
    button[key="buy_btn"] { background: linear-gradient(135deg, #00FF88 0%, #008DFF 100%) !important; color: black !important; }
    button[key="sell_btn"] { background: linear-gradient(135deg, #FF3366 0%, #FF8A00 100%) !important; color: white !important; }
    section[data-testid="stSidebar"] { background-color: #0a0a0a !important; border-right: 1px solid #222; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. EXECUTION ENGINE ---
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
            "volume": float(volume),
            "type": order_type,
            "price": tick.ask if order_type == 0 else tick.bid,
            "magic": 1162026,
            "comment": "PATRO AI V11.6",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        mt5.order_send(request)
        st.balloons()

# --- 4. SIDEBAR INPUTS ---
asset_dict = {"XAUUSD": "GC=F", "US30": "^DJI", "GBPUSD": "GBPUSD=X"}
with st.sidebar:
    st.title("🌌 PATRO V11.6")
    choice = st.selectbox("Market Asset", list(asset_dict.keys()))
    ticker = asset_dict[choice]

    st.error("⚠️ **NEWS WATCH**\nInstitutional Volatility Alert.")
    st.divider()
    
    st.markdown("### 📋 INSTITUTIONAL SOP")
    s1 = st.checkbox("MTF Confluence Check", value=True)
    s2 = st.checkbox("VWAP Proximity", value=True)
    s3 = st.checkbox("Volume Confirmation", value=True)
    sop_count = sum([s1, s2, s3])

    st.divider()
    st.markdown("### 🧮 RISK CALCULATOR")
    balance = st.number_input("Balance ($)", value=1000)
    risk_pct = st.slider("Risk %", 0.5, 5.0, 1.0)
    sl_pips = st.number_input("Stop Loss Pips", value=30)
    lots = max((balance * (risk_pct/100)) / (sl_pips * 10), 0.01) if sl_pips > 0 else 0.01
    st.success(f"Lot Size: **{lots:.2f}**")
    
    st.divider()
    tf = st.radio("Main Chart TF", ["1m", "5m", "15m"], index=1, horizontal=True)
    matrix_container = st.empty()

# --- 5. THE LIVE ENGINE ---
@st.fragment(run_every=7)
def dashboard_engine():
    # 5a. SIDEBAR MATRIX
    matrix_data = []
    for mtf in ["1m", "5m", "15m"]:
        df_m = yf.download(ticker, period="1d", interval=mtf, progress=False)
        if not df_m.empty:
            if isinstance(df_m.columns, pd.MultiIndex): df_m.columns = df_m.columns.get_level_values(0)
            vwap_m = ta.vwap(df_m['High'], df_m['Low'], df_m['Close'], df_m['Volume']).iloc[-1]
            status = "🟢 BULL" if df_m['Close'].iloc[-1] > vwap_m else "🔴 BEAR"
            matrix_data.append({"TF": mtf, "Status": status})
    
    with matrix_container:
        st.markdown("### 📊 TREND MATRIX")
        st.table(pd.DataFrame(matrix_data))

    # 5b. MAIN DATA
    data = yf.download(ticker, period="5d", interval=tf, auto_adjust=True, progress=False)
    if data is not None and not data.empty:
        if isinstance(data.columns, pd.MultiIndex): data.columns = data.columns.get_level_values(0)
        
        # INDICATORS
        data['VWAP'] = ta.vwap(data['High'], data['Low'], data['Close'], data['Volume'])
        data['ADX'] = ta.adx(data['High'], data['Low'], data['Close'])['ADX_14']
        macd = ta.macd(data['Close'])
        data['MACD_H'] = macd['MACDh_12_26_9']
        data['Vol_Avg'] = data['Volume'].rolling(window=20).mean()
        data['Is_Spike'] = data['Volume'] > (data['Vol_Avg'] * 2.5)
        
        # AUDIO ALERT (Cloud Safe)
        if data['Is_Spike'].iloc[-1] and WINDOWS_AUDIO:
            try: winsound.Beep(1000, 400)
            except: pass

        # ENTRY LOGIC
        data['Raw'] = 0
        data.loc[(data['Close'] > data['VWAP']) & (data['MACD_H'] > 0) & (data['ADX'] > 22), 'Raw'] = 1
        data.loc[(data['Close'] < data['VWAP']) & (data['MACD_H'] < 0) & (data['ADX'] > 22), 'Raw'] = -1
        
        last = data.iloc[-1]
        
        # CONFIDENCE CALCULATION
        current_bias = "🟢 BULL" if last['Raw'] == 1 else "🔴 BEAR" if last['Raw'] == -1 else None
        bias_count = sum([1 for m in matrix_data if m['Status'] == current_bias]) if current_bias else 0
        final_conf = int(((bias_count / 3) * 40) + ((sop_count / 3) * 40) + (20 if last['Raw'] != 0 else 0))
        
        adx_val = last['ADX']
        strength, s_clr = ("STRONG", "#00FF88") if adx_val > 25 else ("WEAK", "#777")
        status_clr = "#00FF88" if last['Raw'] == 1 else "#FF3366" if last['Raw'] == -1 else "#777"

        # UI CARDS
        sc, st_col = st.columns(2)
        with sc:
            st.markdown(f'<div class="glass-card" style="border-bottom:4px solid {status_clr};">AI CONFIDENCE<br><h1 style="color:{status_clr};">{final_conf}%</h1></div>', unsafe_allow_html=True)
        with st_col:
            st.markdown(f'<div class="glass-card" style="border-bottom:4px solid {s_clr};">STRENGTH<br><h1 style="color:{s_clr};">{int(adx_val)}</h1>{strength}</div>', unsafe_allow_html=True)

        # BUTTONS
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🚀 EXECUTE BUY", key="buy_btn"): place_justmarket_trade(choice, 0, lots)
        with c2:
            if st.button("📉 EXECUTE SELL", key="sell_btn"): place_justmarket_trade(choice, 1, lots)

        # CHART
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.7, 0.3])
        fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name="Price"), row=1, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=data['VWAP'], line=dict(color='orange', width=2), name="VWAP"), row=1, col=1)
        fig.add_trace(go.Bar(x=data.index, y=data['Volume'], marker_color=['#FFFF00' if s else '#333' for s in data['Is_Spike']]), row=2, col=1)

        fig.update_layout(height=650, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True, key=f"chart_{choice}")

dashboard_engine()
