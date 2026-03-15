import streamlit as st
import streamlit.components.v1 as components

# 1. PAGE SETUP
st.set_page_config(page_title="PATRO AI PRO V12.1.33", layout="wide")
st.markdown("<style>.stApp { background: #000; color: #fff; }</style>", unsafe_allow_html=True)

# 2. THE MARKET KILLER HEADER (DXY & News)
ticker_html = """
<div class="tradingview-widget-container">
  <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js" async>
  {
  "symbols": [
    { "proName": "INDEX:DXY", "title": "USD INDEX (DXY)" },
    { "proName": "OANDA:XAUUSD", "title": "GOLD" },
    { "proName": "FX_IDC:EURUSD", "title": "EUR/USD" }
  ],
  "showSymbolLogo": true, "colorTheme": "dark", "isTransparent": true, "displayMode": "adaptive", "locale": "en"
}
  </script>
</div>
"""
components.html(ticker_tape_html, height=50)

# 3. SMC RISK CALCULATOR (The Account Saver)
st.sidebar.header("🛡️ RISK CALCULATOR")
balance = st.sidebar.number_input("Account Balance ($)", value=1000)
risk_percent = st.sidebar.slider("Risk Per Trade (%)", 0.5, 5.0, 1.0)
stop_loss_pips = st.sidebar.number_input("Stop Loss (Pips)", value=20)

risk_amount = balance * (risk_percent / 100)
# Standard Gold calculation for lot size
lot_size = risk_amount / (stop_loss_pips * 10) 

st.sidebar.success(f"PRO LOT SIZE: {lot_size:.2f}")
st.sidebar.info(f"You are risking: ${risk_amount:.2f}")

# 4. INSTITUTIONAL CORRELATION HUB
st.markdown("<h2 style='text-align:center; color:#00FF88;'>🏦 INSTITUTIONAL KILLER HUB</h2>", unsafe_allow_html=True)
col_gauge, col_dxy = st.columns([1, 1])

with col_gauge:
    # SMC Analysis Gauge
    gauge_html = """
    <div class="tradingview-widget-container">
      <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>
      { "interval": "15m", "width": "100%", "isTransparent": true, "height": "220", "symbol": "OANDA:XAUUSD", "showIntervalTabs": false, "displayMode": "single", "locale": "en", "colorTheme": "dark" }
      </script>
    </div>
    """
    components.html(gauge_html, height=230)

with col_dxy:
    # DXY Comparison (If DXY is Red, Gold is Green)
    st.markdown("<p style='text-align:center; color:#888;'>DXY CORRELATION (DOLLAR)</p>", unsafe_allow_html=True)
    dxy_gauge = """
    <div class="tradingview-widget-container">
      <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-mini-symbol-overview.js" async>
      { "symbol": "INDEX:DXY", "width": "100%", "height": "180", "locale": "en", "dateRange": "12M", "colorTheme": "dark", "trendLineColor": "#37a6ef", "underLineColor": "rgba(55, 166, 239, 0.15)", "isTransparent": true, "autosize": false }
      </script>
    </div>
    """
    components.html(dxy_gauge, height=190)

# 5. LIVE CHART
st.subheader("📊 LIVE XAUUSD MARKET STRUCTURE")
chart_html = """
<div class="tradingview-widget-container" style="height:600px;">
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
components.html(chart_html, height=600)

# 6. ECONOMIC CALENDAR (The News Filter)
calendar_html = """
<div class="tradingview-widget-container">
  <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-events.js" async>
  { "colorTheme": "dark", "isTransparent": true, "width": "100%", "height": "300", "locale": "en", "importanceFilter": "-1,0,1" }
  </script>
</div>
"""
components.html(calendar_html, height=310)
