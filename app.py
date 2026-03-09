import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go

# --- 1. CORE CONFIG ---
st.set_page_config(page_title="PATRO AI PRO V11.6", layout="wide")
st.markdown("<style>.stApp { background: #020202; color: #e0e0e0; }</style>", unsafe_allow_html=True)

# --- 2. THE PERMANENT FRAME (Outside Fragment) ---
st.title("🌌 PATRO AI PRO V11.6 | INSTITUTIONAL")

with st.sidebar:
    st.header("🏢 TRADING DESK")
    asset_choice = st.selectbox("Asset", ["GOLD", "GBPUSD", "US30"])
    ticker_map = {"GOLD":"GC=F", "GBPUSD":"GBPUSD=X", "US30":"^DJI"}
    target_ticker = ticker_map[asset_choice]
    
    st.divider()
    sop_spot = st.empty()  # For Institutional SOPs
    matrix_spot = st.empty() # For MTF Price Action

# --- 3. INSTITUTIONAL ENGINE ---
def get_clean_data(ticker):
    df = yf.download(ticker, period="2d", interval="1m", progress=False, auto_adjust=True)
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    return df

@st.fragment(run_every="10s")
def run_institutional_core(ticker, label):
    df = get_clean_data(ticker)
    if df.empty or len(df) < 10: return

    # --- A. PRICE ACTION LOGIC (No Indicators) ---
    current_price = df.Close.iloc[-1]
    prev_price = df.Close.iloc[-2]
    high_24h = df.High.max()
    low_24h = df.Low.min()
    
    # Identify Institutional "Fair Value Gaps" (FVG)
    # Simple logic: If current candle open is far from previous candle close
    is_imbalance = abs(df.Open.iloc[-1] - df.Close.iloc[-2]) > (df.High.iloc[-1] - df.Low.iloc[-1]) * 0.5
    
    # --- B. SIDEBAR UPDATES (Remote) ---
    with sop_spot.container():
        st.subheader("📋 INSTITUTIONAL SOP")
        st.markdown(f"""
        * **HTF Trend:** {'🟢 BULLISH' if current_price > df.Close.iloc[-50] else '🔴 BEARISH'}
        * **Liquidity:** {'⚠️ VOID DETECTED' if is_imbalance else '✅ STABLE'}
        * **Daily Range:** {round(high_24h - low_24h, 2)} Pips
        """)
        st.divider()

    with matrix_spot.container():
        st.subheader("⚡ PRICE MATRIX")
        trend = "⬆️" if current_price > prev_price else "⬇️"
        st.metric(label="LIVE PRICE", value=f"{current_price:,.2f}", delta=f"{trend} {abs(current_price-prev_price):,.2f}")

    # --- C. MAIN DASHBOARD ---
    # Smart Confluence Score (Based on Price Structure, not Indicators)
    score = 50
    if current_price > df.Open.iloc[0]: score += 20 # Session Strength
    if not is_imbalance: score += 15 # Stability
    if current_price > high_24h * 0.99: score += 10 # Breakout Momentum
    
    color = "#00FF88" if score > 70 else "#FF3366" if score < 40 else "#FFA500"

    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown(f"""
            <div style="border: 2px solid {color}; border-radius: 10px; padding: 20px; text-align: center; background: {color}05;">
                <p style="margin:0; font-size: 12px; color: #888;">INSTITUTIONAL BIAS</p>
                <h1 style="margin:0; font-size: 55px; color: {color};">{score}%</h1>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        msg = "🚀 INSTITUTIONAL BUY" if score > 70 else "📉 LIQUIDITY GRAB (SELL)" if score < 40 else "⌛ ACCUMULATION ZONE"
        st.markdown(f"<h2 style='color:{color}; margin-top:15px;'>{msg}</h2>", unsafe_allow_html=True)
        st.caption(f"Last Institutional Scan: {pd.Timestamp.now().strftime('%H:%M:%S')} EAT")

    # --- D. THE CLEAN CHART (Price Only) ---
    fig = go.Figure()
    # Candlesticks
    fig.add_trace(go.Candlestick(
        x=df.index, open=df.Open, high=df.High, low=df.Low, close=df.Close,
        name="Market Price",
        increasing_line_color='#00FF88', decreasing_line_color='#FF3366'
    ))
    
    # Highlight Liquidity Zones (Session High/Low)
    fig.add_hline(y=high_24h, line_dash="dot", line_color="#444", annotation_text="Prev High")
    fig.add_hline(y=low_24h, line_dash="dot", line_color="#444", annotation_text="Prev Low")

    fig.update_layout(
        height=550, template="plotly_dark", 
        xaxis_rangeslider_visible=False,
        margin=dict(l=0,r=0,t=0,b=0),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig, use_container_width=True, key=f"clean_chart_{label}")

# --- 4. EXECUTION ---
run_institutional_core(target_ticker, asset_choice)
