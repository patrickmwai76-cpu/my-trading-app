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

# --- 2. PREMIUM INTERFACE SETUP (Video Look) ---
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

# --- 3. JUSTMARKETS EXECUTION ENGINE ---
def place_justmarket_trade(symbol, order_type, volume=0.01):
    if not MT5_AVAILABLE:
        st.warning("⚠️ Local Windows MT5 required.")
        return
    if not mt5.initialize(): return
    
    # Force JustMarkets Suffix
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

# --- 4. DATA ENGINE (Your original logic + Optimizations) ---
@st.cache_data(ttl=15)
def get_patro_data(ticker, interval):
    try:
        df = yf.download(ticker, period="5d", interval=interval, auto_adjust=True, progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        df['VWAP'] = ta.vwap(df['High'], df['Low'], df['Close'], df['Volume'])
        df['SMA200'] = ta.sma(df['Close'], length=200)
        df['RSI'] = ta.rsi(df['Close'], length=14)
        macd = ta.macd(df['Close'])
        df['MACD_H'] = macd['MACDh_12_26_9']
        df['ADX'] = ta.adx(df['High'], df['Low'], df['Close'])['ADX_14']
        df['Vol_Avg'] = df['Volume'].rolling(window=20).mean()
        df['Is_Spike'] = df['Volume'] > (df['Vol_Avg'] * 2.5)
        return df.dropna()
    except: return None

# --- 5. SIDEBAR: RESTORED SOP, NEWS & RISK ---
with st.sidebar:
    st.title("🌌 PATRO V11.6")
    st.error("⚠️ **HIGH IMPACT NEWS**\nUS NFP / CPI Data - Impact: 🔴")
    
    st.divider()
    st.markdown("### 📋 INSTITUTIONAL SOP")
    sop_mtf = st.checkbox("Trend Matrix Confluence", value=True)
    sop_vwap = st.checkbox("Price Action near VWAP", value=True)
    sop_vol = st.checkbox("Volume Confirmation", value=True)
    sop_mom = st.checkbox("Momentum Guard (MACD/RSI)", value=True)
    
    st.divider()
    st.markdown("### 🧮 RISK CALCULATOR")
    balance = st.number_input("Account Balance ($)", value=1000)
    risk_pct = st.slider("Risk Per Trade %", 0.5, 5.0, 1.0)
    stop_pips = st.number_input("Stop Loss (Pips)", value=30)
    lots = max((balance * (risk_pct / 100)) / (stop_pips * 10), 0.01) if stop_pips > 0 else 0.01
    st.success(f"Recommended Lot: **{lots:.2f}**")

    st.divider()
    asset_dict = {"XAUUSD": "GC=F", "US30": "^DJI", "GBPUSD": "GBPUSD=X"}
    choice = st.selectbox("Market", list(asset_dict.keys()))
    tf = st.radio("Timeframe", ["1m", "5m", "15m"], horizontal=True, index=1)

# --- 6. LIVE DASHBOARD ENGINE ---
df1, df5, df15 = get_patro_data(asset_dict[choice], "1m"), get_patro_data(asset_dict[choice], "5m"), get_patro_data(asset_dict[choice], "15m")
active_df = {"1m": df1, "5m": df5, "15m": df15}[tf]

if active_df is not None:
    last = active_df.iloc[-1]
    
    # --- CONFLUENCE AI SCORE LOGIC ---
    # MTF Score (40%)
    bias_1m = 1 if df1.iloc[-1]['Close'] > df1.iloc[-1]['VWAP'] else -1
    bias_5m = 1 if df5.iloc[-1]['Close'] > df5.iloc[-1]['VWAP'] else -1
    bias_15m = 1 if df15.iloc[-1]['Close'] > df15.iloc[-1]['VWAP'] else -1
    mtf_trends = [bias_1m, bias_5m, bias_15m]
    
    # Calculate Final Bias & Score
    current_bias = 1 if last['Close'] > last['VWAP'] and last['MACD_H'] > 0 else -1 if last['Close'] < last['VWAP'] and last['MACD_H'] < 0 else 0
    match_count = mtf_trends.count(current_bias) if current_bias != 0 else 0
    
    final_conf = int(((match_count / 3) * 40) + 60 if current_bias != 0 else 0)
    status_clr = "#00FF88" if current_bias == 1 else "#FF3366" if current_bias == -1 else "#777"
    signal_text = "🚀 BUY" if current_bias == 1 else "📉 SELL" if current_bias == -1 else "SCANNING..."

    # --- TOP HEADER: AI SCORE & SIGNAL ---
    st.markdown(f"""
        <div class="glass-card" style="border-bottom: 4px solid {status_clr};">
            <p style="color:#666; letter-spacing:3px; font-size:10px; margin:0;">PATRO AI CONFLUENCE SCORE</p>
            <h1 style="color:{status_clr}; font-size:65px; margin:5px 0;">{final_conf}%</h1>
            <h2 style="color:{status_clr}; margin:0; letter-spacing:2px;">{signal_text}</h2>
        </div>
    """, unsafe_allow_html=True)

    # EXECUTION BUTTONS
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🚀 EXECUTE BUY", key="buy_btn"):
            place_justmarket_trade(choice, 0, lots)
    with c2:
        if st.button("📉 EXECUTE SELL", key="sell_btn"):
            place_justmarket_trade(choice, 1, lots)

    # --- CHARTING ---
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.02, row_heights=[0.5, 0.1, 0.4])
    fig.add_trace(go.Candlestick(x=active_df.index, open=active_df['Open'], high=active_df['High'], low=active_df['Low'], close=active_df['Close'], name="Price"), row=1, col=1)
    fig.add_trace(go.Scatter(x=active_df.index, y=active_df['VWAP'], line=dict(color='orange', width=2), name="VWAP"), row=1, col=1)
    fig.add_trace(go.Scatter(x=active_df.index, y=active_df['SMA200'], line=dict(color='white', width=1.5, dash='dot'), name="SMA 200"), row=1, col=1)
    
    # Asia Zones
    asia = active_df.between_time('03:00', '09:00')
    if not asia.empty:
        fig.add_hline(y=asia['High'].max(), line_dash="dot", line_color="cyan", row=1, col=1)
        fig.add_hline(y=asia['Low'].min(), line_dash="dot", line_color="magenta", row=1, col=1)

    fig.add_trace(go.Bar(x=active_df.index, y=active_df['Volume'], marker_color=['#FFFF00' if s else '#333' for s in active_df['Is_Spike']]), row=2, col=1)
    fig.add_trace(go.Bar(x=active_df.index, y=active_df['MACD_H'], marker_color=['#00FF88' if v >= 0 else '#FF3366' for v in active_df['MACD_H']]), row=3, col=1)
    fig.add_trace(go.Scatter(x=active_df.index, y=active_df['RSI'], line=dict(color='#C084FC', width=1.5)), row=3, col=1)

    fig.update_layout(height=800, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig, use_container_width=True)
