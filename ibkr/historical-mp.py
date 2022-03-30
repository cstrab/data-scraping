from ib_insync import *
from sqlalchemy import create_engine
from datetime import datetime, timedelta

def main():
    ib = IB()
    ib.connect('127.0.0.1', 7496, clientId=1)

    stocktik = 'PLTR'
    stockipo = datetime(2020, 9, 30)
    pullfreq = 30
    pullfreqstr = str(pullfreq) + " D"
    start = datetime.now()
    # start = datetime(2020, 10, 17)

    while start >= stockipo:
        stock = Stock(stocktik, 'SMART', 'USD')

        bars = ib.reqHistoricalData(
            stock,
            endDateTime=start,
            durationStr=pullfreqstr,
            barSizeSetting='1 min',
            whatToShow='MIDPOINT',
            useRTH=True
        )

        df = util.df(bars)
        print(df)
        # engine = create_engine('postgresql://user_1:test123@192.168.1.217:5432/stocks_db')
        # df.to_sql(stocktik, engine, if_exists='append')
        start = start - timedelta(days=pullfreq)

if __name__ == '__main__':
    main()
