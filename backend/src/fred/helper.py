import numpy as np
import pandas as pd
def weighted_ma(series, n=50):
    w = np.arange(1, n+1)
    return series.rolling(n).apply(lambda x: np.dot(x, w)/w.sum(), raw=True)
 
def weighted_junk_ma(series, n=30):
    w = np.arange(1, n+1)
    return series.rolling(n).apply(lambda x: np.dot(x, w)/w.sum(), raw=True)
 
def to_series(df):
    if isinstance(df, pd.DataFrame):
        s = df.set_index("date")["value"]
        s.index = pd.to_datetime(s.index)
        # Ensure the values are numeric
        s = pd.to_numeric(s, errors='coerce')
        return s.sort_index()
    return df

