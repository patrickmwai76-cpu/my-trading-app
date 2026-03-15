import streamlit as st
import pandas as pd
import pandas_ta as ta
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime

# 1. PAGE SETUP (The "Wide" layout can sometimes hide charts on mobile)
st.set_page_config(page_title="PATRO AI PRO V12.1.16", layout="centered") 
st.markdown("<style>.stApp { background: #000; color: #fff; }</style>", unsafe_allow_html=True)

# 2. DATA ENGINE
def get_market_data(ticker):
    try:
        df = yf.download(ticker, period="1d", interval="5m", progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        df['VWAP'] = ta.vwap(df.High, df.Low, df.Close, df.Volume)
        df['ATR'] = ta.atr(df.High, df.Low, df.Close, length=14)
        return df.dropna()
    except Exception as e:
        st.error(f"Data Error: {e}")
        return None

# 3. SIDEBAR (Everything stays here)
with st.sidebar:
    st.header("🏢 COMMAND")
    asset = st.selectbox("Select Asset", ["GOLD", "GBPUSD", "US30"], key="asset_select")
    ticker_map = {"GOLD":"GC=F", "GBPUSD":"GBPUSD=X", "US30":"^DJI"}
    
    st.divider()
    st.subheader("💰 RISK")
    bal = st.number_input("Balance", 1000)
    risk = st.slider("Risk %", 1, 5, 2)
    
    st.divider()
    st.subheader("📡 NEWS")
    st.error("🚨 HIGH VOLATILITY DETECTED")

# 4. MAIN APP LOGIC (Simplified for visibility)
df = get_market_data(ticker_map[asset])

if df is not None:
    cp = df.Close.iloc[-1]
    vwap_val = df.VWAP.iloc[-1]
    atr = df.ATR.iloc[-1]
    
    # Simple Signal Logic
    if cp > (vwap_val + (atr * 0.5)): 
        sig, col = "BUY", "#00FF88"
    elif cp < (vwap_val - (atr * 0.5)): 
        sig, col = "SELL", "#FF3366"
    else: 
        sig, col = "WAIT", "#FFA500"

    # Header Box
    st.markdown(f"""
        <div style='border:4px solid {col}; padding:20px; border-radius:15px; background:#111; text-align:center;'>
            <h1 style='color:{col}; margin:0;'>BANK {sig} ZONE</h1>
            <p style='color:gray; margin:5px;'>Price: {cp:,.2f} | SMC Logic Active</p>
        </div>
    """, unsafe_allow_html=True)

    # 5. THE CHART (Force Render Settings)
    fig = go.Figure()

    # Candlesticks
    fig.add_trace(go.Candlestick(
        x=df.index, open=df.Open, high=df.High, low=df.Low, close=df.Close,
        increasing_line_color='#00FF88', decreasing_line_color='#FF3366'
    ))

    # Background Shading
    fig.add_vrect(x0=df.index[0], x1=df.index[-1], fillcolor=col, opacity=0.08, layer="below", line_width=0)

    # Floating Label
    fig.add_annotation(x=df.index[-1], y=cp, text=f"<b>{sig}</b>", bgcolor=col, font=dict(color="black", size=20), showarrow=True)

    # Entry/TP/SL Lines
    tp = cp + (atr * 3) if sig == "BUY" else cp - (atr * 3)
    sl = cp - (atr * 1.5) if sig == "BUY" else cp + (atr * 1.5)
    fig.add_hline(y=vwap_val, line_color="white", annotation_text="ENTRY")
    fig.add_hline(y=tp, line_color="#00FF88", line_dash="dash", annotation_text="TP")
    fig.add_hline(y=sl, line_color="#FF3366", line_dash="dash", annotation_text="SL")

    # Layout - CRITICAL: fixed height and use_container_width=True
    fig.update_layout(
        height=550, 
        template="plotly_dark", 
        paper_bgcolor="black", 
        plot_bgcolor="black", 
        xaxis_rangeslider_visible=False,
        margin=dict(l=10, r=10, t=10, b=10)
    )

    # Display Command
    st.plotly_chart(fig, use_container_width=True, theme=None)

    # 6. HISTORY TABLE
    st.divider()
    st.subheader("📜 SIGNAL HISTORY")
    st.table(pd.DataFrame([{"Time": datetime.now().strftime("%H:%M"), "Signal": sig, "Price": cp}]))
else:
    st.warning("⚠️ Waiting for Market Data... Refreshing.")
    st.button("Manual Refresh")
