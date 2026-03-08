import streamlit as st
import pandas as pd
import pandas_ta as ta
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import logging

# --- 1. SILENT LOGGING & MT5 CHECK (REMAINS THE SAME) ---
logging.getLogger('streamlit').setLevel(logging.CRITICAL)
try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False

# --- 2. PREMIUM INTERFACE SETUP (REMAINS THE SAME) ---
st.set_page_config(page_title="PATRO AI PRO V11.6", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .stApp { background-color: #050505; color: white; }
    header, footer, #MainMenu {visibility: hidden;}
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 20px; text-align: center; margin-bottom: 20px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.8);
    }
    div.stButton > button {
        border-radius: 12px !important; font-weight: 900 !important;
        height: 3.5em !important; width: 100% !important;
        text-transform: uppercase; transition: 0.3s;
    }
    button[key="buy_btn"] { background: linear-gradient(135deg, #00FF88 0%, #008DFF 100%) !important; color: black !important; }
    button[key="sell_btn"] { background: linear-gradient(135deg, #FF3366 0%, #FF8A00 100%) !important; color: white !important; }
    section[data-testid="stSidebar"] { background-color: #0a0a0a !important; border-right: 1px solid #222; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. EXECUTION ENGINE (REMAINS THE SAME) ---
def place_justmarket_trade(symbol, order_type, volume=0.01):
    if not MT5_AVAILABLE:
        st.warning("⚠️ Local Windows MT5 required.")
        return
    if not mt5.initialize(): return
    symbol_name = "XAUUSD.m" if "GC=F" in symbol else f"{symbol}.m"
    mt5.symbol_select(symbol_name, True)
    tick = mt5.symbol_info_tick(symbol_name)
    if tick:
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol_name,
            "volume": float(volume),
            "type": order_type,
            "price": tick.ask if order_type == 0 else tick.bid,
            "magic": 1162026,
            "comment": "PATRO AI V11.6",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        mt5.order_send(request)
        st.balloons()

# --- 4. SIDEBAR INPUTS (REMAINS THE SAME) ---
asset_dict = {"XAUUSD": "GC=F", "US30": "^DJI", "GBPUSD": "GBPUSD=X"}
with st.sidebar:
    st.title("🌌 PATRO V11.6")
    choice = st.selectbox("Market Asset", list(asset_dict.keys()))
    ticker = asset_dict[choice]

    st.error("⚠️ **NEWS WATCH**\nUS Iran Conflict Impacting Gold.")
    st.divider()
    st.markdown("### 📋 INSTITUTIONAL SOP")
    st.checkbox("MTF Confluence Check", value=True)
    st.checkbox("VWAP Proximity", value=True)
    st.checkbox("Volume Confirmation", value=True)
    
    st.divider()
    st.markdown("### 🧮 RISK CALCULATOR")
    balance = st.number_input("Balance ($)", value=1000)
    risk_pct = st.slider("Risk %", 0.5, 5.0, 1.0)
    sl_pips = st.number_input("Stop Loss Pips", value=30)
    lots = max((balance * (risk_pct/100)) / (sl_pips * 10), 0.01) if sl_pips > 0 else 0.01
    st.success(f"Lot Size: **{lots:.2f}**")
    
    st.divider()
    tf = st.radio("Main Chart TF", ["1m", "5m", "15m"], index=1, horizontal=True)
    matrix_container = st.empty()

# --- 5. THE LIVE ENGINE ---
@st.fragment(run_every=7)
def dashboard_engine():
    # 5a. UPDATE SIDEBAR MATRIX
    matrix_data = []
    for mtf in ["1m", "5m", "15m"]:
        df_m = yf.download(ticker, period="1d", interval=mtf, progress=False)
        if not df_m.empty:
            if isinstance(df_m.columns, pd.MultiIndex): df_m.columns = df_m.columns.get_level_values(0)
            vwap_m = ta.vwap(df_m['High'], df_m['Low'], df_m['Close'], df_m['Volume']).iloc[-1]
            status = "🟢 BULL" if df_m['Close'].iloc[-1] > vwap_m else "🔴 BEAR"
            matrix_data.append({"TF": mtf, "Status": status})
    
    with matrix_container:
        st.markdown("### 📊 TREND MATRIX")
        st.table(pd.DataFrame(matrix_data))

    # 5b. MAIN DATA FETCH
    data = yf.download(ticker, period="5d", interval=tf, auto_adjust=True, progress=False)
    if data is not None and not data.empty:
        if isinstance(data.columns, pd.MultiIndex): data.columns = data.columns.get_level_values(0)
        
        # INDICATORS
        data['VWAP'] = ta.vwap(data['High'], data['Low'], data['Close'], data['Volume'])
        adx_df = ta.adx(data['High'], data['Low'], data['Close'])
        data['ADX'] = adx_df['ADX_14']
        macd = ta.macd(data['Close'])
        data['MACD_H'] = macd['MACDh_12_26_9']
        data['Vol_Avg'] = data['Volume'].rolling(window=20).mean()
        data['Is_Spike'] = data['Volume'] > (data['Vol_Avg'] * 2.5)
        
        # ENTRY LOGIC
        data['Raw'] = 0
        data.loc[(data['Close'] > data['VWAP']) & (data['MACD_H'] > 0) & (data['ADX'] > 22), 'Raw'] = 1
        data.loc[(data['Close'] < data['VWAP']) & (data['MACD_H'] < 0) & (data['ADX'] > 22), 'Raw'] = -1
        data['Entry'] = data['Raw'].diff().fillna(0)
        
        last = data.iloc[-1]
        
        # AI SCORE CALCULATION
        current_bias = "🟢 BULL" if last['Raw'] == 1 else "🔴 BEAR" if last['Raw'] == -1 else None
        bias_count = sum([1 for m in matrix_data if m['Status'] == current_bias]) if current_bias else 0
        final_conf = int(((bias_count / 3) * 40) + 60 if last['Raw'] != 0 else 0)
        
        # TREND STRENGTH METER LOGIC
        adx_val = last['ADX']
        if adx_val < 20: strength, s_clr = "WEAK/RANGING", "#777"
        elif adx_val < 25: strength, s_clr = "EMERGING", "#008DFF"
        elif adx_val < 50: strength, s_clr = "STRONG", "#00FF88"
        else: strength, s_clr = "EXTREME", "#FFFF00"

        status_clr = "#00FF88" if last['Raw'] == 1 else "#FF3366" if last['Raw'] == -1 else "#777"
        signal_text = "🚀 BUY" if last['Raw'] == 1 else "📉 SELL" if last['Raw'] == -1 else "SCANNING..."

        # TOP UI CARDS
        score_col, strength_col = st.columns(2)
        with score_col:
            st.markdown(f"""
                <div class="glass-card" style="border-bottom: 4px solid {status_clr}; height: 220px;">
                    <p style="color:#666; letter-spacing:3px; font-size:10px; margin:0;">AI CONFLUENCE</p>
                    <h1 style="color:{status_clr}; font-size:60px; margin:5px 0;">{final_conf}%</h1>
                    <h3 style="color:{status_clr}; margin:0;">{signal_text}</h3>
                </div>
            """, unsafe_allow_html=True)
        with strength_col:
            st.markdown(f"""
                <div class="glass-card" style="border-bottom: 4px solid {s_clr}; height: 220px;">
                    <p style="color:#666; letter-spacing:3px; font-size:10px; margin:0;">TREND STRENGTH</p>
                    <h1 style="color:{s_clr}; font-size:60px; margin:5px 0;">{int(adx_val)}</h1>
                    <h3 style="color:{s_clr}; margin:0;">{strength}</h3>
                </div>
            """, unsafe_allow_html=True)

        # EXECUTION BUTTONS
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🚀 EXECUTE BUY", key="buy_btn"):
                place_justmarket_trade(choice, 0, lots)
        with c2:
            if st.button("📉 EXECUTE SELL", key="sell_btn"):
                place_justmarket_trade(choice, 1, lots)

        # CHARTING (REMAINS THE SAME)
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.02, row_heights=[0.5, 0.1, 0.4])
        fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name="Price"), row=1, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=data['VWAP'], line=dict(color='orange', width=2), name="VWAP"), row=1, col=1)
        
        buys = data[data['Entry'] == 1]; sells = data[data['Entry'] == -1]
        fig.add_trace(go.Scatter(x=buys.index, y=buys['Low']*0.999, mode="markers", marker=dict(symbol="triangle-up", size=15, color="#00FF88"), name="BUY"), row=1, col=1)
        fig.add_trace(go.Scatter(x=sells.index, y=sells['High']*1.001, mode="markers", marker=dict(symbol="triangle-down", size=15, color="#FF3366"), name="SELL"), row=1, col=1)

        fig.add_trace(go.Bar(x=data.index, y=data['Volume'], marker_color=['#FFFF00' if s else '#333' for s in data['Is_Spike']]), row=2, col=1)
        fig.add_trace(go.Bar(x=data.index, y=data['MACD_H'], marker_color=['#00FF88' if v >= 0 else '#FF3366' for v in data['MACD_H']]), row=3, col=1)

        fig.update_layout(height=800, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True, key=f"chart_{choice}")

dashboard_engine()
