# $ psql <USER> -h 127.0.0.1 -d <DATABASE>

CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  username VARCHAR(128) UNIQUE NOT NULL,
  password TEXT NOT NULL,
  cookie TEXT,
  -- access_token TEXT,
  -- refresh_token TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP
);

CREATE TABLE BillHead (
  id SERIAL PRIMARY KEY,
  bill_no TEXT,
  company_id TEXT,
  ship_id TEXT,
  sp_no TEXT,
  total_amount TEXT,
  bill_date TEXT
);
