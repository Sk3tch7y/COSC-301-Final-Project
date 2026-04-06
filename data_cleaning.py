import csv
import os
import tempfile
from datetime import datetime
from pathlib import Path

import psycopg2 as pg
from psycopg2.extras import execute_batch

DB_NAME = os.getenv("POSTGRES_DB", "financial_data")
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "other_pw")
DB_HOST = os.getenv("POSTGRES_HOST", "127.0.0.1")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")


def ensure_schema(conn):
    init_sql_path = Path(__file__).with_name("init.sql")
    with open(init_sql_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    with conn.cursor() as cur:
        cur.execute(schema_sql)
    conn.commit()


def copy_transactions_data(conn):
    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            newline="",
            encoding="utf-8",
            delete=False,
            suffix=".csv",
        ) as tmp:
            temp_path = tmp.name
            writer = csv.writer(tmp)

            with open("data/transactions_data.csv", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                count = 0

                for row in reader:
                    date_val = row["date"].strip()
                    transaction_date_sql = date_val if date_val else r"\N"

                    amount_val = row["amount"].replace("$", "").replace(",", "").strip()
                    amount_val = (
                        amount_val
                        if amount_val and amount_val.lower() != "none"
                        else r"\N"
                    )

                    id_val = row["id"].strip()
                    client_id_val = row["client_id"].strip()
                    card_id_val = row["card_id"].strip()
                    merchant_id_val = row["merchant_id"].strip()
                    mcc_val = row["mcc"].strip()

                    writer.writerow([
                        id_val if id_val and id_val.lower() != "none" else r"\N",
                        transaction_date_sql,
                        client_id_val if client_id_val and client_id_val.lower() != "none" else r"\N",
                        card_id_val if card_id_val and card_id_val.lower() != "none" else r"\N",
                        amount_val,
                        row["use_chip"].strip() if row["use_chip"].strip() else r"\N",
                        merchant_id_val if merchant_id_val and merchant_id_val.lower() != "none" else r"\N",
                        row["merchant_city"].strip() if row["merchant_city"].strip() else r"\N",
                        row["merchant_state"].strip() if row["merchant_state"].strip() else r"\N",
                        row["zip"].strip() if row["zip"].strip() else r"\N",
                        mcc_val if mcc_val and mcc_val.lower() != "none" else r"\N",
                        row["errors"].strip() if row["errors"].strip() else r"\N",
                    ])

                    count += 1
                    if count % 500000 == 0:
                        print(f"[Transactions] Prepared {count}/13305915 rows for COPY")

        with conn.cursor() as cur, open(temp_path, "r", encoding="utf-8") as tmp_read:
            copy_sql = """
                COPY transactions_data (
                    id, transaction_date, client_id, card_id, amount, use_chip,
                    merchant_id, merchant_city, merchant_state, zip, mcc, errors
                )
                FROM STDIN WITH (
                    FORMAT csv,
                    NULL '\\N'
                )
            """
            cur.copy_expert(copy_sql, tmp_read)

        conn.commit()
        print("[Transactions] COPY complete.")

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


def clean_data():
    if not (
        Path("data/cards_data.csv").is_file()
        and Path("data/transactions_data.csv").is_file()
        and Path("data/users_data.csv").is_file()
    ):
        print("Data Missing")
        return

    conn = pg.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
    )

    ensure_schema(conn)

    cur = conn.cursor()

    # Check and load clients_data
    cur.execute("SELECT COUNT(*) FROM clients_data;")
    result = cur.fetchone()
    if result is not None and result[0] == 0:
        with open("data/users_data.csv", newline="", encoding="utf-8") as f:
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
                page_size=5000,
            )
        conn.commit()
        print("clients_data load complete.")
    else:
        print("clients_data already has rows, skipping users_data.csv")

    # Check and load cards_data
    cur.execute("SELECT COUNT(*) FROM cards_data;")
    result = cur.fetchone()
    if result is not None and result[0] == 0:
        with open("data/cards_data.csv", newline="", encoding="utf-8") as f:
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
                page_size=10000,
            )
        conn.commit()
        print("cards_data load complete.")
    else:
        print("cards_data already has rows, skipping cards_data.csv")

    # Check and load transactions_data
    cur.execute("SELECT COUNT(*) FROM transactions_data;")
    result = cur.fetchone()
    if result is not None and result[0] == 0:
        print("Starting COPY load for transactions_data...")
        copy_transactions_data(conn)
    else:
        print("transactions_data already has rows, skipping transactions_data.csv")

    cur.close()
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
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            continue
    return None


def clean_clients_data_row(row):
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
    return cleaned


def clean_cards_data_row(row):
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
    return cleaned
