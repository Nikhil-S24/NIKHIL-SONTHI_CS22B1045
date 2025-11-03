import pandas as pd
import numpy as np
import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta
from statsmodels.regression.linear_model import OLS
from statsmodels.tools import add_constant
from statsmodels.tsa.stattools import adfuller


# ---------- Database Connection ----------
def fetch_ticks(symbols=["btcusdt", "ethusdt"], minutes=30):
    """
    Fetch last `minutes` of tick data for given symbols from MySQL.
    """
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="nikhil",
            database="quant_data"
        )

        dfs = {}
        for sym in symbols:
            query = f"""
            SELECT timestamp, price FROM ticks
            WHERE symbol='{sym.upper()}'
            AND timestamp > NOW() - INTERVAL {minutes} MINUTE
            ORDER BY timestamp ASC
            """
            dfs[sym] = pd.read_sql(query, connection)
            dfs[sym]["timestamp"] = pd.to_datetime(dfs[sym]["timestamp"])
            dfs[sym].set_index("timestamp", inplace=True)

        connection.close()
        return dfs

    except Error as e:
        print(f"❌ MySQL Error: {e}")
        return None


def kalman_filter_hedge_ratio(y, x):
    """
    Estimate dynamic hedge ratio between y (BTC) and x (ETH) using Kalman Filter.
    Returns array of hedge ratios matching input length.
    """
    delta = 1e-5  # small transition variance
    obs_var = 0.001  # observation variance

    n = len(y)
    hedge_ratio = np.zeros(n)
    P = np.zeros(n)
    
    # Initial guesses
    hedge_ratio[0] = 0
    P[0] = 1

    for t in range(1, n):
        # Prediction step
        hedge_ratio[t] = hedge_ratio[t-1]
        P[t] = P[t-1] + delta

        # Update step
        if np.isnan(x[t]) or np.isnan(y[t]): 
            continue
        K = P[t] * x[t] / (x[t]**2 * P[t] + obs_var)
        hedge_ratio[t] += K * (y[t] - hedge_ratio[t] * x[t])
        P[t] *= (1 - K * x[t])

    return hedge_ratio

# ---------- Core Analytics ----------
def compute_analytics(df1, df2, symbol1="BTCUSDT", symbol2="ETHUSDT", resample_interval="10s"):
    """
    Compute hedge ratio, dynamic hedge ratio (Kalman Filter),
    spread, z-score, rolling correlation, and ADF test.
    """
    # --- Resample prices ---
    df1_resampled = df1["price"].resample(resample_interval).mean().dropna()
    df2_resampled = df2["price"].resample(resample_interval).mean().dropna()

    combined = pd.concat([df1_resampled, df2_resampled], axis=1)
    combined.columns = [symbol1, symbol2]
    combined.dropna(inplace=True)

    # --- Static hedge ratio using OLS ---
    X = add_constant(combined[symbol2])
    model = OLS(combined[symbol1], X).fit()
    hedge_ratio = model.params[symbol2]

    # --- Dynamic hedge estimation using Kalman Filter ---
    combined["kalman_hedge"] = kalman_filter_hedge_ratio(
        combined[symbol1].values, combined[symbol2].values
    )
    combined["dynamic_spread"] = combined[symbol1] - combined["kalman_hedge"] * combined[symbol2]

    # --- Static spread & z-score ---
    combined["spread"] = combined[symbol1] - hedge_ratio * combined[symbol2]
    combined["zscore"] = (combined["spread"] - combined["spread"].mean()) / combined["spread"].std()

    # --- Rolling correlation (5-period window) ---
    combined["rolling_corr"] = combined[symbol1].rolling(5).corr(combined[symbol2])

    combined.fillna(method="ffill", inplace=True)

    # --- ADF test on spread ---
    try:
        adf_result = adfuller(combined["spread"].dropna())
        adf_pvalue = adf_result[1]
    except:
        adf_pvalue = np.nan

    # --- Return results ---
    return {
        "data": combined,
        "hedge_ratio": hedge_ratio,
        "adf_pvalue": adf_pvalue
    }


if __name__ == "__main__":
    symbols = ["btcusdt", "ethusdt"]

    dfs = fetch_ticks(symbols, minutes=60)
    if dfs:
        result = compute_analytics(dfs["btcusdt"], dfs["ethusdt"])
        print("\n📊 Analytics Summary")
        print("----------------------------")
        print(f"Hedge Ratio: {result['hedge_ratio']:.4f}")
        print(f"ADF p-value: {result['adf_pvalue']:.4f}")
        print(result["data"].tail())

