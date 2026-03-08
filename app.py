import streamlit as st
import pandas as pd
import pandas_ta as ta
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import logging
import time

# --- 1. SAFE MT5 IMPORT & SILENT LOGGING ---
logging.getLogger('streamlit').setLevel(logging.CRITICAL)

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
        padding: 25px; text-align: center; margin-bottom: 20px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.8);
    }
    div.stButton > button {
        border-radius: 12px !important; font-weight: 900 !important;
        height: 3.5em !important; width: 100% !important;
        text-transform: uppercase; transition: 0.3s;
    }
    section[data-testid="stSidebar"] { background-color: #0a0a0a !important; border-right: 1px solid #222; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. EXECUTION ENGINE ---
def place_justmarket_trade(symbol, order_type, volume=0.01):
    if not MT5_AVAILABLE:
        st.warning("⚠️ Local Windows MT5 required.")
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
            "price": tick.ask if order_type == 0 else tick.bid,
            "magic": 1162026,
            "comment": "PATRO AI V11.6",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        mt5.order_send(request)
        st.balloons()

# --- 4. INSTITUTIONAL SIDEBAR (Static) ---
with st.sidebar:
    st.title("🌌 PATRO V11.6")
    st.error("⚠️ **NEWS WATCH**\nCheck for CPI/NFP releases.")
    
    st.divider()
    st.markdown("### 📋 INSTITUTIONAL SOP")
    st.checkbox("Trend Confluence", value=True)
    st.checkbox("VWAP Proximity", value=True)
    st.checkbox("Volume Confirmation", value=True)
    
    st.divider()
    st.markdown("### 🧮 RISK CALCULATOR")
    balance = st.number_input("Balance ($)", value=1000)
    risk_pct = st.slider("Risk %", 0.5, 5.0, 1.0)
    sl_pips = st.number_input("Stop Loss Pips", value=30)
    lots = (balance * (risk_pct/100)) / (sl_pips * 10) if sl_pips > 0 else 0.01
    st.success(f"Lot Size: **{lots:.2f}**")

    st.divider()
    asset_dict = {"XAUUSD": "GC=F", "US30": "^DJI", "GBPUSD": "GBPUSD=X"}
    choice = st.selectbox("Market Asset", list(asset_dict.keys()))
    tf = st.radio("Timeframe", ["1m", "5m", "15m"], index=1, horizontal=True)

# --- 5. THE LIVE FRAGMENT (Refreshing Part) ---
@st.fragment(run_every=7)
def dashboard_engine():
    ticker = asset_dict[choice]
    data = yf.download(ticker, period="5d", interval=tf, auto_adjust=True, progress=False)
    
    if data is not None and not data.empty:
        if isinstance(data.columns, pd.MultiIndex): 
            data.columns = data.columns.get_level_values(0)
        
        # --- CALCULATIONS ---
        data['VWAP'] = ta.vwap(data['High'], data['Low'], data['Close'], data['Volume'])
        data['SMA200'] = ta.sma(data['Close'], length=200)
        data['ADX'] = ta.adx(data['High'], data['Low'], data['Close'])['ADX_14']
        macd = ta.macd(data['Close'])
        data['MACD_H'] = macd['MACDh_12_26_9']
        data['RSI'] = ta.rsi(data['Close'], length=14)
        data['Vol_Avg'] = data['Volume'].rolling(window=20).mean()
        data['Is_Spike'] = data['Volume'] > (data['Vol_Avg'] * 2.5)
        
        data['Raw'] = 0
        data.loc[(data['Close'] > data['VWAP']) & (data['MACD_H'] > 0) & (data['ADX'] > 22), 'Raw'] = 1
        data.loc[(data['Close'] < data['VWAP']) & (data['MACD_H'] < 0) & (data['ADX'] > 22), 'Raw'] = -1
        data['Entry'] = data['Raw'].diff().fillna(0)
        
        last = data.iloc[-1]
        
        # AI Score
        conf = 0
        if last['Close'] > last['VWAP']: conf += 25
        if last['MACD_H'] > 0: conf += 25
        if last['ADX'] > 25: conf += 25
        if 40 < last['RSI'] < 70: conf += 25
        
        status_clr = "#00FF88" if last['Raw'] == 1 else "#FF3366" if last['Raw'] == -1 else "#777"
        
        # --- UI DISPLAY ---
        st.markdown(f"""
            <div class="glass-card" style="border-bottom: 4px solid {status_clr};">
                <p style="color:#666; letter-spacing:3px; font-size:10px; margin:0;">AI ANALYSIS CONFIDENCE</p>
                <h1 style="color:{status_clr}; font-size:60px; margin:5px 0;">{conf}%</h1>
                <p style="opacity:0.5; letter-spacing:2px; font-size:10px;">AUTO-REFRESHING EVERY 7 SECONDS</p>
            </div>
        """, unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            if st.button("🚀 EXECUTE BUY", use_container_width=True):
                place_justmarket_trade(choice, 0, lots)
        with c2:
            if st.button("📉 EXECUTE SELL", use_container_width=True):
                place_justmarket_trade(choice, 1, lots)

        # --- CHARTS ---
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.02, row_heights=[0.5, 0.15, 0.35])
        fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name="Price"), row=1, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=data['VWAP'], line=dict(color='orange', width=2), name="VWAP"), row=1, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=data['SMA200'], line=dict(color='white', width=1, dash='dot'), name="SMA 200"), row=1, col=1)
        
        # Asia Zones
        asia = data.between_time('03:00', '09:00')
        if not asia.empty:
            ah, al = asia['High'].max(), asia['Low'].min()
            fig.add_hline(y=ah, line_dash="dot", line_color="cyan", row=1, col=1)
            fig.add_hline(y=al, line_dash="dot", line_color="magenta", row=1, col=1)

        # Entry Arrows
        buys = data[data['Entry'] == 1]; sells = data[data['Entry'] == -1]
        fig.add_trace(go.Scatter(x=buys.index, y=buys['Low']*0.999, mode="markers", marker=dict(symbol="triangle-up", size=15, color="#00FF88"), name="BUY"), row=1, col=1)
        fig.add_trace(go.Scatter(x=sells.index, y=sells['High']*1.001, mode="markers", marker=dict(symbol="triangle-down", size=15, color="#FF3366"), name="SELL"), row=1, col=1)

        fig.add_trace(go.Bar(x=data.index, y=data['Volume'], marker_color=['#FFFF00' if s else '#444444' for s in data['Is_Spike']]), row=2, col=1)
        fig.add_trace(go.Bar(x=data.index, y=data['MACD_H'], marker_color=['#00FF88' if v >= 0 else '#FF3366' for v in data['MACD_H']]), row=3, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=data['RSI'], line=dict(color='#C084FC', width=1.5)), row=3, col=1)

        fig.update_layout(height=850, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True, key=f"chart_{choice}_{tf}")

# Run the live fragment
dashboard_engine()
