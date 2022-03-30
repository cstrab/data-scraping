import sqlalchemy as db
import pandas as pd
import psycopg2 as pg
import pandas.io.sql as psql

engine = db.create_engine('postgresql://user_1:test123@192.168.1.217:5432/stocks_db')

def get_stock_data(
        start=None,
        end=None,
):
    parameters = {'start': start,
                    'end': end, }
    df_stocks = psql.read_sql('''
    SELECT * FROM "PLTR"
    WHERE date BETWEEN %(start)s AND %(end)s
    ORDER BY date
    ''',
    con=engine,
    params=parameters)

    return df_stocks
