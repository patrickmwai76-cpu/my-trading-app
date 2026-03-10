import streamlit as st
import pandas as pd
import pandas_ta as ta
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime

# --- 1. CORE CONFIG ---
st.set_page_config(page_title="PATRO AI PRO V12.0.0", layout="wide")
st.markdown("<style>.stApp { background: #010101; color: #ffffff; }</style>", unsafe_allow_html=True)

# --- 2. DATA & SMC ENGINE ---
def get_market_data(ticker, interval="5m"):
    try:
        df = yf.download(ticker, period="5d", interval=interval, progress=False, auto_adjust=True)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        # Indicators
        df['RSI'] = ta.rsi(df.Close, length=14)
        df['VWAP'] = ta.vwap(df.High, df.Low, df.Close, df.Volume)
        
        # SMC: Fair Value Gaps (FVG)
        df['FVG_Up'] = (df['Low'].shift(-1) > df['High'].shift(1)) & (df['Close'] > df['Open'])
        df['FVG_Down'] = (df['High'].shift(-1) < df['Low'].shift(1)) & (df['Close'] < df['Open'])
        
        # SMC: Order Blocks (OB)
        df['OB_Buy'] = (df['Close'] > df['High'].shift(1)) & (df['Close'].shift(1) < df['Open'].shift(1))
        df['OB_Sell'] = (df['Close'] < df['Low'].shift(1)) & (df['Close'].shift(1) > df['Open'].shift(1))
        
        return df
    except: return None

# --- 3. UI LAYOUT ---
st.title("🌌 PATRO AI PRO V12.0.0 | INSTITUTIONAL GRADE")

with st.sidebar:
    st.header("🏢 TRADING DESK")
    asset_choice = st.selectbox("Market Target", ["GOLD", "GBPUSD", "US30"])
    ticker_map = {"GOLD":"GC=F", "GBPUSD":"GBPUSD=X", "US30":"^DJI"}
    target_ticker = ticker_map[asset_choice]
    
    st.divider()
    st.subheader("📰 NEWS SCANNER")
    st.warning("⚠️ High Volatility: Trump Iran Comments")
    st.info("📅 Next Fed Meeting: March 18, 2026")
    st.divider()
    st.write("✅ MTF Filter: ACTIVE")
    st.write("✅ FVG Engine: ACTIVE")

# --- 4. LIVE DASHBOARD ---
@st.fragment(run_every="15s")
def render_app():
    # Multi-Timeframe Confirmation
    df_5m = get_market_data(target_ticker, "5m")
    df_1h = get_market_data(target_ticker, "1h")
    
    if df_5m is None or len(df_5m) < 10:
        st.error("Connecting to Liquidity Provider...")
        return

    # Institutional Bias (1H)
    bias_1h = "BULLISH" if df_1h.Close.iloc[-1] > df_1h.VWAP.iloc[-1] else "BEARISH"
    curr_sig = "BUY" if df_5m.Close.iloc[-1] > df_5m.VWAP.iloc[-1] else "SELL"
    
    # Volume Check (1.5x)
    vol_avg = df_5m.Volume.tail(20).mean()
    bank_vol = df_5m.Volume.iloc[-1] > (vol_avg * 1.5)
    
    # FINAL SIGNAL LOGIC
    is_sure = (bias_1h == "BULLISH" and curr_sig == "BUY" and bank_vol) or \
              (bias_1h == "BEARISH" and curr_sig == "SELL" and bank_vol)
    
    sig_text = f"🏦 BANK {curr_sig} (SURE)" if is_sure else "⌛ WAIT (RETAIL NOISE)"
    sig_col = "#00FF88" if is_sure and curr_sig == "BUY" else "#FF3366" if is_sure else "#FFA500"

    # Top Metrics
    m1, m2, m3 = st.columns([2, 1, 1])
    m1.markdown(f"<div style='border:2px solid {sig_col}; padding:15px; border-radius:10px; background:#111; text-align:center;'><h1 style='color:{sig_col}; margin:0;'>{sig_text}</h1></div>", unsafe_allow_html=True)
    m2.metric("CURRENT PRICE", f"{df_5m.Close.iloc[-1]:,.2f}")
    m3.metric("1H TREND", bias_1h)

    # --- MAIN CHART ---
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df_5m.index, open=df_5m.Open, high=df_5m.High, low=df_5m.Low, close=df_5m.Close, name="Price"))
    fig.add_trace(go.Scatter(x=df_5m.index, y=df_5m.VWAP, line=dict(color='cyan', dash='dot', width=1), name="VWAP"))

    # DRAW SMC ELEMENTS
    limit = len(df_5m) - 2
    for i in range(1, limit):
        # 1. Order Blocks (Solid Boxes)
        if df_5m['OB_Buy'].iloc[i]:
            fig.add_shape(type="rect", x0=df_5m.index[i], x1=df_5m.index[-1], y0=df_5m.Low.iloc[i], y1=df_5m.High.iloc[i], fillcolor="green", opacity=0.15, line_width=0)
        if df_5m['OB_Sell'].iloc[i]:
            fig.add_shape(type="rect", x0=df_5m.index[i], x1=df_5m.index[-1], y0=df_5m.Low.iloc[i], y1=df_5m.High.iloc[i], fillcolor="red", opacity=0.15, line_width=0)
        
        # 2. Fair Value Gaps (FVG)
        if df_5m['FVG_Up'].iloc[i]:
            fig.add_shape(type="rect", x0=df_5m.index[i], x1=df_5m.index[i+2], y0=df_5m.High.iloc[i-1], y1=df_5m.Low.iloc[i+1], fillcolor="#00FF88", opacity=0.3, line_width=1)
        if df_5m['FVG_Down'].iloc[i]:
            fig.add_shape(type="rect", x0=df_5m.index[i], x1=df_5m.index[i+2], y0=df_5m.Low.iloc[i-1], y1=df_5m.High.iloc[i+1], fillcolor="#FF3366", opacity=0.3, line_width=1)

    fig.update_layout(height=600, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig, use_container_width=True)

    # RSI Sub-Chart
    rsi_fig = go.Figure()
    rsi_fig.add_trace(go.Scatter(x=df_5m.index, y=df_5m.RSI, line=dict(color='#FFD700', width=1.5), name="RSI"))
    rsi_fig.add_hline(y=70, line_dash="dash", line_color="red")
    rsi_fig.add_hline(y=30, line_dash="dash", line_color="green")
    rsi_fig.update_layout(height=180, template="plotly_dark", margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(rsi_fig, use_container_width=True)

render_app()
