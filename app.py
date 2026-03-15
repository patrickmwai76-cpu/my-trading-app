import streamlit as st
import streamlit.components.v1 as components

# 1. PAGE SETUP
st.set_page_config(page_title="PATRO AI PRO V12.1.27", layout="wide")
st.markdown("<style>.stApp { background: #000; color: #fff; }</style>", unsafe_allow_html=True)

# 2. THE SIGNAL FILTER GAUGE (Use this while you search for the indicator)
st.markdown("<h2 style='text-align:center; color:#00FF88;'>🏦 SMART MONEY ANALYSIS HUB</h2>", unsafe_allow_html=True)
col1, col2 = st.columns([1, 1])

with col1:
    # Technical Analysis Widget (Acts as an automatic SMC filter)
    ta_gauge = """
    <div class="tradingview-widget-container">
      <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>
      { "interval": "5m", "width": "100%", "isTransparent": true, "height": "220", "symbol": "OANDA:XAUUSD", "showIntervalTabs": true, "displayMode": "single", "locale": "en", "colorTheme": "dark" }
      </script>
    </div>
    """
    components.html(ta_gauge, height=230)

with col2:
    st.markdown("""
        <div style='background:#111; padding:20px; border-radius:15px; border:1px solid #333; height:220px;'>
            <h3 style='color:#00FF88; margin-top:0;'>🛡️ NO-FAKE PROTOCOL</h3>
            <p>1. Check the Gauge on the left.</p>
            <p>2. Only trade if it says <b>"STRONG BUY"</b> or <b>"STRONG SELL"</b>.</p>
            <p>3. If it says "Neutral", the SMC signal is likely fake.</p>
        </div>
    """, unsafe_allow_html=True)

# 3. THE ADVANCED CHART (Unlocks more Indicator options)
st.subheader("📊 LIVE SMC STRUCTURE (ADVANCED VIEW)")
advanced_chart = """
<div class="tradingview-widget-container" style="height:650px;">
  <div id="tradingview_advanced"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
  <script type="text/javascript">
  new TradingView.widget({
    "autosize": true,
    "symbol": "OANDA:XAUUSD",
    "interval": "5",
    "timezone": "Etc/UTC",
    "theme": "dark",
    "style": "1",
    "locale": "en",
    "toolbar_bg": "#f1f3f6",
    "enable_publishing": false,
    "withdateranges": true,
    "hide_side_toolbar": false,
    "allow_symbol_change": true,
    "details": true,
    "hotlist": true,
    "calendar": true,
    "show_popup_button": true,
    "popup_width": "1000",
    "popup_height": "650",
    "container_id": "tradingview_advanced"
  });
  </script>
</div>
"""
components.html(advanced_chart, height=650)
