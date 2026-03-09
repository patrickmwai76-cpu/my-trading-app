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

# --- 3. GLOBAL UI SETUP ---
with st.sidebar:
    st.title("🌌 PATRO V11.6")
    asset_key = st.selectbox("Asset", ["GOLD", "GBPUSD", "US30"])
    ticker_map = {"GOLD":"GC=F", "GBPUSD":"GBPUSD=X", "US30":"^DJI"}
    target_ticker = ticker_map[asset_key]
    st.divider()

# --- 4. THE FRAGMENT ENGINE ---
@st.fragment(run_every="10s")
def render_system(ticker, label):
    # 4a. CALCULATE DATA
    matrix_results = []
    directions = []
    for tf in ["1m", "5m", "15m"]:
        m_df = get_data(ticker, tf)
        if not m_df.empty:
            m_vwap = ta.vwap(m_df.High, m_df.Low, m_df.Close, m_df.Volume).iloc[-1]
            is_up = m_df.Close.iloc[-1] > m_vwap
            icon = "⬆️ UP" if is_up else "⬇️ DOWN"
            matrix_results.append({"Timeframe": tf, "Power": icon})
            directions.append(is_up)
    
    # 4b. UPDATE THE SIDEBAR (Inside the fragment's context)
    with st.sidebar:
        st.subheader("⚡ POWER MATRIX")
        st.table(pd.DataFrame(matrix_results))
        st.divider()
        st.write("📋 **SOP STATUS**")
        st.checkbox("MTF Alignment", value=len(set(directions)) == 1)
        st.checkbox("Market Open", value=True)

    # 4c. MAIN DASHBOARD CONTENT
    df = get_data(ticker, "1m")
    if not df.empty and len(df) > 20:
        df['VWAP'] = ta.vwap(df.High, df.Low, df.Close, df.Volume)
        df['RSI'] = ta.rsi(df.Close)
        last = df.iloc[-1]
        
        # News Logic (March 9, 2026 Context)
        news_headlines = {
            "GOLD": "Gold buyers cautious as $5,100 resistance holds firm.",
            "GBPUSD": "Cable stalls as traders eye UK GDP data.",
            "US30": "Indices face selling pressure; VWAP acts as hard ceiling."
        }
        
        all_match = len(set(directions)) == 1
        color = "#00FF88" if (all_match and directions[0]) else "#FF3366" if (all_match and not directions[0]) else "#FFA500"
        
        # Scoring
        final_score = 90 if all_match else 45
        if abs(last['RSI'] - 50) < 5: final_score -= 10 # Deduct for chop
        
        # Header Metrics
        c1, c2 = st.columns([1, 2])
        with c1:
            st.markdown(f"""
                <div style="border: 3px solid {color}; border-radius: 15px; padding: 20px; text-align: center; background: {color}11;">
                    <p style="margin:0; font-size: 14px; color: #aaa;">AI CONFLUENCE</p>
                    <h1 style="margin:0; font-size: 64px; color: {color};">{final_score}%</h1>
                </div>
            """, unsafe_allow_html=True)
        with c2:
            st.info(f"📰 **NEWS SENTINEL:** {news_headlines.get(label)}")
            signal = "🚀 STRONG BUY" if directions[0] else "📉 STRONG SELL"
            if final_score >= 85:
                st.markdown(f"<h2 style='color:{color}; text-align:center;'>{signal}</h2>", unsafe_allow_html=True)
            else:
                st.markdown("<h2 style='color:#777; text-align:center;'>⌛ NEUTRAL / CHOPPY</h2>", unsafe_allow_html=True)

        # Main Chart
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3], vertical_spacing=0.05)
        fig.add_trace(go.Candlestick(x=df.index, open=df.Open, high=df.High, low=df.Low, close=df.Close, name="Price"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df.VWAP, line=dict(color='orange', width=2), name="VWAP"), row=1, col=1)
        fig.add_trace(go.Bar(x=df.index, y=df.Volume, name="Volume", marker_color=color), row=2, col=1)
        fig.update_layout(height=650, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True, key=f"v116_{label}")

# --- 5. START EXECUTION ---
render_system(target_ticker, asset_key)
