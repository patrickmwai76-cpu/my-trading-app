import streamlit as st
import pandas as pd
import pandas_ta as ta
import yfinance as yf
import plotly.graph_objects as go

# --- 1. CORE CONFIG ---
st.set_page_config(page_title="PATRO AI PRO V11.6.3", layout="wide")
st.markdown("<style>.stApp { background: #050505; color: #00FFCC; }</style>", unsafe_allow_html=True)

# --- 2. THE ENGINE ---
def get_institutional_data(ticker, interval):
    try:
        df = yf.download(ticker, period="2d", interval=interval, progress=False, auto_adjust=True)
        if df.empty: return pd.DataFrame()
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        # 1. Hidden SMC Logic (Fair Value Gaps & Momentum)
        df['RSI'] = ta.rsi(df.Close, length=14)
        macd = ta.macd(df.Close)
        df['MACD'] = macd['MACD_12_26_9']
        df['SIG'] = macd['MACDs_12_26_9']
        
        # 2. Institutional FVG Detection
        df['Prev_High'] = df['High'].shift(2)
        df['Next_Low'] = df['Low']
        df['FVG_Bull'] = (df['Next_Low'] > df['Prev_High']) & (df['Close'].shift(1) > df['Open'].shift(1))
        
        return df
    except: return pd.DataFrame()

@st.fragment(run_every="8s")
def run_bank_commander():
    # Asset Selection
    asset = st.sidebar.selectbox("Select Target", ["GOLD", "GBPUSD", "US30"])
    ticker = {"GOLD":"GC=F", "GBPUSD":"GBPUSD=X", "US30":"^DJI"}[asset]
    
    # Data Stream
    d1, d5, d15 = get_institutional_data(ticker, "1m"), get_institutional_data(ticker, "5m"), get_institutional_data(ticker, "15m")
    if d1.empty: return

    # --- A. INSTITUTIONAL BIAS MATRIX ---
    def check_bank_bias(df):
        r, m, s = df['RSI'].iloc[-1], df['MACD'].iloc[-1], df['SIG'].iloc[-1]
        has_fvg = df['FVG_Bull'].tail(10).any() # Is there an unmitigated FVG?
        if r > 50 and m > s: return "🏦 BANK BUY" if has_fvg else "🟢 RETAIL BUY"
        if r < 50 and m < s: return "📉 BANK SELL"
        return "⚪ NEUTRAL"

    b1, b5, b15 = check_bank_bias(d1), check_bank_bias(d5), check_bank_bias(d15)

    # --- B. UI DASHBOARD ---
    st.sidebar.subheader("🏦 SMART MONEY MATRIX")
    st.sidebar.table(pd.DataFrame([{"TF": "1M", "Bias": b1}, {"TF": "5M", "Bias": b5}, {"TF": "15M", "Bias": b15}]))

    # Signal Logic
    is_strong_buy = "BANK BUY" in b1 and "BANK BUY" in b5 and "BANK BUY" in b15
    score = 99 if is_strong_buy else 50
    color = "#00FFCC" if is_strong_buy else "#FFA500"

    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown(f"<div style='border:2px solid {color}; padding:20px; border-radius:15px; text-align:center;'><h1>{score}%</h1><p>BANK CONFLUENCE</p></div>", unsafe_allow_html=True)
    with c2:
        msg = "🚀 INSTITUTIONAL RALLY" if is_strong_buy else "⌛ HUNTING LIQUIDITY"
        st.markdown(f"<h1 style='color:{color};'>{msg}</h1>", unsafe_allow_html=True)
        st.caption(f"Price: {d1.Close.iloc[-1]:,.2f} | Last Update: {pd.Timestamp.now().strftime('%H:%M:%S')} EAT")

    # --- C. THE CHART (Marking the Hunt) ---
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=d1.index, open=d1.Open, high=d1.High, low=d1.Low, close=d1.Close, name="Price"))
    
    # Mark the Session Low (The Liquidity Hunt Zone)
    session_low = d1.Low.min()
    fig.add_hline(y=session_low, line_dash="dash", line_color="#FF3366", annotation_text="Liquidity Pool (Stops)")
    
    fig.update_layout(height=600, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig, use_container_width=True)

# --- EXECUTE ---
run_bank_commander()
