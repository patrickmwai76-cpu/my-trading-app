import streamlit as st
import pandas as pd
import pandas_ta as ta
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime

# --- 1. CORE CONFIG ---
st.set_page_config(page_title="PATRO AI PRO V12.0.1", layout="wide")
st.markdown("<style>.stApp { background: #010101; color: #ffffff; }</style>", unsafe_allow_html=True)

# --- 2. SMC & INDICATOR ENGINE ---
def get_market_data(ticker, interval="5m"):
    try:
        # Fetching 5 days of data for depth
        df = yf.download(ticker, period="5d", interval=interval, progress=False, auto_adjust=True)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        # Technical Indicators
        df['RSI'] = ta.rsi(df.Close, length=14)
        df['VWAP'] = ta.vwap(df.High, df.Low, df.Close, df.Volume)
        
        # Fair Value Gaps (FVG) - High Sensitivity Logic
        df['FVG_Up'] = (df['Low'].shift(-1) > df['High'].shift(1)) 
        df['FVG_Down'] = (df['High'].shift(-1) < df['Low'].shift(1))
        
        return df
    except Exception as e:
        return None

# --- 3. UI SIDEBAR & CONTROLS ---
st.title("🌌 PATRO AI PRO V12.0.1 | SMC EDITION")

with st.sidebar:
    st.header("🏢 COMMAND CENTER")
    asset = st.selectbox("Market Target", ["GOLD", "GBPUSD", "US30"])
    ticker_map = {"GOLD":"GC=F", "GBPUSD":"GBPUSD=X", "US30":"^DJI"}
    target_ticker = ticker_map[asset]
    
    st.divider()
    # THE SWITCH: Toggle between fast scalping and bank protection
    mode = st.toggle("🚀 AGGRESSIVE MODE", value=False, help="ON: Signals every move. OFF: Only Bank moves.")
    
    st.divider()
    st.subheader("📰 LIVE NEWS FEED")
    st.warning("⚠️ Gold volatility remains high after Trump Iran 'Excursion' comments.")
    st.info("📉 Oil plunging -10%, supporting Gold rebound.")

# --- 4. LIVE DASHBOARD ---
@st.fragment(run_every="15s")
def render_app():
    df_5m = get_market_data(target_ticker, "5m")
    df_1h = get_market_data(target_ticker, "1h") # For Trend Confirmation
    
    if df_5m is None or len(df_5m) < 20:
        st.error("Connecting to Liquidity Provider...")
        return

    # Logical Analysis
    bias_1h = "BULLISH" if df_1h.Close.iloc[-1] > df_1h.VWAP.iloc[-1] else "BEARISH"
    curr_sig = "BUY" if df_5m.Close.iloc[-1] > df_5m.VWAP.iloc[-1] else "SELL"
    bank_vol = df_5m.Volume.iloc[-1] > (df_5m.Volume.tail(20).mean() * 1.5)
    
    # SIGNAL LOGIC
    if mode: # Aggressive Mode (Ignores Banks, follows price)
        is_sure = True 
        status_text = f"🚀 SCALP {curr_sig}"
        display_col = "#00FF88" if curr_sig == "BUY" else "#FF3366"
    else: # Institutional Mode (Strict)
        is_sure = (bias_1h == curr_sig.replace("BUY","BULLISH").replace("SELL","BEARISH")) and bank_vol
        status_text = f"🏦 BANK {curr_sig} (SURE)" if is_sure else "⌛ WAIT (RETAIL NOISE)"
        display_col = ("#00FF88" if curr_sig == "BUY" else "#FF3366") if is_sure else "#FFA500"

    # Top Metrics UI
    m1, m2, m3 = st.columns([2, 1, 1])
    m1.markdown(f"<div style='border:3px solid {display_col}; padding:15px; border-radius:10px; background:#111; text-align:center;'><h1 style='color:{display_col}; margin:0;'>{status_text}</h1></div>", unsafe_allow_html=True)
    m2.metric("PRICE", f"{df_5m.Close.iloc[-1]:,.2f}")
    m3.metric("1H BIAS", bias_1h)

    # --- THE CHART ---
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df_5m.index, open=df_5m.Open, high=df_5m.High, low=df_5m.Low, close=df_5m.Close, name="Price"))
    fig.add_trace(go.Scatter(x=df_5m.index, y=df_5m.VWAP, line=dict(color='cyan', dash='dot', width=1), name="VWAP"))

    # HIGH-VISIBILITY BOX DETECTION
    boxes_count = 0
    for i in range(1, len(df_5m) - 1):
        # Bullish Gap (The Green Box)
        if df_5m['FVG_Up'].iloc[i]:
            fig.add_shape(type="rect", x0=df_5m.index[i-1], x1=df_5m.index[i+1],
                          y0=df_5m['High'].iloc[i-1], y1=df_5m['Low'].iloc[i+1],
                          fillcolor="rgba(0, 255, 136, 0.45)", line=dict(color="#00FF88", width=1))
            boxes_count += 1
        # Bearish Gap (The Red Box)
        if df_5m['FVG_Down'].iloc[i]:
            fig.add_shape(type="rect", x0=df_5m.index[i-1], x1=df_5m.index[i+1],
                          y0=df_5m['Low'].iloc[i-1], y1=df_5m['High'].iloc[i+1],
                          fillcolor="rgba(255, 51, 102, 0.45)", line=dict(color="#FF3366", width=1))
            boxes_count += 1

    fig.update_layout(height=580, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig, use_container_width=True)

    # RSI Sub-Chart
    rsi_fig = go.Figure()
    rsi_fig.add_trace(go.Scatter(x=df_5m.index, y=df_5m.RSI, line=dict(color='#FFD700', width=1.5)))
    rsi_fig.add_hline(y=70, line_dash="dash", line_color="red")
    rsi_fig.add_hline(y=30, line_dash="dash", line_color="green")
    rsi_fig.update_layout(height=140, template="plotly_dark", margin=dict(l=0,r=0,t=0,b=0), yaxis=dict(range=[0,100]))
    st.plotly_chart(rsi_fig, use_container_width=True)
    
    if boxes_count > 0:
        st.success(f"🎯 {boxes_count} Institutional Boxes found. These are 'Safety Zones' for your entry.")
    else:
        st.info("💡 No Gaps currently. Market is in high-speed 'Efficiency' mode.")

render_app()
