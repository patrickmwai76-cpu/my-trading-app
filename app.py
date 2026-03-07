import streamlit as st
import pandas as pd
import pandas_ta as ta
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import MetaTrader5 as mt5
from datetime import datetime

# --- 1. PREMIUM PAGE SETUP ---
st.set_page_config(page_title="PATRO AI PRO V11.6", layout="wide", initial_sidebar_state="collapsed")

# Custom CSS for the "Video Look"
st.markdown("""
    <style>
    .stApp { background-color: #050505; color: white; }
    header, footer, #MainMenu {visibility: hidden;}
    
    /* Glassmorphism Signal Card */
    .signal-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 25px;
        padding: 30px;
        text-align: center;
        box-shadow: 0 15px 35px rgba(0,0,0,0.8);
        margin-bottom: 20px;
    }

    /* Neon Execution Buttons */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #00FF88 0%, #00D1FF 100%);
        color: black !important;
        border: none;
        font-weight: 900;
        height: 3.8em;
        width: 100%;
        border-radius: 15px;
        box-shadow: 0 0 20px rgba(0, 255, 136, 0.35);
    }

    div[data-testid="stButton"] > button[key="sell_btn"] {
        background: linear-gradient(135deg, #FF3366 0%, #FF5E3A 100%) !important;
        color: white !important;
        box-shadow: 0 0 20px rgba(255, 51, 102, 0.35) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. JUSTMARKETS EXECUTION ENGINE ---
def execute_trade(symbol, order_type, lot_size=0.01):
    if not mt5.initialize():
        st.error("MT5 initialization failed. Open JustMarkets MT5 App!")
        return

    # Ensure symbol is correct for JustMarkets
    jm_symbol = "XAUUSD.m" if "GC=F" in symbol else symbol
    
    if not mt5.symbol_select(jm_symbol, True):
        st.error(f"Symbol {jm_symbol} not found in Market Watch!")
        return

    tick = mt5.symbol_info_tick(jm_symbol)
    price = tick.ask if order_type == mt5.ORDER_TYPE_BUY else tick.bid
    
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": jm_symbol,
        "volume": lot_size,
        "type": order_type,
        "price": price,
        "magic": 116,
        "comment": "PATRO V11.6",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        st.error(f"Trade Error: {result.comment}")
    else:
        st.balloons()
        st.success(f"TRADE EXECUTED: {jm_symbol} @ {result.price}")

# --- 3. DATA ENGINE ---
@st.cache_data(ttl=15)
def get_patro_data(ticker, interval):
    try:
        df = yf.download(ticker, period="5d", interval=interval, auto_adjust=True, progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): 
            df.columns = df.columns.get_level_values(0)
        
        df['VWAP'] = ta.vwap(df['High'], df['Low'], df['Close'], df['Volume'])
        df['SMA200'] = ta.sma(df['Close'], length=200)
        df['RSI'] = ta.rsi(df['Close'], length=14)
        macd = ta.macd(df['Close'])
        df['MACD_H'] = macd['MACDh_12_26_9']
        df['ADX'] = ta.adx(df['High'], df['Low'], df['Close'])['ADX_14']
        
        return df.dropna()
    except: return None

# --- 4. SIDEBAR & INPUTS ---
with st.sidebar:
    st.title("🌌 PATRO V11.6")
    asset_dict = {"XAUUSD": "GC=F", "US30": "^DJI", "GBPUSD": "GBPUSD=X"}
    choice = st.selectbox("Market", list(asset_dict.keys()))
    tf = st.radio("Timeframe", ["1m", "5m", "15m"], index=1, horizontal=True)
    lot_size = st.number_input("Trade Lot Size", value=0.01, step=0.01)

# --- 5. SIGNAL PROCESSING (Real Signal Filter) ---
data = get_patro_data(asset_dict[choice], tf)

if data is not None:
    # A. Logic for signals
    data['Raw'] = 0
    data.loc[(data['Close'] > data['VWAP']) & (data['MACD_H'] > 0) & (data['ADX'] > 28), 'Raw'] = 1
    data.loc[(data['Close'] < data['VWAP']) & (data['MACD_H'] < 0) & (data['ADX'] > 28), 'Raw'] = -1
    
    # B. Filter: Trigger only on trend CHANGE (Fixed 'too many signals')
    data['Entry'] = data['Raw'].diff().fillna(0)
    
    last = data.iloc[-1]
    status_clr = "#00FF88" if last['Raw'] == 1 else "#FF3366" if last['Raw'] == -1 else "#555"
    status_txt = "LOCKED BUY" if last['Raw'] == 1 else "LOCKED SELL" if last['Raw'] == -1 else "SCANNING..."

    # --- 6. HEADER UI ---
    st.markdown(f"""
        <div class="signal-card" style="border-top: 5px solid {status_clr};">
            <h1 style="color: {status_clr}; font-size: 50px; margin:0;">{status_txt}</h1>
            <p style="opacity:0.5; letter-spacing:2px;">ADX POWER: {last['ADX']:.1f}% | RSI: {last['RSI']:.0f}</p>
        </div>
    """, unsafe_allow_html=True)

    c_buy, c_sell = st.columns(2)
    with c_buy:
        if st.button("🚀 EXECUTE BUY", use_container_width=True):
            execute_trade(asset_dict[choice], mt5.ORDER_TYPE_BUY, lot_size)
    with c_sell:
        if st.button("📉 EXECUTE SELL", key="sell_btn", use_container_width=True):
            execute_trade(asset_dict[choice], mt5.ORDER_TYPE_SELL, lot_size)

    # --- 7. CHARTING ---
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.7, 0.3])
    fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name="Price"), row=1, col=1)
    
    # Plot ONLY Real Entries
    buys = data[data['Entry'] == 1]
    fig.add_trace(go.Scatter(x=buys.index, y=buys['Low']*0.999, mode="markers+text", text="BUY", textposition="bottom center",
                             marker=dict(symbol="triangle-up", size=15, color="#00FF88", line=dict(width=1, color="white"))), row=1, col=1)
    
    sells = data[data['Entry'] == -1]
    fig.add_trace(go.Scatter(x=sells.index, y=sells['High']*1.001, mode="markers+text", text="SELL", textposition="top center",
                             marker=dict(symbol="triangle-down", size=15, color="#FF3366", line=dict(width=1, color="white"))), row=1, col=1)

    fig.add_trace(go.Scatter(x=data.index, y=data['VWAP'], line=dict(color='orange', width=2), name="VWAP"), row=1, col=1)
    fig.add_trace(go.Scatter(x=data.index, y=data['SMA200'], line=dict(color='white', width=1, dash='dot'), name="SMA 200"), row=1, col=1)
    
    # Momentum Layer
    h_clrs = ['#00FF88' if v >= 0 else '#FF3366' for v in data['MACD_H']]
    fig.add_trace(go.Bar(x=data.index, y=data['MACD_H'], marker_color=h_clrs, name="MACD"), row=2, col=1)
    fig.add_trace(go.Scatter(x=data.index, y=data['RSI'], line=dict(color='#C084FC', width=1), name="RSI"), row=2, col=1)

    fig.update_layout(height=700, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig, use_container_width=True)
