import streamlit as st
import pandas as pd
import pandas_ta as ta
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- 1. PREMIUM INTERFACE ---
st.set_page_config(page_title="PATRO AI PRO V11.6", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .stApp { background-color: #050505; color: white; }
    header, footer, #MainMenu {visibility: hidden;}
    .signal-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 25px; text-align: center; margin-bottom: 20px;
    }
    section[data-testid="stSidebar"] { background-color: #0a0a0a !important; border-right: 1px solid #222; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. THE STABLE ENGINE ---
@st.cache_data(ttl=20)
def get_patro_data(ticker, interval):
    try:
        df = yf.download(ticker, period="5d", interval=interval, auto_adjust=True, progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): 
            df.columns = df.columns.get_level_values(0)
        
        # INDICATORS
        df['VWAP'] = ta.vwap(df['High'], df['Low'], df['Close'], df['Volume'])
        df['SMA200'] = ta.sma(df['Close'], length=200)
        df['ADX'] = ta.adx(df['High'], df['Low'], df['Close'])['ADX_14']
        macd = ta.macd(df['Close'])
        df['MACD_H'] = macd['MACDh_12_26_9']
        df['RSI'] = ta.rsi(df['Close'], length=14)
        
        # TREND & SIGNAL LOGIC
        df['Raw'] = 0
        df.loc[(df['Close'] > df['VWAP']) & (df['MACD_H'] > 0) & (df['ADX'] > 22), 'Raw'] = 1
        df.loc[(df['Close'] < df['VWAP']) & (df['MACD_H'] < 0) & (df['ADX'] > 22), 'Raw'] = -1
        df['Entry'] = df['Raw'].diff().fillna(0)
        return df.dropna()
    except: return None

# --- 3. INSTITUTIONAL SIDEBAR ---
with st.sidebar:
    st.title("🌌 PATRO V11.6")
    st.error("⚠️ **NEWS WATCH**\nCheck for CPI/NFP releases.")
    
    st.divider()
    st.markdown("### 📋 INSTITUTIONAL SOP")
    st.checkbox("Trend Confluence", value=True)
    st.checkbox("VWAP Proximity", value=True)
    st.checkbox("Volume Spike", value=True)
    st.checkbox("Momentum Guard", value=True)
    
    st.divider()
    st.markdown("### 🧮 RISK CALCULATOR")
    balance = st.number_input("Balance ($)", value=1000)
    risk_pct = st.slider("Risk %", 0.5, 5.0, 1.0)
    sl_pips = st.number_input("Stop Loss Pips", value=30)
    
    # JustMarkets Lot Calculation
    lots = (balance * (risk_pct/100)) / (sl_pips * 10) if sl_pips > 0 else 0.01
    st.success(f"Recommended Lot: **{lots:.2f}**")

    st.divider()
    asset_dict = {"XAUUSD": "GC=F", "US30": "^DJI", "GBPUSD": "GBPUSD=X"}
    choice = st.selectbox("Market Asset", list(asset_dict.keys()))
    tf = st.radio("Timeframe", ["1m", "5m", "15m"], index=1, horizontal=True)

# --- 4. MAIN DASHBOARD ---
data = get_patro_data(asset_dict[choice], tf)

if data is not None:
    last = data.iloc[-1]
    
    # POWER & TREND CALCULATION
    trend_state = "BULLISH" if last['Close'] > last['VWAP'] else "BEARISH"
    power_val = last['ADX']
    status_clr = "#00FF88" if last['Raw'] == 1 else "#FF3366" if last['Raw'] == -1 else "#777"
    status_txt = "LOCKED BUY" if last['Raw'] == 1 else "LOCKED SELL" if last['Raw'] == -1 else "SCANNING..."

    # Top Metric Bar
    col1, col2, col3 = st.columns(3)
    col1.metric("TREND", trend_state, delta=None)
    col2.metric("MARKET POWER", f"{power_val:.1f}%", delta="Strong" if power_val > 25 else "Weak")
    col3.metric("RSI", f"{last['RSI']:.0f}")

    st.markdown(f"""
        <div class="signal-card" style="border-top: 5px solid {status_clr};">
            <h1 style="color: {status_clr}; font-size: 50px; margin: 0; font-weight: 800;">{status_txt}</h1>
            <p style="opacity:0.5; letter-spacing:3px;">JUSTMARKETS {choice}.m | V11.6 PRO ENGINE</p>
        </div>
    """, unsafe_allow_html=True)

    # Charting (Candles + VWAP + SMA)
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.7, 0.3])
    fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name="Price"), row=1, col=1)
    
    # Entry Markers
    buys = data[data['Entry'] == 1]; sells = data[data['Entry'] == -1]
    fig.add_trace(go.Scatter(x=buys.index, y=buys['Low']*0.999, mode="markers+text", text="BUY", textposition="bottom center", marker=dict(symbol="triangle-up", size=15, color="#00FF88")), row=1, col=1)
    fig.add_trace(go.Scatter(x=sells.index, y=sells['High']*1.001, mode="markers+text", text="SELL", textposition="top center", marker=dict(symbol="triangle-down", size=15, color="#FF3366")), row=1, col=1)

    fig.add_trace(go.Scatter(x=data.index, y=data['VWAP'], line=dict(color='orange', width=2), name="VWAP"), row=1, col=1)
    fig.add_trace(go.Scatter(x=data.index, y=data['SMA200'], line=dict(color='white', width=1, dash='dot'), name="SMA 200"), row=1, col=1)
    
    # MACD Histogram
    h_clrs = ['#00FF88' if v >= 0 else '#FF3366' for v in data['MACD_H']]
    fig.add_trace(go.Bar(x=data.index, y=data['MACD_H'], marker_color=h_clrs, name="MACD"), row=2, col=1)

    fig.update_layout(height=800, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig, use_container_width=True)
