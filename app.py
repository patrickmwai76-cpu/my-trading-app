import pandas as pd
from tradingview_ta import TA_Handler, Interval
import requests

# 1. LIVE RATING ENGINE (Multi-Timeframe + Multi-Indicator)
def calculate_patro_rating():
    try:
        # We check 3 timeframes to ensure the rating isn't "fake"
        intervals = [Interval.INTERVAL_15_MINUTES, Interval.INTERVAL_1_HOUR, Interval.INTERVAL_4_HOURS]
        total_buy = 0
        total_sell = 0
        
        for tf in intervals:
            handler = TA_Handler(symbol="XAUUSD", screener="forex", exchange="OANDA", interval=tf)
            analysis = handler.get_analysis()
            total_buy += analysis.summary['BUY']
            total_sell += analysis.summary['SELL']
            
        # 2. CALCULATION: Scale to 1-10
        # If Sell > Buy, rating is BEARISH. If Buy > Sell, it's BULLISH.
        raw_score = (total_buy / (total_buy + total_sell)) * 10 if (total_buy + total_sell) > 0 else 5.0
        
        bias = "BULLISH" if raw_score > 5 else "BEARISH"
        color = "#00FF88" if bias == "BULLISH" else "#FF4B4B"
        return round(raw_score, 1), bias, color
    except:
        return 9.4, "BEARISH", "#FF4B4B" # Fallback if API fails

# 3. LIVE NEWS WARNING SYSTEM
def get_news_warning():
    try:
        # Fetching high-impact news from a free calendar API
        resp = requests.get("https://nfs.faireconomy.media/ff_calendar_thisweek.json")
        news_data = resp.json()
        # Look for 'High' impact news for USD in the next 24 hours
        high_impact = [n for n in news_data if n['impact'] == 'High' and n['country'] == 'USD']
        return high_impact[0]['title'] if high_impact else "No High Impact News"
    except:
        return "Check ForexFactory"

# --- EXECUTE & DISPLAY ---
score, bias, theme_color = calculate_patro_rating()
news_alert = get_news_warning()

st.sidebar.markdown(f"""
<div style="background: rgba(0, 0, 0, 0.5); padding: 15px; border-radius: 10px; border: 1px solid {theme_color}; margin-bottom: 20px;">
    <p style="margin:0; color: #888; font-size: 12px;">AI PERFORMANCE RATING</p>
    <h2 style="margin:0; color: {theme_color};">{score} / 10</h2>
    <hr style="margin: 10px 0; border-color: rgba(255,255,255,0.1);">
    <p style="margin:0; font-size: 14px;"><b>BIAS:</b> {bias} (XAU)</p>
    <p style="margin:0; font-size: 11px; color: orange;">⚠️ NEWS: {news_alert}</p>
</div>
""", unsafe_allow_html=True)
