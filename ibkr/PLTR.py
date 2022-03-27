from ib_insync import *
from sqlalchemy import create_engine
from datetime import datetime, timedelta

def main():
    ib = IB()
    ib.connect('127.0.0.1', 7496, clientId=1)

    stocktik = 'PLTR'
    pulltype = ['TRADES',
                'MIDPOINT',
                'BID',
                'ASK',
                'BID_ASK',
                'HISTORICAL_VOLATILITY',
                'OPTION_IMPLIED_VOLATILITY',
                ]
    pullfreq = 1
    pullfreqstr = str(pullfreq) + " D"
    start = datetime.now()

    stock = Stock(stocktik, 'SMART', 'USD')

    for type in pulltype:
        bars = ib.reqHistoricalData(
            stock,
            endDateTime=start,
            durationStr=pullfreqstr,
            barSizeSetting='1 min',
            whatToShow=type,
            useRTH=True
        )
        df = util.df(bars)
        engine = create_engine('postgresql://user_1:test123@192.168.1.217:5432/stocks_db')
        df.to_sql('TEST_'+str(type), engine, if_exists='replace')
        print(type)
        # ib.sleep(10)

if __name__ == '__main__':
    main()