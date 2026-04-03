from datetime import datetime
from pathlib import Path

import psycopg2 as pg
from psycopg2.extras import execute_batch


# Not currently used, no filtering is needed ATM;
def filter_data():
    if not (
        Path("data/cards_data.csv").is_file()
        and Path("data/transactions_data.csv").is_file()
        and Path("data/users_data.csv").is_file()
    ):
        print("Data Missing")
        return

    # setup database connection:

    conn = pg.connect(
        dbname="financial_data",
        user="postgres",
        password="other_pw",
        host="localhost",
        port="5432",
    )

    cur = conn.cursor()

    # remove all transactions from 2019 because it was an incomplete year of transactions
    cur.execute("""
    DELETE FROM transactions_data 
    WHERE transaction_date >= '2019-01-01 00:00:00';
    """)

    conn.commit()
    cur.close()
    conn.close()
