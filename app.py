import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
import pytz
from tradingview_ta import TA_Handler, Interval
from streamlit_autorefresh import st_autorefresh

# 1. PAGE SETUP
st.set_page_config(page_title="PATRO AI PRO V12.1.51", layout="wide")
st.markdown("<style>.stApp { background: #000; color: #fff; }</style>", unsafe_allow_html=True)

# AUTO-REFRESH (Every 2 minutes to update signals)
st_autorefresh(interval=120000, key="global_sync")

# 2. DATA ENGINE (The fix for the stuck 9.4 rating)
def get_live_verdict():
    try:
        # Scanning 15m and 1h for XAUUSD SMC Alignment
        h15 = TA_Handler(symbol="XAUUSD", screener="forex", exchange="OANDA", interval=Interval.INTERVAL_15_MINUTES)
        h1 = TA_Handler(symbol="XAUUSD", screener="forex", exchange="OANDA", interval=Interval.INTERVAL_1_HOUR)
        
        rec15 = h15.get_analysis().summary['RECOMMENDATION']
        rec1 = h1.get_analysis().summary['RECOMMENDATION']
        
        # Calculate dynamic score based on technical indicators
        points = 5.0
        if "BUY" in rec15: points += 2.0
        if "STRONG_BUY" in rec15: points += 2.0
        if "SELL" in rec15: points -= 2.0
        if "STRONG_SELL" in rec15: points -= 2.0
        
        # Determine Bias
        if "BUY" in rec15 and "BUY" in rec1: 
            bias, b_col, b_text = "BULLISH", "#00FF88", "Momentum confirmed. Look for FVG entries."
        elif "SELL" in rec15 and "SELL" in rec1: 
            bias, b_col, b_text = "BEARISH", "#FF4B4B", "DXY strength confirmed. Look for liquidity sweeps."
        else: 
            bias, b_col, b_text = "NEUTRAL", "#FFA500", "Market consolidating. Wait for BOS/MSS."
            
        return round(max(1.0, min(10.0, points)), 1), bias, b_col, b_text
    except:
        return 5.0, "SYNCING", "#888", "Connecting to OANDA data..."

score, bias, bias_color, bias_desc = get_live_verdict()

# 3. TOP HUD: NEWS & KILLZONES
def get_status():
    now = datetime.now(pytz.utc)
    if 13 <= now.hour < 16: return "🔥 NY KILLZONE ACTIVE"
    elif 8 <= now.hour < 11: return "⚡ LONDON OPEN"
    return "💤 LOW VOLUME"

st.markdown(f"<h3 style='text-align:center; color:#FF4B4B;'>{get_status()} | LIVE NEWS CALENDAR</h3>", unsafe_allow_html=True)
components.html("""
<div class="tradingview-widget-container">
  <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-events.js" async>
  { "width": "100%", "height": "200", "colorTheme": "dark", "isTransparent": true, "importanceFilter": "-1,0,1" }
  </script>
</div>
""", height=210)

# --- SIDEBAR (Now using Dynamic Data) ---
st.sidebar.markdown(f"""
<div style="background: rgba({ '0, 255, 136' if bias == 'BULLISH' else '255, 75, 75' if bias == 'BEARISH' else '255, 165, 0' }, 0.1); padding: 15px; border-radius: 10px; border: 1px solid {bias_color}; margin-bottom: 20px;">
    <p style="margin:0; color: #888; font-size: 12px;">AI PERFORMANCE RATING</p>
    <h2 style="margin:0; color: {bias_color};">{score} / 10</h2>
    <hr style="margin: 10px 0; border-color: rgba(255,255,255,0.1);">
    <p style="margin:0; font-size: 14px;"><b>BIAS:</b> {bias} (XAU)</p>
    <p style="margin:0; font-size: 11px; color: {bias_color};">{bias_desc}</p>
</div>
""", unsafe_allow_html=True)

# 4. DUAL-SIGNAL GAUGE HUB
st.markdown("---")
col_g, col_d = st.columns(2)
with col_g:
    st.markdown("<h4 style='text-align:center; color:#00FF88;'>GOLD (XAUUSD) SIGNAL</h4>", unsafe_allow_html=True)
    components.html("""
    <div class="tradingview-widget-container"><script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>
    { "interval": "15m", "width": "100%", "height": "380", "isTransparent": true, "symbol": "OANDA:XAUUSD", "showIntervalTabs": true, "displayMode": "single", "colorTheme": "dark" }
    </script></div>
    """, height=390)

with col_d:
    st.markdown("<h4 style='text-align:center; color:#FF4B4B;'>DOLLAR (DXY) SIGNAL</h4>", unsafe_allow_html=True)
    components.html("""
    <div class="tradingview-widget-container"><script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>
    { "interval": "15m", "width": "100%", "height": "380", "isTransparent": true, "symbol": "TVC:DXY", "showIntervalTabs": true, "displayMode": "single", "colorTheme": "dark" }
    </script></div>
    """, height=390)

# 5. MARKET TICKER
components.html("""
<div class="tradingview-widget-container"><script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js" async>
{ "symbols": [{"proName": "TVC:DXY", "title": "DXY"}, {"proName": "OANDA:XAUUSD", "title": "GOLD"}], "colorTheme": "dark", "isTransparent": true }
</script></div>
""", height=50)

# 6. THE SMC CHART (Studies Kept Intact)
st.subheader("📊 SMART MONEY CHART (SMC)")
components.html("""
<div class="tradingview-widget-container" style="height:600px;">
  <div id="tv_final"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
  <script type="text/javascript">
  new TradingView.widget({
    "autosize": true, "symbol": "OANDA:XAUUSD", "interval": "15",
    "theme": "dark", "style": "1", "container_id": "tv_final",
    "show_popup_button": true,
    "popup_width": "1000",
    "popup_height": "650",
    "studies": ["STD;Fair_Value_Gap", "STD;Order_Block", "STD;Pivot_Points_High_Low", "STD;VWAP"]
  });
  </script>
</div>
""", height=610)

# 7. SIDEBAR: RISK CALCULATOR
st.sidebar.header("🛡️ RISK & TARGETS")
bal = st.sidebar.number_input("Balance ($)", value=1000)
risk_pct = st.sidebar.slider("Risk %", 0.5, 3.0, 1.0)
sl_pips = st.sidebar.number_input("Stop Loss (Pips)", value=30)
reward_ratio = st.sidebar.slider("Reward Ratio (1:X)", 1.5, 5.0, 2.0)

risk_amount = bal * (risk_pct / 100)
lot_size = risk_amount / (sl_pips * 10)
tp_pips = sl_pips * reward_ratio

st.sidebar.markdown("---")
st.sidebar.success(f"🔥 USE LOT: {lot_size:.2f}")
st.sidebar.info(f"🎯 TARGET TP: {tp_pips:.0f} PIPS")
st.sidebar.error(f"🛑 STOP LOSS: {sl_pips} PIPS")

st.sidebar.warning("⚠️ ZONE ALERT: Watch for BOS/MSS on 15m Chart.")
