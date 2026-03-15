import streamlit as st
import pandas as pd
import pandas_ta as ta
import yfinance as yf
import plotly.graph_objects as go

# --- 1. CORE CONFIG ---
st.set_page_config(page_title="PATRO AI PRO V12.1.8", layout="wide")
st.markdown("<style>.stApp { background: #010101; color: #ffffff; }</style>", unsafe_allow_html=True)

# --- 2. DATA ENGINE (FIXED INDEX) ---
def get_market_data(ticker):
    try:
        # Auto_adjust=True is critical for yfinance stability
        df = yf.download(ticker, period="2d", interval="5m", progress=False, auto_adjust=True)
        if df.empty: return None
        
        # Flatten Multi-Index Columns (The 'Black Screen' Killer)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        df['VWAP'] = ta.vwap(df.High, df.Low, df.Close, df.Volume)
        df['ATR'] = ta.atr(df.High, df.Low, df.Close, length=14)
        return df
    except Exception as e:
        st.error(f"Engine Error: {e}")
        return None

# --- 3. UI LAYOUT ---
with st.sidebar:
    st.title("🌌 SMC PRO")
    asset = st.selectbox("Target", ["GOLD", "GBPUSD", "US30"])
    ticker_map = {"GOLD":"GC=F", "GBPUSD":"GBPUSD=X", "US30":"^DJI"}
    target_ticker = ticker_map[asset]

# --- 4. LIVE DASHBOARD ---
@st.fragment(run_every="15s")
def render_app():
    df = get_market_data(target_ticker)
    
    if df is None:
        st.error("No data received. Please check your internet or Ticker symbol.")
        return

    # Signal Logic
    cp = df.Close.iloc[-1]
    vwap_curr = df.VWAP.iloc[-1]
    sig = "BUY" if cp > vwap_curr else "SELL"
    col = "#00FF88" if sig == "BUY" else "#FF3366"

    # BANK HEADER
    st.markdown(f"<div style='border:2px solid {col}; padding:15px; border-radius:10px; text-align:center; background:rgba(255,255,255,0.05);'><h1 style='color:{col}; margin:0;'>🏦 BANK {sig} @ {cp:,.2f}</h1></div>", unsafe_allow_html=True)

    # --- THE CHART (FORCED THEME FIX) ---
    try:
        fig = go.Figure()

        # Add TikTok Background Zones
        for i in range(len(df)-1):
            fill = "rgba(0, 255, 136, 0.03)" if df.Close.iloc[i] > df.VWAP.iloc[i] else "rgba(255, 51, 102, 0.03)"
            fig.add_shape(type="rect", x0=df.index[i], x1=df.index[i+1], y0=df.Low.min(), y1=df.High.max(), fillcolor=fill, line_width=0, layer="below")

        # Candlesticks
        fig.add_trace(go.Candlestick(
            x=df.index, open=df.Open, high=df.High, low=df.Low, close=df.Close,
            increasing_line_color='#00FF88', decreasing_line_color='#FF3366', name="Market"
        ))

        # Floating Signal Label
        label_y = df.Low.iloc[-1] if sig == "BUY" else df.High.iloc[-1]
        fig.add_annotation(x=df.index[-1], y=label_y, text=f"<b>{sig}</b>", bgcolor=col, font=dict(color="black", size=14), showarrow=True)

        # Style Overrides
        fig.update_layout(
            height=700,
            template="plotly_dark", # Force Plotly's own dark theme
            paper_bgcolor="#010101",
            plot_bgcolor="#010101",
            xaxis_rangeslider_visible=False,
            margin=dict(l=0, r=0, t=0, b=0)
        )

        # CRITICAL: theme=None tells Streamlit NOT to touch the colors
        st.plotly_chart(fig, use_container_width=True, theme=None, key="final_render")
        
    except Exception as chart_err:
        st.warning(f"Chart Rendering Issue: {chart_err}")
        st.write("DEBUG DATA:", df.tail()) # Show data if chart fails

render_app()
