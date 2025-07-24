from .fred.fetch_fred import *
from .fred.helper import *
from dotenv import load_dotenv
import pandas as pd, numpy as np, yfinance as yf, matplotlib.pyplot as plt
import os
from .score_leading import score_leading
from .score_timing import score_timing
from .score_confirming import score_confirming

load_dotenv()
start_date = os.getenv("DATA_FROM_DATE")

def score(window: int = 50):
    yc_raw   = to_series(fetch_weekly_fred_series("T10Y3M"))
    m2_raw   = to_series(fetch_monthly_fred_series("M2SL"))
    tga_raw  = to_series(fetch_weekly_fred_series_friday("WTREGEN"))
    rrp_raw  = to_series(fetch_weekly_fred_series("RRPONTSYD"))     
    junk_raw = to_series(fetch_weekly_fred_series("BAMLH0A0HYM2"))
    start_ix = max(s.index[0] for s in (yc_raw, m2_raw, tga_raw, rrp_raw, junk_raw))
    end_ix   = min(s.index[-1] for s in (yc_raw, m2_raw, tga_raw, rrp_raw, junk_raw))
    idx = pd.date_range(start=start_ix, end=end_ix, freq="W-FRI")
    df = pd.DataFrame(index=idx)
    big7 = ["AMZN","NVDA","META","GOOGL","AAPL","MSFT","AVGO"]
    px = (yf.download(big7, start=start_date, auto_adjust=True, progress=False)["Close"])
    px.index = px.index.tz_localize(None) 
    px = px.reindex(idx, method="nearest")
    big7_avg = px[big7].mean(axis=1)
    big7_wma = weighted_ma(big7_avg, n=window)
    valid = big7_wma.first_valid_index()
    if valid is None:
        valid = idx[0]
    valid = pd.Timestamp(valid) 
    sell, buy, liq_90, df = score_leading(idx=idx, valid=valid, df=df)
    j95, calm_junk, df = score_confirming(idx=idx, sell=sell, buy=buy, df=df)
    buy_zone   = df["regime_bull"] & (df["net_liq_6m_sust"] > liq_90) & calm_junk
    crash_zone = sell  & (df["junk_roc_sm"] > j95)
    df["crash_zone"] = crash_zone
    df["buy_zone"] = buy_zone
    df = score_timing(
        idx=idx, px=px, big7=big7, big7_wma=big7_wma,
        sell=sell, buy=buy, buy_zone=buy_zone, crash_zone=crash_zone, df=df
    )
    
    df["composite_score"] = (
            df["score_leading"] +
            df["score_confirming" ]+ 
            df["score_timing"]
        )
    df["sell_signal"] = (df["composite_score"] > 3).astype(int)
    df["buy_signal"]  = (df["composite_score"] <= -2).astype(int)

    for lbl, a, b in (
            ("2007-03→2008-06","2007-06-01","2010-06-30"),
            ("2019-01→2020-06","2017-01-01","2019-01-01"),
            ("2024-09→2025-06","2019-08-01","2021-06-30")
        ):
            m = (df.index >= a) & (df.index <= b)
            print(f"\n── {lbl} ──")
            print(df.loc[m, [
                "yc","yc_inv","post_inv","score_leading","net_liq_6m","net_liq_6m_sust","score_liquidity","score_confirming",
                "cnt_below","cnt_above","big7_px","big7_wma","score_timing",
                "crash_zone","buy_zone","composite_score",  
            ]].to_string())
    
    # fig, ax = plt.subplots(figsize=(12,6))
    # df["composite_score"].plot(ax=ax, lw=2)
    # x_pos = df.index[0] + pd.Timedelta(days=30)     
    # ax.text(x_pos, 2, "SELL", va="bottom")
    # ax.text(x_pos, -1, "BUY ZONE", va="bottom")
    # ax.axhline(0,   ls="-",  color="gray",label="ZERO")
    # ax.set(title="Regime Score (with Crash-Zone/Buy-Zone Override)", ylabel="Score")
    # ax.grid(alpha=.3)
    # plt.tight_layout()
    # plt.show()
    return df
score() 