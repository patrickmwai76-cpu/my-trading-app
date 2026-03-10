import streamlit as st
import pandas as pd
import pandas_ta as ta
import yfinance as yf
import plotly.graph_objects as go

# --- 1. CONFIG ---
st.set_page_config(page_title="PATRO AI PRO V11.9.0", layout="wide")
st.markdown("<style>.stApp { background: #010101; color: #ffffff; }</style>", unsafe_allow_html=True)

# --- 2. DATA ENGINE ---
def get_clean_data(ticker, interval):
    try:
        df = yf.download(ticker, period="5d", interval=interval, progress=False, auto_adjust=True)
        if df.empty: return pd.DataFrame()
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        return df
    except: return pd.DataFrame()

def add_indicators(df):
    df['RSI'] = ta.rsi(df.Close, length=14)
    df['VWAP'] = ta.vwap(df.High, df.Low, df.Close, df.Volume)
    # Fair Value Gap (FVG) Detection
    df['FVG_Up'] = (df['Low'].shift(-1) > df['High'].shift(1)) & (df['Close'] > df['Open'])
    df['FVG_Down'] = (df['High'].shift(-1) < df['Low'].shift(1)) & (df['Close'] < df['Open'])
    return df

# --- 3. UI & LOGIC ---
st.title("🌌 PATRO AI PRO V11.9.0 | MTF + FVG")

with st.sidebar:
    st.header("🏢 SETTINGS")
    asset = st.selectbox("Target", ["GOLD", "GBPUSD", "US30"])
    ticker = {"GOLD":"GC=F", "GBPUSD":"GBPUSD=X", "US30":"^DJI"}[asset]
    st.divider()
    st.write("🟢 **FVG Detection:** ON")
    st.write("🔵 **MTF Filter:** ON")

@st.fragment(run_every="15s")
def run_app():
    # Fetch 5m (Entry) and 1H (Confirmation)
    df_5m = add_indicators(get_clean_data(ticker, "5m"))
    df_1h = add_indicators(get_clean_data(ticker, "1h"))
    
    if df_5m.empty or df_1h.empty: return

    # MTF Bias Logic
    bias_1h = "BULLISH" if df_1h.Close.iloc[-1] > df_1h.VWAP.iloc[-1] else "BEARISH"
    signal_5m = "BUY" if df_5m.Close.iloc[-1] > df_5m.VWAP.iloc[-1] else "SELL"
    
    # Final SURE Signal: Do 1H and 5m match?
    is_sure = (bias_1h == "BULLISH" and signal_5m == "BUY") or (bias_1h == "BEARISH" and signal_5m == "SELL")
    sig_text = f"🏦 BANK {signal_5m} (SURE)" if is_sure else "⌛ WAIT (MTF CLASH)"
    sig_col = "#00FF88" if is_sure and signal_5m == "BUY" else "#FF3366" if is_sure else "#FFA500"

    # Display Metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("1H TREND BIAS", bias_1h)
    c2.markdown(f"<h2 style='color:{sig_col}; text-align:center;'>{sig_text}</h2>", unsafe_allow_html=True)
    c3.metric("CURRENT RSI", f"{df_5m.RSI.iloc[-1]:.2f}")

    # --- CHART ---
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df_5m.index, open=df_5m.Open, high=df_5m.High, low=df_5m.Low, close=df_5m.Close, name="5m Price"))
    fig.add_trace(go.Scatter(x=df_5m.index, y=df_5m.VWAP, line=dict(color='cyan', dash='dot'), name="VWAP"))
    
    # Highlight FVGs (Imbalances)
    for i in range(1, len(df_5m)-1):
        if df_5m['FVG_Up'].iloc[i]:
            fig.add_shape(type="rect", x0=df_5m.index[i], x1=df_5m.index[i+2], y0=df_5m['High'].iloc[i-1], y1=df_5m['Low'].iloc[i+1], fillcolor="green", opacity=0.3, line_width=0)
        if df_5m['FVG_Down'].iloc[i]:
            fig.add_shape(type="rect", x0=df_5m.index[i], x1=df_5m.index[i+2], y0=df_5m['Low'].iloc[i-1], y1=df_5m['High'].iloc[i+1], fillcolor="red", opacity=0.3, line_width=0)

    fig.update_layout(height=600, template="plotly_dark", xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

run_app()
