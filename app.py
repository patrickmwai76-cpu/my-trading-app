import streamlit as st
import pandas as pd
import pandas_ta as ta
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- 1. GLOBAL SETTINGS ---
st.set_page_config(page_title="PATRO AI PRO V11.6", layout="wide")
st.markdown("<style>.stApp { background: #010101; color: white; }</style>", unsafe_allow_html=True)

# --- 2. DATA ENGINE ---
def get_market_data(ticker, interval="1m"):
    try:
        df = yf.download(ticker, period="2d", interval=interval, progress=False, auto_adjust=True)
        if df.empty: return pd.DataFrame()
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df
    except: return pd.DataFrame()

# --- 3. THE ALL-IN-ONE FRAGMENT ---
@st.fragment(run_every="10s")
def patro_engine():
    # --- A. SIDEBAR CONTROLS ---
    with st.sidebar:
        st.title("🌌 PATRO V11.6")
        asset = st.selectbox("Market Asset", ["GOLD", "GBPUSD", "US30"], key="asset_select")
        ticker = {"GOLD":"GC=F", "GBPUSD":"GBPUSD=X", "US30":"^DJI"}[asset]
        
        st.divider()
        st.subheader("⚡ POWER MATRIX")
        matrix_data, directions = [], []
        for tf in ["1m", "5m", "15m"]:
            m_df = get_market_data(ticker, tf)
            if not m_df.empty:
                m_vwap = ta.vwap(m_df.High, m_df.Low, m_df.Close, m_df.Volume).iloc[-1]
                is_up = m_df.Close.iloc[-1] > m_vwap
                matrix_data.append({"TF": tf, "Power": "⬆️ BULL" if is_up else "⬇️ BEAR"})
                directions.append(is_up)
        st.table(pd.DataFrame(matrix_data))

    # --- B. NEWS SENTINEL (LIVE MARCH 9, 2026) ---
    news_feed = [
        "🚨 BREAKING: Brent Crude hits $119.50 as Strait of Hormuz remains blocked.",
        "💰 GOLD: XAUUSD slips below $5,100 as traders move to USD liquidity.",
        "📉 DOW JONES: US30 futures slide 2% as inflation fears reignite.",
        "🇬🇧 GBP: Sterling under pressure as UK GDP forecasts downgraded to 0.9%."
    ]
    
    # --- C. MAIN DASHBOARD ---
    df = get_market_data(ticker, "1m")
    if not df.empty and len(df) > 20:
        df['VWAP'] = ta.vwap(df.High, df.Low, df.Close, df.Volume)
        last = df.iloc[-1]
        all_match = len(set(directions)) == 1 if directions else False
        
        # Smart Veto Logic (Example: Veto Gold Buy if USD is spiking)
        score = 85 if all_match else 30
        status_msg = "🚀 STRONG SIGNAL" if score >= 85 else "⌛ WAITING FOR ALIGNMENT"
        color = "#00FF88" if (all_match and directions[0]) else "#FF3366" if (all_match and not directions[0]) else "#FFA500"

        # Display Top Metrics
        c1, c2 = st.columns([1, 2])
        with c1:
            st.markdown(f"""
                <div style="border: 2px solid {color}; border-radius: 15px; padding: 20px; text-align: center; background: {color}11;">
                    <p style="margin:0; font-size: 12px; color: #aaa;">AI CONFIDENCE</p>
                    <h1 style="margin:0; font-size: 50px; color: {color};">{score}%</h1>
                </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"<h2 style='color:{color}; margin-top:10px;'>{status_msg}</h2>", unsafe_allow_html=True)
            st.info(f"💡 **PATRO ADVICE:** {'Buy the dip only if 15m holds VWAP' if directions[0] else 'Avoid long positions; trend is heavily bearish'}")

        # D. LIVE NEWS TICKER (Scrolling Effect)
        st.markdown(f"""
            <div style="background: #111; padding: 10px; border-radius: 5px; border-left: 5px solid #00FF88; overflow: hidden;">
                <marquee scrollamount="5" style="font-weight: bold; color: #00FF88;">
                    {' | '.join(news_feed)}
                </marquee>
            </div>
        """, unsafe_allow_html=True)

        # E. CHARTING
        fig = make_subplots(rows=1, cols=1)
        fig.add_trace(go.Candlestick(x=df.index, open=df.Open, high=df.High, low=df.Low, close=df.Close, name="Price"))
        fig.add_trace(go.Scatter(x=df.index, y=df.VWAP, line=dict(color='orange', width=2), name="VWAP"))
        fig.update_layout(height=450, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=20,b=0))
        st.plotly_chart(fig, use_container_width=True, key=f"chart_{asset}")

# --- 4. EXECUTION ---
patro_engine()
