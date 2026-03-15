import streamlit as st
import streamlit.components.v1 as components
import pandas as pd

# 1. THEME & LAYOUT
st.set_page_config(page_title="PATRO AI PRO V12.1.23", layout="wide")
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
        "GOLD (XAUUSD)": "OANDA:XAUUSD",
        "GBPUSD": "FX:GBPUSD",
        "US30": "CURRENCYCOM:US30",
        "BITCOIN": "BINANCE:BTCUSDT"
    }
    target_sym = tv_symbols[asset_choice]

    st.divider()
    st.subheader("✅ ANTI-FAKE CHECKLIST")
    c1 = st.checkbox("SMC Zone Touched?")
    c2 = st.checkbox("CHoCH/BOS Confirmed?")
    c3 = st.checkbox("Volume Spike Detected?")
    
    if c1 and c2 and c3:
        st.success("🔥 SIGNAL: HIGH CONVICTION")
    else:
        st.warning("⚠️ STATUS: ANALYZING STRUCTURE")

# 3. TOP DASHBOARD (TikTok Style)
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    status_text = "BANK BUY ZONE" if (c1 and c2 and c3) else "WAITING FOR LIQUIDITY"
    border_col = "#00FF88" if (c1 and c2 and c3) else "#555"
    st.markdown(f"""
        <div style='border:3px solid {border_col}; padding:20px; border-radius:15px; background:#111; text-align:center;'>
            <h1 style='color:{border_col}; margin:0;'>{status_text}</h1>
            <p style='color:gray; margin:0;'>Institutional Flow Analysis Active</p>
        </div>
    """, unsafe_allow_html=True)

with col2:
    # Live Technical Gauge for "Sure" Signals
    gauge_html = f"""
    <div class="tradingview-widget-container">
      <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>
      {{
      "interval": "5m",
      "width": "100%",
      "isTransparent": true,
      "height": "180",
      "symbol": "{target_sym}",
      "showIntervalTabs": false,
      "displayMode": "single",
      "locale": "en",
      "colorTheme": "dark"
    }}
      </script>
    </div>
    """
    components.html(gauge_html, height=200)

with col3:
    st.metric("CONFIDENCE", "92%" if (c1 and c2) else "40%", "+5% Today")

# 4. THE LIVE CHART (With Auto-Indicators)
st.subheader(f"📊 {asset_choice} LIVE SMC STRUCTURE")

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
    "container_id": "tradingview_chart",
    "studies": [
      "RSI@tv-basicstudies",
      "BollingerBands@tv-basicstudies",
      "Volume@tv-basicstudies"
    ]
  }});
  </script>
</div>
"""
components.html(chart_html, height=600)

# 5. SMC RULES BOX
st.divider()
st.markdown("### 🏛️ SMART MONEY RULES")
r1, r2, r3 = st.columns(3)
r1.info("**STEP 1: Identify**\nWait for price to hit a Supply or Demand zone.")
r2.info("**STEP 2: Confirm**\nLook for RSI to cross 50 and Volume to turn Green.")
r3.info("**STEP 3: Execute**\nEnter with a 1:3 Risk/Reward ratio.")
