import streamlit as st
import pandas as pd
import pandas_ta as ta
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests

# --- 1. SETTINGS & AI CONFIG ---
st.set_page_config(page_title="PATRO AI PRO V11.6", layout="wide")
st.markdown("<style>.stApp { background: #050505; color: white; }</style>", unsafe_allow_html=True)

# --- 2. LIVE NEWS SENTINEL (Heuristic Analysis) ---
def get_news_sentiment(asset):
    # Simulated News Analysis for March 9, 2026 
    # In a live env, replace with a NewsAPI/EODHD call
    news_map = {
        "GOLD": {"sentiment": -0.2, "headline": "Gold stable at $5,100 as Middle East risk premium fades."},
        "GBPUSD": {"sentiment": 0.1, "headline": "GBP holds steady ahead of US Inflation data."},
        "US30": {"sentiment": -0.5, "headline": "Dow Futures tumble as Oil stays above $100."}
    }
    return news_map.get(asset, {"sentiment": 0, "headline": "No major news."})

# --- 3. THE POWER ENGINE ---
def get_data(ticker, tf="1m"):
    df = yf.download(ticker, period="2d", interval=tf, progress=False, auto_adjust=True)
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    return df

@st.fragment(run_every="10s")
def patro_core():
    # --- 4. THE SIDEBAR POWER MATRIX ---
    with st.sidebar:
        st.title("🌌 PATRO V11.6")
        asset_key = st.selectbox("Asset", ["GOLD", "GBPUSD", "US30"])
        ticker = {"GOLD":"GC=F", "GBPUSD":"GBPUSD=X", "US30":"^DJI"}[asset_key]
        
        st.divider()
        st.subheader("⚡ POWER MATRIX")
        matrix = []
        for tf in ["1m", "5m", "15m"]:
            m_df = get_data(ticker, tf)
            m_vwap = ta.vwap(m_df.High, m_df.Low, m_df.Close, m_df.Volume).iloc[-1]
            status = "UP ⬆️" if m_df.Close.iloc[-1] > m_vwap else "DOWN ⬇️"
            matrix.append({"TF": tf, "Power": status})
        st.table(pd.DataFrame(matrix))

    # --- 5. MAIN ANALYSIS ---
    df = get_data(ticker, "1m")
    df['VWAP'] = ta.vwap(df.High, df.Low, df.Close, df.Volume)
    df['RSI'] = ta.rsi(df.Close)
    
    # News Check
    news = get_news_sentiment(asset_key)
    
    # Logic: Match all arrows + News
    all_up = all(m['Power'] == "UP ⬆️" for m in matrix)
    all_down = all(m['Power'] == "DOWN ⬇️" for m in matrix)
    
    score = 0
    if all_up: score += 50
    if all_down: score += 50
    if news['sentiment'] > 0 and all_up: score += 40
    if news['sentiment'] < 0 and all_down: score += 40
    score += (20 if 40 < df['RSI'].iloc[-1] < 60 else 10)

    # --- 6. TOP UI DISPLAY ---
    c1, c2 = st.columns([1, 2])
    with c1:
        color = "#00FF88" if all_up and news['sentiment'] >= 0 else "#FF3366" if all_down and news['sentiment'] <= 0 else "#FFA500"
        st.markdown(f"""
            <div style="border: 2px solid {color}; padding:20px; border-radius:15px; text-align:center;">
                <h1 style="color:{color}; margin:0;">{score}%</h1>
                <p style="color:#aaa;">AI CONFLUENCE</p>
            </div>
        """, unsafe_allow_html=True)
    
    with c2:
        st.info(f"📰 **NEWS SENTINEL:** {news['headline']}")
        if score >= 85:
            action = "🚀 STRONG BUY" if all_up else "📉 STRONG SELL"
            st.success(f"**ACTION:** {action}")
        else:
            st.warning("**ACTION:** WAIT - News or Timeframes do not match!")

    # --- 7. CHART ---
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3])
    fig.add_trace(go.Candlestick(x=df.index, open=df.Open, high=df.High, low=df.Low, close=df.Close, name="Price"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df.VWAP, line=dict(color='orange'), name="VWAP"), row=1, col=1)
    fig.add_trace(go.Bar(x=df.index, y=df.Volume, name="Volume"), row=2, col=1)
    fig.update_layout(height=600, template="plotly_dark", xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

patro_core()
