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

# --- 3. SIDEBAR (STABLE AREA) ---
# Move sidebar calls OUTSIDE the fragment to prevent the StreamlitAPIException
with st.sidebar:
    st.title("🌌 PATRO V11.6")
    asset_key = st.selectbox("Market Asset", ["GOLD", "GBPUSD", "US30"])
    ticker_map = {"GOLD":"GC=F", "GBPUSD":"GBPUSD=X", "US30":"^DJI"}
    target_ticker = ticker_map[asset_key]
    
    st.divider()
    st.subheader("📋 SOP CHECKLIST")
    f_conf = st.checkbox("MTF Alignment Check", value=True)
    f_vol = st.checkbox("Volume Threshold Check", value=True)
    
    # Placeholder for the Matrix (Fragment will fill this)
    matrix_container = st.empty()

# --- 4. THE LIVE FRAGMENT ENGINE ---
@st.fragment(run_every="10s")
def live_dashboard(ticker, label):
    # 4a. Multi-Timeframe Matrix Logic
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
    
    # Update the sidebar matrix from within the fragment using the placeholder
    matrix_container.table(pd.DataFrame(matrix_results))

    # 4b. Main Analysis (1m)
    df = get_data(ticker, "1m")
    if not df.empty and len(df) > 20:
        df['VWAP'] = ta.vwap(df.High, df.Low, df.Close, df.Volume)
        df['RSI'] = ta.rsi(df.Close, length=14)
        last = df.iloc[-1]
        
        # News Analysis (Simulated for March 9, 2026)
        news_headlines = {
            "GOLD": "Gold tests $5,100 resistance as geopolitical tension holds.",
            "GBPUSD": "Pound steady ahead of BoE interest rate commentary.",
            "US30": "Dow under pressure as oil prices spike above $100."
        }
        
        # --- AI SCORE CALCULATION ---
        all_match = len(set(directions)) == 1
        base_score = 60 if all_match else 20
        sop_bonus = (f_conf + f_vol) * 15
        rsi_bonus = 10 if (last['RSI'] > 55 or last['RSI'] < 45) else 0
        final_score = base_score + sop_bonus + rsi_bonus

        # --- ACTION UI ---
        color = "#00FF88" if (all_match and directions[0]) else "#FF3366" if (all_match and not directions[0]) else "#FFA500"
        
        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown(f"""
                <div style="border: 3px solid {color}; border-radius: 15px; padding: 20px; text-align: center; background: {color}11;">
                    <p style="margin:0; font-size: 14px; color: #aaa;">AI CONFIDENCE</p>
                    <h1 style="margin:0; font-size: 60px; color: {color};">{final_score}%</h1>
                </div>
            """, unsafe_allow_html=True)
            
        with col2:
            st.info(f"📰 **NEWS SENTINEL:** {news_headlines.get(label)}")
            if final_score >= 85:
                signal = "🚀 STRONG BUY" if directions[0] else "📉 STRONG SELL"
                st.markdown(f"<h2 style='color:{color}; text-align:center;'>{signal}</h2>", unsafe_allow_html=True)
            else:
                st.markdown("<h2 style='color:#777; text-align:center;'>⌛ SCANNING...</h2>", unsafe_allow_html=True)

        # --- CHART ---
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3], vertical_spacing=0.05)
        fig.add_trace(go.Candlestick(x=df.index, open=df.Open, high=df.High, low=df.Low, close=df.Close, name="Price"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df.VWAP, line=dict(color='orange', width=2), name="VWAP"), row=1, col=1)
        fig.add_trace(go.Bar(x=df.index, y=df.Volume, name="Volume", marker_color=color), row=2, col=1)
        fig.update_layout(height=600, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True, key=f"chart_{label}")

# Start the fixed engine
live_dashboard(target_ticker, asset_key)
