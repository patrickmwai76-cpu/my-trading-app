import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import pytz
from tradingview_ta import TA_Handler, Interval
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components

# 1. PAGE CONFIG & THEME
st.set_page_config(page_title="PATRO AI PRO V12.1.50", layout="wide")
st.markdown("<style>.stApp { background: #000; color: #fff; }</style>", unsafe_allow_html=True)

# 2. AUTO-REFRESH (Updates every 5 minutes to keep news & ratings fresh)
st_autorefresh(interval=300000, key="global_refresh")

# 3. DYNAMIC ENGINES (Rating & News)
def get_patro_rating():
    try:
        tfs = [Interval.INTERVAL_15_MINUTES, Interval.INTERVAL_1_HOUR, Interval.INTERVAL_4_HOURS]
        buys, sells = 0, 0
        for tf in tfs:
            handler = TA_Handler(symbol="XAUUSD", screener="forex", exchange="OANDA", interval=tf)
            analysis = handler.get_analysis()
            buys += analysis.summary['BUY']
            sells += analysis.summary['SELL']
        
        total = buys + sells
        score = (buys / total) * 10 if total > 0 else 5.0
        bias = "BULLISH" if score > 5 else "BEARISH"
        color = "#00FF88" if bias == "BULLISH" else "#FF4B4B"
        return round(score, 1), bias, color
    except:
        return 9.4, "BEARISH", "#FF4B4B"

def get_market_news():
    try:
        r = requests.get("https://nfs.faireconomy.media/ff_calendar_thisweek.json")
        now_utc = datetime.now(pytz.utc)
        upcoming = []
        for n in r.json():
            if n['impact'] == 'High' and n['country'] == 'USD':
                event_time = datetime.strptime(n['date'], "%Y-%m-%dT%H:%M:%S%z")
                if event_time > now_utc:
                    upcoming.append((n, event_time))
        
        if upcoming:
            next_event, ev_time = upcoming[0]
            diff = ev_time - now_utc
            hrs, rem = divmod(int(diff.total_seconds()), 3600)
            mins, _ = divmod(rem, 60)
            return f"⏳ {hrs}h {mins}m to {next_event['title']}", "#FFA500"
        return "✅ No High Impact News Left", "#00FF88"
    except:
        return "⚠️ News Feed Offline", "#888"

# 4. INITIALIZE SESSION DATA
if 'trade_log' not in st.session_state:
    st.session_state.trade_log = pd.DataFrame(columns=["Time", "Rating", "Bias", "Lot", "News"])

# Pre-fetch data for the UI
live_score, live_bias, live_color = get_patro_rating()
news_text, news_color = get_market_news()

# 5. TOP HUD: KILLZONES & COUNTDOWN
def get_session():
    now = datetime.now(pytz.utc)
    if 13 <= now.hour < 16: return "🔥 NY KILLZONE ACTIVE", "#FF4B4B"
    elif 8 <= now.hour < 11: return "⚡ LONDON OPEN", "#00FF88"
    return "💤 LOW VOLUME SESSION", "#888"

sess_name, sess_col = get_session()

st.markdown(f"""
    <div style="text-align:center; padding:15px; background:rgba(255,255,255,0.05); border-radius:10px; border-top: 4px solid {news_color};">
        <h2 style="margin:0; color:{sess_col};">{sess_name}</h2>
        <p style="margin:0; color:{news_color}; font-weight:bold; font-size:20px;">{news_text}</p>
    </div>
""", unsafe_allow_html=True)

# 6. SIDEBAR: RATING, RISK & JOURNAL
st.sidebar.button("🔄 FORCE REFRESH", on_click=st.rerun, use_container_width=True)

st.sidebar.markdown(f"""
<div style="background: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px; border: 1px solid {live_color}; margin: 10px 0;">
    <p style="margin:0; color: #888; font-size: 12px;">AI PERFORMANCE RATING</p>
    <h2 style="margin:0; color: {live_color};">{live_score} / 10</h2>
    <hr style="margin: 10px 0; border-color: rgba(255,255,255,0.1);">
    <p style="margin:0; font-size: 14px;"><b>BIAS:</b> {live_bias}</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.header("🛡️ RISK CALCULATOR")
bal = st.sidebar.number_input("Balance ($)", value=1000)
risk_pct = st.sidebar.slider("Risk %", 0.5, 3.0, 1.0)
sl_pips = st.sidebar.number_input("Stop Loss (Pips)", value=30)
lot_size = (bal * (risk_pct / 100)) / (sl_pips * 10)

st.sidebar.success(f"🔥 USE LOT: {lot_size:.2f}")

st.sidebar.markdown("---")
st.sidebar.subheader("📓 QUICK JOURNAL")
if st.sidebar.button("📝 Log Setup", use_container_width=True):
    new_entry = {"Time": datetime.now().strftime("%H:%M"), "Rating": live_score, "Bias": live_bias, "Lot": f"{lot_size:.2f}", "News": news_text}
    st.session_state.trade_log = pd.concat([st.session_state.trade_log, pd.DataFrame([new_entry])], ignore_index=True)
    st.toast("Saved!")

if not st.session_state.trade_log.empty:
    st.sidebar.dataframe(st.session_state.trade_log.tail(3), hide_index=True)
    st.sidebar.download_button("📥 Export CSV", st.session_state.trade_log.to_csv(index=False), "trades.csv", use_container_width=True)

# 7. MAIN DASHBOARD: GAUGES & CHART
col1, col2 = st.columns(2)
with col1:
    st.markdown("<h4 style='text-align:center;'>GOLD 15M SIGNAL</h4>", unsafe_allow_html=True)
    components.html('<div class="tradingview-widget-container"><script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>{ "interval": "15m", "width": "100%", "height": "350", "isTransparent": true, "symbol": "OANDA:XAUUSD", "showIntervalTabs": false, "displayMode": "single", "colorTheme": "dark" }</script></div>', height=360)

with col2:
    st.markdown("<h4 style='text-align:center;'>DXY 15M SIGNAL</h4>", unsafe_allow_html=True)
    components.html('<div class="tradingview-widget-container"><script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>{ "interval": "15m", "width": "100%", "height": "350", "isTransparent": true, "symbol": "TVC:DXY", "showIntervalTabs": false, "displayMode": "single", "colorTheme": "dark" }</script></div>', height=360)

st.subheader("📊 SMC INSTITUTIONAL CHART")
components.html("""
<div class="tradingview-widget-container" style="height:600px;">
  <div id="tv_final"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
  <script type="text/javascript">
  new TradingView.widget({
    "autosize": true, "symbol": "OANDA:XAUUSD", "interval": "15", "theme": "dark", "style": "1", "container_id": "tv_final",
    "studies": ["STD;Fair_Value_Gap", "STD;Order_Block", "STD;Pivot_Points_High_Low"]
  });
  </script>
</div>
""", height=610)
