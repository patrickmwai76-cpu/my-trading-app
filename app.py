import streamlit as st
import pandas as pd
import pandas_ta as ta
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- 1. SETTINGS & APP CONFIG ---
st.set_page_config(page_title="PATRO AI PRO V11.6", layout="wide")
st.markdown("<style>.stApp { background: #050505; color: white; }</style>", unsafe_allow_html=True)

# --- 2. DATA ENGINE ---
def get_data(ticker, tf="1m"):
    try:
        df = yf.download(ticker, period="2d", interval=tf, progress=False, auto_adjust=True)
        if df.empty: return pd.DataFrame()
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df
    except:
        return pd.DataFrame()

# --- 3. THE ANALYTICS FRAGMENT ---
@st.fragment(run_every="10s")
def patro_core_fragment(ticker, label):
    # 3a. News Sentinel
    news_feed = [
        "🚨 MARCH 9: Gold tests $5,100 resistance; Oil spikes above $100.",
        "📊 VOLATILITY: GBPUSD neutral as UK GDP data looms.",
        "📉 US30: Indices under pressure; VWAP holding as hard ceiling."
    ]

    # 3b. Matrix Calculation
    matrix_results = []
    directions = []
    for tf in ["1m", "5m", "15m"]:
        m_df = get_data(ticker, tf)
        if not m_df.empty:
            m_vwap = ta.vwap(m_df.High, m_df.Low, m_df.Close, m_df.Volume).iloc[-1]
            is_up = m_df.Close.iloc[-1] > m_vwap
            matrix_results.append({"TF": tf, "Power": "⬆️ UP" if is_up else "⬇️ DOWN"})
            directions.append(is_up)

    # 3c. Update the Sidebar (Inside the sidebar context)
    with st.sidebar:
        st.divider()
        st.subheader("⚡ POWER MATRIX")
        st.table(pd.DataFrame(matrix_results))
        st.divider()
        st.write("📊 **SENTINEL TICKER**")
        st.caption(news_feed[0] if "GOLD" in label else news_feed[1])

    # 3d. Main Dashboard Content
    df = get_data(ticker, "1m")
    if not df.empty and len(df) > 20:
        df['VWAP'] = ta.vwap(df.High, df.Low, df.Close, df.Volume)
        df['RSI'] = ta.rsi(df.Close)
        
        all_match = len(set(directions)) == 1
        score = 90 if all_match else 40
        color = "#00FF88" if (all_match and directions[0]) else "#FF3366" if (all_match and not directions[0]) else "#FFA500"

        # UI Header
        c1, c2 = st.columns([1, 2])
        with c1:
            st.markdown(f"""
                <div style="border: 3px solid {color}; border-radius: 15px; padding: 20px; text-align: center; background: {color}11;">
                    <p style="margin:0; font-size: 14px; color: #aaa;">AI CONFLUENCE</p>
                    <h1 style="margin:0; font-size: 60px; color: {color};">{score}%</h1>
                </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
                <div style="background: #111; padding: 15px; border-radius: 10px; border-left: 5px solid {color};">
                    <marquee scrollamount="4" style="color: {color}; font-weight: bold;">{' | '.join(news_feed)}</marquee>
                </div>
            """, unsafe_allow_html=True)
            status = "🚀 STRONG BUY" if (all_match and directions[0]) else "📉 STRONG SELL" if (all_match and not directions[0]) else "⌛ CHOPPY / WAIT"
            st.markdown(f"<h2 style='color:{color}; text-align:center; margin-top:10px;'>{status}</h2>", unsafe_allow_html=True)

        # Main Chart
        fig = make_subplots(rows=1, cols=1)
        fig.add_trace(go.Candlestick(x=df.index, open=df.Open, high=df.High, low=df.Low, close=df.Close, name="Price"))
        fig.add_trace(go.Scatter(x=df.index, y=df.VWAP, line=dict(color='orange', width=2), name="VWAP"))
        fig.update_layout(height=500, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True, key=f"v116_{label}")

# --- 4. MAIN EXECUTION ---
with st.sidebar:
    st.title("🌌 PATRO V11.6")
    asset_key = st.selectbox("Asset", ["GOLD", "GBPUSD", "US30"])
    ticker_map = {"GOLD":"GC=F", "GBPUSD":"GBPUSD=X", "US30":"^DJI"}
    target_ticker = ticker_map[asset_key]

# Call the fragment (It will now correctly update the sidebar it was called from)
patro_core_fragment(target_ticker, asset_key)
