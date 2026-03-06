import streamlit as st
import pandas as pd
import pandas_ta as ta
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pytz

# 1. PAGE SETUP
st.set_page_config(page_title="PATRO AI PRO V11.7", layout="wide")

# 2. DATA ENGINE (v11.7.1: Added Data Validation)
@st.cache_data(ttl=30)
def get_patro_data(ticker, interval):
    try:
        # Request slightly more data to ensure SMA 200 has enough points
        df = yf.download(ticker, period="5d", interval=interval, auto_adjust=True, progress=False)
        if df is None or len(df) < 200: return None 
        
        if isinstance(df.columns, pd.MultiIndex): 
            df.columns = df.columns.get_level_values(0)
        
        # Technicals
        df['VWAP'] = ta.vwap(df['High'], df['Low'], df['Close'], df['Volume'])
        df['SMA200'] = ta.sma(df['Close'], length=200) 
        df['RSI'] = ta.rsi(df['Close'], length=14)      
        
        # FULL MACD
        macd = ta.macd(df['Close'])
        df['MACD'] = macd.iloc[:, 0]
        df['MACD_S'] = macd.iloc[:, 2]
        df['MACD_H'] = macd.iloc[:, 1]
        
        df['ADX'] = ta.adx(df['High'], df['Low'], df['Close'])['ADX_14']
        
        # VOLUME SPIKE
        df['Vol_Avg'] = df['Volume'].rolling(window=20).mean()
        df['Is_Spike'] = df['Volume'] > (df['Vol_Avg'] * 2.5)
        
        return df.dropna()
    except Exception as e:
        return None

# 3. SIDEBAR & ASSET SELECTION
with st.sidebar:
    st.title("🌌 PATRO V11.7.1")
    asset_dict = {"XAUUSD": "GC=F", "US30": "^DJI", "GBPUSD": "GBPUSD=X"}
    choice = st.selectbox("Market", list(asset_dict.keys()))
    tf = st.radio("Timeframe", ["1m", "5m", "15m"], horizontal=True, index=2)

# 4. FETCH DATA WITH SAFETY
df1 = get_patro_data(asset_dict[choice], "1m")
df5 = get_patro_data(asset_dict[choice], "5m")
df15 = get_patro_data(asset_dict[choice], "15m")

def get_bias(df):
    if df is None or df.empty: return 0
    l = df.iloc[-1]
    if l['Close'] > l['VWAP'] and l['MACD_H'] > 0: return 1
    if l['Close'] < l['VWAP'] and l['MACD_H'] < 0: return -1
    return 0

# Check if current timeframe data exists before plotting
active_df = {"1m": df1, "5m": df5, "15m": df15}[tf]

if active_df is None or active_df.empty:
    st.error(f"❌ Waiting for more {tf} data to calculate SMA 200. Please try a higher timeframe or wait.")
else:
    # 5. HEADER: SIGNAL LOCK
    b1, b5, b15 = get_bias(df1), get_bias(df5), get_bias(df15)
    last = active_df.iloc[-1]
    confluence = (b1 + b5 + b15)
    
    signal_text, signal_clr = "⚖️ SCANNING", "#808080"
    if abs(confluence) == 3 and last['ADX'] > 25:
        if confluence == 3 and last['Close'] > last['SMA200'] and last['RSI'] < 70:
            signal_text, signal_clr = "🚀 LOCKED BUY", "#00FF00"
        elif confluence == -3 and last['Close'] < last['SMA200'] and last['RSI'] > 30:
            signal_text, signal_clr = "📉 LOCKED SELL", "#FF0000"

    st.markdown(f"<h1 style='color:{signal_clr}; text-align:center;'>{signal_text}</h1>", unsafe_allow_html=True)

    # 6. CHARTING: 4-ROW STABLE BUILD
    fig = make_subplots(
        rows=4, cols=1, 
        shared_xaxes=True, 
        vertical_spacing=0.03, 
        row_heights=[0.5, 0.1, 0.2, 0.2]
    )
    
    # ROW 1: Price + SMA 200
    fig.add_trace(go.Candlestick(x=active_df.index, open=active_df['Open'], high=active_df['High'], low=active_df['Low'], close=active_df['Close'], name="Price"), row=1, col=1)
    fig.add_trace(go.Scatter(x=active_df.index, y=active_df['SMA200'], line=dict(color='white', width=1, dash='dot'), name="SMA 200"), row=1, col=1)
    fig.add_trace(go.Scatter(x=active_df.index, y=active_df['VWAP'], line=dict(color='orange', width=2), name="VWAP"), row=1, col=1)

    # ROW 2: Volume
    v_colors = ['#FFFF00' if s else '#444444' for s in active_df['Is_Spike']]
    fig.add_trace(go.Bar(x=active_df.index, y=active_df['Volume'], marker_color=v_colors, name="Volume"), row=2, col=1)

    # ROW 3: MACD
    fig.add_trace(go.Bar(x=active_df.index, y=active_df['MACD_H'], name="MACD Hist"), row=3, col=1)
    fig.add_trace(go.Scatter(x=active_df.index, y=active_df['MACD'], line=dict(color='#00E5FF'), name="MACD"), row=3, col=1)

    # ROW 4: RSI
    fig.add_trace(go.Scatter(x=active_df.index, y=active_df['RSI'], line=dict(color='#C084FC'), name="RSI"), row=4, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=4, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=4, col=1)

    fig.update_layout(height=900, template="plotly_dark", xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)
