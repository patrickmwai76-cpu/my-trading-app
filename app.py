import streamlit as st
import pandas as pd
import pandas_ta as ta
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pytz

# 1. PAGE SETUP
st.set_page_config(page_title="PATRO AI PRO V11.2", layout="wide")

# 2. DATA ENGINE
@st.cache_data(ttl=30)
def get_patro_data(ticker, interval):
    try:
        df = yf.download(ticker, period="2d", interval=interval, auto_adjust=True, progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        # Technicals
        df['VWAP'] = ta.vwap(df['High'], df['Low'], df['Close'], df['Volume'])
        macd = ta.macd(df['Close'])
        df['MACD_H'] = macd.iloc[:, 1]
        df['ADX'] = ta.adx(df['High'], df['Low'], df['Close'])['ADX_14']
        return df.dropna()
    except: return None

# 3. SIDEBAR: SOP & CONTROLS
with st.sidebar:
    st.title("🌌 PATRO V11.2")
    st.markdown("### 📋 INSTITUTIONAL SOP")
    sop_trend = st.checkbox("Trend Matrix Confluence", value=True)
    sop_vwap = st.checkbox("Price Action near VWAP", value=True)
    sop_vol = st.checkbox("Volume Confirmation", value=True)
    sop_macd = st.checkbox("Momentum Guard", value=True)
    
    st.divider()
    asset_dict = {"XAUUSD": "GC=F", "US30": "^DJI", "GBPUSD": "GBPUSD=X"}
    choice = st.selectbox("Market", list(asset_dict.keys()))
    tf = st.radio("Timeframe", ["1m", "5m", "15m"], horizontal=True)

# 4. TREND CONFLUENCE & POWER LOGIC
df1, df5, df15 = get_patro_data(asset_dict[choice], "1m"), get_patro_data(asset_dict[choice], "5m"), get_patro_data(asset_dict[choice], "15m")

def get_bias(df):
    if df is None: return 0
    l = df.iloc[-1]
    if l['Close'] > l['VWAP'] and l['MACD_H'] > 0: return 1
    if l['Close'] < l['VWAP'] and l['MACD_H'] < 0: return -1
    return 0

b1, b5, b15 = get_bias(df1), get_bias(df5), get_bias(df15)
active_df = {"1m": df1, "5m": df5, "15m": df15}[tf]

# 5. HEADER: SIGNAL & POWER
signal_text, signal_clr = "⚖️ SCANNING", "#808080"
if active_df is not None:
    last, prev = active_df.iloc[-1], active_df.iloc[-2]
    power_up = last['ADX'] > prev['ADX']
    arrow = "▲" if power_up else "▼"
    arrow_clr = "#00FF00" if power_up else "#FF0000"
    
    # TRIPLE-LOCK LOGIC
    confluence = (b1 + b5 + b15)
    if abs(confluence) == 3 and last['ADX'] > 25 and power_up:
        signal_text = "🚀 LOCKED BUY" if confluence == 3 else "📉 LOCKED SELL"
        signal_clr = "#00FF00" if confluence == 3 else "#FF0000"

    # Display Trend Power
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(f"<h1 style='color:{signal_clr};'>{signal_text}</h1>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"### POWER: {last['ADX']:.1f}% <span style='color:{arrow_clr}'>{arrow}</span>", unsafe_allow_html=True)

# 6. CHARTING WITH SESSIONS
if active_df is not None:
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.7, 0.3])
    fig.add_trace(go.Candlestick(x=active_df.index, open=active_df['Open'], high=active_df['High'], low=active_df['Low'], close=active_df['Close'], name="Price"), row=1, col=1)
    fig.add_trace(go.Scatter(x=active_df.index, y=active_df['VWAP'], line=dict(color='orange', width=2), name="VWAP"), row=1, col=1)
    
    # Session Rectangles (EAT: London 10-18, NY 15-00)
    for i in range(0, len(active_df), 5):
        dt = active_df.index[i].astimezone(pytz.timezone('Africa/Nairobi'))
        if 10 <= dt.hour < 18:
            fig.add_vrect(x0=dt, x1=dt, fillcolor="blue", opacity=0.02, layer="below", line_width=0)
        if 15 <= dt.hour < 24:
            fig.add_vrect(x0=dt, x1=dt, fillcolor="green", opacity=0.02, layer="below", line_width=0)

    fig.add_trace(go.Bar(x=active_df.index, y=active_df['MACD_H'], name="MACD"), row=2, col=1)
    fig.update_layout(height=800, template="plotly_dark", xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)
