
-- 1
CREATE TABLE IF NOT EXISTS clients_data (
  id INT PRIMARY KEY,
  current_age INT,
  retirement_age INT,
  birth_year INT,
  birth_month INT,
  gender TEXT,
  address TEXT,
  latitude NUMERIC(8,5),
  longitude NUMERIC(8,5),
  per_capita_income FLOAT,
  yearly_income FLOAT,
  total_debt FLOAT,
  credit_score INT,
  num_credit_cards INT
);

-- 2
CREATE TABLE IF NOT EXISTS cards_data (
  id INT PRIMARY KEY,
  client_id INT REFERENCES clients_data(id),
  card_brand TEXT,
  card_type TEXT,
  card_number TEXT,            
  expires TIMESTAMP,
  cvv TEXT,                    
  has_chip BOOLEAN,
  num_cards_issued INT,
  credit_limit FLOAT,
  acct_open_date TIMESTAMP,
  year_pin_last_changed INT,
  card_on_dark_web BOOLEAN
);


-- 3
CREATE TABLE IF NOT EXISTS transactions_data (
  id BIGINT PRIMARY KEY,
  transaction_date TIMESTAMP,
  client_id INT REFERENCES clients_data(id),
  card_id INT REFERENCES cards_data(id),
  amount FLOAT,
  use_chip TEXT,
  merchant_id INT,
  merchant_city TEXT,
  merchant_state TEXT,
  zip TEXT,
  mcc INT,
  errors TEXT
);
