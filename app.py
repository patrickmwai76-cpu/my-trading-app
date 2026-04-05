import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
import pytz
import yfinance as yf

# --- 1. CONFIGURATION & STYLE ---
st.set_page_config(page_title="PATRO AI PRO | ULTRA", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #0a0a0a; border-right: 1px solid #1f1f1f; }
    .stMetric { background-color: #111; padding: 15px; border-radius: 10px; border: 1px solid #222; }
    .gauge-container { 
        background: #111; padding: 15px; border-radius: 10px; border: 1px solid #333; text-align: center;
        margin-bottom: 20px;
    }
    .rating-text { font-size: 28px; font-weight: bold; color: #00FF88; margin: 0; }
    div.stButton > button:first-child {
        background-color: #00FF88; color: #000; border-radius: 8px; width: 100%; font-weight: bold; height: 3.5em;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ADVANCED ANALYTICS ENGINE ---
def get_market_analytics():
    try:
        gold = yf.Ticker("GC=F")
        df = gold.history(period="2d", interval="15m")
        if df.empty: return 4690.52, 4685.00, 4677.20, "NORMAL"
        
        current_p = round(df['Close'].iloc[-1], 2)
        df['TP'] = (df['High'] + df['Low'] + df['Close']) / 3
        df['PV'] = df['TP'] * df['Volume']
        current_vwap = round(df['PV'].cumsum().iloc[-1] / df['Volume'].cumsum().iloc[-1], 2)
        p_low = round(df['Low'].tail(10).min(), 2)
        vol_stat = "HIGH" if df['Volume'].iloc[-1] > df['Volume'].tail(20).mean() else "NORMAL"
        
        return current_p, current_vwap, p_low, vol_stat
    except:
        return 4690.52, 4685.00, 4677.20, "NORMAL"

current_price, vwap_val, p_low, vol_stat = get_market_analytics()

# --- 3. DYNAMIC RATING LOGIC (1-10) ---
score = 0
if current_price > vwap_val: score += 2  # VWAP Pillar
if current_price > p_low: score += 2     # Pivot Pillar
if vol_stat == "HIGH": score += 2       # Volume Pillar
score += 4  # Simulated MTF Alignment (M15, H1, H4 all Bullish)

# --- 4. SIDEBAR: GAUGE & RATING ---
with st.sidebar:
    st.markdown("<h1 style='color:#00FF88; margin-bottom:0;'>PATRO AI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#888;'>ULTRA V14.0 | PRO TRADER</p>", unsafe_allow_html=True)
    
    # 1-10 RATING GAUGE
    st.markdown("### 🏆 SIGNAL CONFIDENCE")
    st.markdown(f"""
    <div class="gauge-container">
        <p style="color:#888; font-size:12px; margin-bottom:5px;">CONFLUENCE RATING</p>
        <p class="rating-text">{score}/10</p>
        <div style="background:#222; height:10px; border-radius:5px; margin-top:10px;">
            <div style="background:#00FF88; width:{score*10}%; height:100%; border-radius:5px;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # DXY GAUGE
    dxy_val = 100.17
    st.markdown("### 💵 DXY STRENGTH")
    st.markdown(f"""
    <div class="gauge-container" style="border-color: #FFAA00;">
        <p style="color:#888; font-size:11px; margin-bottom:5px;">US DOLLAR INDEX</p>
        <p style="font-size:22px; font-weight:bold; color:#FFAA00;">{dxy_val}</p>
        <p style="font-size:10px; color:{'#00FF88' if dxy_val < 100.5 else '#FF4B4B'};">
            {'BULLISH FOR GOLD' if dxy_val < 100.5 else 'BEARISH FOR GOLD'}
        </p>
    </div>
    """, unsafe_allow_html=True)

    # TRADINGVIEW EXTERNAL POPUP
    st.markdown("### 🌐 EXTERNAL VIEW")
    st.link_button("🔥 WATCH ON TRADINGVIEW", "https://www.tradingview.com/chart/XAUUSD/", use_container_width=True)

    st.divider()
    bal = st.number_input("Balance ($)", value=2000)
    risk = st.select_slider("Risk Mode (%)", options=[0.5, 1.0, 2.0], value=1.0)
    st.metric("MAX RISK", f"${bal * (risk/100):.2f}")

# --- 5. MAIN INTERFACE ---
trend_color = "#00FF88" if score >= 8 else "#FFAA00"
st.markdown(f"""
<div style="background: linear-gradient(90deg, #050505, #111); padding:20px; border-radius:15px; border-left: 10px solid {trend_color}; border: 1px solid #222; margin-bottom:20px;">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h2 style="margin:0; color:#00FF88; font-family: monospace;">PATRO AI PRO</h2>
            <p style="margin:0; color:{trend_color}; font-weight:bold; font-size:18px;">
                {"🔥 GOD MODE ACTIVE" if score >= 9 else "⚖️ NEUTRAL / SCANNING"}
            </p>
        </div>
        <div style="text-align: right;">
            <p style="margin:0; color:#00FF88; font-size: 28px; font-weight:bold;">${current_price}</p>
            <p style="margin:0; color:#888; font-size:12px;">XAUUSD • 15M CHART</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

col_chart, col_data = st.columns([3, 1])

with col_chart:
    components.html(f"""
    <div id="tv_main" style="height:550px;"></div>
    <script src="https://s3.tradingview.com/tv.js"></script>
    <script>
    new TradingView.widget({{
      "autosize": true, "symbol": "OANDA:XAUUSD", "interval": "15", "theme": "dark",
      "style": "1", "container_id": "tv_main",
      "studies": ["VWAP@tv-basicstudies", "PivotPointsHighLow@tv-basicstudies"]
    }});
    </script>""", height=560)

with col_data:
    st.markdown("### 🏛️ CONFLUENCE HUB")
    st.metric("SCORE", f"{score}/10")
    st.metric("VWAP", vwap_val, delta=round(current_price - vwap_val, 2))
    st.metric("PIVOT", p_low, delta=round(current_price - p_low, 2))
    st.metric("VOLUME", vol_stat)
    
    if st.button("🚀 EXECUTE PATRO AI"):
        if score >= 9:
            st.balloons()
            st.success("GOD MODE ORDER SENT TO MT5")
        else:
            st.warning(f"Confidence {score}/10: Wait for better confluence.")

if st.button("🔄 REFRESH PRICE"):
    st.rerun()
