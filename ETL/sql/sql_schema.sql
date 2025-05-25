CREATE TABLE IF NOT EXISTS users (
    user_id VARCHAR PRIMARY KEY,
    country VARCHAR,
    signup_time TIMESTAMP
);

CREATE TABLE IF NOT EXISTS publishers (
    id SERIAL PRIMARY KEY,
    name VARCHAR UNIQUE
);

CREATE TABLE IF NOT EXISTS artists (
    id SERIAL PRIMARY KEY,
    name VARCHAR UNIQUE
);

CREATE TABLE IF NOT EXISTS songs (
    id SERIAL PRIMARY KEY,
    title VARCHAR,
    publisher_id INTEGER REFERENCES publishers(id),
    artist_id INTEGER REFERENCES artists(id)
);

CREATE TABLE IF NOT EXISTS events (
    ued UUID PRIMARY KEY,
    user_id VARCHAR REFERENCES users(user_id),
    song_id INTEGER REFERENCES songs(id),
    event_time TIMESTAMP
);