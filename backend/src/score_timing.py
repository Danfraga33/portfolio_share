from .fred.fetch_fred import *
from .fred.helper import *
from dotenv import load_dotenv
import pandas as pd, numpy as np, yfinance as yf, matplotlib.pyplot as plt
import os

load_dotenv()
start_date = os.getenv("DATA_FROM_DATE")
def score_timing(idx, px,big7, big7_wma, sell, buy, buy_zone, crash_zone,df, window: int = 50,):
   cnt_below = pd.DataFrame({t: (px[t] < weighted_ma(px[t], n=window)).astype(int) for t in big7}).sum(axis=1)
   cnt_above = pd.DataFrame({t: (px[t] > weighted_ma(px[t], n=window)).astype(int) for t in big7}).sum(axis=1)
   
   big7_avg = px[big7].mean(axis=1)
   df["big7_px"]   = big7_avg.reindex(idx)
   df["big7_wma"]  = big7_wma.reindex(idx)
   df["cnt_below"] = cnt_below.reindex(idx)
   df["cnt_above"] = cnt_above.reindex(idx)
   
   buy_zone_choices    = [-1.0, -0.5]  # in buy zone (strong)
   not_buy_zone_choices= [-2.0, -1.5]  # in not buy zone (mild)
   
   normal_sell_choices = [1.0, 0.5]
   crash_sell_choices  = [2.0, 1.5]
   
   sb1     = sell & (df["cnt_below"] >= 4)
   sb2    = sell & (df["big7_px"] * 1.05 < df["big7_wma"])
   
   state   = False
   states  = []
   for cnt in df["cnt_above"]:
       state = True if cnt >= 5 else False if cnt <= 2 else state
       states.append(state)
   bf1     = buy & pd.Series(states, index=df.index)
   bf2     = buy & (df["big7_px"] > df["big7_wma"]*1.05)
   bf2roll = bf2.rolling(2).sum() > 1
   buy_conds  = [bf2roll, bf1]
   sell_conds = [sb2, sb1]
   buy_timing = np.where(
            buy_zone,
            np.select(buy_conds, buy_zone_choices, default=0.0),
            np.select(buy_conds, not_buy_zone_choices, default=0.0)
   )
   normal_sell_timing = np.select(sell_conds, normal_sell_choices, default=0.0)
   crash_sell_timing  = np.select(sell_conds, crash_sell_choices,  default=0.0)
   normal_timing = normal_sell_timing + buy_timing
   crash_timing  = crash_sell_timing  + buy_timing
   df["score_timing"] = np.where(
            crash_zone,
            crash_timing,
            normal_timing
   )
   
   return df