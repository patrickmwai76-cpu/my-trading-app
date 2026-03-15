import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
import pytz

# 1. PAGE SETUP
st.set_page_config(page_title="PATRO AI PRO V12.1.50", layout="wide")
st.markdown("<style>.stApp { background: #000; color: #fff; }</style>", unsafe_allow_html=True)

# 2. TOP HUD: NEWS & KILLZONES
def get_status():
    now = datetime.now(pytz.utc)
    if 13 <= now.hour < 16: return "🔥 NY KILLZONE ACTIVE"
    elif 8 <= now.hour < 11: return "⚡ LONDON OPEN"
    return "💤 LOW VOLUME"

st.markdown(f"<h3 style='text-align:center; color:#FF4B4B;'>{get_status()} | LIVE NEWS CALENDAR</h3>", unsafe_allow_html=True)
components.html("""
<div class="tradingview-widget-container">
  <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-events.js" async>
  { "width": "100%", "height": "200", "colorTheme": "dark", "isTransparent": true, "importanceFilter": "-1,0,1" }
  </script>
</div>
""", height=210)

# 3. DUAL-SIGNAL GAUGE HUB (XAUUSD & DXY)
st.markdown("---")
col_g, col_d = st.columns(2)
with col_g:
    st.markdown("<h4 style='text-align:center; color:#00FF88;'>GOLD (XAUUSD) SIGNAL</h4>", unsafe_allow_html=True)
    components.html("""
    <div class="tradingview-widget-container"><script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>
    { "interval": "15m", "width": "100%", "height": "380", "isTransparent": true, "symbol": "OANDA:XAUUSD", "showIntervalTabs": true, "displayMode": "single", "colorTheme": "dark" }
    </script></div>
    """, height=390)

with col_d:
    st.markdown("<h4 style='text-align:center; color:#FF4B4B;'>DOLLAR (DXY) SIGNAL</h4>", unsafe_allow_html=True)
    components.html("""
    <div class="tradingview-widget-container"><script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>
    { "interval": "15m", "width": "100%", "height": "380", "isTransparent": true, "symbol": "TVC:DXY", "showIntervalTabs": true, "displayMode": "single", "colorTheme": "dark" }
    </script></div>
    """, height=390)

# 4. MARKET TICKER
components.html("""
<div class="tradingview-widget-container"><script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js" async>
{ "symbols": [{"proName": "TVC:DXY", "title": "DXY"}, {"proName": "OANDA:XAUUSD", "title": "GOLD"}], "colorTheme": "dark", "isTransparent": true }
</script></div>
""", height=50)

# 5. THE SMC CHART (With Pop-up button restored)
st.subheader("📊 SMART MONEY CHART (SMC)")
components.html("""
<div class="tradingview-widget-container" style="height:600px;">
  <div id="tv_final"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
  <script type="text/javascript">
  new TradingView.widget({
    "autosize": true, "symbol": "OANDA:XAUUSD", "interval": "15",
    "theme": "dark", "style": "1", "container_id": "tv_final",
    "show_popup_button": true,
    "popup_width": "1000",
    "popup_height": "650",
    "studies": ["STD;Fair_Value_Gap", "STD;Order_Block", "STD;Pivot_Points_High_Low", "STD;VWAP"]
  });
  </script>
</div>
""", height=610)

# 6. SIDEBAR: RISK CALCULATOR
st.sidebar.header("🛡️ RISK & TARGETS")
bal = st.sidebar.number_input("Balance ($)", value=1000)
risk_pct = st.sidebar.slider("Risk %", 0.5, 3.0, 1.0)
sl_pips = st.sidebar.number_input("Stop Loss (Pips)", value=30)
reward_ratio = st.sidebar.slider("Reward Ratio (1:X)", 1.5, 5.0, 2.0)

# Lot Calc
risk_amount = bal * (risk_pct / 100)
lot_size = risk_amount / (sl_pips * 10)
tp_pips = sl_pips * reward_ratio

st.sidebar.markdown("---")
st.sidebar.success(f"🔥 USE LOT: {lot_size:.2f}")
st.sidebar.info(f"🎯 TARGET TP: {tp_pips:.0f} PIPS")
st.sidebar.error(f"🛑 STOP LOSS: {sl_pips} PIPS")
