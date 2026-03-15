import streamlit as st
import streamlit.components.v1 as components

# 1. PAGE SETUP
st.set_page_config(page_title="PATRO PRO V12.1.44", layout="wide")
st.markdown("<style>.stApp { background: #000; color: #fff; }</style>", unsafe_allow_html=True)

# 2. THE TOP MARKET TICKER
ticker_html = """
<div class="tradingview-widget-container">
  <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js" async>
  {
  "symbols": [
    { "proName": "TVC:DXY", "title": "USD INDEX" },
    { "proName": "OANDA:XAUUSD", "title": "GOLD" }
  ],
  "showSymbolLogo": true, "colorTheme": "dark", "isTransparent": true, "displayMode": "adaptive", "locale": "en"
  }
  </script>
</div>
"""
components.html(ticker_html, height=50)

# 3. DUAL-SIGNAL HUB (Now with Fixed DXY Source)
st.markdown("<h2 style='text-align:center; color:#00FF88;'>🏛️ INVERSE POWER HUB</h2>", unsafe_allow_html=True)

col_gold, col_dxy = st.columns(2)

with col_gold:
    st.markdown("<p style='text-align:center; color:#888;'>XAUUSD (GOLD) SIGNAL</p>", unsafe_allow_html=True)
    gold_gauge = """
    <div class="tradingview-widget-container">
      <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>
      { "interval": "15m", "width": "100%", "isTransparent": true, "height": "350", "symbol": "OANDA:XAUUSD", "showIntervalTabs": true, "displayMode": "single", "locale": "en", "colorTheme": "dark" }
      </script>
    </div>
    """
    components.html(gold_gauge, height=360)

with col_dxy:
    st.markdown("<p style='text-align:center; color:#888;'>DXY (DOLLAR INDEX) - FIXED</p>", unsafe_allow_html=True)
    # Changed from INDEX:DXY to TVC:DXY for better compatibility
    dxy_gauge = """
    <div class="tradingview-widget-container">
      <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>
      { "interval": "15m", "width": "100%", "isTransparent": true, "height": "350", "symbol": "TVC:DXY", "showIntervalTabs": true, "displayMode": "single", "locale": "en", "colorTheme": "dark" }
      </script>
    </div>
    """
    components.html(dxy_gauge, height=360)

# 4. LIVE CORRELATION CHART (Overlaying TVC:DXY)
st.subheader("📊 CORRELATION: XAUUSD vs TVC:DXY")
comparison_chart = """
<div class="tradingview-widget-container" style="height:500px;">
  <div id="tv_comparison"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
  <script type="text/javascript">
  new TradingView.widget({
    "autosize": true, "symbol": "OANDA:XAUUSD", "interval": "15",
    "theme": "dark", "style": "1", "container_id": "tv_comparison",
    "studies": [
        { "id": "Overlay@tv-basicstudies", "inputs": { "symbol": "TVC:DXY" } }
    ]
  });
  </script>
</div>
"""
components.html(comparison_chart, height=510)

# 5. SIDEBAR
st.sidebar.header("🛡️ RISK & RULES")
bal = st.sidebar.number_input("Balance", value=1000)
risk = st.sidebar.slider("Risk %", 0.5, 3.0, 1.0)
sl = st.sidebar.number_input("SL Pips", value=30)
st.sidebar.success(f"PRO LOT: {(bal * (risk/100)) / (sl * 10):.2f}")
