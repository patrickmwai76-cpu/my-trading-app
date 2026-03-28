import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
import pytz

# --- 1. SAFE IMPORT FOR TRADINGVIEW_TA ---
try:
    from tradingview_ta import TA_Handler, Interval
    HAS_TA = True
except ImportError:
    HAS_TA = False

# --- 2. THEME & ADVANCED GLASS CSS ---
st.set_page_config(page_title="PATRO AI PRO", layout="wide")

st.markdown("""
<style>
    .stApp { background: #000; color: #fff; }
    [data-testid="stVerticalBlock"] > div:has(div.tradingview-widget-container) {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 10px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .stSidebar { background-color: #050505 !important; }
</style>
""", unsafe_allow_html=True)

# --- 3. LIVE DATA ENGINE (With Error Handling) ---
def get_live_data():
    if not HAS_TA:
        return 5.0, "SYNCING", "#888"
    try:
        handler = TA_Handler(symbol="XAUUSD", screener="forex", exchange="OANDA", interval="15m")
        rec = handler.get_analysis().summary['RECOMMENDATION']
        if "STRONG_BUY" in rec: return 9.2, "🚀 STRONG BUY", "#00FF88"
        if "BUY" in rec: return 7.5, "🚀 BUY", "#00FF88"
        if "SELL" in rec: return 2.5, "📉 SELL", "#FF4B4B"
        return 5.0, "⚖️ NEUTRAL", "#FFA500"
    except:
        return 5.0, "OFFLINE", "#444"

score, signal, s_col = get_live_data()

# --- 4. TOP HUD ---
st.markdown(f"""
<div style="text-align:center; padding:15px; border-bottom: 2px solid {s_col};">
    <h2 style="color:{s_col}; margin:0;">{signal} | {score}/10</h2>
    <p style="color:#888; margin:0;">PATRO AI ALGORITHM V12.8.6</p>
</div>
""", unsafe_allow_html=True)

# --- 5. THE ADVANCED SMC CHART (Fixed Study Names) ---
st.subheader("📊 MASTER SMC TERMINAL")
components.html(f"""
<div id="tv_chart_main" style="height:600px;"></div>
<script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
<script type="text/javascript">
new TradingView.widget({{
  "autosize": true, "symbol": "OANDA:XAUUSD", "interval": "15", "theme": "dark", "style": "1",
  "container_id": "tv_chart_main",
  "show_popup_button": true,
  "studies": [
    "PivotPointsHighLow@tv-basicstudies", 
    "VWAP@tv-basicstudies"
  ]
}});
</script>""", height=610)

# --- 6. SIDEBAR RISK & STATUS ---
with st.sidebar:
    st.title("🛡️ TERMINAL")
    st.metric("BIAS", signal, delta=score, delta_color="normal")
    
    st.markdown("---")
    bal = st.number_input("Balance ($)", value=1000)
    sl = st.number_input("Stop Loss (Pips)", value=30)
    risk = st.slider("Risk %", 0.5, 3.0, 1.0)
    
    lot = (bal * (risk/100)) / (sl * 10)
    st.success(f"🔥 REC LOT: {lot:.2f}")

    if not HAS_TA:
        st.error("Error: Run 'pip install tradingview-ta' in your terminal.")
