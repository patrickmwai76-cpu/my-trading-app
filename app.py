import streamlit as st
import streamlit.components.v1 as components

# 1. CORE INTERFACE
st.set_page_config(page_title="PATRO AI PRO V12.1.25", layout="wide")
st.markdown("""
    <style>
    .stApp { background: #000; color: #fff; }
    iframe { border-radius: 15px !important; border: 1px solid #333 !important; }
    </style>
""", unsafe_allow_html=True)

# 2. SIDEBAR COMMANDS
with st.sidebar:
    st.header("🏢 SMC COMMAND")
    asset_choice = st.selectbox("Select Target", ["GOLD (XAUUSD)", "GBPUSD", "US30", "BITCOIN"])
    
    tv_symbols = {
        "GOLD (XAUUSD)": "OANDA:XAUUSD", "GBPUSD": "FX:GBPUSD",
        "US30": "CURRENCYCOM:US30", "BITCOIN": "BINANCE:BTCUSDT"
    }
    target_sym = tv_symbols[asset_choice]

    st.divider()
    st.subheader("✅ NO-FAKE CHECKLIST")
    c1 = st.checkbox("SMC Zone Touched?")
    c2 = st.checkbox("CHoCH/BOS Confirmed?")
    c3 = st.checkbox("Gauge says 'STRONG'?")
    
    if c1 and c2 and c3:
        st.success("🔥 SIGNAL: HIGH CONVICTION")
    else:
        st.warning("⚠️ STATUS: ANALYZING")

# 3. TOP DASHBOARD (The Signal Filter)
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    status_text = "BANK ENTRY ACTIVE" if (c1 and c2 and c3) else "WAITING FOR SMC SETUP"
    border_col = "#00FF88" if (c1 and c2 and c3) else "#555"
    st.markdown(f"""
        <div style='border:3px solid {border_col}; padding:20px; border-radius:15px; background:#111; text-align:center;'>
            <h1 style='color:{border_col}; margin:0;'>{status_text}</h1>
        </div>
    """, unsafe_allow_html=True)

with col2:
    # Technical Gauge
    gauge_html = f"""
    <div class="tradingview-widget-container">
      <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>
      {{ "interval": "5m", "width": "100%", "isTransparent": true, "height": "180", "symbol": "{target_sym}", "showIntervalTabs": false, "displayMode": "single", "locale": "en", "colorTheme": "dark" }}
      </script>
    </div>
    """
    components.html(gauge_html, height=190)

with col3:
    st.metric("SMC SPREAD", "0.1", "Low Cost")
    st.metric("VOLATILITY", "High", "Optimal")

# 4. THE LIVE CHART (Popup Button Restored)
st.subheader(f"📊 {asset_choice} 5M STRUCTURE")
chart_html = f"""
<div class="tradingview-widget-container" style="height:600px;">
  <div id="tradingview_chart"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
  <script type="text/javascript">
  new TradingView.widget({{
    "autosize": true,
    "symbol": "{target_sym}",
    "interval": "5",
    "timezone": "Etc/UTC",
    "theme": "dark",
    "style": "1",
    "locale": "en",
    "enable_publishing": false,
    "hide_side_toolbar": false,
    "allow_symbol_change": true,
    "show_popup_button": true,  /* This restores the pop-up expand button */
    "popup_width": "1000",
    "popup_height": "650",
    "container_id": "tradingview_chart",
    "studies": ["RSI@tv-basicstudies", "BollingerBands@tv-basicstudies"]
  }});
  </script>
</div>
"""
components.html(chart_html, height=600)

# 5. MARKET SESSIONS
st.divider()
st.subheader("🕒 LIVE MARKET SESSIONS (EST)")
s1, s2, s3 = st.columns(3)
s1.info("**LONDON**\n3:00 AM - 12:00 PM")
s2.success("**NEW YORK**\n8:00 AM - 5:00 PM")
s3.warning("**TOKYO**\n7:00 PM - 4:00 AM")
