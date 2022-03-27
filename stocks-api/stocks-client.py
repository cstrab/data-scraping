import requests
from datetime import datetime

def get_data(start,end):
    url = 'http://127.0.0.1:8000/stocks'
    parameters = {'start': start,
                  'end': end,
        }
    json = requests.get(url,params = parameters).json()
    # data = pd.read_json(json,orient='table')
    # return data
    return json

data = get_data(datetime(2022,1,1), datetime(2022,5,1))
print(data)