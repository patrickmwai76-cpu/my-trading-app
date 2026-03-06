import streamlit as st
import pandas as pd
import pandas_ta as ta
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 1. PAGE SETUP
st.set_page_config(page_title="PATRO AI PRO V10.7", layout="wide")

# 2. BULLETPROOF DATA ENGINE
@st.cache_data(ttl=30)
def get_patro_data(ticker, interval):
    try:
        df = yf.download(ticker, period="2d", interval=interval, auto_adjust=True, progress=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        if df.empty: return None
        
        # Indicators
        df['VWAP'] = ta.vwap(df['High'], df['Low'], df['Close'], df['Volume'])
        macd = ta.macd(df['Close'])
        df['MACD_H'] = macd.iloc[:, 1]
        df['ADX'] = ta.adx(df['High'], df['Low'], df['Close'])['ADX_14']
        return df.dropna()
    except: return None

# 3. SIDEBAR CONTROLS
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

# 4. TREND MATRIX LOGIC
df1, df5, df15 = get_patro_data(ticker, "1m"), get_patro_data(ticker, "5m"), get_patro_data(ticker, "15m")

def check_trend(df):
    if df is None: return 0
    l = df.iloc[-1]
    if l['Close'] > l['VWAP'] and l['MACD_H'] > 0: return 1
    if l['Close'] < l['VWAP'] and l['MACD_H'] < 0: return -1
    return 0

t1, t5, t15 = check_trend(df1), check_trend(df5), check_trend(df15)

with st.sidebar:
    st.divider()
    st.markdown("### 🔍 TREND MATRIX")
    st.write(f"1M: {'🟢' if t1==1 else '🔴' if t1==-1 else '⚪'}")
    st.write(f"5M: {'🟢' if t5==1 else '🔴' if t5==-1 else '⚪'}")
    st.write(f"15M: {'🟢' if t15==1 else '🔴' if t15==-1 else '⚪'}")

# 5. POWER METER & SIGNAL FILTER
active_df = {"1m": df1, "5m": df5, "15m": df15}[tf]
signal_text, signal_clr = "⚖️ NEUTRAL / SCANNING", "#808080"

if active_df is not None:
    last, prev = active_df.iloc[-1], active_df.iloc[-2]
    pwr_rising = last['ADX'] > prev['ADX']
    
    with st.sidebar:
        st.divider()
        arrow = "▲" if pwr_rising else "▼"
        arrow_clr = "#00FF00" if pwr_rising else "#FF0000"
        st.markdown(f"### ⚡ POWER: {last['ADX']:.1f}% <span style='color:{arrow_clr}'>{arrow}</span>", unsafe_allow_html=True)
        st.progress(min(last['ADX']/100, 1.0))

    # TRIPLE LOCK SIGNAL FILTER
    confluence = t1 + t5 + t15
    if abs(confluence) == 3 and last['ADX'] >= 25 and pwr_rising:
        signal_text = "🚀 LOCKED BUY" if confluence == 3 else "📉 LOCKED SELL"
        signal_clr = "#00FF00" if confluence == 3 else "#FF0000"

st.markdown(f"<h1 style='text-align:center; color:{signal_clr};'>{signal_text}</h1>", unsafe_allow_html=True)

# 6. FULL 3-PANE CHARTING
if active_df is not None:
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.6, 0.1, 0.3])
    fig.add_trace(go.Candlestick(x=active_df.index, open=active_df['Open'], high=active_df['High'], low=active_df['Low'], close=active_df['Close'], name="Price"), row=1, col=1)
    fig.add_trace(go.Scatter(x=active_df.index, y=active_df['VWAP'], line=dict(color='orange', width=2), name="VWAP"), row=1, col=1)
    fig.add_trace(go.Bar(x=active_df.index, y=active_df['Volume'], name="Volume"), row=2, col=1)
    fig.add_trace(go.Bar(x=active_df.index, y=active_df['MACD_H'], name="MACD"), row=3, col=1)
    fig.update_layout(height=850, template="plotly_dark", xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)
