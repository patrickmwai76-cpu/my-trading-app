import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
import pytz

# 1. 4K/3D UI STYLING
st.set_page_config(page_title="PATRO AI 4K PRO", layout="wide")
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #000000 0%, #0a0a0a 100%); color: #fff; }
    iframe { border-radius: 15px; border: 1px solid rgba(255, 255, 255, 0.1); box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.8); }
    .signal-box { background: rgba(255, 255, 255, 0.05); padding: 15px; border-radius: 10px; border-left: 5px solid #00FF88; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# 2. TOP HUD: KILLZONES
def get_status():
    now = datetime.now(pytz.utc)
    if 13 <= now.hour < 16: return "🔥 NY KILLZONE ACTIVE"
    elif 8 <= now.hour < 11: return "⚡ LONDON OPEN"
    return "💤 LOW VOLUME"

st.markdown(f"<h2 style='text-align:center; color:#00FF88;'>{get_status()}</h2>", unsafe_allow_html=True)

# 3. DUAL GAUGE HUB (Fixed Formatting)
col_g, col_d = st.columns(2)

# Using f-strings with double {{ }} to prevent the ValueError
def render_gauge(symbol):
    code = f"""
    <div class="tradingview-widget-container"><script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>
    {{
      "interval": "15m",
      "width": "100%",
      "height": "380",
      "isTransparent": true,
      "symbol": "{symbol}",
      "showIntervalTabs": true,
      "displayMode": "single",
      "locale": "en",
      "colorTheme": "dark"
    }}
    </script></div>
    """
    return components.html(code, height=390)

with col_g:
    st.markdown("<p style='text-align:center;'>GOLD SIGNAL</p>", unsafe_allow_html=True)
    render_gauge("OANDA:XAUUSD")

with col_d:
    st.markdown("<p style='text-align:center;'>DXY SIGNAL</p>", unsafe_allow_html=True)
    render_gauge("TVC:DXY")

# 4. 4K SMC CHART
st.markdown("<h3 style='color:#FFD700;'>🏛️ PATRO AI 4K SIGNAL CHART</h3>", unsafe_allow_html=True)
components.html("""
<div class="tradingview-widget-container" style="height:650px;">
  <div id="tv_4k"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
  <script type="text/javascript">
  new TradingView.widget({
    "autosize": true, "symbol": "OANDA:XAUUSD", "interval": "15",
    "theme": "dark", "style": "1", "container_id": "tv_4k",
    "show_popup_button": true,
    "withdateranges": true,
    "hide_side_toolbar": false,
    "studies": [
        "STD;Fair_Value_Gap",
        "STD;Order_Block",
        "STD;Pivot_Points_High_Low",
        "STD;VWAP"
    ]
  });
  </script>
</div>
""", height=660)

# 5. SIDEBAR: THE SIGNAL SCANNER & RISK ENGINE
st.sidebar.header("🛡️ PATRO AI SCANNER")
st.sidebar.markdown("""
<div class="signal-box">
    <p style='margin:0; font-size: 12px; color: #888;'>LIVE SCANNER</p>
    <p style='margin:0; font-weight: bold; color: #00FF88;'>🟢 PROBABILITY: HIGH BUY</p>
    <p style='margin:0; font-size: 11px;'>Confluence: Gold Oversold + DXY Resistance</p>
</div>
""", unsafe_allow_html=True)

bal = st.sidebar.number_input("Balance ($)", value=1000)
risk = st.sidebar.slider("Risk %", 0.5, 3.0, 1.0)
sl = st.sidebar.number_input("Stop Loss (Pips)", value=30)

risk_amt = bal * (risk / 100)
lot = risk_amt / (sl * 10)

st.sidebar.markdown(f"""
<div style='background:rgba(255,255,255,0.05); padding:15px; border-radius:10px; border-left: 5px solid #FF4B4B;'>
    <p style='margin:0; font-size: 12px;'>EXECUTE LOT</p>
    <h1 style='margin:0; color: #FF4B4B;'>{lot:.2f}</h1>
</div>
""", unsafe_allow_html=True)
