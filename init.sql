-- 1
CREATE TABLE clients_data (
  id INT PRIMARY KEY,
  current_age INT,
  retirement_age INT,
  birth_year INT,
  birth_month INT,
  gender TEXT,
  address TEXT,
  latitude NUMERIC(8,5),
  longitude NUMERIC(8,5),
  per_capita_income MONEY,
  yearly_income MONEY,
  total_debt MONEY,
  credit_score INT,
  num_credit_cards INT
);
COPY clients_data FROM '/docker/data/users_data.csv' DELIMITER ',' CSV HEADER;

-- 2
CREATE TABLE cards_data (
  id INT PRIMARY KEY,
  client_id INT REFERENCES clients_data(id),
  card_brand TEXT,
  card_type TEXT,
  card_number TEXT,            
  expires VARCHAR(7),
  cvv TEXT,                    
  has_chip BOOLEAN,
  num_cards_issued INT,
  credit_limit MONEY,
  acct_open_date VARCHAR(7),
  year_pin_last_changed INT,
  card_on_dark_web BOOLEAN
);
COPY cards_data FROM '/docker/data/cards_data.csv' DELIMITER ',' CSV HEADER;

-- 3
CREATE TABLE transactions_data (
  id BIGINT PRIMARY KEY,
  transaction_date TIMESTAMP,
  client_id INT REFERENCES clients_data(id),
  card_id INT REFERENCES cards_data(id),
  amount MONEY,
  use_chip TEXT,
  merchant_id INT,
  merchant_city TEXT,
  merchant_state TEXT,
  zip TEXT,
  mcc INT,
  errors TEXT
);
COPY transactions_data FROM '/docker/data/transactions_data.csv' DELIMITER ',' CSV HEADER;
