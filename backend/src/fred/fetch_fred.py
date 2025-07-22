import requests
from dotenv import load_dotenv
import pandas as pd
import os
load_dotenv()
FRED_API_KEY = os.getenv("FRED_API_KEY")
DATA_FROM_DATE = os.getenv("DATA_FROM_DATE")
def fetch_monthly_fred_series(series_id):
    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {
        'series_id': series_id,
        'api_key': FRED_API_KEY,
        'file_type': 'json',
        'sort_order': 'desc',
        'observation_start': DATA_FROM_DATE,
        'frequency': 'm'
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data['observations'])
        df = df[df['value'] != '.']
        df['value'] = pd.to_numeric(df['value'])
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        df = df[['date', 'value']].reset_index(drop=True)

        friday_index = pd.date_range(start=df['date'].min(), end=pd.Timestamp.today(), freq='W-FRI')
        weekly_df = pd.DataFrame({'date': friday_index})
        weekly_df = pd.merge_asof(weekly_df, df, on='date', direction='backward')

        return weekly_df
    else:
        raise Exception(f"FRED API error {response.status_code}: {response.text}")
     
def fetch_weekly_fred_series(series_id):
    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {
        'series_id': series_id,
        'api_key': FRED_API_KEY,
        'file_type': 'json',
        'sort_order': 'desc',
        'observation_start': DATA_FROM_DATE,
        'frequency': 'wef'
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data['observations'])
        df = df[df['value'] != '.']
        df['value'] = pd.to_numeric(df['value'])
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        df = df[['date', 'value']].reset_index(drop=True)
        return df
    else:
        raise Exception(f"FRED API error {response.status_code}: {response.text}")     
    
def fetch_weekly_fred_series_friday(series_id):
    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {
        'series_id': series_id,
        'api_key': FRED_API_KEY,
        'file_type': 'json',
        'sort_order': 'desc',
        'observation_start': DATA_FROM_DATE,
        'frequency': 'w'
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data['observations'])
        df = df[df['value'] != '.']
        df['value'] = pd.to_numeric(df['value'])
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        df = df[['date', 'value']].reset_index(drop=True)
        df = df.set_index('date')

        friday_index = pd.date_range(start=df.index.min(), end=df.index.max(), freq='W-FRI')
        df_friday = df.reindex(friday_index, method='ffill')
        df_friday.index.name = 'date'
        df_friday = df_friday.reset_index()

        return df_friday
    else:
        raise Exception(f"FRED API error {response.status_code}: {response.text}")

def fetch_quarterly_fred_series_weekly(series_id):
    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {
        'series_id': series_id,
        'api_key': FRED_API_KEY,
        'file_type': 'json',
        'sort_order': 'desc',
        'observation_start': DATA_FROM_DATE,
        'frequency': 'q'
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data['observations'])
        df = df[df['value'] != '.']
        df['value'] = pd.to_numeric(df['value'])
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        df = df[['date', 'value']].reset_index(drop=True)
        df = df.set_index('date')

        friday_index = pd.date_range(start=df.index.min(), end=pd.Timestamp.today(), freq='W-FRI')
    
        df_weekly = df.reindex(friday_index, method='ffill')
        df_weekly.index.name = 'date'
        df_weekly = df_weekly.reset_index()

        return df_weekly
    else:
        raise Exception(f"FRED API error {response.status_code}: {response.text}")
