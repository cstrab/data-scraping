import requests
import pandas as pd
from datetime import datetime

def request_data(start, end):
    url = 'http://127.0.0.1:8000/stocks'
    parameters = {'start': start,
                  'end': end,}
    json = requests.get(url,params = parameters).json()
    df = pd.read_json(json,orient='records')
    return df

data = request_data(datetime(2022,1,1), datetime(2022,2,1))
print(data)