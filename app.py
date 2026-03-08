import streamlit as st
import pandas as pd
import pandas_ta as ta
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import logging

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

# --- 3. SILENT JUSTMARKETS EXECUTION ENGINE ---
def place_justmarket_trade(symbol, order_type, volume=0.01):
    if not MT5_AVAILABLE:
        st.warning("⚠️ Execution requires running locally on Windows with MetaTrader 5 installed.")
        return

    if not mt5.initialize():
        return
    
    # JustMarkets Symbol Fix (.m suffix)
    symbol_name = "XAUUSD.m" if "GC=F" in symbol else f"{symbol}.m"
    
    mt5.symbol_select(symbol_name, True)
    tick = mt5.symbol_info_tick(symbol_name)
    if tick is None: return
    
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol_name,
        "volume": volume,
        "type": order_type,
        "price": tick.ask if order_type == mt5.ORDER_TYPE_BUY else tick.bid,
        "magic": 1162026,
        "comment": "PATRO AI V11.6 EXEC",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    
    result = mt5.order_send(request)
    if result.retcode == mt5.TRADE_RETCODE_DONE:
        st.balloons()

# --- 4. DATA ENGINE (Stable Original Logic) ---
@st.cache_data(ttl=20)
def get_patro_data(ticker, interval):
    try:
        df = yf.download(ticker, period="5d", interval=interval, auto_adjust=True, progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): 
            df.columns = df.columns.get_level_values(0)
        
        df['VWAP'] = ta.vwap(df['High'], df['Low'], df['Close'], df['Volume'])
        df['SMA200'] = ta.sma(df['Close'], length=200)
        df['ADX'] = ta.adx(df['High'], df['Low'], df['Close'])['ADX_14']
        macd = ta.macd(df['Close'])
        df['MACD_H'] = macd['MACDh_12_26_9']
        df['RSI'] = ta.rsi(df['Close'], length=14)
        
        # Original Spike Logic
        df['Vol_Avg'] = df['Volume'].rolling(window=20).mean()
        df['Is_Spike'] = df['Volume'] > (df['Vol_Avg'] * 2.5)
        
        # Signal Generation
        df['Raw'] = 0
        df.loc[(df['Close'] > df['VWAP']) & (df['MACD_H'] > 0) & (df['ADX'] > 22), 'Raw'] = 1
        df.loc[(df['Close'] < df['VWAP']) & (df['MACD_H'] < 0) & (df['ADX'] > 22), 'Raw'] = -1
        df['Entry'] = df['Raw'].diff().fillna(0)
        return df.dropna()
    except: return None

# --- 5. INSTITUTIONAL SIDEBAR ---
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
    st.success(f"Recommended Lot: **{lots:.2f}**")

    st.divider()
    asset_dict = {"XAUUSD": "GC=F", "US30": "^DJI", "GBPUSD": "GBPUSD=X"}
    choice = st.selectbox("Market Asset", list(asset_dict.keys()))
    tf = st.radio("Timeframe", ["1m", "5m", "15m"], index=1, horizontal=True)

# --- 6. MAIN DASHBOARD ---
data = get_patro_data(asset_dict[choice], tf)

if data is not None:
    last = data.iloc[-1]
    
    # AI CONFIDENCE CALCULATION
    conf_score = 0
    if last['Close'] > last['VWAP']: conf_score += 25
    if last['MACD_H'] > 0: conf_score += 25
    if last['ADX'] > 25: conf_score += 25
    if 40 < last['RSI'] < 70: conf_score += 25
    
    status_clr = "#00FF88" if last['Raw'] == 1 else "#FF3366" if last['Raw'] == -1 else "#777"
    
    # Glassmorphism Confidence Header
    st.markdown(f"""
        <div class="glass-card" style="border-bottom: 4px solid {status_clr};">
            <p style="color:#666; letter-spacing:3px; font-size:10px; margin:0;">AI ANALYSIS CONFIDENCE</p>
            <h1 style="color:{status_clr}; font-size:60px; margin:5px 0;">{conf_score}%</h1>
            <p style="opacity:0.5; letter-spacing:2px;">JUSTMARKETS {choice}.m | V11.6 PRO ENGINE</p>
        </div>
    """, unsafe_allow_html=True)

    # EXECUTION BUTTONS
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🚀 EXECUTE BUY", use_container_width=True):
            place_justmarket_trade(choice, mt5.ORDER_TYPE_BUY, lots)
    with c2:
        if st.button("📉 EXECUTE SELL", use_container_width=True):
            place_justmarket_trade(choice, mt5.ORDER_TYPE_SELL, lots)

    # CHARTING (Preserved Original Visuals)
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.02, row_heights=[0.5, 0.15, 0.35])
    
    # ROW 1: Price + Indicators
    fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name="Price"), row=1, col=1)
    fig.add_trace(go.Scatter(x=data.index, y=data['VWAP'], line=dict(color='orange', width=2), name="VWAP"), row=1, col=1)
    fig.add_trace(go.Scatter(x=data.index, y=data['SMA200'], line=dict(color='white', width=1, dash='dot'), name="SMA 200"), row=1, col=1)
    
    # Asia Zones
    asia = data.between_time('03:00', '09:00')
    if not asia.empty:
        ah, al = asia['High'].max(), asia['Low'].min()
        fig.add_hline(y=ah, line_dash="dot", line_color="cyan", annotation_text="ASIA H", row=1, col=1)
        fig.add_hline(y=al, line_dash="dot", line_color="magenta", annotation_text="ASIA L", row=1, col=1)

    # Entry Arrows
    buys = data[data['Entry'] == 1]; sells = data[data['Entry'] == -1]
    fig.add_trace(go.Scatter(x=buys.index, y=buys['Low']*0.999, mode="markers+text", text="BUY", marker=dict(symbol="triangle-up", size=15, color="#00FF88")), row=1, col=1)
    fig.add_trace(go.Scatter(x=sells.index, y=sells['High']*1.001, mode="markers+text", text="SELL", marker=dict(symbol="triangle-down", size=15, color="#FF3366")), row=1, col=1)

    # ROW 2: Volume Spikes
    v_colors = ['#FFFF00' if spike else '#444444' for spike in data['Is_Spike']]
    fig.add_trace(go.Bar(x=data.index, y=data['Volume'], marker_color=v_colors, name="Volume"), row=2, col=1)
    
    # ROW 3: MACD & RSI
    h_clrs = ['#00FF88' if v >= 0 else '#FF3366' for v in data['MACD_H']]
    fig.add_trace(go.Bar(x=data.index, y=data['MACD_H'], marker_color=h_clrs, name="MACD"), row=3, col=1)
    fig.add_trace(go.Scatter(x=data.index, y=data['RSI'], line=dict(color='#C084FC', width=1.5), name="RSI Overlay"), row=3, col=1)

    fig.update_layout(height=850, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig, use_container_width=True)
