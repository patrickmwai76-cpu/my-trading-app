import streamlit as st
import pandas as pd
import pandas_ta as ta
import yfinance as yf
import plotly.graph_objects as go

# --- 1. CORE CONFIG ---
st.set_page_config(page_title="PATRO AI PRO V11.6.3", layout="wide")
st.markdown("<style>.stApp { background: #010101; color: #00FFCC; }</style>", unsafe_allow_html=True)

# --- 2. SIDEBAR (OUTSIDE FRAGMENT TO PREVENT ERRORS) ---
with st.sidebar:
    st.header("🏢 COMMAND CENTER")
    # Placing widgets here prevents the 'WidgetsNotAllowedOutsideError'
    asset_choice = st.selectbox("Market Target", ["GOLD", "GBPUSD", "US30"])
    ticker_map = {"GOLD":"GC=F", "GBPUSD":"GBPUSD=X", "US30":"^DJI"}
    target_ticker = ticker_map[asset_choice]
    
    st.divider()
    # Placeholders for fragment to update
    matrix_spot = st.empty()
    sl_spot = st.empty()

# --- 3. ANALYTICS ENGINE ---
def get_market_data(ticker, interval):
    try:
        df = yf.download(ticker, period="2d", interval=interval, progress=False, auto_adjust=True)
        if df.empty: return pd.DataFrame()
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        df['RSI'] = ta.rsi(df.Close, length=14)
        macd = ta.macd(df.Close)
        df['MACD'] = macd['MACD_12_26_9']
        df['SIG'] = macd['MACDs_12_26_9']
        return df
    except: return pd.DataFrame()

# --- 4. THE PULSE (8-SECOND LOOP) ---
@st.fragment(run_every="8s")
def start_pulse(ticker, label):
    # Fetch Data
    d1, d5, d15 = get_market_data(ticker, "1m"), get_market_data(ticker, "5m"), get_market_data(ticker, "15m")
    if d1.empty: return

    # A. Bias Logic
    def get_bias(df):
        r, m, s = df['RSI'].iloc[-1], df['MACD'].iloc[-1], df['SIG'].iloc[-1]
        if r > 50 and m > s: return "🟢 BULL"
        if r < 50 and m < s: return "🔴 BEAR"
        return "⚪ NEUTRAL"

    b1, b5, b15 = get_bias(d1), get_bias(d5), get_bias(d15)
    current_price = d1.Close.iloc[-1]
    session_low = d1.Low.min()

    # B. Push Updates to Sidebar
    with matrix_spot.container():
        st.caption(f"MTF MATRIX ({pd.Timestamp.now().strftime('%H:%M:%S')})")
        st.table(pd.DataFrame([{"TF": "1M", "Bias": b1}, {"TF": "5M", "Bias": b5}, {"TF": "15M", "Bias": b15}]))
    
    with sl_spot.container():
        st.error(f"HARD-LOCK SL: {session_low:,.2f}")

    # C. Main Display
    is_strong = (b1 == b5 == b15 == "🟢 BULL")
    color = "#00FFCC" if is_strong else "#FFA500"
    
    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown(f"<div style='border:2px solid {color}; padding:20px; border-radius:10px; text-align:center;'><h2>{98 if is_strong else 50}%</h2><p>CONFIDENCE</p></div>", unsafe_allow_html=True)
    with c2:
        msg = "🚀 STRONG RALLY" if is_strong else "⌛ ACCUMULATING"
        st.markdown(f"<h1 style='color:{color};'>{msg}</h1>", unsafe_allow_html=True)

    # D. Institutional Chart
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=d1.index, open=d1.Open, high=d1.High, low=d1.Low, close=d1.Close, name="Price"))
    fig.add_hline(y=session_low, line_dash="dash", line_color="#FF3366", annotation_text="Liquidity Floor")
    fig.update_layout(height=500, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig, use_container_width=True)

# --- 5. EXECUTION ---
start_pulse(target_ticker, asset_choice)
