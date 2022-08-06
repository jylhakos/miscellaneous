# $ psql <USER> -h 127.0.0.1 -d <DATABASE>

CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  username VARCHAR(128) UNIQUE NOT NULL,
  password TEXT NOT NULL,
  token TEXT,
  -- access_token TEXT,
  -- refresh_token TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP
);