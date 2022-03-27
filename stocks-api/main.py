from fastapi import FastAPI, Query, Body
from datetime import datetime
from lib import stock_connect

description = 'Stock API allows the user to download data directly from the Stocks SQL database'

app = FastAPI(
    title = 'Stock API',
    version = '1.0',
    description = description
)

@app.get('/stocks')
async def stocks_df(
                    start: datetime,
                    end: datetime):

    df = stock_connect.get_stock_data(start,end)

    if type(df) != str:
        json = df.to_json(date_format='iso', orient='table')
        return json
    else:
        return df

if __name__ == '__main__':
    app.run()
