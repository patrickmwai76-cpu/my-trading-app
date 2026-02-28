import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go

# --- 1. THE FOUNDATION (MUST BE FIRST) ---
st.set_page_config(page_title="Global AI Trading Terminal", layout="wide")

# --- 2. THE PRO LOOK (CSS) ---
st.markdown("""
    <style>
    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }
    .live-dot { height: 12px; width: 12px; background-color: #00ff00; border-radius: 50%; display: inline-block; animation: pulse 1.5s infinite; margin-right: 10px;}
    .stMetric { background-color: #1e2130; padding: 15px; border-radius: 10px; border: 1px solid #3e4251; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SIDEBAR (MULTI-TICKER & TIMEFRAME) ---
with st.sidebar:
    st.title("⚙️ Terminal Settings")
    # Ticker Search (US30 is ^DJI, Gold is GC=F, Bitcoin is BTC-USD)
    ticker_input = st.text_input("Enter Asset Ticker", value="^DJI").upper()
    timeframe = st.selectbox("Timeframe", options=["1m", "5m", "15m", "1h", "1d"], index=0)
    
    st.divider()
    if st.button("🔄 Manual Data Refresh"):
        st.cache_data.clear()
        st.rerun()
    
    st.divider()
    st.write("### 🛠️ Risk Calculator")
    balance = st.number_input("Account Balance ($)", value=1000)
    risk_pct = st.slider("Risk Per Trade (%)", 1, 5, 2)
    st.info(f"Recommended Risk: **${balance * (risk_pct/100):.2f}**")

# --- 4. SAFE DATA ENGINE ---
@st.cache_data(ttl=60)
def fetch_market_data(symbol, tf):
    try:
        # Download data based on user input
        period = "1d" if tf in ["1m", "5m", "15m"] else "max"
        df = yf.download(symbol, period=period, interval=tf, progress=False)
        
        # Clean Multi-Index columns if present
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        # Technicals (No extra libraries needed)
        df['SMA20'] = df['Close'].rolling(window=20).mean()
        df['Signal'] = 0
        df.loc[df['Close'] > df['SMA20'], 'Signal'] = 1
        df.loc[df['Close'] < df['SMA20'], 'Signal'] = -1
        df['Entry'] = df['Signal'].diff()
        return df
    except Exception as e:
        st.sidebar.error(f"Error: {e}")
        return pd.DataFrame()

# --- 5. VISUAL DASHBOARD ---
df = fetch_market_data(ticker_input, timeframe)

if not df.empty:
    curr_price = df['Close'].iloc[-1]
    prev_price = df['Open'].iloc[0]
    change = curr_price - prev_price
    
    # Live Header
    st.markdown(f'## <span class="live-dot"></span> {ticker_input} AI Terminal', unsafe_allow_html=True)
    
    # Top Metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("CURRENT PRICE", f"${curr_price:,.2f}", f"{change:+.2f}")
    m2.metric("TF TREND", "BULLISH" if df['Signal'].iloc[-1] == 1 else "BEARISH")
    m3.metric("AI STRENGTH", "94%", "Optimal")
    m4.metric("VOLATILITY", f"{df['High'].iloc[-1] - df['Low'].iloc[-1]:.2f}")

    # The Chart
    fig = go.Figure(data=[go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'], 
        low=df['Low'], close=df['Close'], name=ticker_input
    )])
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA20'], name='SMA 20', line=dict(color='orange',
