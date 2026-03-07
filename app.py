import streamlit as st
import pandas as pd
import pandas_ta as ta
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- 1. BRANDED UI SETUP ---
st.set_page_config(page_title="PATRO AI PRO", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for Neon Branding
st.markdown("""
    <style>
    .stApp { background-color: #050505; }
    
    /* Header Logo Style */
    .main-header {
        background: linear-gradient(90deg, #00C9FF 0%, #92FE9D 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 50px;
        font-weight: 900;
        text-align: center;
        margin-bottom: -10px;
        letter-spacing: -2px;
    }
    .sub-header {
        text-align: center;
        color: #555;
        font-size: 14px;
        letter-spacing: 5px;
        margin-bottom: 30px;
    }
    
    /* Sidebar Glassmorphism */
    section[data-testid="stSidebar"] {
        background-color: rgba(10, 10, 10, 0.95) !important;
        border-right: 1px solid #222;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. HEADER LOGO ---
st.markdown('<p class="main-header">PATRO AI PRO</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">ALGORITHMIC TRADING SYSTEMS</p>', unsafe_allow_html=True)

# --- 3. THE STABLE ENGINE ---
@st.cache_data(ttl=20)
def get_market_data(ticker, interval):
    try:
        df = yf.download(ticker, period="5d", interval=interval, auto_adjust=True, progress=False)
        if isinstance(df.columns, pd.MultiIndex): 
            df.columns = df.columns.get_level_values(0)
        
        # INDICATORS
        df['VWAP'] = ta.vwap(df['High'], df['Low'], df['Close'], df['Volume'])
        df['SMA200'] = ta.sma(df['Close'], length=200)
        df['RSI'] = ta.rsi(df['Close'], length=14)
        
        # MOMENTUM SIGNALS
        macd = ta.macd(df['Close'])
        df['MACD_H'] = macd['MACDh_12_26_9']
        df['Signal'] = 0
        df.loc[(df['Close'] > df['VWAP']) & (df['MACD_H'] > 0), 'Signal'] = 1
        df.loc[(df['Close'] < df['VWAP']) & (df['MACD_H'] < 0), 'Signal'] = -1
        df['Entry'] = df['Signal'].diff().fillna(0)
        
        return df.dropna()
    except: return None

# --- 4. THE SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2586/2586117.png", width=80) # Modern AI Icon
    st.markdown("### 🛠️ DASHBOARD CONTROLS")
    asset = st.selectbox("Select Pair", ["GC=F", "^DJI", "EURUSD=X"], format_func=lambda x: "GOLD (XAUUSD)" if x=="GC=F" else x)
    tf = st.radio("Timeframe", ["1m", "5m", "15m"], index=1, horizontal=True)
    
    st.divider()
    st.markdown("### 📊 RISK MANAGER")
    bal = st.number_input("Balance", value=1000)
    sl = st.number_input("SL Pips", value=30)
    risk = st.slider("Risk %", 0.5, 3.0, 1.0)
    lot = (bal * (risk/100)) / (sl * 10) if sl > 0 else 0.01
    st.info(f"Recommended Lot: **{lot:.2f}**")

# --- 5. MAIN CHART ---
data = get_market_data(asset, tf)

if data is not None:
    last = data.iloc[-1]
    clr = "#00FF88" if last['Signal'] == 1 else "#FF3366" if last['Signal'] == -1 else "#777"
    
    # Live Signal Banner
    st.markdown(f"""
        <div style="background: {clr}22; border: 1px solid {clr}; padding: 20px; border-radius: 15px; text-align: center;">
            <h2 style="color: {clr}; margin: 0;">{"BUY CONFIRMED" if last['Signal']==1 else "SELL CONFIRMED" if last['Signal']==-1 else "NEUTRAL"}</h2>
        </div>
    """, unsafe_allow_html=True)

    # Candlestick Chart
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name="Price"))
    fig.add_trace(go.Scatter(x=data.index, y=data['VWAP'], line=dict(color='orange', width=2), name="VWAP"))
    
    # Entry Markers
    buys = data[data['Entry'] == 1]; sells = data[data['Entry'] == -1]
    fig.add_trace(go.Scatter(x=buys.index, y=buys['Low']*0.999, mode="markers", marker=dict(symbol="triangle-up", size=15, color="#00FF88"), name="Buy"))
    fig.add_trace(go.Scatter(x=sells.index, y=sells['High']*1.001, mode="markers", marker=dict(symbol="triangle-down", size=15, color="#FF3366"), name="Sell"))

    fig.update_layout(height=600, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig, use_container_width=True)
