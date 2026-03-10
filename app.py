import streamlit as st
import pandas as pd
import pandas_ta as ta
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime

# --- 1. CORE CONFIG ---
st.set_page_config(page_title="PATRO AI PRO V11.8.0", layout="wide")
st.markdown("<style>.stApp { background: #010101; color: #ffffff; }</style>", unsafe_allow_html=True)

# --- 2. UI HEADER ---
st.title("🌌 PATRO AI PRO V11.8.0 | SMC + ORDER BLOCKS")

with st.sidebar:
    st.header("🏢 INSTITUTIONAL DESK")
    asset_choice = st.selectbox("Market Target", ["GOLD", "GBPUSD", "US30"])
    ticker_map = {"GOLD":"GC=F", "GBPUSD":"GBPUSD=X", "US30":"^DJI"}
    target_ticker = ticker_map[asset_choice]
    
    st.divider()
    vol_spot = st.empty() 
    st.info("SMC Mode: Active (BOS + OB Detection)")

# --- 3. THE SMC ENGINE ---
def get_market_data(ticker):
    try:
        df = yf.download(ticker, period="5d", interval="5m", progress=False, auto_adjust=True)
        if df.empty: return pd.DataFrame()
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        # A. Basic Indicators (RSI & VWAP)
        df['RSI'] = ta.rsi(df.Close, length=14)
        df['VWAP'] = ta.vwap(df.High, df.Low, df.Close, df.Volume)
        
        # B. Order Block Detection Logic
        df['OB_Buy'] = False
        df['OB_Sell'] = False
        
        for i in range(2, len(df)):
            # Bullish OB: Last down candle before a massive move up (Displacement)
            if df['Close'].iloc[i] > df['High'].iloc[i-1] and df['Close'].iloc[i-1] < df['Open'].iloc[i-1]:
                if (df['Close'].iloc[i] - df['Open'].iloc[i]) > (df['ATR'] if 'ATR' in df else 0.5):
                    df.at[df.index[i-1], 'OB_Buy'] = True
            
            # Bearish OB: Last up candle before a massive move down
            if df['Close'].iloc[i] < df['Low'].iloc[i-1] and df['Close'].iloc[i-1] > df['Open'].iloc[i-1]:
                df.at[df.index[i-1], 'OB_Sell'] = True
                
        return df
    except: return pd.DataFrame()

def get_signal(df):
    if len(df) < 10: return "⌛ SCANNING", "#888888"
    
    curr_close = df['Close'].iloc[-1]
    curr_vwap = df['VWAP'].iloc[-1]
    curr_rsi = df['RSI'].iloc[-1]
    vol_avg = df['Volume'].tail(20).mean()
    is_bank_vol = df['Volume'].iloc[-1] > (vol_avg * 1.5)

    # SMC Signal Logic
    if curr_close > curr_vwap and curr_rsi > 55 and is_bank_vol:
        return "🏦 BANK BUY (SURE)", "#00FF88"
    if curr_close < curr_vwap and curr_rsi < 45 and is_bank_vol:
        return "🏦 BANK SELL (SURE)", "#FF3366"
    
    return "⌛ RETAIL NOISE (WAIT)", "#FFA500"

# --- 4. LIVE DASHBOARD ---
@st.fragment(run_every="10s")
def render_dashboard(ticker, label):
    df = get_market_data(ticker)
    if df.empty: 
        st.error("Waiting for Market Feed...")
        return

    sig_text, sig_col = get_signal(df)
    
    # Header Metrics
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        st.markdown(f"<div style='border:2px solid {sig_col}; padding:10px; border-radius:10px; background:#111; text-align:center;'><h2 style='color:{sig_col};'>{sig_text}</h2></div>", unsafe_allow_html=True)
    with c2:
        st.metric("PRICE", f"{df.Close.iloc[-1]:,.2f}")
    with c3:
        st.metric("RSI", f"{df.RSI.iloc[-1]:.2f}")

    # --- THE CHART ---
    fig = go.Figure()
    
    # 1. Candlesticks
    fig.add_trace(go.Candlestick(x=df.index, open=df.Open, high=df.High, low=df.Low, close=df.Close, name="Price"))
    
    # 2. VWAP Line
    fig.add_trace(go.Scatter(x=df.index, y=df.VWAP, line=dict(color='cyan', width=1, dash='dot'), name="VWAP"))
    
    # 3. Order Block Boxes
    recent_df = df.tail(50)
    for idx, row in recent_df.iterrows():
        if row['OB_Buy']: # Green Zone
            fig.add_shape(type="rect", x0=idx, x1=df.index[-1], y0=row['Low'], y1=row['High'], fillcolor="green", opacity=0.2, line_width=0)
        if row['OB_Sell']: # Red Zone
            fig.add_shape(type="rect", x0=idx, x1=df.index[-1], y0=row['Low'], y1=row['High'], fillcolor="red", opacity=0.2, line_width=0)

    fig.update_layout(height=650, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig, use_container_width=True, key=f"chart_{label}")

    # RSI Line Sub-chart
    rsi_fig = go.Figure()
    rsi_fig.add_trace(go.Scatter(x=df.index, y=df.RSI, line=dict(color='#FFD700', width=2), name="RSI"))
    rsi_fig.add_hline(y=70, line_dash="dash", line_color="red")
    rsi_fig.add_hline(y=30, line_dash="dash", line_color="green")
    rsi_fig.update_layout(height=200, template="plotly_dark", margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(rsi_fig, use_container_width=True)

render_dashboard(target_ticker, asset_choice)
