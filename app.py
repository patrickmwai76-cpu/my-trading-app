import streamlit as st
import pandas as pd
import pandas_ta as ta
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- 1. APP CONFIG (Must be at the very top) ---
st.set_page_config(page_title="PATRO AI PRO V11.6", layout="wide")
st.markdown("<style>.stApp { background: #050505; color: white; }</style>", unsafe_allow_html=True)

# --- 2. THE PERMANENT UI (Outside the fragment) ---
st.title("🌌 PATRO AI PRO V11.6")

with st.sidebar:
    st.header("🎮 CONTROL CENTER")
    asset_choice = st.selectbox("Select Asset", ["GOLD", "GBPUSD", "US30"])
    ticker_map = {"GOLD":"GC=F", "GBPUSD":"GBPUSD=X", "US30":"^DJI"}
    target_ticker = ticker_map[asset_choice]
    st.divider()
    # These placeholders are the "Remote Controls" for the fragment
    matrix_spot = st.empty() 
    news_spot = st.empty()

# --- 3. DATA ENGINE ---
def get_live_data(ticker, tf="1m"):
    try:
        df = yf.download(ticker, period="2d", interval=tf, progress=False, auto_adjust=True)
        if df.empty: return pd.DataFrame()
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        return df
    except: return pd.DataFrame()

# --- 4. THE LIVE ENGINE (The Fragment) ---
@st.fragment(run_every="10s")
def run_patro_engine(ticker, label):
    # 4a. Logic: Multi-Timeframe Matrix
    matrix_list = []
    directions = []
    for tf in ["1m", "5m", "15m"]:
        m_df = get_live_data(ticker, tf)
        if not m_df.empty:
            vwap = ta.vwap(m_df.High, m_df.Low, m_df.Close, m_df.Volume).iloc[-1]
            is_up = m_df.Close.iloc[-1] > vwap
            matrix_list.append({"TF": tf, "Power": "⬆️ BULL" if is_up else "⬇️ BEAR"})
            directions.append(is_up)

    # 4b. Remote Update Sidebar (Using the placeholders)
    with matrix_spot.container():
        st.write("### ⚡ POWER MATRIX")
        st.table(pd.DataFrame(matrix_list))
    
    with news_spot.container():
        st.write("📊 **SENTINEL**")
        st.caption(f"Last Scan: {pd.Timestamp.now().strftime('%H:%M:%S')}")

    # 4c. Main Dashboard Calculations
    df = get_live_data(ticker, "1m")
    if not df.empty and len(df) > 20:
        df['VWAP'] = ta.vwap(df.High, df.Low, df.Close, df.Volume)
        
        all_match = len(set(directions)) == 1 if directions else False
        score = 90 if all_match else 45
        color = "#00FF88" if (all_match and directions[0]) else "#FF3366" if (all_match and not directions[0]) else "#FFA500"

        # 4d. Ticker & Score UI
        news_text = "🚨 GOLD AT ALL-TIME HIGH $5,100 | OIL HITS $100 | USD STRENGTHENING"
        st.markdown(f"""
            <div style="background: #111; padding: 10px; border-radius: 5px; border-left: 5px solid {color}; margin-bottom:20px;">
                <marquee scrollamount="6" style="color: {color}; font-weight: bold;">{news_text}</marquee>
            </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown(f"""
                <div style="border: 3px solid {color}; border-radius: 15px; padding: 20px; text-align: center; background: {color}11;">
                    <h1 style="margin:0; font-size: 60px; color: {color};">{score}%</h1>
                    <p style="margin:0; color: #aaa;">AI CONFLUENCE</p>
                </div>
            """, unsafe_allow_html=True)
        with col2:
            signal = "🚀 STRONG BUY" if (all_match and directions[0]) else "📉 STRONG SELL" if (all_match and not directions[0]) else "⌛ WAIT"
            st.markdown(f"<h1 style='color:{color}; padding-top:15px;'>{signal}</h1>", unsafe_allow_html=True)

        # 4e. Main Chart
        fig = make_subplots(rows=1, cols=1)
        fig.add_trace(go.Candlestick(x=df.index, open=df.Open, high=df.High, low=df.Low, close=df.Close, name="Price"))
        fig.add_trace(go.Scatter(x=df.index, y=df.VWAP, line=dict(color='orange', width=2), name="VWAP"))
        fig.update_layout(height=500, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True, key=f"chart_{label}")

# --- 5. EXECUTION ---
run_patro_engine(target_ticker, asset_choice)
