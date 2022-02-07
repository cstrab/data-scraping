import psycopg2
from pandas_datareader import data as pdr
import pandas as pd

import config as cfg


class SymbolScraper:

    connection = None
    cursor = None
    debug: bool

    def __init__(
        self,
        debug = False,
        database_host = "",
        database_port = 5432,
        database_name = "",
        database_user = "",
        database_password = "",
    ):

        if database_host:
            self.connection = psycopg2.connect(
                database=database_name,
                user=database_user,
                password=database_password,
                host=database_host,
                port=database_port
            )
            self.cursor = self.connection.cursor()
            print(f"Connected to {database_name} as {database_user}.")
        else:
            print("No database config provided. Results will not be saved.")

        self.debug = debug


    def save_symbols(self, symbols: pd.DataFrame):
        if self.debug:
            print("Saving symbols...")

        if not self.connection:
            return
            
        try:
            # TODO: Change this so that only new records are inserted
            # and old records are maintained and/or updated
            # Truncate existing table
            sql = "TRUNCATE TABLE symbols"
            self.cursor.execute(sql)

            data = ()
            for symbol, row in symbols.iterrows():
                data += ((
                    symbol,
                    row["Security Name"],
                    row["Market Category"],
                    row["Financial Status"],
                    row["Listing Exchange"],
                ),)

            # Insert updated records?
            sql = """INSERT INTO symbols (symbol, name, market_category, financial_status, listing_exchange) 
            VALUES (%s, %s, %s, %s, %s);"""
            self.cursor.executemany(sql, data)
            self.connection.commit()
        except Exception as exp:
            self.connection.rollback()
            print(f"Error saving symbols: {exp}")


    def update_symbols(self):
        print("Update symbols...")
        symbols = pdr.get_nasdaq_symbols()
        self.save_symbols(symbols)


def main():
    symbol_scraper = SymbolScraper(
        debug = cfg.DEBUG,
        database_host = cfg.DATABASE_HOST,
        database_port = cfg.DATABASE_PORT,
        database_name = cfg.DATABASE_NAME,
        database_user = cfg.DATABASE_USER,
        database_password = cfg.DATABASE_PASSWORD
    )
    symbol_scraper.update_symbols()


if __name__ == "__main__":
    main()
