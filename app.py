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
        padding: 20px; text-align: center; margin-bottom: 20px;
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

# --- 4. INSTITUTIONAL SIDEBAR ---
with st.sidebar:
    st.title("🌌 PATRO V11.6")
    st.error("⚠️ **NEWS WATCH**\nUS Iran Conflict Impacting Gold.")
    
    st.divider()
    st.markdown("### 📋 INSTITUTIONAL SOP")
    st.checkbox("MTF Confluence Check", value=True)
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
    tf = st.radio("Main Chart TF", ["1m", "5m", "15m"], index=1, horizontal=True)

# --- 5. THE LIVE MTF ENGINE ---
@st.fragment(run_every=7)
def dashboard_engine():
    ticker = asset_dict[choice]
    
    # --- MTF SCAN & CONFLUENCE CALC ---
    mtf_trend = []
    confluence_display = {}
    
    for check_tf in ["1m", "5m", "15m"]:
        check_df = yf.download(ticker, period="1d", interval=check_tf, progress=False)
        if not check_df.empty:
            if isinstance(check_df.columns, pd.MultiIndex): check_df.columns = check_df.columns.get_level_values(0)
            cvwap = ta.vwap(check_df['High'], check_df['Low'], check_df['Close'], check_df['Volume'])
            # 1 for Bullish, -1 for Bearish
            trend_val = 1 if check_df['Close'].iloc[-1] > cvwap.iloc[-1] else -1
            mtf_trend.append(trend_val)
            confluence_display[check_tf] = "🟢 BULL" if trend_val == 1 else "🔴 BEAR"

    # PRIMARY DATA
    data = yf.download(ticker, period="5d", interval=tf, auto_adjust=True, progress=False)
    
    if data is not None and not data.empty:
        if isinstance(data.columns, pd.MultiIndex): data.columns = data.columns.get_level_values(0)
        
        # INDICATORS
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
        
        # --- NEW CONFLUENCE AI SCORE ---
        # 40% based on MTF alignment (All 3 TFs same = 40, 2 same = 20, 0 same = 0)
        tf_match_count = mtf_trend.count(1) if last['Raw'] == 1 else mtf_trend.count(-1)
        mtf_score = (tf_match_count / 3) * 40
        
        # 60% based on Technicals (RSI, ADX, MACD, VWAP)
        tech_score = 0
        if (last['Raw'] == 1 and last['Close'] > last['VWAP']) or (last['Raw'] == -1 and last['Close'] < last['VWAP']): tech_score += 15
        if last['ADX'] > 25: tech_score += 15
        if (last['Raw'] == 1 and last['MACD_H'] > 0) or (last['Raw'] == -1 and last['MACD_H'] < 0): tech_score += 15
        if 30 < last['RSI'] < 70: tech_score += 15
        
        final_conf = int(mtf_score + tech_score)
        status_clr = "#00FF88" if last['Raw'] == 1 else "#FF3366" if last['Raw'] == -1 else "#777"

        # --- TOP GAUGE ---
        m1, m2, m3 = st.columns(3)
        for i, (tf_key, val) in enumerate(confluence_display.items()):
            cols = [m1, m2, m3]
            cols[i].markdown(f'<div class="glass-card"><p style="margin:0; font-size:12px; opacity:0.6;">{tf_key} TREND</p><h3 style="margin:0;">{val}</h3></div>', unsafe_allow_html=True)

        st.markdown(f"""
            <div class="glass-card" style="border-bottom: 4px solid {status_clr};">
                <p style="color:#666; letter-spacing:3px; font-size:10px; margin:0;">CONFLUENCE AI SCORE</p>
                <h1 style="color:{status_clr}; font-size:65px; margin:5px 0;">{final_conf}%</h1>
                <p style="opacity:0.5; font-size:10px;">REFRESHING: 7S | MODE: INSTITUTIONAL MTF</p>
            </div>
        """, unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            if st.button("🚀 EXECUTE BUY", use_container_width=True, key="buy_btn"):
                place_justmarket_trade(choice, 0, lots)
        with c2:
            if st.button("📉 EXECUTE SELL", use_container_width=True, key="sell_btn"):
                place_justmarket_trade(choice, 1, lots)

        # --- CHART ---
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

        # Arrows
        buys = data[data['Entry'] == 1]; sells = data[data['Entry'] == -1]
        fig.add_trace(go.Scatter(x=buys.index, y=buys['Low']*0.999, mode="markers", marker=dict(symbol="triangle-up", size=15, color="#00FF88"), name="BUY"), row=1, col=1)
        fig.add_trace(go.Scatter(x=sells.index, y=sells['High']*1.001, mode="markers", marker=dict(symbol="triangle-down", size=15, color="#FF3366"), name="SELL"), row=1, col=1)

        fig.add_trace(go.Bar(x=data.index, y=data['Volume'], marker_color=['#FFFF00' if s else '#444444' for s in data['Is_Spike']]), row=2, col=1)
        fig.add_trace(go.Bar(x=data.index, y=data['MACD_H'], marker_color=['#00FF88' if v >= 0 else '#FF3366' for v in data['MACD_H']]), row=3, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=data['RSI'], line=dict(color='#C084FC', width=1.5)), row=3, col=1)

        fig.update_layout(height=800, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True, key=f"chart_{choice}_{tf}")

# Run Engine
dashboard_engine()
