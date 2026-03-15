import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
import pytz

# 1. THE "KILLZONE" ENGINE (When to trade)
def get_market_status():
    now_utc = datetime.now(pytz.utc)
    # New York Killzone: 13:00 - 16:00 UTC (The highest Gold volume)
    if 13 <= now_utc.hour < 16:
        return "🔥 NY KILLZONE ACTIVE (HIGH VOLATILITY)"
    # London Open: 08:00 - 11:00 UTC
    elif 8 <= now_utc.hour < 11:
        return "⚡ LONDON OPEN (TREND SETTING)"
    return "💤 LOW VOLUME (WAIT FOR OPEN)"

# 2. INTERFACE SETUP
st.set_page_config(page_title="PATRO PRO FINAL", layout="wide")
st.markdown("<style>.stApp { background: #000; color: #fff; }</style>", unsafe_allow_html=True)

# 3. TOP HUD (Live Session & Ticker)
status = get_market_status()
st.markdown(f"<h4 style='text-align:center; color:#FF4B4B;'>{status}</h4>", unsafe_allow_html=True)

# 4. THE MASTER GAUGE (Unified Timeframes)
st.markdown("<h3 style='text-align:center; color:#00FF88;'>🎯 UNIFIED SIGNAL HUB</h3>", unsafe_allow_html=True)
gauge_html = """
<div class="tradingview-widget-container">
  <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>
  {
    "interval": "15m", "width": "100%", "height": "400", "isTransparent": true,
    "symbol": "OANDA:XAUUSD", "showIntervalTabs": true, "displayMode": "single", "colorTheme": "dark"
  }
  </script>
</div>
"""
components.html(gauge_html, height=410)

# 5. THE SMC STRUCTURE CHART (Missing Piece: Auto-labels Order Blocks)
st.markdown("### 🏛️ SMC STRUCTURE & LIQUIDITY")
smc_chart_html = """
<div class="tradingview-widget-container" style="height:550px;">
  <div id="tradingview_smc"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
  <script type="text/javascript">
  new TradingView.widget({
    "autosize": true, "symbol": "OANDA:XAUUSD", "interval": "15",
    "theme": "dark", "style": "1", "container_id": "tradingview_smc",
    "studies": [
        "STD;Fair_Value_Gap", 
        "STD;Order_Block"
    ],
    "show_popup_button": true
  });
  </script>
</div>
"""
components.html(smc_chart_html, height=550)

# 6. THE "GOLD KILLER" CHECKLIST (Sidebar)
st.sidebar.header("🛡️ FINAL EXECUTION")
st.sidebar.markdown("---")
# Risk Calc
bal = st.sidebar.number_input("Balance ($)", 1000)
risk = st.sidebar.slider("Risk %", 0.5, 3.0, 1.0)
sl = st.sidebar.number_input("SL Pips", 30)
lot = (bal * (risk/100)) / (sl * 10)
st.sidebar.success(f"LOT SIZE: {lot:.2f}")

st.sidebar.markdown("### ✅ THE 3-STEP CHECK")
c1 = st.sidebar.checkbox("1H & 15m Gauge Match?")
c2 = st.sidebar.checkbox("DXY Moving Opposite?")
c3 = st.sidebar.checkbox("Killzone Active?")

if c1 and c2 and c3:
    st.sidebar.balloons()
    st.sidebar.warning("🚀 ALL CONFLUENCE MET: HIGH PROBABILITY")
