import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
import pytz
from tradingview_ta import TA_Handler, Interval
from streamlit_autorefresh import st_autorefresh

# 1. ADVANCED UI STYLING (The "Glassmorphism" Look)
st.set_page_config(page_title="PATRO AI PRO", layout="wide")

st.markdown("""
<style>
    /* Global App Background */
    .stApp {
        background: radial-gradient(circle at top right, #1a1a2e, #000000);
        color: #ffffff;
    }
    
    /* Glassmorphism Cards */
    div[data-testid="stVerticalBlock"] > div:has(div.tradingview-widget-container) {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 15px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.8);
    }

    /* Glowing Sidebar */
    [data-testid="stSidebar"] {
        background-color: #0a0a0a !important;
        border-right: 1px solid #00FF8822;
    }

    /* Indicator Badge Styling */
    .indicator-badge {
        padding: 5px 12px;
        border-radius: 50px;
        font-weight: bold;
        font-size: 12px;
        text-transform: uppercase;
        border: 1px solid;
    }
</style>
""", unsafe_allow_html=True)

st_autorefresh(interval=120000, key="patro_ultra_sync")

# 2. DATA ENGINE
def get_live_verdict():
    try:
        h15 = TA_Handler(symbol="XAUUSD", screener="forex", exchange="OANDA", interval=Interval.INTERVAL_15_MINUTES)
        rec15 = h15.get_analysis().summary['RECOMMENDATION']
        
        if "BUY" in rec15: return "🚀 BULLISH", "#00FF88", "STRONG DEMAND AT SUPPORT"
        elif "SELL" in rec15: return "📉 BEARISH", "#FF4B4B", "LIQUIDITY SWEEP DETECTED"
        return "⚖️ NEUTRAL", "#FFA500", "WAIT FOR BREAK OF STRUCTURE"
    except: return "SYNC", "#888", "RECONNECTING..."

status, s_col, s_desc = get_live_verdict()

# 3. TOP HUD: NEON STATUS & EVENTS
now = datetime.now(pytz.utc).strftime('%H:%M')
st.markdown(f"""
<div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 20px; background: rgba(0,0,0,0.4); border-radius: 15px; border-left: 5px solid {s_col};">
    <div>
        <h4 style="margin:0; color:{s_col};">{status} | {now} UTC</h4>
        <p style="margin:0; font-size:12px; color:#888;">{s_desc}</p>
    </div>
    <div style="text-align:right;">
        <span class="indicator-badge" style="color:#00FF88; border-color:#00FF88;">XAUUSD LIVE</span>
    </div>
</div>
""", unsafe_allow_html=True)

# 4. SIDEBAR: THE AI BRAIN
st.sidebar.markdown(f"""
<div style="text-align:center; padding:25px; background: linear-gradient(145deg, #0f0f0f, #1a1a1a); border-radius:20px; border: 1px solid {s_col}44;">
    <p style="color:#888; font-size:11px; letter-spacing:2px;">INSTITUTIONAL BIAS</p>
    <h1 style="color:{s_col}; margin:10px 0; font-size:42px;">{status.split()[-1]}</h1>
    <div style="height:4px; width:60%; background:{s_col}; margin:auto; border-radius:10px; box-shadow: 0 0 15px {s_col};"></div>
</div>
""", unsafe_allow_html=True)

# 5. THE ADVANCED SMC CHART
st.markdown("### 📊 PATRO SMC TERMINAL")
components.html(f"""
<div class="tradingview-widget-container" style="height:650px; border-radius:20px; overflow:hidden;">
  <div id="tv_adv"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
  <script type="text/javascript">
  new TradingView.widget({{
    "autosize": true, "symbol": "OANDA:XAUUSD", "interval": "15",
    "theme": "dark", "style": "1", "container_id": "tv_adv",
    "enable_publishing": false, "hide_side_toolbar": false,
    "allow_symbol_change": true, "show_popup_button": true,
    "popup_width": "1000", "popup_height": "650",
    "backgroundColor": "rgba(0, 0, 0, 1)",
    "gridColor": "rgba(255, 255, 255, 0.05)",
    "studies": [
        "STD;Fair_Value_Gap", 
        "STD;Order_Block", 
        "STD;Pivot_Points_High_Low", # This creates the "H" and "L" labels
        "STD;VWAP"
    ]
  }});
  </script>
</div>
""", height=660)

# 6. DUAL DASHBOARD GAUGES
col1, col2 = st.columns(2)
with col1:
    components.html("""<iframe src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js?{"interval":"15m","width":"100%","height":"350","isTransparent":true,"symbol":"OANDA:XAUUSD","showIntervalTabs":true,"displayMode":"single","colorTheme":"dark"}" height="360" width="100%" style="border:none;"></iframe>""", height=360)
with col2:
    components.html("""<iframe src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js?{"interval":"15m","width":"100%","height":"350","isTransparent":true,"symbol":"TVC:DXY","showIntervalTabs":true,"displayMode":"single","colorTheme":"dark"}" height="360" width="100%" style="border:none;"></iframe>""", height=360)

# 7. RISK CALCULATOR (Sidebar Bottom)
st.sidebar.markdown("---")
st.sidebar.subheader("🛡️ SMART RISK")
bal = st.sidebar.number_input("Capital", value=1000)
sl = st.sidebar.number_input("SL Pips", value=25)
st.sidebar.success(f"🔥 RECOMMENDED LOT: {round((bal*0.01)/(sl*10), 2)}")
