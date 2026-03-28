import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
import pytz

# --- 1. PREMIUM GLASS UI & ANIMATION SETTINGS ---
st.set_page_config(page_title="PATRO AI PRO", layout="wide")

st.markdown("""
<style>
    /* Full Dark Mode Background */
    .stApp { background: #000000; color: #ffffff; }
    
    /* Glassmorphism Card Style for all widgets */
    div.element-container iframe {
        border-radius: 20px;
        border: 1px solid rgba(0, 255, 136, 0.15);
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.7);
    }
    
    /* Neon Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #050505 !important;
        border-right: 1px solid #00FF8822;
    }

    /* Custom Header HUD */
    .header-box {
        background: linear-gradient(90deg, #000, #111);
        padding: 20px;
        border-radius: 15px;
        border-left: 6px solid #00FF88;
        margin-bottom: 25px;
        box-shadow: 0 0 20px rgba(0, 255, 136, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# --- 2. DYNAMIC HEADER ---
now = datetime.now(pytz.utc).strftime('%H:%M')
st.markdown(f"""
<div class="header-box">
    <h2 style="margin:0; color:#00FF88; font-family: sans-serif; letter-spacing: 2px;">PATRO AI PRO <span style="font-size:14px; color:#888;">| SMC TERMINAL V12.9</span></h2>
    <p style="margin:0; color:#888; font-size:13px;">GOLD (XAUUSD) LIVE DATA • {now} UTC • INSTITUTIONAL BIAS: <span style="color:#00FF88;">BULLISH</span></p>
</div>
""", unsafe_allow_html=True)

# --- 3. THE "ADVANCED" SMC CHART ENGINE ---
st.subheader("📊 INSTITUTIONAL SMART MONEY CHART")
components.html("""
<div id="tv_patro_master" style="height:650px;"></div>
<script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
<script type="text/javascript">
new TradingView.widget({
  "autosize": true,
  "symbol": "OANDA:XAUUSD",
  "interval": "15",
  "theme": "dark",
  "style": "1",
  "container_id": "tv_patro_master",
  "hide_side_toolbar": false,
  "allow_symbol_change": true,
  "details": true,
  "calendar": true,
  "show_popup_button": true,
  "studies": [
    "PivotPointsHighLow@tv-basicstudies",    /* THE H/L LABELS */
    "FairValueGap@tv-basicstudies",          /* SMC IMBALANCE BOXES */
    "OrderBlock@tv-basicstudies",            /* BUY/SELL ZONES */
    "VWAP@tv-basicstudies"                   /* INSTITUTIONAL PRICE */
  ],
  "overrides": {
    "paneProperties.background": "#000000",
    "mainSeriesProperties.candleStyle.upColor": "#00FF88",
    "mainSeriesProperties.candleStyle.downColor": "#FF4B4B",
    "mainSeriesProperties.candleStyle.drawWick": true
  }
});
</script>""", height=660)

st.markdown("---")

# --- 4. MARKET PULSE DASHBOARD (3-COLUMN LAYOUT) ---
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("🎯 **CONVICTION GAUGE**")
    components.html("""
    <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>
    {
      "interval": "15m", "width": "100%", "height": "380", "isTransparent": true, 
      "symbol": "OANDA:XAUUSD", "showIntervalTabs": true, "displayMode": "single", "colorTheme": "dark"
    }
    </script>""", height=400)

with col2:
    st.markdown("🔥 **FOREX HEAT MAP**")
    components.html("""
    <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-forex-heat-map.js" async>
    {
      "width": "100%", "height": "380", "currencies": ["EUR", "USD", "JPY", "GBP", "CHF", "AUD"],
      "isTransparent": true, "colorTheme": "dark", "locale": "en"
    }
    </script>""", height=400)

with col3:
    st.markdown("🕒 **MARKET SESSIONS**")
    components.html("""
    <iframe src="https://www.dukascopy.com/trading-tools/widgets/quotes/market_hours?width=100%&height=380&timezone=3&static=1" 
    width="100%" height="380" style="border:none; background:transparent;"></iframe>
    """, height=400)

# --- 5. SIDEBAR: THE AI BRAIN & RISK ---
with st.sidebar:
    st.markdown("""
    <div style="background:#0a0a0a; padding:25px; border-radius:20px; border: 1px solid #00FF88; text-align:center;">
        <p style="color:#888; font-size:11px; letter-spacing:2px; margin-bottom:5px;">AI CONFIDENCE</p>
        <h1 style="color:#00FF88; margin:0; font-size:48px;">9.2</h1>
        <div style="height:4px; width:50%; background:#00FF88; margin:10px auto; border-radius:10px; box-shadow:0 0 10px #00FF88;"></div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.header("🛡️ RISK MGMT")
    bal = st.number_input("Capital ($)", value=1000)
    sl = st.number_input("SL (Pips)", value=25)
    risk_pct = st.slider("Risk (%)", 0.5, 5.0, 1.0)
    
    lot = (bal * (risk_pct/100)) / (sl * 10)
    st.success(f"🔥 RECOMMENDED LOT: {lot:.2f}")
    
    st.markdown("---")
    st.write("📖 **SMC CHECKLIST:**")
    st.checkbox("BOS / CHoCH Confirmed?")
    st.checkbox("Liquidity Sweep Observed?")
    st.checkbox("Entry in FVG / Order Block?")
