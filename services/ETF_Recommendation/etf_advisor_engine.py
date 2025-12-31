import joblib
import pandas as pd
import yfinance as yf
import numpy as np
import os
from pathlib import Path

# Load model once at import time
SCRIPT_DIR = Path(__file__).resolve().parent
MODEL_PATH = SCRIPT_DIR / "ETF_LongTerm_Model_20251201.pkl"
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")

model = joblib.load(MODEL_PATH)
print("ETF Model loaded – December 2025 version")

tickers = ["SPY", "ACWI", "EFA", "VEU", "VWO", "VNQ", "TLT", "IEF", "LQD", "GLD", "DBC", "BWX"]

# Download and cache data
prices = yf.download(tickers, period="max", auto_adjust=True, progress=False)["Close"]
prices = prices[tickers].dropna()

# Build features – 100% identical to your training code
returns = prices.pct_change()
mom_21 = prices.pct_change(21)
mom_63 = prices.pct_change(63)
mom_126 = prices.pct_change(126)
mom_252 = prices.pct_change(252)
mom_504 = prices.pct_change(504)
acceleration = prices.pct_change(21) - prices.pct_change(252)
near_52wh = prices / prices.rolling(252).max()

spy_mom = prices["SPY"].pct_change(63)
dbc_mom = prices["DBC"].pct_change(63)
spread = spy_mom - dbc_mom

anti = pd.DataFrame(index=prices.index, columns=tickers)
for t in tickers:
    anti[t] = -spread if t in ["DBC", "GLD"] else spread

feature_list = [
    mom_21.add_suffix("_mom_mom_21d"),
    mom_63.add_suffix("_mom_63d"),
    mom_126.add_suffix("_mom_126d"),
    mom_252.add_suffix("_mom_252d"),
    mom_504.add_suffix("_mom_504d"),
    (mom_252 - mom_21).add_suffix("_dual_mom"),
    (prices / prices.rolling(252).max() - 1).add_suffix("_dist_52whigh"),
    (prices / prices.rolling(50).mean()).add_suffix("_vs_sma50"),
    (prices / prices.rolling(200).mean()).add_suffix("_vs_sma200"),
    (prices.rolling(50).mean() > prices.rolling(200).mean())
    .astype(int)
    .add_suffix("_golden_cross"),
    (returns.rolling(63).std() * np.sqrt(252)).add_suffix("_vol_63d"),
    (returns.rolling(252).std() * np.sqrt(252)).add_suffix("_vol_252d"),
    mom_63.rank(axis=1, pct=True).add_suffix("_rs_63d"),
    mom_252.rank(axis=1, pct=True).add_suffix("_rs_252d"),
    mom_504.rank(axis=1, pct=True).add_suffix("_rs_504d"),
    acceleration.add_suffix("_acceleration_21vs252"),
    near_52wh.add_suffix("_near_52wh"),
    anti.add_suffix("_anti_commodity_bias"),
]

features_all = pd.concat(feature_list, axis=1).dropna()

reasons = {
    "SPY": "US market leadership & AI/tech growth engine",
    "ACWI": "Global diversification – safest default",
    "EFA": "Developed ex-US – attractive valuations",
    "VEU": "Broad international exposure",
    "VWO": "Emerging markets catch-up",
    "VNQ": "Real estate recovery",
    "TLT": "Long bonds rally on rate cuts",
    "IEF": "Safe intermediate bonds",
    "LQD": "Corporate bond spread compression",
    "GLD": "Gold – inflation & war hedge",
    "DBC": "Commodities tailwind",
    "BWX": "International bonds & currency play",
}


def get_recommendation(amount: float, specific_date: str = None):
    day = prices.index[-1] if specific_date is None else pd.to_datetime(specific_date)
    day = prices.index[prices.index <= day][-1]

    row = features_all.loc[day]
    preds = {}
    for t in tickers:
        cols = [c for c in row.index if c.startswith(t + "_")]
        X = row[cols].values.reshape(1, -1)
        preds[t] = model.predict(X, predict_disable_shape_check=True)[0]

    df = pd.DataFrame(list(preds.items()), columns=["ETF", "2Y"])
    df = df.sort_values("2Y", ascending=False)

    best = df.iloc[0]["2Y"]

    if best > 0.22:
        alloc = df.iloc[[0]].copy()
        alloc["Weight"] = 1.0
        strategy = "concentrated"
    elif best > 0.15:
        alloc = df[df["2Y"] > 0.15].head(3).copy()
        alloc["Weight"] = 1.0 / len(alloc)
        strategy = "diversified"
    else:
        alloc = pd.DataFrame({"ETF": ["ACWI"], "2Y": [best], "Weight": [1.0]})
        strategy = "safe"

    alloc["Amount_EUR"] = (alloc["Weight"] * amount).round().astype(int)
    alloc["forecast_2y"] = alloc["2Y"]
    alloc["reason"] = alloc["ETF"].map(reasons)

    return {
        "date": day.date(),
        "total_amount": float(amount),
        "strategy": strategy,
        "expected_2y_return": float(best),
        "allocations": alloc[["ETF", "forecast_2y", "Weight", "Amount_EUR", "reason"]].to_dict(
            orient="records"
        ),
    }
