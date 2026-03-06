import streamlit as st
import pandas as pd
import pandas_ta as ta
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- 1. NEXT-LEVEL UI CONFIGURATION ---
st.set_page_config(page_title="PATRO AI PRO V11.6", layout="wide", initial_sidebar_state="collapsed")

# Custom CSS for the "Video Look" (Matches your screenshot)
st.markdown("""
    <style>
    .stApp { background-color: #050505; color: white; }
    header, footer, #MainMenu {visibility: hidden;}
    
    /* Glassmorphism Signal Card */
    .signal-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 25px;
        padding: 35px 20px;
        text-align: center;
        box-shadow: 0 15px 35px rgba(0,0,0,0.7);
        margin-bottom: 25px;
    }

    /* Neon BUY Button */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #00FF88 0%, #00D1FF 100%);
        color: black !important;
        border: none;
        font-weight: 900;
        height: 3.8em;
        width: 100%;
        border-radius: 15px;
        box-shadow: 0 0 20px rgba(0, 255, 136, 0.35);
        transition: 0.3s;
    }

    /* Neon SELL Button */
    div[data-testid="stButton"] > button[key="sell_btn"] {
        background: linear-gradient(135deg, #FF3366 0%, #FF5E3A 100%) !important;
        color: white !important;
        box-shadow: 0 0 20px rgba(255, 51, 102, 0.35) !important;
    }

    section[data-testid="stSidebar"] { background-color: #0a0a0a !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA ENGINE ---
@st.cache_data(ttl=30)
def get_patro_data(ticker, interval):
    try:
        df = yf.download(ticker, period="5d", interval=interval, auto_adjust=True, progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): 
            df.columns = df.columns.get_level_values(0)
        
        df['VWAP'] = ta.vwap(df['High'], df['Low'], df['Close'], df['Volume'])
        df['SMA200'] = ta.sma(df['Close'], length=200)
        df['RSI'] = ta.rsi(df['Close'], length=14)
        macd = ta.macd(df['Close'])
        df['MACD_H'] = macd['MACDh_12_26_9']
        df['ADX'] = ta.adx(df['High'], df['Low'], df['Close'])['ADX_14']
        df['Vol_Avg'] = df['Volume'].rolling(window=20).mean()
        df['Is_Spike'] = df['Volume'] > (df['Vol_Avg'] * 2.5)
        return df.dropna()
    except: return None

# --- 3. SIDEBAR & RISK ---
with st.sidebar:
    st.title("🌌 PATRO V11.6")
    st.warning("⚠️ **HIGH IMPACT NEWS**")
    st.divider()
    st.markdown("### 📋 INSTITUTIONAL SOP")
    st.checkbox("Trend Matrix Confluence", value=True)
    st.checkbox("Price Action near VWAP", value=True)
    st.checkbox("Volume Confirmation", value=True)
    
    st.divider()
    balance = st.number_input("Account Balance ($)", value=1000)
    risk_pct = st.slider("Risk Per Trade %", 0.5, 5.0, 1.0)
    stop_pips = st.number_input("Stop Loss (Pips)", value=30)
    recommended_lots = (balance * (risk_pct / 100)) / (stop_pips * 10) 
    st.success(f"Recommended Lot: {recommended_lots:.2f}")

    asset_dict = {"XAUUSD": "GC=F", "US30": "^DJI", "GBPUSD": "GBPUSD=X"}
    choice = st.selectbox("Market", list(asset_dict.keys()))
    tf = st.radio("Timeframe", ["1m", "5m", "15m"], horizontal=True, index=1)

# --- 4. SIGNAL BIAS & FILTER ---
df1, df5, df15 = get_patro_data(asset_dict[choice], "1m"), get_patro_data(asset_dict[choice], "5m"), get_patro_data(asset_dict[choice], "15m")

def get_bias(df):
    if df is None or df.empty: return 0
    l = df.iloc[-1]
    if l['Close'] > l['VWAP'] and l['MACD_H'] > 0: return 1
    if l['Close'] < l['VWAP'] and l['MACD_H'] < 0: return -1
    return 0

b1, b5, b15 = get_bias(df1), get_bias(df5), get_bias(df15)
active_df = {"1m": df1, "5m": df5, "15m": df15}[tf]

# --- 5. MOBILE-STYLE HEADER ---
if active_df is not None:
    last = active_df.iloc[-1]
    confluence = (b1 + b5 + b15)
    
    signal_text, signal_clr = "⚖️ SCANNING", "#888"
    if abs(confluence) == 3 and last['ADX'] > 28:
        signal_text = "LOCKED BUY" if confluence == 3 else "LOCKED SELL"
        signal_clr = "#00FF88" if confluence == 3 else "#FF3366"

    st.markdown(f"""
        <div class="signal-card">
            <p style="color: #666; letter-spacing: 4px; font-size: 11px; margin-bottom:10px;">V11.6 MONITORING ACTIVE</p>
            <h1 style="color: {signal_clr}; font-size: 58px; margin: 0; font-weight: 800; text-shadow: 0 0 20px {signal_clr}44;">{signal_text}</h1>
            <div style="display: flex; justify-content: space-around; margin-top: 20px; border-top: 1px solid rgba(255,255,255,0.05); padding-top:15px;">
                <div><p style="color:#444; margin:0; font-size:10px;">POWER</p><p style="font-size:20px; color:white;">{last['ADX']:.1f}%</p></div>
                <div><p style="color:#444; margin:0; font-size:10px;">PRICE</p><p style="font-size:20px; color:white;">{last['Close']:.2f}</p></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    c_buy, c_sell = st.columns(2)
    with c_buy: st.button("🚀 INSTANT BUY", use_container_width=True)
    with c_sell: st.button("📉 INSTANT SELL", key="sell_btn", use_container_width=True)

# --- 6. CHARTING WITH TREND ARROWS ---
if active_df is not None:
    # Logic to only show the "REAL" (first) signal
    active_df['Raw'] = 0
    active_df.loc[(active_df['Close'] > active_df['VWAP']) & (active_df['MACD_H'] > 0) & (active_df['ADX'] > 28), 'Raw'] = 1
    active_df.loc[(active_df['Close'] < active_df['VWAP']) & (active_df['MACD_H'] < 0) & (active_df['ADX'] > 28), 'Raw'] = -1
    active_df['Entry'] = active_df['Raw'].diff().fillna(0)

    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.02, row_heights=[0.5, 0.1, 0.4])
    fig.add_trace(go.Candlestick(x=active_df.index, open=active_df['Open'], high=active_df['High'], low=active_df['Low'], close=active_df['Close'], name="Price"), row=1, col=1)
    
    # Entry Arrows & Words on Chart
    buys = active_df[active_df['Entry'] == 1]
    fig.add_trace(go.Scatter(x=buys.index, y=buys['Low']*0.998, mode="markers+text", text="BUY", textposition="bottom center",
                             marker=dict(symbol="triangle-up", size=12, color="#00FF88", line=dict(width=1, color="white")), name="Buy"), row=1, col=1)
    
    sells = active_df[active_df['Entry'] == -1]
    fig.add_trace(go.Scatter(x=sells.index, y=sells['High']*1.002, mode="markers+text", text="SELL", textposition="top center",
                             marker=dict(symbol="triangle-down", size=12, color="#FF3366", line=dict(width=1, color="white")), name="Sell"), row=1, col=1)

    fig.add_trace(go.Scatter(x=active_df.index, y=active_df['VWAP'], line=dict(color='orange', width=2), name="VWAP"), row=1, col=1)
    fig.add_trace(go.Scatter(x=active_df.index, y=active_df['SMA200'], line=dict(color='white', width=1, dash='dot'), name="SMA 200"), row=1, col=1)
    
    # Volume & Momentum
    v_colors = ['#FFFF00' if spike else '#444444' for spike in active_df['Is_Spike']]
    fig.add_trace(go.Bar(x=active_df.index, y=active_df['Volume'], marker_color=v_colors, name="Volume"), row=2, col=1)
    h_colors = ['#00FF88' if val >= 0 else '#FF3366' for val in active_df['MACD_H']]
    fig.add_trace(go.Bar(x=active_df.index, y=active_df['MACD_H'], marker_color=h_colors, name="MACD"), row=3, col=1)
    fig.add_trace(go.Scatter(x=active_df.index, y=active_df['RSI'], line=dict(color='#C084FC', width=1.5), name="RSI"), row=3, col=1)

    fig.update_layout(height=850, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
