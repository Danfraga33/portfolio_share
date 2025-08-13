from .fred.fetch_fred import *
from .fred.helper import *
from dotenv import load_dotenv
import pandas as pd, numpy as np, yfinance as yf, matplotlib.pyplot as plt
import os
load_dotenv()
start_date = os.getenv("DATA_FROM_DATE")

def score_confirming(idx, sell, buy, df):
    # 1) Align & fill upstream series BEFORE using them
    claims = to_series(fetch_weekly_fred_series_friday("IC4WSA")).reindex(idx).ffill()
    junk   = to_series(fetch_weekly_fred_series("BAMLH0A0HYM2")).reindex(idx).ffill()

    df["junk"] = junk
    df["4w_claims"] = claims

    # 2) Junk momentum
    df["junk_roc"]    = df["junk"].pct_change()
    df["junk_roc_sm"] = df["junk_roc"].rolling(12, min_periods=1).mean()
    df["wma_junk"]    = weighted_junk_ma(df["junk"]).reindex(idx)

    # 3) Quantiles on valid data
    j68 = df["junk_roc_sm"].quantile(0.68)
    j95 = df["junk_roc_sm"].quantile(0.95)
    calm_junk = df["junk_roc_sm"].abs() <= j68

    # 4) Claims YoY and 12w changes — silence deprecation by setting fill_method=None
    claims_yoy = df["4w_claims"].pct_change(52, fill_method=None)
    claims_12w = df["4w_claims"].pct_change(12, fill_method=None)

    # 5) Conditions (tune thresholds to actually fire)
    below_wma_junk       = df["junk"] < df["wma_junk"]
    elevating_junk_bonds = df["junk_roc_sm"] > j95

    # TIP: recent cycles rarely see <200k; use a percentile or a slightly higher cut
    low_claims_abs = df["4w_claims"] < 230_000          # was 200_000 (too tight)
    low_claims_trend = (claims_yoy <= 0)  # non-worsening YoY

    conf_conds = [
        sell & elevating_junk_bonds & (df["4w_claims"] > 270_000) & (claims_yoy > -0.15),
        sell & (elevating_junk_bonds | ((df["4w_claims"] > 270_000) & (claims_yoy > -0.15))),
        buy  & below_wma_junk & low_claims_abs & low_claims_trend,
        buy  & below_wma_junk
    ]
    junk_choices = [1.25, 0.75, -0.75, -0.5]

    df["score_confirming"] = np.select(conf_conds, junk_choices, default=0.0).clip(-1.5, 1.5)
    print({
  "sell_true": int(sell.sum()),
  "buy_true": int(buy.sum()),
  "elev_junk": int((df["junk_roc_sm"] > j95).sum()),
  "below_wma": int((df["junk"] < df["wma_junk"]).sum()),
  "claims_low": int((df["4w_claims"] < 230_000).sum()),
  "claims_yoy<=0": int((df["4w_claims"].pct_change(52, fill_method=None) <= 0).sum()),
  "calm_junk": int((df["junk_roc_sm"].abs() <= j68).sum()),
})
    print(df[["junk","wma_junk","junk_roc_sm","4w_claims"]].tail(3).to_string())
    return j95, calm_junk, df
