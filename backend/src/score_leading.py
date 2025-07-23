import pandas as pd, numpy as np
from .fred.fetch_fred import *
from .fred.helper import *

def score_leading(*, idx: pd.DatetimeIndex, valid: pd.Timestamp, df: pd.DataFrame | None = None):
    """
    Combined LEADING block:
      - Yield curve logic
      - Liquidity logic (+ flow modifiers)
      - Override rule: if YC score > 0 but liquidity is EXTREME, liquidity takes control

    Returns
    -------
    sell : pd.Series[bool]
    buy  : pd.Series[bool]
    liq_90 : float
    df   : pd.DataFrame  # includes all intermediate cols + final score_leading
    """
    # -------------------- Prep --------------------
    ix = idx[idx >= valid]
    if df is None:
        df = pd.DataFrame(index=ix)
    else:
        df = df.reindex(ix).copy()

    # -------------------- Yield Curve --------------------
    yc_raw = to_series(fetch_weekly_fred_series("T10Y3M"))
    df["yc"]     = yc_raw.reindex(ix, method="nearest").ffill()
    df["yc_inv"] = (df["yc"] < 0).astype(bool)

    df["inv_12m"]  = df["yc_inv"].rolling(52, min_periods=1).max().shift(1).fillna(False).astype(bool)
    df["post_inv"] = (~df["yc_inv"]) & df["inv_12m"]

    bull_start = df["yc"] >= 2.5
    bull_end   = df["yc"] < 0

    rb = pd.Series(pd.NA, index=ix, dtype="boolean")
    rb.loc[bull_start] = True
    rb.loc[bull_end]   = False
    df["regime_bull"] = rb.ffill().fillna(False).astype(bool)

    score_yc = pd.Series(0.5, index=ix, dtype=float)    # baseline
    score_yc.loc[df["post_inv"]]    = 1.5
    score_yc.loc[df["yc_inv"]]      = 0.5               # stays 0.5 while inverted
    score_yc.loc[df["regime_bull"]] = -1.0              # bull override
    df["score_yc"] = score_yc

    # -------------------- Liquidity --------------------
    m2  = to_series(fetch_monthly_fred_series("M2SL" )).reindex(ix, method="nearest").ffill()
    tga = to_series(fetch_weekly_fred_series_friday("WTREGEN")).reindex(ix, method="nearest").ffill()
    rrp = to_series(fetch_weekly_fred_series("RRPONTSYD")).reindex(ix, method="nearest").fillna(0).bfill().ffill()

    df["net_liq"]          = m2 - tga - rrp
    df["net_liq_6m"]       = df["net_liq"].pct_change(26)
    df["net_liq_6m_sust"]  = df["net_liq_6m"].rolling(4, min_periods=1).mean()

    q = df["net_liq_6m"].dropna()
    liq_68, liq_80, liq_90, liq_95 = q.quantile([0.68, 0.80, 0.90, 0.95])

    s = df["net_liq_6m_sust"]
    extreme = s > liq_95
    strong  = (s > liq_90) & ~extreme
    good    = (s > liq_80) & ~strong
    weak    = s < 0
    normal  = ~(extreme | strong | good | weak)

    base_liq = np.select(
        [extreme, strong, good, normal, weak],
        [-3.0,   -2.0,  -1.5,  0.0,    0.75],
        default=np.nan
    )
    base_liq = pd.Series(base_liq, index=ix).ffill().fillna(0.25)

    # --- Flow modifiers (gated) ---
    rrp_4w = rrp.diff(4)
    tga_4w = tga.diff(4)
    rrp_thr = rrp_4w.abs().rolling(52, min_periods=26).quantile(0.70)
    tga_thr = tga_4w.abs().rolling(52, min_periods=26).quantile(0.70)

    rrp_down = rrp_4w < -rrp_thr
    tga_down = tga_4w < -tga_thr
    rrp_up   = rrp_4w >  rrp_thr
    tga_up   = tga_4w >  tga_thr

    bull_raw = rrp_down & tga_down
    bear_raw = rrp_up   | tga_up

    bull_flow = bull_raw.rolling(2, min_periods=2).sum() == 2
    bear_flow = bear_raw.rolling(2, min_periods=2).sum() == 2

    # gates
    bull_gate = (base_liq >= 0.0) & (base_liq <= 0.75)  # neutral/weak liquidity
    bear_gate = (base_liq <  0.0) & (base_liq > -2.0)   # good but not extreme

    flow_adj = pd.Series(0.0, index=ix)
    flow_adj.loc[bull_flow & bull_gate] -= 1.5
    flow_adj.loc[bear_flow & bear_gate] += 0.5

    score_liq = (base_liq + flow_adj).astype(float)
    df["score_liquidity"] = score_liq
    df["liq_extreme"] = extreme

    # -------------------- Override rule --------------------
    strong_or_extreme = strong | extreme
    condition_triggered = (score_yc > 0) & (strong | extreme)

    override_active = pd.Series(False, index=df.index)
    active = False
    for date in df.index:
        if condition_triggered.loc[date]:
            active = True
        if df["net_liq_6m_sust"].loc[date] < 0:
            active = False
        override_active.loc[date] = active

    df["score_leading"] = score_yc.copy()
    df.loc[override_active, "score_leading"] = score_liq.loc[override_active]


    sell = df["score_leading"] >= 1
    buy  = df["score_leading"] <= -1

    return sell, buy, liq_90, df
