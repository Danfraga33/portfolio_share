from .fred.fetch_fred import *
from .fred.helper import *
from dotenv import load_dotenv
import pandas as pd, numpy as np, yfinance as yf, matplotlib.pyplot as plt
import os

load_dotenv()
start_date = os.getenv("DATA_FROM_DATE")

def score(window: int = 50):
    """
    Regime score by function:
      - Leading:    Yield curve, Liquidity
      - Confirming: Junk ROC (Michez)
      - Timing:     Breadth (Mag-7 WMA or >=3 below WMA),
                    with heavier weights in crash and buy zones
    """
    # ---- FRED SERIES ----
    yc_raw   = to_series(fetch_weekly_fred_series("T10Y3M"))
    junk_raw = to_series(fetch_weekly_fred_series("BAMLH0A0HYM2"))
    m2_raw   = to_series(fetch_monthly_fred_series("M2SL"))
    tga_raw  = to_series(fetch_weekly_fred_series_friday("WTREGEN"))
    rrp_raw  = to_series(fetch_weekly_fred_series("RRPONTSYD"))

    start_ix = max(s.index[0] for s in (yc_raw, m2_raw, tga_raw, rrp_raw, junk_raw))
    end_ix   = min(s.index[-1] for s in (yc_raw, m2_raw, tga_raw, rrp_raw, junk_raw))
    idx = pd.date_range(start=start_ix, end=end_ix, freq="W-FRI")

    yc   = yc_raw.reindex(idx, method="nearest").ffill()
    junk = junk_raw.reindex(idx, method="nearest").ffill()
    m2   = m2_raw.reindex(idx, method="nearest").ffill()
    tga  = tga_raw.reindex(idx, method="nearest").ffill()
    rrp  = rrp_raw.reindex(idx, method="nearest").fillna(0).bfill().ffill()
    net_liq = (m2 - tga - rrp).dropna()

    # ---- PRICE SERIES ----
    big7 = ["AMZN","NVDA","META","GOOGL","AAPL","MSFT","AVGO"]
    px = (yf.download(big7, start=start_date, auto_adjust=True, progress=False)["Close"]
            .reindex(idx, method="nearest"))
    big7_avg = px[big7].mean(axis=1)
    big7_wma = weighted_ma(big7_avg, n=window)
    cnt_below = pd.DataFrame({t: (px[t] < weighted_ma(px[t], n=window)).astype(int) for t in big7}).sum(axis=1)
    cnt_above = pd.DataFrame({t: (px[t] > weighted_ma(px[t], n=window)).astype(int) for t in big7}).sum(axis=1)

    valid = big7_wma.first_valid_index()
    if valid is None:
        print("No valid data yet")
        return pd.DataFrame()
    idx = idx[idx >= valid]

    df = pd.DataFrame(index=idx)
    df["yc"]        = yc.reindex(idx)
    df["junk"]      = junk.reindex(idx)
    df["net_liq"]   = net_liq.reindex(idx)
    df["big7_px"]   = big7_avg.reindex(idx)
    df["big7_wma"]  = big7_wma.reindex(idx)
    df["cnt_below"] = cnt_below.reindex(idx)
    df["cnt_above"] = cnt_above.reindex(idx)

    # ---- Leading Indicators ----
    df["yc_inv"]           = (df["yc"] < 0).astype(int)
    df["yc_inv_sust"]      = df["yc_inv"].rolling(4, min_periods=1).mean() == 1
    df["was_inv_12m_sust"] = df["yc_inv_sust"].rolling(52, min_periods=1).max().fillna(0).astype(int)
    df["post_inv"]         = ((df["yc"] >= 0) & (df["was_inv_12m_sust"] == 1)).astype(int)

    df["regime_bull"] = False
    df.loc[df["yc"] >= 2.5, "regime_bull"] = True
    for i in range(1, len(df)):
        if df.iloc[i]["yc"] < 0:
            df.iloc[i, df.columns.get_loc("regime_bull")] = False
        elif df.iloc[i-1]["regime_bull"]:
            df.iloc[i, df.columns.get_loc("regime_bull")] = True

    # ---- Liquidity Momentum ----
    df["net_liq_6m"]      = df["net_liq"].pct_change(26)
    df["net_liq_6m_sust"] = df["net_liq_6m"].rolling(4, min_periods=1).mean()
    df["liq_mom2"]        = df["net_liq_6m"].diff(2)
    df["liq_neg_flags"]   = (df["net_liq_6m_sust"] < 0).astype(int)
    df["liq_neg_sust"]    = df["liq_neg_flags"].rolling(4, min_periods=4).sum() == 4
    df["bear_liq"]        = df["liq_neg_sust"] & (df["liq_mom2"] < 0)

    liq_90 = df["net_liq_6m"].dropna().quantile(0.90)
    liq_95 = df["net_liq_6m"].dropna().quantile(0.95)

    # --- Score Leading ---
    lead_conds = [
        df["regime_bull"],
        df["yc_inv"] & ~df["regime_bull"],
        df["post_inv"] & ~df["regime_bull"]
    ]
    lead_choices = [-1.0, 1.0, 1.5]
    df["score_leading"] = np.select(lead_conds, lead_choices, default=0.0)
    extreme_liq = (df["net_liq_6m_sust"] > liq_95)
    strong_liq  = (df["net_liq_6m_sust"] > liq_90) & (df["net_liq_6m_sust"] <= liq_95)
    weak_liq    = (df["net_liq_6m_sust"] < liq_90)
    df["liq_95_flag"]  = extreme_liq
    df["liq_95_roll2"] = df["liq_95_flag"].rolling(2, min_periods=2).sum() == 2
    df.loc[df["liq_95_roll2"], "score_leading"] -= 3.0

    # --- Score Liquidity ---
    sell = df["score_leading"] >= 1
    buy  = df["score_leading"] <= -1
    liq_conds = [
        extreme_liq,
        strong_liq,
        sell & weak_liq,
    ]
    liq_choices = [-3.0, -0.5, 0.5]
    df["score_liquidity"] = np.select(liq_conds, liq_choices, default=0.0)

    # --- Score Confirming (Junk ROC) ---
    df["junk_roc"]    = df["junk"].pct_change()
    df["junk_roc_sm"] = df["junk_roc"].rolling(12, min_periods=1).mean()
    df["wma_junk"] = weighted_junk_ma(df["junk"])
    
    j68 = df["junk_roc_sm"].quantile(0.68)
    j95 = df["junk_roc_sm"].quantile(0.95)
    calm_junk = df["junk_roc_sm"].abs() <= j68
    below_wma_junk = df["junk"] < df["wma_junk"]
    elevating_junk_bonds = df["junk_roc_sm"] > j95
    conf_conds = [
        sell & elevating_junk_bonds,
        buy  & below_wma_junk 
    ]
    junk_choices = [0.5, -0.5]
    df["score_confirming"] = np.select(conf_conds, junk_choices, default=0.0)
    df["score_confirming"] += df["bear_liq"].astype(float)

    # --- Breadth Flags ---
    sb1     = sell & (df["cnt_below"] >= 4)
    sb2     = sell & (df["big7_px"] * 1.05 < df["big7_wma"])
    state   = False
    states  = []
    for cnt in df["cnt_above"]:
        state = True if cnt >= 5 else False if cnt <= 2 else state
        states.append(state)
    bf1     = buy & pd.Series(states, index=df.index)
    bf2     = buy & (df["big7_px"] > df["big7_wma"]*1.05)
    bf2roll = bf2.rolling(2).sum() > 1

    print('j95',j95)
    # --- CRASH-ZONE & BUY-ZONE FLAGS ---
    crash_zone = sell  & (df["junk_roc_sm"] > j95)
    df["crash_zone"] = crash_zone
    buy_zone = df["regime_bull"] & (df['net_liq_6m_sust'] > liq_90) & calm_junk
    df["buy_zone"] = buy_zone

    # --- PICK TIMING CHOICES BASED ON ZONE ---
    # always these for sell
    normal_sell_choices = [1.0, 0.5]
    crash_sell_choices  = [2.0, 1.5]

    # these change for buy
    buy_zone_choices    = [-1.0, -0.5]  # in buy zone (strong)
    not_buy_zone_choices= [-2.0, -1.5]  # in not buy zone (mild)

    sell_conds = [sb2, sb1]
    buy_conds  = [bf2roll, bf1]

    # Compute sell timing for normal and crash
    normal_sell_timing = np.select(sell_conds, normal_sell_choices, default=0.0)
    crash_sell_timing  = np.select(sell_conds, crash_sell_choices,  default=0.0)

    # Buy timing (choose strong or mild per row)
    buy_timing = np.where(
        buy_zone,
        np.select(buy_conds, buy_zone_choices, default=0.0),
        np.select(buy_conds, not_buy_zone_choices, default=0.0)
    )

    # Combine sell and buy timing (mutually exclusive)
    normal_timing = normal_sell_timing + buy_timing
    crash_timing  = crash_sell_timing  + buy_timing

    df["score_timing"] = np.where(
        crash_zone,
        crash_timing,
        normal_timing
    )

    # --- Composite & Signals ---
    df["composite_score"] = (
        df["score_leading"] +
        df["score_liquidity"] +
        # df["score_confirming"] +
        df["score_timing"]
    )
    df["sell_signal"] = (df["composite_score"] > 2).astype(int)
    df["buy_signal"]  = (df["composite_score"] < -2).astype(int)

    # --- Diagnostics (optional print/plot) ---
    for lbl, a, b in (
        ("2007-03→2008-06","2007-06-01","2010-06-30"),
        ("2019-01→2020-06","2017-01-01","2019-01-01"),
        ("2024-09→2025-06","2019-08-01","2021-06-30")
    ):
        m = (df.index >= a) & (df.index <= b)
        print(f"\n── {lbl} ──")
        print(df.loc[m, [
            "yc","yc_inv","post_inv","score_leading","net_liq_6m","net_liq_6m_sust","score_liquidity",
            "junk","liq_neg_sust","junk_roc","junk_roc_sm","wma_junk","score_confirming",
            "cnt_below","cnt_above","big7_px","big7_wma","score_timing",
            "crash_zone","buy_zone","composite_score",
        ]].to_string())

    # fig, ax = plt.subplots(figsize=(12,6))
    # df["composite_score"].plot(ax=ax, lw=2)
    # x_pos = df.index[0] + pd.Timedelta(days=30)     
    # ax.text(x_pos, 2, "SELL", va="bottom")
    # ax.text(x_pos, 1.5, "REBALANCE AGGRESSIVELY", va="bottom")
    # ax.text(x_pos, 1, "REBALANCE", va="bottom")
    # ax.text(x_pos, -1, "BUY ZONE", va="bottom")
    # ax.axhline(0,   ls="-",  color="gray",label="ZERO")
    # ax.set(title="Regime Score (with Crash-Zone/Buy-Zone Override)", ylabel="Score")
    # ax.grid(alpha=.3)
    # plt.tight_layout()
    # plt.show()

    return df
