import csv
import queue
import threading
from datetime import datetime
from pathlib import Path

import psycopg2 as pg
from psycopg2.extras import execute_batch


def db_writer_thread(conn, query, data_queue, table_name):
    """This thread runs constantly, taking batches from the queue and inserting them."""
    # We create a separate cursor for this thread for thread-safety
    cur = conn.cursor()
    total = 0

    while True:
        batch = data_queue.get()

        if batch is None:
            data_queue.task_done()
            break

        execute_batch(cur, query, batch)
        conn.commit()

        total += len(batch)
        print(f"[{table_name}] Committed {total}/13305915 rows")
        data_queue.task_done()

    cur.close()
    print(f"[{table_name}] Finished! Total committed: {total} rows.")


def clean_data():
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
        port="5431",
    )

    cur = conn.cursor()

    # Check and load clients_data
    cur.execute("SELECT COUNT(*) FROM clients_data;")
    result = cur.fetchone()
    if result is not None and result[0] == 0:
        with open("data/users_data.csv") as f:
            reader = csv.DictReader(f)
            cleaned_data = (clean_clients_data_row(row) for row in reader)
            execute_batch(
                cur,
                """
                INSERT INTO clients_data (
                    id, current_age, retirement_age, birth_year, birth_month, gender, address,
                    latitude, longitude, per_capita_income, yearly_income, total_debt,
                    credit_score, num_credit_cards
                ) VALUES (
                    %(id)s, %(current_age)s, %(retirement_age)s, %(birth_year)s, %(birth_month)s, %(gender)s, %(address)s,
                    %(latitude)s, %(longitude)s, %(per_capita_income)s, %(yearly_income)s, %(total_debt)s,
                    %(credit_score)s, %(num_credit_cards)s
                );
                """,
                cleaned_data,
                page_size=1000,
            )
    else:
        print("clients_data already has rows, skipping users_data.csv")

    # Check and load cards_data
    cur.execute("SELECT COUNT(*) FROM cards_data;")
    result = cur.fetchone()
    if result is not None and result[0] == 0:
        with open("data/cards_data.csv") as f:
            reader = csv.DictReader(f)
            cleaned_data = (clean_cards_data_row(row) for row in reader)
            execute_batch(
                cur,
                """
                INSERT INTO cards_data (
                    id, client_id, card_brand, card_type, card_number, expires, cvv, has_chip,
                    num_cards_issued, credit_limit, acct_open_date, year_pin_last_changed, card_on_dark_web
                ) VALUES (
                    %(id)s, %(client_id)s, %(card_brand)s, %(card_type)s, %(card_number)s, %(expires)s, %(cvv)s, %(has_chip)s,
                    %(num_cards_issued)s, %(credit_limit)s, %(acct_open_date)s, %(year_pin_last_changed)s, %(card_on_dark_web)s
                );
                """,
                cleaned_data,
                page_size=5000,
            )
    else:
        print("cards_data already has rows, skipping cards_data.csv")

    # Check and load transactions_data
    cur.execute("SELECT COUNT(*) FROM transactions_data;")
    result = cur.fetchone()
    if result is not None and result[0] == 0:
        print("Starting threaded insert for transactions_data...")

        query = """
            INSERT INTO transactions_data (
                id, transaction_date, client_id, card_id, amount, use_chip, merchant_id,
                merchant_city, merchant_state, zip, mcc, errors
            ) VALUES (
                %(id)s, %(transaction_date)s, %(client_id)s, %(card_id)s, %(amount)s, %(use_chip)s, %(merchant_id)s,
                %(merchant_city)s, %(merchant_state)s, %(zip)s, %(mcc)s, %(errors)s
            );
        """

        data_queue = queue.Queue(maxsize=5)
        writer = threading.Thread(
            target=db_writer_thread, args=(conn, query, data_queue, "Transactions")
        )
        writer.start()

        with open("data/transactions_data.csv") as f:
            reader = csv.DictReader(f)
            batch = []

            for row in reader:
                batch.append(clean_transactions_data_row(row))
                if len(batch) >= 10000:
                    data_queue.put(batch)
                    batch = []

            if batch:
                data_queue.put(batch)
        data_queue.put(None)
        writer.join()
    else:
        print("transactions_data already has rows, skipping transactions_data.csv")

    cur.close()
    conn.commit()
    conn.close()


def sql_bool(val):
    return bool(val)


def sql_float(val):
    if val is None or val == "" or str(val).lower() == "none":
        return None
    return float(val)


def sql_int(val):
    if val is None or val == "" or str(val).lower() == "none":
        return None
    return int(val)


def normalize_month_year(date_str):
    if not date_str or date_str.strip().lower() == "none":
        return None
    date_str = date_str.strip()
    for fmt in ("%m/%Y", "%Y-%m", "%m-%Y"):
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime("%Y-%m")
        except Exception:
            continue
    return None


def clean_clients_data_row(row):
    # print("Original clients_data row:", row)
    cleaned = {
        "id": sql_int(row["id"]),
        "current_age": sql_int(row["current_age"]),
        "retirement_age": sql_int(row["retirement_age"]),
        "birth_year": sql_int(row["birth_year"]),
        "birth_month": sql_int(row["birth_month"]),
        "gender": row["gender"].strip(),
        "address": row["address"].strip(),
        "latitude": sql_float(row["latitude"]),
        "longitude": sql_float(row["longitude"]),
        "per_capita_income": sql_float(
            row["per_capita_income"].replace("$", "").replace(",", "")
        ),
        "yearly_income": sql_float(
            row["yearly_income"].replace("$", "").replace(",", "")
        ),
        "total_debt": sql_float(row["total_debt"].replace("$", "").replace(",", "")),
        "credit_score": sql_int(row["credit_score"]),
        "num_credit_cards": sql_int(row["num_credit_cards"]),
    }
    # print("Cleaned clients_data entry:", cleaned)
    return cleaned


def clean_cards_data_row(row):
    # print("Original cards_data row:", row)
    cleaned = {
        "id": sql_int(row["id"]),
        "client_id": sql_int(row["client_id"]),
        "card_brand": row["card_brand"].strip(),
        "card_type": row["card_type"].strip(),
        "card_number": row["card_number"].strip(),
        "expires": normalize_month_year(row["expires"]),
        "cvv": row["cvv"].strip(),
        "has_chip": sql_bool(
            row["has_chip"].strip().lower() in ("true", "1", "t", "yes")
        ),
        "num_cards_issued": sql_int(row["num_cards_issued"]),
        "credit_limit": sql_float(
            row["credit_limit"].replace("$", "").replace(",", "")
        ),
        "acct_open_date": normalize_month_year(row["acct_open_date"]),
        "year_pin_last_changed": sql_int(row["year_pin_last_changed"]),
        "card_on_dark_web": sql_bool(
            row["card_on_dark_web"].strip().lower() in ("true", "1", "t", "yes")
        ),
    }
    # print("Cleaned cards_data entry:", cleaned)
    return cleaned


def clean_transactions_data_row(row):
    # print("Original transactions_data row:", row)
    # Parse timestamp
    try:
        transaction_date = datetime.strptime(row["date"].strip(), "%Y-%m-%d %H:%M:%S")
        transaction_date_sql = transaction_date.strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        print(f"Date parsing failed for {row.get('date')}: {e}")
        transaction_date_sql = None

    cleaned = {
        "id": sql_int(row["id"]),
        "transaction_date": transaction_date_sql,
        "client_id": sql_int(row["client_id"]),
        "card_id": sql_int(row["card_id"]),
        "amount": sql_float(row["amount"].replace("$", "").replace(",", "")),
        "use_chip": row["use_chip"].strip(),
        "merchant_id": sql_int(row["merchant_id"]),
        "merchant_city": row["merchant_city"].strip(),
        "merchant_state": row["merchant_state"].strip(),
        "zip": row["zip"].strip(),
        "mcc": sql_int(row["mcc"]),
        "errors": row["errors"].strip(),
    }
    # print("Cleaned transactions_data entry:", cleaned)
    return cleaned
