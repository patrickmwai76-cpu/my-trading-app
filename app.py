import streamlit as st
import pandas as pd
import pandas_ta as ta
import yfinance as yf
import plotly.graph_objects as go

# --- 1. CORE CONFIG ---
st.set_page_config(page_title="PATRO AI PRO V11.7.0", layout="wide")
st.markdown("<style>.stApp { background: #010101; color: #ffffff; }</style>", unsafe_allow_html=True)

# --- 2. PERMANENT UI ---
st.title("🌌 PATRO AI PRO V11.7.0 | INSTITUTIONAL SMC")

with st.sidebar:
    st.header("🏢 INSTITUTIONAL DESK")
    asset_choice = st.selectbox("Market Target", ["GOLD", "GBPUSD", "US30"])
    # Adjusted Tickers for 2026 feeds
    ticker_map = {"GOLD":"GC=F", "GBPUSD":"GBPUSD=X", "US30":"^DJI"}
    target_ticker = ticker_map[asset_choice]
    
    st.divider()
    mtf_spot = st.empty()  
    vol_spot = st.empty() 
    st.info("SMC Mode: Active (BOS + 1.5x Vol)")

# --- 3. ANALYTICS ENGINE ---
def get_mtf_data(ticker, interval):
    try:
        # Fetching enough data for 20-period lookback
        df = yf.download(ticker, period="3d", interval=interval, progress=False, auto_adjust=True)
        if df.empty: return pd.DataFrame()
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        # Core Indicators
        df['RSI'] = ta.rsi(df.Close, length=14)
        macd = ta.macd(df.Close)
        df['MACD'] = macd['MACD_12_26_9']
        df['SIG'] = macd['MACDs_12_26_9']
        df['ATR'] = ta.atr(df.High, df.Low, df.Close, length=14)
        return df
    except: return pd.DataFrame()

def get_institutional_signal(df):
    if len(df) < 30: return "⌛ SCANNING", "#888888"
    
    # A. Institutional Volume Filter (1.5x Threshold)
    vol_avg = df['Volume'].tail(20).mean()
    curr_vol = df['Volume'].iloc[-1]
    is_bank_vol = curr_vol > (vol_avg * 1.5)

    # B. Break of Structure (BOS) 
    prev_high = df['High'].iloc[-21:-1].max()
    prev_low = df['Low'].iloc[-21:-1].min()
    curr_close = df['Close'].iloc[-1]
    
    # C. Body Momentum (Must be 60% of candle)
    candle_range = df['High'].iloc[-1] - df['Low'].iloc[-1]
    body_size = abs(df['Close'].iloc[-1] - df['Open'].iloc[-1])
    is_strong_move = (body_size / candle_range) > 0.6 if candle_range != 0 else False

    # D. BIAS CHECK
    r, m, s = df['RSI'].iloc[-1], df['MACD'].iloc[-1], df['SIG'].iloc[-1]

    if curr_close > prev_high and is_bank_vol and is_strong_move and r > 50:
        return "🏦 BANK BUY (SURE)", "#00FF88"
    
    if curr_close < prev_low and is_bank_vol and is_strong_move and r < 50:
        return "🏦 BANK SELL (SURE)", "#FF3366"

    return "⌛ RETAIL NOISE (WAIT)", "#FFA500"

@st.fragment(run_every="8s")
def run_master_pulse(ticker, label):
    # Fetching 1m for precision and 5m for confirmation
    d1, d5 = get_mtf_data(ticker, "1m"), get_mtf_data(ticker, "5m")
    if d1.empty: return

    signal_text, signal_color = get_institutional_signal(d1)

    # --- SIDEBAR UPDATES ---
    with vol_spot.container():
        vol_ratio = d1['Volume'].iloc[-1] / d1['Volume'].tail(10).mean()
        st.write(f"**Institutional Power:** {vol_ratio:.2f}x")

    # --- MAIN DASHBOARD ---
    c1, c2, c3 = st.columns([1.5, 1, 1.5])
    with c1:
        st.markdown(f"""
            <div style='border:3px solid {signal_color}; padding:15px; border-radius:15px; text-align:center; background:#111;'>
                <h2 style='color:{signal_color}; margin:0;'>{signal_text}</h2>
                <p style='margin:0; opacity:0.6;'>MTF CONFIRMATION: {label}</p>
            </div>
            """, unsafe_allow_html=True)
    with c2:
        st.metric("CURRENT PRICE", f"{d1.Close.iloc[-1]:,.2f}")
    with c3:
        trend = "BULLISH" if d5.Close.iloc[-1] > d5.Close.iloc[-10] else "BEARISH"
        st.markdown(f"### Trend Bias: {trend}")

    # --- CHART WITH ANNOTATIONS ---
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=d1.index, open=d1.Open, high=d1.High, low=d1.Low, close=d1.Close, name="Price"))
    
    # Logic to only place the "SURE" label if it triggers
    if "BANK" in signal_text:
        fig.add_annotation(
            x=d1.index[-1], y=d1['High'].iloc[-1],
            text=f"<b>{signal_text}</b>",
            showarrow=True, arrowhead=2, arrowcolor=signal_color,
            font=dict(size=16, color="white"),
            bgcolor=signal_color, borderpad=4
        )

    fig.update_layout(height=600, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig, use_container_width=True, key=f"pulse_{label}")

run_master_pulse(target_ticker, asset_choice)
