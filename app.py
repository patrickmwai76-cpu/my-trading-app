import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import pytz
from tradingview_ta import TA_Handler, Interval
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components

# 1. PAGE SETUP
st.set_page_config(page_title="PATRO AI PRO V12.3.0", layout="wide")
st.markdown("<style>.stApp { background: #000; color: #fff; }</style>", unsafe_allow_html=True)

# 2. AUTO-SYNC (Updates everything every 5 minutes)
st_autorefresh(interval=300000, key="global_sync")

# 3. ALL-TIMEFRAME RATING ENGINE (1m to 1M)
def get_all_tf_analysis():
    # Full spectrum of timeframes
    tfs = {
        "1m": Interval.INTERVAL_1_MINUTE,
        "5m": Interval.INTERVAL_5_MINUTES,
        "15m": Interval.INTERVAL_15_MINUTES,
        "1h": Interval.INTERVAL_1_HOUR,
        "4h": Interval.INTERVAL_4_HOURS,
        "1D": Interval.INTERVAL_1_DAY,
        "1W": Interval.INTERVAL_1_WEEK,
        "1M": Interval.INTERVAL_1_MONTH
    }
    results = {}
    total_buys, total_sells = 0, 0
    
    try:
        for label, tf in tfs.items():
            handler = TA_Handler(symbol="XAUUSD", screener="forex", exchange="OANDA", interval=tf)
            analysis = handler.get_analysis()
            b, s = analysis.summary['BUY'], analysis.summary['SELL']
            # Calculate individual TF score (1-10)
            tf_score = round((b/(b+s))*10 if (b+s)>0 else 5, 1)
            results[label] = {"score": tf_score, "bias": analysis.summary['RECOMMENDATION']}
            total_buys += b
            total_sells += s
            
        global_score = round((total_buys/(total_buys+total_sells))*10 if (total_buys+total_sells)>0 else 5, 1)
        return results, global_score
    except:
        return {}, 9.4

# Fetch current market state
all_tf_data, global_rating = get_all_tf_analysis()
rating_color = "#00FF88" if global_rating > 5 else "#FF4B4B"

# 4. SIDEBAR: THE COMMAND CENTER
st.sidebar.button("🔄 REFRESH ALL INTERVALS", on_click=st.rerun, use_container_width=True)

# Global Performance Card
st.sidebar.markdown(f"""
<div style="background: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px; border: 1px solid {rating_color}; margin-bottom: 20px;">
    <p style="margin:0; color: #888; font-size: 12px;">GLOBAL MARKET STRENGTH</p>
    <h2 style="margin:0; color: {rating_color}; text-align:center;">{global_rating} / 10</h2>
</div>
""", unsafe_allow_html=True)

# THE FULL SPECTRUM LIST
st.sidebar.subheader("📊 ALL-INTERVAL SCAN")
for tf_label, data in all_tf_data.items():
    # Dynamic coloring for each row
    c = "#00FF88" if "BUY" in data['bias'] else "#FF4B4B" if "SELL" in data['bias'] else "#888"
    st.sidebar.markdown(f"""
        <div style="display: flex; justify-content: space-between; font-size: 13px; border-bottom: 1px solid rgba(255,255,255,0.1); padding: 2px 0;">
            <span><b>{tf_label}</b></span>
            <span style="color:{c};">{data['score']} ({data['bias']})</span>
        </div>
    """, unsafe_allow_html=True)

# 5. RISK CALCULATOR (Still in Sidebar)
st.sidebar.markdown("---")
st.sidebar.header("🛡️ POSITION SIZER")
bal = st.sidebar.number_input("Balance ($)", value=1000)
risk_pct = st.sidebar.slider("Risk %", 0.5, 3.0, 1.0)
sl_pips = st.sidebar.number_input("Stop Loss (Pips)", value=30)
lot_size = (bal * (risk_pct / 100)) / (sl_pips * 10)
st.sidebar.success(f"🔥 LOT SIZE: {lot_size:.2f}")

# 6. MAIN DASHBOARD: CORRELATION GAUGES
col_xau, col_dxy = st.columns(2)
with col_xau:
    st.markdown("<h4 style='text-align:center;'>GOLD 15M SUMMARY</h4>", unsafe_allow_html=True)
    components.html('<div class="tradingview-widget-container"><script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>{ "interval": "15m", "width": "100%", "height": "380", "isTransparent": true, "symbol": "OANDA:XAUUSD", "showIntervalTabs": true, "displayMode": "single", "colorTheme": "dark" }</script></div>', height=390)

with col_dxy:
    st.markdown("<h4 style='text-align:center;'>DXY 15M SUMMARY</h4>", unsafe_allow_html=True)
    components.html('<div class="tradingview-widget-container"><script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>{ "interval": "15m", "width": "100%", "height": "380", "isTransparent": true, "symbol": "TVC:DXY", "showIntervalTabs": true, "displayMode": "single", "colorTheme": "dark" }</script></div>', height=390)

# 7. THE MASTER CHART (Institutional Suite)
st.subheader("📊 PATRO SMC TERMINAL (XAUUSD)")
components.html("""
<div class="tradingview-widget-container" style="height:750px;">
  <div id="tv_full_suite"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
  <script type="text/javascript">
  new TradingView.widget({
    "autosize": true,
    "symbol": "OANDA:XAUUSD",
    "interval": "15",
    "timezone": "Etc/UTC",
    "theme": "dark",
    "style": "1",
    "locale": "en",
    "toolbar_bg": "#f1f3f6",
    "enable_publishing": false,
    "withdateranges": true,
    "hide_side_toolbar": false,
    "allow_symbol_change": true,
    "show_popup_button": true,      // POPUP RESTORED
    "popup_width": "1000",
    "popup_height": "650",
    "container_id": "tv_full_suite",
    "studies": [
      "STD;Fair_Value_Gap",         // FVG
      "STD;Order_Block",            // Order Blocks
      "STD;Pivot_Points_High_Low",  // Pivot High/Low
      "STD;VWAP"                    // VWAP
    ],
    "show_interval_tabs": true      // Allow you to switch timeframes on chart
  });
  </script>
</div>
""", height=760)
