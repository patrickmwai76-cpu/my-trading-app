import streamlit as st
import streamlit.components.v1 as components

# 1. CORE INTERFACE
st.set_page_config(page_title="PATRO AI PRO V12.1.39", layout="wide")
st.markdown("<style>.stApp { background: #000; color: #fff; }</style>", unsafe_allow_html=True)

# 2. THE TOP MARKET TICKER
ticker_html = """
<div class="tradingview-widget-container">
  <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js" async>
  {
  "symbols": [
    { "proName": "INDEX:DXY", "title": "USD INDEX" },
    { "proName": "OANDA:XAUUSD", "title": "GOLD" },
    { "proName": "BITSTAMP:BTCUSD", "title": "BTC" }
  ],
  "showSymbolLogo": true, "colorTheme": "dark", "isTransparent": true, "displayMode": "adaptive", "locale": "en"
  }
  </script>
</div>
"""
components.html(ticker_html, height=50)

# 3. THE MASTER SIGNAL HUB (Single Gauge with Multi-Timeframe Tabs)
st.markdown("<h2 style='text-align:center; color:#00FF88;'>🎯 MASTER SIGNAL HUB</h2>", unsafe_allow_html=True)

col_gauge, col_heatmap = st.columns([1, 1])

with col_gauge:
    # Single Gauge with Tabs (1m, 5m, 15m, 1h, 4h, 1D)
    st.markdown("<p style='text-align:center; color:#888;'>TECHNICAL SUMMARY (CLICK TABS TO SWITCH)</p>", unsafe_allow_html=True)
    master_gauge_html = """
    <div class="tradingview-widget-container">
      <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>
      {
        "interval": "15m",
        "width": "100%",
        "isTransparent": true,
        "height": "380",
        "symbol": "OANDA:XAUUSD",
        "showIntervalTabs": true,
        "displayMode": "single",
        "locale": "en",
        "colorTheme": "dark"
      }
      </script>
    </div>
    """
    components.html(master_gauge_html, height=390)

with col_heatmap:
    # Forex Heatmap to check USD Strength vs Others
    st.markdown("<p style='text-align:center; color:#888;'>GLOBAL CURRENCY STRENGTH</p>", unsafe_allow_html=True)
    heatmap_html = """
    <div class="tradingview-widget-container">
      <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-forex-heat-map.js" async>
      { "width": "100%", "height": "380", "currencies": ["EUR", "USD", "JPY", "GBP", "CHF", "AUD", "CAD"], "isTransparent": true, "colorTheme": "dark", "locale": "en" }
      </script>
    </div>
    """
    components.html(heatmap_html, height=390)

# 4. THE LIVE CHART (VWAP Anchor)
st.subheader("📊 LIVE XAUUSD (GOLD) STRUCTURE")
chart_html = """
<div class="tradingview-widget-container" style="height:550px;">
  <div id="tradingview_chart"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
  <script type="text/javascript">
  new TradingView.widget({
    "autosize": true, "symbol": "OANDA:XAUUSD", "interval": "15",
    "timezone": "Etc/UTC", "theme": "dark", "style": "1",
    "locale": "en", "toolbar_bg": "#111", "enable_publishing": false,
    "hide_side_toolbar": false, "allow_symbol_change": true,
    "show_popup_button": true, "container_id": "tradingview_chart",
    "studies": ["VWAP@tv-basicstudies"]
  });
  </script>
</div>
"""
components.html(chart_html, height=550)

# 5. RISK CALCULATOR (Sidebar)
st.sidebar.header("🛡️ RISK MANAGEMENT")
balance = st.sidebar.number_input("Account Balance ($)", value=1000)
risk_pct = st.sidebar.slider("Risk Per Trade (%)", 0.5, 3.0, 1.0)
sl_pips = st.sidebar.number_input("Stop Loss (Pips)", value=30)

risk_cash = balance * (risk_pct / 100)
pro_lot = risk_cash / (sl_pips * 10)

st.sidebar.success(f"🔥 PRO LOT SIZE: {pro_lot:.2f}")
st.sidebar.info(f"Risking: ${risk_cash:.2f}")
