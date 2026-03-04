import streamlit as st
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf

# 1. SYSTEM SETUP
st.set_page_config(page_title="PATRO AI PRO V8.9", layout="wide")

# 2. SIDEBAR - SQUEEZED & FULL FEATURED
with st.sidebar:
    st.title("🌌 PATRO CONTROL")
    news_mode = st.toggle("ACTIVATE NEWS GUARD", value=True)
    if st.button("🔄 FORCE DATA SYNC"):
        st.cache_data.clear()
        st.rerun()
    
    st.divider()
    st.markdown("### 📋 INSTITUTIONAL SOP")
    sop_trend = st.checkbox("Trend Matrix Confluence", value=True)
    sop_vwap = st.checkbox("Price Action near VWAP", value=True)
    sop_vol = st.checkbox("Volume Confirmation", value=True)
    sop_macd = st.checkbox("MACD Momentum Guard", value=True)
    
    st.divider()
    st.markdown("### ⚙️ VISUALS")
    show_analysis = st.toggle("Show MACD Analysis Row", value=True)
    
    st.divider()
    asset_map = {"XAUUSD (GOLD)": "GC=F", "US30 (DOW JONES)": "^DJI"}
    asset_label = st.selectbox("Asset", list(asset_map.keys()))
    tf = st.radio("Timeframe", ["1m", "5m", "15m"], horizontal=True, index=1)

# 3. SMART DATA ENGINE (PREVENTS KEYERROR)
@st.cache_data(ttl=30)
def get_clean_data(ticker, interval):
    df = yf.download(ticker, period="1d", interval=interval)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    # Calculate Indicators
    df['SMA'] = ta.sma(df['Close'], length=20)
    df['VWAP'] = ta.vwap(df['High'], df['Low'], df['Close'], df['Volume'])
    
    # SMART MACD: Auto-finds column names to prevent errors
    macd = ta.macd(df['Close'])
    df = pd.concat([df, macd], axis=1)
    # Map the first 3 columns of MACD output to standard names
    df['MACD_Line'] = macd.iloc[:, 0]
    df['MACD_Hist'] = macd.iloc[:, 1]
    df['MACD_Signal'] = macd.iloc[:, 2]
    
    # SMART ADX: Auto-finds Power column
    adx = ta.adx(df['High'], df['Low'], df['Close'])
    df['ADX_Power'] = adx.iloc[:, 0]
    
    return df.dropna()

try:
    df = get_clean_data(asset_map[asset_label], tf)
    last, prev = df.iloc[-1], df.iloc[-2]

    # POWER METER (SIDEBAR)
    with st.sidebar:
        st.divider()
        arrow = "▲" if last['ADX_Power'] > prev['ADX_Power'] else "▼"
        color = "green" if arrow == "▲" else "red"
        st.markdown(f"### ⚡ POWER: {last['ADX_Power']:.1f}% <span style='color:{color}'>{arrow}</span>", unsafe_allow_html=True)
        st.progress(min(max(last['ADX_Power'] / 100, 0.0), 1.0))

    # 4. TRIPLE-STACK CHART (Price -> Volume -> MACD)
    rows = 3 if show_analysis else 1
    heights = [0.5, 0.2, 0.3] if show_analysis else [1.0]
    fig = make_subplots(rows=rows, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=heights)

    # TOP: PRICE
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['VWAP'], line=dict(color='orange', width=2), name="VWAP"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA'], line=dict(color='cyan', width=1), name="SMA 20"), row=1, col=1)

    if show_analysis:
        # MIDDLE: VOLUME
        v_colors = ['#26A69A' if df['Close'][i] >= df['Open'][i] else '#EF5350' for i in range(len(df))]
        fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name="Volume", marker_color=v_colors), row=2, col=1)

        # BOTTOM: MACD HISTOGRAM
        h_colors = ['#26A69A' if val > 0 else '#EF5350' for val in df['MACD_Hist']]
        fig.add_trace(go.Bar(x=df.index, y=df['MACD_Hist'], name="Hist", marker_color=h_colors), row=3, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['MACD_Line'], line=dict(color='#2962FF'), name="MACD"), row=3, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['MACD_Signal'], line=dict(color='#FF6D00'), name="Signal"), row=3, col=1)

    fig.update_layout(height=850 if show_analysis else 600, template="plotly_dark", xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"🛑 CRITICAL ERROR: {e}")
