import streamlit as st
import pandas as pd
import pandas_ta as ta
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime

# --- 1. CORE CONFIG ---
st.set_page_config(page_title="PATRO AI PRO V12.0.7", layout="wide")
st.markdown("<style>.stApp { background: #010101; color: #ffffff; }</style>", unsafe_allow_html=True)

# --- 2. DATA ENGINE ---
def get_market_data(ticker, interval="5m"):
    try:
        df = yf.download(ticker, period="5d", interval=interval, progress=False, auto_adjust=True)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        df['RSI'] = ta.rsi(df.Close, length=14)
        df['VWAP'] = ta.vwap(df.High, df.Low, df.Close, df.Volume)
        df['ATR'] = ta.atr(df.High, df.Low, df.Close, length=14)
        
        # FVG Detection
        df['FVG_Up'] = (df['Low'].shift(-1) > df['High'].shift(1)) 
        df['FVG_Down'] = (df['High'].shift(-1) < df['Low'].shift(1))
        
        return df
    except:
        return None

# --- 3. SIDEBAR CONTROLS ---
st.title("🌌 PATRO AI PRO V12.0.7 | SMC ULTIMATE")

with st.sidebar:
    st.header("🏢 COMMAND CENTER")
    asset = st.selectbox("Market Target", ["GOLD", "GBPUSD", "US30"])
    ticker_map = {"GOLD":"GC=F", "GBPUSD":"GBPUSD=X", "US30":"^DJI"}
    target_ticker = ticker_map[asset]
    
    st.divider()
    mode = st.toggle("🚀 AGGRESSIVE MODE", value=False)
    
    st.divider()
    st.subheader("📡 LIVE NEWS ALERTS")
    # NEWS FLASH: US CPI is out in < 5 hours
    st.error("🚨 3:30 PM EAT: US CPI Inflation Report. High Risk!")
    st.warning("⚔️ WAR UPDATE: Intense strikes confirmed. Gold support at $5,153.")

# --- 4. LIVE DASHBOARD ---
@st.fragment(run_every="15s")
def render_app():
    df_5m = get_market_data(target_ticker, "5m")
    df_1h = get_market_data(target_ticker, "1h")
    
    if df_5m is None or len(df_5m) < 20:
        st.error("Searching for Bank Liquidity...")
        return

    # --- LOGIC CALCULATIONS ---
    cp = df_5m.Close.iloc[-1]
    atr = df_5m.ATR.iloc[-1]
    vwap_curr = df_5m.VWAP.iloc[-1]
    bias_1h = "BULLISH" if df_1h.Close.iloc[-1] > df_1h.VWAP.iloc[-1] else "BEARISH"
    curr_sig = "BUY" if cp > vwap_curr else "SELL"
    
    # 2-Minute Confirmation
    confirmed = df_5m.Close.iloc[-1] > df_5m.VWAP.iloc[-1] and df_5m.Close.iloc[-2] > df_5m.VWAP.iloc[-2] if curr_sig == "BUY" else df_5m.Close.iloc[-1] < df_5m.VWAP.iloc[-1] and df_5m.Close.iloc[-2] < df_5m.VWAP.iloc[-2]

    # --- ENTRY ZONE FILTER ---
    # We only want to enter if we are within $2.00 of the VWAP (The Bank Price)
    dist_from_entry = abs(cp - vwap_curr)
    is_too_late = dist_from_entry > 2.0  # If more than $2 away, it's a chase
    
    # Institutional TP/SL
    sl_dist = atr * 1.5
    tp_dist = sl_dist * 2.5
    bank_tp = cp + tp_dist if curr_sig == "BUY" else cp - tp_dist
    bank_sl = cp - sl_dist if curr_sig == "BUY" else cp + sl_dist

    # Strength
    strength = 0
    if (curr_sig == "BUY" and df_5m.RSI.iloc[-1] > 50) or (curr_sig == "SELL" and df_5m.RSI.iloc[-1] < 50): strength += 30
    if (curr_sig == "BUY" and bias_1h == "BULLISH") or (curr_sig == "SELL" and bias_1h == "BEARISH"): strength += 40
    if confirmed: strength += 30

    # SIGNAL UI (Logic for "Too Late")
    is_sure = (bias_1h == curr_sig.replace("BUY","BULLISH").replace("SELL","BEARISH")) and confirmed
    
    if is_too_late:
        status = "⌛ WAIT (TOO LATE)"
        col = "#FFA500" # Orange for caution
    elif is_sure:
        status = f"🏦 BANK {curr_sig} (SURE)"
        col = "#00FF88" if curr_sig == "BUY" else "#FF3366"
    else:
        status = "⌛ WAIT (RETAIL TRAP)"
        col = "#FFA500"

    # Top Metrics
    m1, m2, m3 = st.columns([2, 1, 1])
    m1.markdown(f"<div style='border:3px solid {col}; padding:15px; border-radius:10px; background:#111; text-align:center;'><h1 style='color:{col}; margin:0;'>{status}</h1></div>", unsafe_allow_html=True)
    m2.metric("PRICE", f"{cp:,.2f}")
    m3.metric("STRENGTH", f"{strength}%")

    st.progress(strength / 100)
    
    if is_too_late:
        st.warning(f"⚠️ Price is {dist_from_entry:.2f} away from Bank Entry. Waiting for pullback to {vwap_curr:.2f}")

    # --- THE CHART ---
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df_5m.index, open=df_5m.Open, high=df_5m.High, low=df_5m.Low, close=df_5m.Close, name="Price"))
    fig.add_trace(go.Scatter(x=df_5m.index, y=df_5m.VWAP, line=dict(color='cyan', dash='dot', width=1), name="VWAP"))

    # TP/SL LINES WITH PRICE LABELS
    fig.add_hline(y=bank_tp, line_dash="dash", line_color="#00FF88", annotation_text=f"TP: {bank_tp:.2f}")
    fig.add_hline(y=bank_sl, line_dash="dash", line_color="#FF3366", annotation_text=f"SL: {bank_sl:.2f}")

    # BOX DETECTION (FVG)
    for i in range(len(df_5m)-40, len(df_5m)-1):
        if df_5m['FVG_Up'].iloc[i]:
            fig.add_shape(type="rect", x0=df_5m.index[i-1], x1=df_5m.index[i+1], y0=df_5m['High'].iloc[i-1], y1=df_5m['Low'].iloc[i+1],
                          fillcolor="rgba(0, 255, 136, 0.3)", line=dict(width=0))
        if df_5m['FVG_Down'].iloc[i]:
            fig.add_shape(type="rect", x0=df_5m.index[i-1], x1=df_5m.index[i+1], y0=df_5m['Low'].iloc[i-1], y1=df_5m['High'].iloc[i+1],
                          fillcolor="rgba(255, 51, 102, 0.3)", line=dict(width=0))

    fig.update_layout(height=600, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig, use_container_width=True)

render_app()
