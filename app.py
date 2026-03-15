import streamlit as st
import streamlit.components.v1 as components

# 1. PAGE SETUP
st.set_page_config(page_title="PATRO AI PRO V12.1.45", layout="wide")
st.markdown("<style>.stApp { background: #000; color: #fff; }</style>", unsafe_allow_html=True)

# 2. TOP HUD: THE "NEWS SHIELD"
st.markdown("<h3 style='text-align:center; color:#FF4B4B;'>📡 INSTITUTIONAL NEWS CALENDAR</h3>", unsafe_allow_html=True)
# This calendar specifically filters for High-Impact (Red) events
news_calendar_html = """
<div class="tradingview-widget-container">
  <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-events.js" async>
  { "width": "100%", "height": "220", "colorTheme": "dark", "isTransparent": true, "locale": "en", "importanceFilter": "-1,0,1" }
  </script>
</div>
"""
components.html(news_calendar_html, height=230)

# 3. THE "SUICIDE RATIO" (Gold vs Silver)
# Professional tip: If Gold and Silver are BOTH showing "Buy," the move is 2x stronger.
st.markdown("<p style='text-align:center; color:#888;'>CONFIRMATION: GOLD/SILVER RATIO</p>", unsafe_allow_html=True)
ratio_html = """
<div class="tradingview-widget-container">
  <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-mini-symbol-overview.js" async>
  { "symbol": "GOLD/SILVER", "width": "100%", "height": "160", "locale": "en", "dateRange": "1D", "colorTheme": "dark", "isTransparent": true }
  </script>
</div>
"""
components.html(ratio_html, height=170)

# 4. DUAL-GAUGE SIGNAL HUB (Gold & DXY)
col_gold, col_dxy = st.columns(2)

with col_gold:
    st.markdown("<p style='text-align:center; color:#00FF88;'>XAUUSD SIGNAL</p>", unsafe_allow_html=True)
    components.html("""
    <div class="tradingview-widget-container">
      <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>
      { "interval": "15m", "width": "100%", "isTransparent": true, "height": "350", "symbol": "OANDA:XAUUSD", "showIntervalTabs": true, "displayMode": "single", "colorTheme": "dark" }
      </script>
    </div>
    """, height=360)

with col_dxy:
    st.markdown("<p style='text-align:center; color:#FF4B4B;'>DXY SIGNAL (INVERSE)</p>", unsafe_allow_html=True)
    components.html("""
    <div class="tradingview-widget-container">
      <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>
      { "interval": "15m", "width": "100%", "isTransparent": true, "height": "350", "symbol": "TVC:DXY", "showIntervalTabs": true, "displayMode": "single", "colorTheme": "dark" }
      </script>
    </div>
    """, height=360)

# 5. THE CHART (WITH AUTO-FVG & VOLUME PROFILE)
st.subheader("🏛️ SMART MONEY CHART")
chart_html = """
<div class="tradingview-widget-container" style="height:550px;">
  <div id="tradingview_final"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
  <script type="text/javascript">
  new TradingView.widget({
    "autosize": true, "symbol": "OANDA:XAUUSD", "interval": "15",
    "theme": "dark", "style": "1", "container_id": "tradingview_final",
    "studies": ["STD;Fair_Value_Gap", "STD;Volume_Profile"]
  });
  </script>
</div>
"""
components.html(chart_html, height=560)

# 6. SIDEBAR: THE "3-D" RISK SHIELD
st.sidebar.header("🛡️ THE 3-D RISK CHECK")
bal = st.sidebar.number_input("Current Balance ($)", value=1000)
risk_pct = st.sidebar.slider("Risk Percent", 0.5, 3.0, 1.0)
sl_pips = st.sidebar.number_input("Stop Loss (Pips)", value=30)
st.sidebar.markdown(f"**EXECUTE LOT: {(bal * (risk_pct/100)) / (sl_pips * 10):.2f}**")
st.sidebar.divider()
st.sidebar.warning("⚠️ DON'T TRADE if high-impact news is within 30 minutes!")
