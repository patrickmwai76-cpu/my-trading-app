import streamlit as st
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf

# 1. PAGE SETUP
st.set_page_config(page_title="PATRO AI PRO V8.8", layout="wide")

# 2. DATA ENGINE (MULTI-TIMEFRAME)
@st.cache_data(ttl=30)
def get_mtf_data(ticker):
    tf_list = ["1m", "5m", "15m"]
    results = {}
    for t in tf_list:
        df = yf.download(ticker, period="1d", interval=t)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        # Technicals
        df['SMA'] = ta.sma(df['Close'], length=20)
        df['VWAP'] = ta.vwap(df['High'], df['Low'], df['Close'], df['Volume'])
        adx_df = ta.adx(df['High'], df['Low'], df['Close'])
        df['ADX'] = adx_df['ADX_14']
        macd = ta.macd(df['Close'])
        df['Hist'] = macd['MACDh_12_26_9']
        results[t] = df.dropna()
    return results

# 3. SIDEBAR - ALL 4 SOPs & VISUALS RESTORED
with st.sidebar:
    st.title("🌌 PATRO CONTROL")
    news_mode = st.toggle("ACTIVATE NEWS GUARD", value=True)
    if st.button("🔄 FORCE DATA SYNC"):
        st.cache_data.clear()
        st.rerun()
    
    st.divider()
    # RESTORED: ALL 4 INSTITUTIONAL SOPS
    st.markdown("### 📋 INSTITUTIONAL SOP")
    sop_trend = st.checkbox("Trend Matrix Confluence", value=True)
    sop_vwap = st.checkbox("Price Action near VWAP", value=True)
    sop_vol = st.checkbox("Volume Confirmation", value=True)
    sop_macd = st.checkbox("MACD Momentum Guard", value=True)
    
    st.divider()
    # RESTORED: VISUALS SECTION
    st.markdown("### ⚙️ VISUALS")
    show_analysis = st.toggle("Show MACD Analysis Row", value=True)
    
    st.divider()
    asset_map = {"XAUUSD (GOLD)": "GC=F", "US30 (DOW JONES)": "^DJI"}
    asset_label = st.selectbox("Asset", list(asset_map.keys()))
    ticker = asset_map[asset_label]
    
    manual_tf = st.radio("Manual Chart View", ["1m", "5m", "15m"], horizontal=True, index=1)

# 4. ALIGNMENT & MAIN DATA
data_pack = get_mtf_data(ticker)
def get_arrow(df):
    return "▲" if df['ADX'].iloc[-1] > df['ADX'].iloc[-2] else "▼"

arrows = {t: get_arrow(data_pack[t]) for t in ["1m", "5m", "15m"]}
all_green = all(a == "▲" for a in arrows.values())

# 5. TOP ALIGNMENT BAR
if all_green:
    st.markdown(f"""<div style="background-color:#FFD700; padding:10px; border-radius:10px; text-align:center; color:black;">
    <strong>🏆 TRIPLE ALIGNMENT: 1m:▲ | 5m:▲ | 15m:▲ — HIGH PROBABILITY BUY</strong></div>""", unsafe_allow_html=True)
else:
    st.markdown(f"""<div style="background-color:#222; padding:10px; border-radius:10px; text-align:center; color:white;">
    Alignment Status: 1m:{arrows['1m']} | 5m:{arrows['5m']} | 15m:{arrows['15m']}</div>""", unsafe_allow_html=True)

# 6. TRIPLE-STACK CHART (Price -> Volume -> MACD)
df = data_pack[manual_tf]
rows = 3 if show_analysis else 1
fig = make_subplots(rows=rows, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.5, 0.2, 0.3] if show_analysis else [1.0])

# Main Chart
fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"), row=1, col=1)
fig.add_trace(go.Scatter(x=df.index, y=df['VWAP'], line=dict(color='orange', width=2), name="VWAP"), row=1, col=1)

if show_analysis:
    # Volume in Middle
    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name="Volume", marker_color='grey'), row=2, col=1)
    # MACD at Bottom
    hist_colors = ['#26A69A' if v > 0 else '#EF5350' for v in df['Hist']]
    fig.add_trace(go.Bar(x=df.index, y=df['Hist'], name="MACD Hist", marker_color=hist_colors), row=3, col=1)

fig.update_layout(height=800 if show_analysis else 600, template="plotly_dark", xaxis_rangeslider_visible=False)
st.plotly_chart(fig, use_container_width=True)
