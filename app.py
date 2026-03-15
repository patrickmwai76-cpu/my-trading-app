import streamlit as st
import streamlit.components.v1 as components

# 1. PAGE SETUP
st.set_page_config(page_title="PATRO PRO V12.1.43", layout="wide")
st.markdown("<style>.stApp { background: #000; color: #fff; }</style>", unsafe_allow_html=True)

# 2. THE TOP MARKET TICKER
ticker_html = """
<div class="tradingview-widget-container">
  <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js" async>
  {
  "symbols": [
    { "proName": "INDEX:DXY", "title": "USD INDEX" },
    { "proName": "OANDA:XAUUSD", "title": "GOLD" }
  ],
  "showSymbolLogo": true, "colorTheme": "dark", "isTransparent": true, "displayMode": "adaptive", "locale": "en"
  }
  </script>
</div>
"""
components.html(ticker_html, height=50)

# 3. DUAL-SIGNAL COMMAND CENTER
st.markdown("<h2 style='text-align:center; color:#00FF88;'>🏛️ INVERSE POWER HUB</h2>", unsafe_allow_html=True)

# We use two columns to put the Gold Signal and Dollar Signal side-by-side
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
    st.markdown("<p style='text-align:center; color:#888;'>DXY (DOLLAR) SIGNAL</p>", unsafe_allow_html=True)
    dxy_gauge = """
    <div class="tradingview-widget-container">
      <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>
      { "interval": "15m", "width": "100%", "isTransparent": true, "height": "350", "symbol": "INDEX:DXY", "showIntervalTabs": true, "displayMode": "single", "locale": "en", "colorTheme": "dark" }
      </script>
    </div>
    """
    components.html(dxy_gauge, height=360)

# 4. THE MASTER COMPARISON CHART
st.subheader("📊 CORRELATION: GOLD VS. DOLLAR")
# This chart overlay is the ultimate "No-Miss" tool
comparison_chart = """
<div class="tradingview-widget-container" style="height:500px;">
  <div id="tv_comparison"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
  <script type="text/javascript">
  new TradingView.widget({
    "autosize": true, "symbol": "OANDA:XAUUSD", "interval": "15",
    "theme": "dark", "style": "1", "container_id": "tv_comparison",
    "studies": [
        { "id": "Overlay@tv-basicstudies", "inputs": { "symbol": "INDEX:DXY" } }
    ]
  });
  </script>
</div>
"""
components.html(comparison_chart, height=510)

# 5. RISK SIDEBAR
st.sidebar.header("🛡️ RISK & CHECKLIST")
bal = st.sidebar.number_input("Balance ($)", value=1000)
risk = st.sidebar.slider("Risk %", 0.5, 3.0, 1.0)
sl = st.sidebar.number_input("SL Pips", value=30)
st.sidebar.success(f"PRO LOT: {(bal * (risk/100)) / (sl * 10):.2f}")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🏹 THE KILLER RULE")
st.sidebar.info("BUY GOLD only if DXY Gauge is RED (Sell).")
st.sidebar.info("SELL GOLD only if DXY Gauge is GREEN (Buy).")
