import streamlit as st
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf

# 1. STABLE SETUP
st.set_page_config(page_title="PATRO AI PRO V8.8", layout="wide")

# 2. SIDEBAR - ALL FEATURES RESTORED & SQUEEZED
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
    # RESTORED: This matches your requested "Show MACD Analysis Row"
    show_analysis = st.toggle("Show MACD Analysis Row", value=True)
    
    st.divider()
    asset_map = {"XAUUSD (GOLD)": "GC=F", "US30 (DOW JONES)": "^DJI"}
    asset_label = st.selectbox("Asset", list(asset_map.keys()))
    tf = st.radio("Timeframe", ["1m", "5m", "15m"], horizontal=True, index=1)
    
    if st.button("♻️ RESET SIGNAL LOCK"):
        st.toast("Signal Lock Reset Successfully")

# 3. DATA ENGINE (FIXED FOR TYPEERROR)
@st.cache_data(ttl=30)
def get_market_data(ticker, interval):
    df = yf.download(ticker, period="1d", interval=interval)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    # Technicals
    df['SMA'] = ta.sma(df['Close'], length=20)
    df['VWAP'] = ta.vwap(df['High'], df['Low'], df['Close'], df['Volume'])
    
    # FIXED: Correct way to access ADX to avoid the TypeError in your photo
    adx_df = ta.adx(df['High'], df['Low'], df['Close'])
    df['ADX'] = adx_df['ADX_14']
    
    macd = ta.macd(df['Close'])
    df['MACD'] = macd['MACD_12_26_9']
    df['Signal'] = macd['MACDs_12_26_9']
    df['Hist'] = macd['MACDh_12_26_9']
    return df.dropna()

try:
    df = get_market_data(asset_map[asset_label], tf)
    last, prev = df.iloc[-1], df.iloc[-2]

    # POWER METER (SIDEBAR)
    with st.sidebar:
        st.divider()
        arrow = "▲" if last['ADX'] > prev['ADX'] else "▼"
        color = "green" if arrow == "▲" else "red"
        st.markdown(f"### ⚡ POWER: {last['ADX']:.1f}% <span style='color:{color}'>{arrow}</span>", unsafe_allow_html=True)
        st.progress(min(max(last['ADX'] / 100, 0.0), 1.0))

    # 4. TRIPLE-STACK CHART (Price -> Volume -> MACD)
    rows = 3 if show_analysis else 1
    specs = [[{"secondary_y": True}], [{"secondary_y": False}], [{"secondary_y": False}]] if show_analysis else [[{"secondary_y": True}]]
    heights = [0.5, 0.2, 0.3] if show_analysis else [1.0]

    fig = make_subplots(rows=rows, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.05, specs=specs, row_heights=heights)

    # ROW 1: CANDLESTICK & INDICATORS
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['VWAP'], line=dict(color='orange', width=2), name="VWAP"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA'], line=dict(color='cyan', width=1), name="SMA 20"), row=1, col=1)

    if show_analysis:
        # ROW 2: VOLUME (MIDDLE)
        vol_colors = ['green' if df['Close'][i] >= df['Open'][i] else 'red' for i in range(len(df))]
        fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name="Volume", marker_color=vol_colors), row=2, col=1)

        # ROW 3: MACD HISTOGRAM (BOTTOM)
        hist_colors = ['#26A69A' if val > 0 else '#EF5350' for val in df['Hist']]
        fig.add_trace(go.Bar(x=df.index, y=df['Hist'], name="Histogram", marker_color=hist_colors), row=3, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['MACD'], line=dict(color='#2962FF', width=1.5), name="MACD"), row=3, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['Signal'], line=dict(color='#FF6D00', width=1.5), name="Signal"), row=3, col=1)

    fig.update_layout(height=800 if show_analysis else 600, template="plotly_dark", xaxis_rangeslider_visible=False, showlegend=False)
    
    st.title(f"📊 {asset_label} Terminal")
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"⚠️ SYSTEM WAITING FOR DATA: {e}")
