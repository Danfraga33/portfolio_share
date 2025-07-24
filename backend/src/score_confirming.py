from .fred.fetch_fred import *
from .fred.helper import *
from dotenv import load_dotenv
import pandas as pd, numpy as np, yfinance as yf, matplotlib.pyplot as plt
import os
load_dotenv()
start_date = os.getenv("DATA_FROM_DATE")

def score_confirming(idx, sell, buy, df):
   initial_claims= to_series(fetch_weekly_fred_series_friday("IC4WSA"))
   junk_raw = to_series(fetch_weekly_fred_series("BAMLH0A0HYM2"))
   junk = junk_raw.reindex(idx, method="nearest").ffill()

   df["junk"]      = junk.reindex(idx)
   df["4w_claims"] = initial_claims.reindex(idx)
   df["junk_roc"]    = df["junk"].pct_change()
   df["junk_roc_sm"] = df["junk_roc"].rolling(12, min_periods=1).mean()
   df["wma_junk"] = weighted_junk_ma(df["junk"])
   
   j68 = df["junk_roc_sm"].quantile(0.68)
   j95 = df["junk_roc_sm"].quantile(0.95)
   calm_junk = df["junk_roc_sm"].abs() <= j68

   below_wma_junk = df["junk"] < df["wma_junk"]
   elevating_junk_bonds = df["junk_roc_sm"] > j95
   elevated_4w_claims = df['4w_claims'] > 270000 
   elevated_initial_YoY = df['4w_claims'].pct_change(52) > -.15
   elevated_initial = elevated_4w_claims & elevated_initial_YoY
   conf_conds = [
       sell & elevating_junk_bonds & elevated_initial,
       sell & (elevating_junk_bonds | elevated_initial),
       sell & calm_junk,
       buy & below_wma_junk & (df['4w_claims'] < 200_000) & (df['4w_claims'].pct_change(52) <= 0),
       buy  & below_wma_junk, 
       buy & calm_junk,
   ]
   junk_choices = [1.25, 0.75, 0.25, -0.75, -0.5, 0.25]
   
   df["score_confirming"] = np.select(conf_conds, junk_choices, default=0.0).clip(-1.5,1.5)
   return j95, calm_junk, df