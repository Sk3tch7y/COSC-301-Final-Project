import os

import pandas as pd
from sqlalchemy import create_engine

DB_NAME = os.getenv("POSTGRES_DB", "financial_data")
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "other_pw")
DB_HOST = os.getenv("POSTGRES_HOST", "127.0.0.1")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")



def fetch_df(engine, query, params=None):
    return pd.read_sql_query(query, engine, params=params)


def run_eda():
    db_uri = (
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    engine = create_engine(db_uri)

    transactions_missing = fetch_df(
        engine,
        """
        SELECT
            COUNT(*) AS total,
            SUM(CASE WHEN transaction_date IS NULL THEN 1 ELSE 0 END) AS transaction_date_missing,
            SUM(CASE WHEN amount IS NULL THEN 1 ELSE 0 END) AS amount_missing,
            SUM(CASE WHEN use_chip IS NULL OR use_chip = '' THEN 1 ELSE 0 END) AS use_chip_missing,
            SUM(CASE WHEN merchant_id IS NULL THEN 1 ELSE 0 END) AS merchant_id_missing,
            SUM(CASE WHEN merchant_state IS NULL OR merchant_state = '' THEN 1 ELSE 0 END) AS merchant_state_missing,
            SUM(CASE WHEN mcc IS NULL THEN 1 ELSE 0 END) AS mcc_missing
        FROM transactions_data;
        """,
    )
    print("Transactions missingness")
    print(transactions_missing.to_string(index=False))

    clients_missing = fetch_df(
        engine,
        """
        SELECT
            COUNT(*) AS total,
            SUM(CASE WHEN current_age IS NULL THEN 1 ELSE 0 END) AS current_age_missing,
            SUM(CASE WHEN gender IS NULL OR gender = '' THEN 1 ELSE 0 END) AS gender_missing,
            SUM(CASE WHEN credit_score IS NULL THEN 1 ELSE 0 END) AS credit_score_missing,
            SUM(CASE WHEN yearly_income IS NULL THEN 1 ELSE 0 END) AS yearly_income_missing,
            SUM(CASE WHEN total_debt IS NULL THEN 1 ELSE 0 END) AS total_debt_missing
        FROM clients_data;
        """,
    )
    print("\nClients missingness")
    print(clients_missing.to_string(index=False))

    cards_missing = fetch_df(
        engine,
        """
        SELECT
            COUNT(*) AS total,
            SUM(CASE WHEN credit_limit IS NULL THEN 1 ELSE 0 END) AS credit_limit_missing,
            SUM(CASE WHEN card_type IS NULL OR card_type = '' THEN 1 ELSE 0 END) AS card_type_missing,
            SUM(CASE WHEN card_brand IS NULL OR card_brand = '' THEN 1 ELSE 0 END) AS card_brand_missing,
            SUM(CASE WHEN has_chip IS NULL THEN 1 ELSE 0 END) AS has_chip_missing
        FROM cards_data;
        """,
    )
    print("\nCards missingness")
    print(cards_missing.to_string(index=False))

    duplicates = fetch_df(
        engine,
        """
        SELECT
            'clients_data' AS table_name,
            COUNT(*) - COUNT(DISTINCT id) AS duplicate_ids
        FROM clients_data
        UNION ALL
        SELECT
            'cards_data' AS table_name,
            COUNT(*) - COUNT(DISTINCT id) AS duplicate_ids
        FROM cards_data
        UNION ALL
        SELECT
            'transactions_data' AS table_name,
            COUNT(*) - COUNT(DISTINCT id) AS duplicate_ids
        FROM transactions_data;
        """,
    )
    print("\nDuplicate ids")
    print(duplicates.to_string(index=False))

    transactions_stats = fetch_df(
        engine,
        """
        SELECT
            COUNT(*) AS total,
            MIN(amount) AS min_amount,
            PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY amount) AS p25_amount,
            PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY amount) AS median_amount,
            PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY amount) AS p75_amount,
            MAX(amount) AS max_amount,
            AVG(amount) AS avg_amount,
            STDDEV(amount) AS stddev_amount
        FROM transactions_data
        WHERE amount IS NOT NULL;
        """,
    )
    print("\nTransaction amount summary stats")
    print(transactions_stats.to_string(index=False))

    monthly = fetch_df(
        engine,
        """
        SELECT
            DATE_TRUNC('month', transaction_date) AS month,
            COUNT(*) AS transaction_count,
            SUM(amount) AS total_amount
        FROM transactions_data
        WHERE transaction_date IS NOT NULL
        GROUP BY 1
        ORDER BY 1;
        """,
    )
    print("\nMonthly transaction volume")
    print(monthly.to_string(index=False))

    use_chip = fetch_df(
        engine,
        """
        SELECT
            COALESCE(NULLIF(use_chip, ''), 'Unknown') AS use_chip,
            COUNT(*) AS transaction_count,
            AVG(amount) AS avg_amount
        FROM transactions_data
        GROUP BY 1
        ORDER BY transaction_count DESC;
        """,
    )
    print("\nTransactions by method")
    print(use_chip.to_string(index=False))

    age_groups = fetch_df(
        engine,
        """
        SELECT
            CASE
                WHEN c.current_age < 25 THEN '18-24'
                WHEN c.current_age BETWEEN 25 AND 34 THEN '25-34'
                WHEN c.current_age BETWEEN 35 AND 44 THEN '35-44'
                WHEN c.current_age BETWEEN 45 AND 54 THEN '45-54'
                WHEN c.current_age BETWEEN 55 AND 64 THEN '55-64'
                ELSE '65+'
            END AS age_group,
            COUNT(*) AS transaction_count,
            AVG(t.amount) AS avg_amount,
            SUM(t.amount) AS total_amount
        FROM transactions_data t
        JOIN clients_data c ON t.client_id = c.id
        WHERE t.amount IS NOT NULL AND c.current_age IS NOT NULL
        GROUP BY 1
        ORDER BY 1;
        """,
    )
    print("\nAverage transaction amounts by age group")
    print(age_groups.to_string(index=False))

    credit_corr = fetch_df(
        engine,
        """
        SELECT
            corr(t.amount, c.credit_limit) AS corr_amount_credit_limit
        FROM transactions_data t
        JOIN cards_data c ON t.card_id = c.id
        WHERE t.amount IS NOT NULL AND c.credit_limit IS NOT NULL;
        """,
    )
    print("\nCorrelation: amount vs credit limit")
    print(credit_corr.to_string(index=False))

    engine.dispose()
