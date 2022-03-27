import pyodbc
import pandas as pd

def sql_connect():
    conn_str = (
        'DRIVER={Devart ODBC Driver for PostgreSQL};'
        'Server=192.168.1.217;'
        'Port=5432;'
        'Database=stocks_db;'
        'User ID=user_1;'
        'Password=test123;'
        'String Types=Unicode'

        # "DRIVER={PostgreSQL Unicode};"
        # "DATABASE=stocks_db;"
        # "UID=user_1;"
        # "PWD=test123;"
        # "SERVER=192.168.1.217;"
        # "PORT=5432;"
    )
    return pyodbc.connect(conn_str)

def get_stock_data(
        start=None,
        end=None,
        ):

    query_stock_data = f'''
    SELECT
    average
    
    FROM "PLTR"
    LIMIT 10
    '''

    df_stocks = pd.read_sql_query(query_stock_data, sql_connect())
    return df_stocks
