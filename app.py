import streamlit as st
import pandas as pd
import pandas_ta as ta
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- BULLETPROOF DATA ENGINE ---
def get_clean_data(ticker, interval):
    try:
        # We try the most compatible parameter name first
        df = yf.download(
            tickers=ticker, 
            period="2d", 
            interval=interval, 
            auto_adjust=True, 
            multi_level_index=False, # Standard name for stable versions
            progress=False
        )
        
        # If the above fails or returns Multi-Index, we force-clean it manually
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        if df.empty: return None
        
        # Add Your Indicators
        df['VWAP'] = ta.vwap(df['High'], df['Low'], df['Close'], df['Volume'])
        macd = ta.macd(df['Close'])
        df['MACD_H'] = macd.iloc[:, 1]
        df['ADX'] = ta.adx(df['High'], df['Low'], df['Close'])['ADX_14']
        
        return df.dropna()
    except Exception as e:
        # If 'multi_level_index' causes an error, try one more time without it
        st.warning(f"Engine Warning: Adjusting for version... ({e})")
        return yf.download(ticker, period="2d", interval=interval, auto_adjust=True, progress=False)

# --- SIDEBAR (Everything Restored) ---
with st.sidebar:
    st.title("🌌 PATRO CONTROL")
    st.markdown("### 📋 INSTITUTIONAL SOP")
    sop1 = st.checkbox("Trend Confluence", value=True)
    sop2 = st.checkbox("Volume Check", value=True)
    
    st.divider()
    asset_dict = {"XAUUSD (GOLD)": "GC=F", "US30 (DOW)": "^DJI"}
    choice = st.selectbox("Market", list(asset_dict.keys()))
    ticker = asset_dict[choice]
    tf = st.radio("Timeframe", ["1m", "5m", "15m"], horizontal=True)

# --- CHART EXECUTION ---
df = get_clean_data(ticker, tf)

if df is not None and not df.empty:
    # Full Chart with Price, Volume, and MACD
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.02, row_heights=[0.6, 0.1, 0.3])
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['VWAP'], line=dict(color='orange', width=2), name="VWAP"), row=1, col=1)
    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name="Volume"), row=2, col=1)
    fig.add_trace(go.Bar(x=df.index, y=df['MACD_H'], name="MACD"), row=3, col=1)
    
    fig.update_layout(height=850, template="plotly_dark", xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.error("🚨 CONNECTION LOST: Yahoo Finance is blocking your request.")
    st.info("Check your internet or click the button in V10.4 to update drivers.")
