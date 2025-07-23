import pandas as pd, numpy as np, yfinance as yf, matplotlib.pyplot as plt
from .fred.fetch_fred import *
from .fred.helper import *
import os

load_dotenv()
start_date = os.getenv("DATA_FROM_DATE")
def score_liquidity(*, df):
    idx = df.index

    m2  = to_series(fetch_monthly_fred_series("M2SL")).reindex(idx, method="nearest").ffill()
    tga = to_series(fetch_weekly_fred_series_friday("WTREGEN")).reindex(idx, method="nearest").ffill()
    rrp = to_series(fetch_weekly_fred_series("RRPONTSYD")).reindex(idx, method="nearest").fillna(0).bfill().ffill()

    df["net_liq"] = m2 - tga - rrp

    df["net_liq_6m"]      = df["net_liq"].pct_change(26)
    df["net_liq_6m_sust"] = df["net_liq_6m"].rolling(4, min_periods=1).mean()
    df["liq_mom2"]        = df["net_liq_6m"].diff(2)
    df["liq_neg_sust"]    = (df["net_liq_6m_sust"] < 0).rolling(4, min_periods=4).sum() == 4
    df["bear_liq"]        = df["liq_neg_sust"] & (df["liq_mom2"] < 0)

    q = df["net_liq_6m"].dropna()
    liq_68, liq_80, liq_90, liq_95 = q.quantile([0.68, 0.80, 0.90, 0.95])

    s = df["net_liq_6m_sust"]
    extreme = s > liq_95
    strong  = (s > liq_90) & ~extreme
    good    = (s > liq_80) & ~strong
    weak    = s < 0
    normal  = ~(extreme | strong | good | weak)

    base = np.select(
        [extreme, strong, good, normal, weak],
        [-3.0,   -2.0,  -1.5,  0.0,    0.75],
        default=np.nan
    )
    base_score = pd.Series(base, index=idx).ffill().fillna(0.25)

    mid_for_bull = (base_score > -2.0) & (base_score >= 0.0)   # meh/weak liquidity
    mid_for_bear = (base_score <  0.0) & (base_score > -2.5)    

    rrp_4w = rrp.diff(4)
    tga_4w = tga.diff(4)
    rrp_thr = rrp_4w.abs().rolling(52, min_periods=26).quantile(0.70)
    tga_thr = tga_4w.abs().rolling(52, min_periods=26).quantile(0.70)
    rrp_big_down = rrp_4w < -rrp_thr
    tga_big_down = tga_4w < -tga_thr
    rrp_big_up   = rrp_4w >  rrp_thr
    tga_big_up   = tga_4w >  tga_thr

    bull_raw = rrp_big_down & tga_big_down          
    bear_raw = rrp_big_up   | tga_big_up

    bull_flow = bull_raw.rolling(2, min_periods=2).sum() == 2
    bear_flow = bear_raw.rolling(2, min_periods=2).sum() == 2

    # ---- choose one approach ----
    # A) binary modifier:
    flow_adj = pd.Series(0.0, index=df.index)
    flow_adj.loc[bull_flow & mid_for_bull] -= 1.5   # or -1.5 for z>2 spikes
    flow_adj.loc[bear_flow & mid_for_bear] += 0.5   # or 0.25 if still too chatty
    df["score_liquidity"] = (base_score + flow_adj).astype(float)
    return sell, buy, liq_90, df
