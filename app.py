import streamlit as st
import pandas as pd
import pandas_ta as ta
import yfinance as yf
import plotly.graph_objects as go

# --- 1. CORE CONFIG ---
st.set_page_config(page_title="PATRO AI PRO V11.6.2", layout="wide")
st.markdown("<style>.stApp { background: #010101; color: #ffffff; }</style>", unsafe_allow_html=True)

# --- 2. PERMANENT UI ---
st.title("🌌 PATRO AI PRO V11.6.2 | ANTI-TRAP EDITION")

with st.sidebar:
    st.header("🏢 INSTITUTIONAL DESK")
    asset_choice = st.selectbox("Market Target", ["GOLD", "GBPUSD", "US30"])
    ticker_map = {"GOLD":"GC=F", "GBPUSD":"GBPUSD=X", "US30":"^DJI"}
    target_ticker = ticker_map[asset_choice]
    
    st.divider()
    mtf_spot = st.empty()  
    vol_spot = st.empty() # New: Institutional Volume Indicator
    sl_spot = st.empty() 

# --- 3. ANALYTICS ENGINE ---
def get_mtf_data(ticker, interval):
    try:
        df = yf.download(ticker, period="2d", interval=interval, progress=False, auto_adjust=True)
        if df.empty: return pd.DataFrame()
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        df['RSI'] = ta.rsi(df.Close, length=14)
        macd = ta.macd(df.Close)
        df['MACD'] = macd['MACD_12_26_9']
        df['SIG'] = macd['MACDs_12_26_9']
        # Volatility Filter
        df['ATR'] = ta.atr(df.High, df.Low, df.Close, length=14)
        return df
    except: return pd.DataFrame()

@st.fragment(run_every="8s")
def run_master_pulse(ticker, label):
    d1, d5, d15 = get_mtf_data(ticker, "1m"), get_mtf_data(ticker, "5m"), get_mtf_data(ticker, "15m")
    if d1.empty: return

    # --- A. ANTI-TRAP BIAS LOGIC ---
    def get_smart_bias(df):
        r, m, s = df['RSI'].iloc[-1], df['MACD'].iloc[-1], df['SIG'].iloc[-1]
        vol_avg = df['Volume'].tail(10).mean()
        curr_vol = df['Volume'].iloc[-1]
        
        # Institutional Confirmation (Volume must be 1.2x average)
        is_bank_move = curr_vol > (vol_avg * 1.2)

        if r > 52 and m > s:
            return "🟢 BUY" if is_bank_move else "⌛ WEAK BUY"
        if r < 48 and m < s:
            return "🔴 SELL" if is_bank_move else "⚪ TRAP (NO VOL)"
        return "⚪ NEUTRAL"

    b1, b5, b15 = get_smart_bias(d1), get_smart_bias(d5), get_smart_bias(d15)

    # --- B. SIDEBAR UPDATES ---
    with mtf_spot.container():
        st.caption(f"ANTI-TRAP MATRIX ({pd.Timestamp.now().strftime('%H:%M:%S')} EAT)")
        st.table(pd.DataFrame([{"TF": "1M", "Power": b1}, {"TF": "5M", "Power": b5}, {"TF": "15M", "Power": b15}]))

    with vol_spot.container():
        vol_ratio = d1['Volume'].iloc[-1] / d1['Volume'].tail(10).mean()
        vol_color = "#00FF88" if vol_ratio > 1.2 else "#FFA500"
        st.markdown(f"**Bank Volume:** <span style='color:{vol_color}'>{vol_ratio:.2f}x</span>", unsafe_allow_html=True)

    # --- C. DASHBOARD SCORING ---
    is_true_sell = (b1 == "🔴 SELL" and b5 == "🔴 SELL")
    is_true_buy = (b1 == "🟢 BUY" and b5 == "🟢 BUY")
    
    score = 98 if is_true_buy else 2 if is_true_sell else 50
    color = "#00FF88" if score > 90 else "#FF3366" if score < 10 else "#FFA500"

    c1, c2, c3 = st.columns([1, 1, 2])
    with c1:
        st.markdown(f"<div style='border:2px solid {color}; padding:10px; border-radius:10px; text-align:center;'><h2>{score}%</h2><p>AI POWER</p></div>", unsafe_allow_html=True)
    with c2:
        st.metric("PRICE", f"{d1.Close.iloc[-1]:,.2f}")
    with c3:
        status = "🚀 INSTITUTIONAL RALLY" if is_true_buy else "📉 BANK DUMP" if is_true_sell else "⚠️ TRAP DETECTED"
        st.markdown(f"<h1 style='color:{color};'>{status}</h1>", unsafe_allow_html=True)

    # --- D. CHART ---
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=d1.index, open=d1.Open, high=d1.High, low=d1.Low, close=d1.Close, name="Price"))
    fig.add_hline(y=d1.Low.min(), line_dash="dash", line_color="#FF3366", annotation_text="Safety Floor")
    fig.update_layout(height=500, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig, use_container_width=True, key=f"pulse_{label}")

run_master_pulse(target_ticker, asset_choice)
