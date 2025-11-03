import streamlit as st
import pandas as pd
import time
import sys, os

# so we can import backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.analytics import fetch_ticks, compute_analytics


# ------------------- Streamlit UI -------------------
st.set_page_config(page_title="Gemscap Quant Dashboard", layout="wide")

st.title("📊 Gemscap Quant Analytics Dashboard")
st.markdown(
    "Real-time quantitative analytics on Binance tick data (BTCUSDT & ETHUSDT)."
)

# --- Sidebar Controls ---
st.sidebar.header("Settings")
timeframe = st.sidebar.selectbox("Data timeframe", [15, 30, 60], index=1)
interval = st.sidebar.selectbox("Resample interval", ["1min", "5min"], index=0)
refresh_rate = st.sidebar.slider("Auto-refresh every (seconds)", 5, 60, 20)

# --- Fetch & Compute ---
with st.spinner("Fetching data & computing analytics..."):
    dfs = fetch_ticks(["btcusdt", "ethusdt"], minutes=timeframe)
    result = compute_analytics(
    dfs["btcusdt"], dfs["ethusdt"], resample_interval="10s"
)


data = result["data"]
if data.empty:
    st.warning("Not enough data yet — let the collector run a few minutes.")
    st.stop()

# --- Summary Metrics ---
col1, col2, col3 = st.columns(3)
col1.metric("Hedge Ratio", f"{result['hedge_ratio']:.3f}")
col2.metric("ADF p-value", f"{result['adf_pvalue']:.3f}" if result["adf_pvalue"] else "n/a")
latest_z = data["zscore"].iloc[-1]
col3.metric("Latest Z-Score", f"{latest_z:.2f}")

# --- Z-score Alert ---
latest_zscore = result["data"]["zscore"].dropna().iloc[-1]
if abs(latest_zscore) > 2:
    st.error(f"⚠️ Alert: Z-score exceeded threshold! (|Z| = {latest_zscore:.2f})")
elif abs(latest_zscore) > 1:
    st.warning(f"⚠️ Caution: Moderate deviation (Z = {latest_zscore:.2f})")
else:
    st.success(f"✅ Stable: Z-score within normal range (Z = {latest_zscore:.2f})")

# --- Charts ---
st.subheader("Price Comparison")
st.line_chart(data[["BTCUSDT", "ETHUSDT"]])

st.subheader("Spread & Z-Score")
st.line_chart(data[["spread", "zscore"]])

st.subheader("Rolling Correlation")
st.line_chart(data[["rolling_corr"]])

# --- Data Export Section ---
st.subheader("📤 Download Processed Analytics Data")
csv = result["data"].to_csv(index=True).encode('utf-8')
st.download_button(
    label="Download analytics data as CSV",
    data=csv,
    file_name="quant_analytics_data.csv",
    mime="text/csv"
)

# --- Alert Section ---
if abs(latest_z) > 2:
    st.error(f"🚨 Z-score = {latest_z:.2f} → Potential mean-reversion signal!")

# --- Auto-refresh note ---
st.caption(f"Dashboard refreshes every {refresh_rate}s automatically.")
time.sleep(refresh_rate)
st.rerun()

