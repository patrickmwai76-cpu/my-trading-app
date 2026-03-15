import streamlit as st
import pandas as pd
import pandas_ta as ta
import yfinance as yf
import plotly.graph_objects as go

# --- 1. CORE CONFIG ---
st.set_page_config(page_title="PATRO AI PRO V12.1.9", layout="wide")
st.markdown("<style>.stApp { background: #000000; color: #ffffff; }</style>", unsafe_allow_html=True)

# --- 2. DATA ENGINE (ROBUST LIST CONVERSION) ---
def get_market_data(ticker):
    try:
        df = yf.download(ticker, period="2d", interval="5m", progress=False, auto_adjust=True)
        if df.empty: return None
        
        # 1. Flatten the data grid
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        # 2. Indicators
        df['VWAP'] = ta.vwap(df.High, df.Low, df.Close, df.Volume)
        df['ATR'] = ta.atr(df.High, df.Low, df.Close, length=14)
        
        # 3. Liquidity (FVG)
        df['FVG_Up'] = (df['Low'].shift(-1) > df['High'].shift(1)) 
        df['FVG_Down'] = (df['High'].shift(-1) < df['Low'].shift(1))
        
        return df.dropna()
    except Exception as e:
        st.error(f"Engine Fault: {e}")
        return None

# --- 3. SIDEBAR ---
with st.sidebar:
    st.title("🏢 SMC PATRO")
    asset = st.selectbox("Target", ["GOLD", "GBPUSD", "US30"])
    ticker_map = {"GOLD":"GC=F", "GBPUSD":"GBPUSD=X", "US30":"^DJI"}
    target_ticker = ticker_map[asset]
    st.info("Status: Operational")

# --- 4. DASHBOARD RENDER ---
@st.fragment(run_every="15s")
def render_app():
    df = get_market_data(target_ticker)
    if df is None: return

    cp = df.Close.iloc[-1]
    vwap_val = df.VWAP.iloc[-1]
    sig = "BUY" if cp > vwap_val else "SELL"
    col = "#00FF88" if sig == "BUY" else "#FF3366"

    # Header Metric
    st.markdown(f"<div style='border:3px solid {col}; padding:10px; border-radius:15px; text-align:center; background:#111;'><h1 style='color:{col}; margin:0;'>🏦 BANK {sig} DETECTED | {cp:,.2f}</h1></div>", unsafe_allow_html=True)

    # --- THE CHART (FIXED FOR VISIBILITY) ---
    fig = go.Figure()

    # FORCE DATA TO LISTS (Prevents "Black Screen" rendering error)
    dates = df.index.tolist()
    opens = df.Open.tolist()
    highs = df.High.tolist()
    lows = df.Low.tolist()
    closes = df.Close.tolist()

    # TikTok Background Zones
    for i in range(len(df)-1):
        zone_col = "rgba(0, 255, 136, 0.05)" if df.Close.iloc[i] > df.VWAP.iloc[i] else "rgba(255, 51, 102, 0.05)"
        fig.add_shape(type="rect", x0=dates[i], x1=dates[i+1], y0=min(lows), y1=max(highs), fillcolor=zone_col, line_width=0, layer="below")

    # Candlesticks
    fig.add_trace(go.Candlestick(
        x=dates, open=opens, high=highs, low=lows, close=closes,
        increasing_line_color='#00FF88', decreasing_line_color='#FF3366', name="Market"
    ))

    # Signal Label (The floating BUY/SELL from your photos)
    fig.add_annotation(
        x=dates[-1], y=closes[-1], text=f"<b>{sig}</b>", 
        bgcolor=col, font=dict(color="black", size=18), showarrow=True, arrowhead=2, arrowcolor=col
    )

    # FVG Liquidity Zones (Restored)
    for i in range(len(df)-20, len(df)-1):
        if df['FVG_Up'].iloc[i]:
            fig.add_shape(type="rect", x0=dates[i-1], x1=dates[i+1], y0=highs[i-1], y1=lows[i+1], fillcolor="rgba(0, 255, 136, 0.2)", line_width=0)
        if df['FVG_Down'].iloc[i]:
            fig.add_shape(type="rect", x0=dates[i-1], x1=dates[i+1], y0=lows[i-1], y1=highs[i+1], fillcolor="rgba(255, 51, 102, 0.2)", line_width=0)

    # Final Styling
    fig.update_layout(
        height=700, template="plotly_dark",
        paper_bgcolor="black", plot_bgcolor="black",
        xaxis_rangeslider_visible=False,
        margin=dict(l=5, r=5, t=5, b=5)
    )

    # st.plotly_chart(..., theme=None) is the key to preventing the black box
    st.plotly_chart(fig, use_container_width=True, theme=None, key="smc_final")

render_app()
