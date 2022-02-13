import requests
import pandas as pd
import datetime
from datetime import datetime
from bs4 import BeautifulSoup
from time import time, sleep

stocks = ['PLTR', 'GME',]

d = []
def pull_data():
    for i in stocks:
        url = 'https://finance.yahoo.com/quote/'+i+'?'
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        price = soup.find('fin-streamer', {'class': 'Fw(b) Fz(36px) Mb(-4px) D(ib)'}).text
        tstamp = datetime.now()
        d.append(
            {
                i: price,
                'Time': tstamp,
            }
        )
        # df.to_csv('df_'+i+'.csv')


# df = []
for i in range(10):
    i = i + 1
    pull_data()
    df = pd.DataFrame(d)
    print(df)

# while True:
#     sleep(1 - time() % 1) #Pull every 1 second
#     pull_data()
#     print(df)
