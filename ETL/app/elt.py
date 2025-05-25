import os
import json
import psycopg2
from datetime import datetime
from dateutil import parser as dtparser

DATA_DIR = "./data"
SQL_DIR = "./sql"

def pg_conn():
    return psycopg2.connect(
        dbname=os.environ.get("DB_NAME", "musicdb"),
        user=os.environ.get("DB_USER", "music"),
        password=os.environ.get("DB_PASS", "music"),
        host=os.environ.get("DB_HOST", "localhost"),
        port=os.environ.get("DB_PORT", "5432")
    )

def load_schema():
    conn = pg_conn()
    cur = conn.cursor()
    with open(os.path.join(SQL_DIR, "schema.sql")) as f:
        cur.execute(f.read())
    conn.commit()
    cur.close()
    conn.close()

def parse_mrmd_file(path):
    publisher = None
    songs = []
    artists = []
    curr_artist = None
    with open(path, encoding="utf-8") as f:
        for line in f:
            t = line[:2]
            if t == "P ":
                publisher = line[2:52].strip()
            elif t == "R ":
                title = line[2:52].strip()
                songs.append({'title': title, 'artist': curr_artist})
            elif t == "A ":
                curr_artist = line[2:52].strip()
                artists.append(curr_artist)
    return publisher, songs, artists

def insert_publisher(cur, name):
    cur.execute("INSERT INTO publishers (name) VALUES (%s) ON CONFLICT (name) DO NOTHING RETURNING id;", (name,))
    cur.execute("SELECT id FROM publishers WHERE name=%s;", (name,))
    return cur.fetchone()[0]

def insert_artist(cur, name):
    cur.execute("INSERT INTO artists (name) VALUES (%s) ON CONFLICT (name) DO NOTHING RETURNING id;", (name,))
    cur.execute("SELECT id FROM artists WHERE name=%s;", (name,))
    return cur.fetchone()[0]

def insert_song(cur, title, publisher_id, artist_id):
    cur.execute(
        "INSERT INTO songs (title, publisher_id, artist_id) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING RETURNING id;",
        (title, publisher_id, artist_id)
    )
    cur.execute(
        "SELECT id FROM songs WHERE title=%s AND publisher_id=%s AND artist_id=%s;",
        (title, publisher_id, artist_id)
    )
    return cur.fetchone()[0]

def insert_user(cur, user):
    cur.execute(
        "INSERT INTO users (user_id, country, signup_time) VALUES (%s, %s, %s) ON CONFLICT (user_id) DO NOTHING;",
        (user["user_id"], user["country"], user["signup_time"])
    )

def insert_event(cur, event):
    cur.execute(
        "INSERT INTO events (ued, user_id, song_id, event_time) VALUES (%s, %s, %s, %s) ON CONFLICT (ued) DO NOTHING;",
        (event["ued"], event["user_id"], event["song_id"], event["event_time"])
    )

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True, help="Date (YYYY-MM-DD) to process")
    args = parser.parse_args()
    process_date = args.date

    # Load schema
    load_schema()

    conn = pg_conn()
    cur = conn.cursor()

    # Load users
    users_file = os.path.join(DATA_DIR, "users", f"{process_date}.json")
    if os.path.exists(users_file):
        with open(users_file) as f:
            users = json.load(f)
            for user in users:
                insert_user(cur, user)
        print(f"Loaded users data for {process_date}")

    # Load songs and artists
    songs_file = os.path.join(DATA_DIR, "songs", f"{process_date}.mrmd")
    publisher_id = None
    song_map = {}
    if os.path.exists(songs_file):
        publisher, songs, artists = parse_mrmd_file(songs_file)
        if publisher:
            publisher_id = insert_publisher(cur, publisher)
        artist_ids = {}
        for a in artists:
            artist_ids[a] = insert_artist(cur, a)
        for song in songs:
            title = song["title"]
            artist_name = song["artist"]
            artist_id = artist_ids.get(artist_name)
            song_id = insert_song(cur, title, publisher_id, artist_id)
            song_map[title] = song_id
        print(f"Loaded songs data for {process_date}")

    # Load events
    events_file = os.path.join(DATA_DIR, "events", f"{process_date}.jsonl")
    if os.path.exists(events_file):
        with open(events_file) as f:
            for line in f:
                event = json.loads(line)
                # Assume event has: ued (uuid), event_time, user_id, song_title
                # Map song_title to song_id
                song_id = song_map.get(event["song_title"])
                if song_id:
                    event_data = {
                        "ued": event["ued"],
                        "user_id": event["user_id"],
                        "song_id": song_id,
                        "event_time": dtparser.parse(event["event_time"])
                    }
                    insert_event(cur, event_data)
        print(f"Loaded events data for {process_date}")

    conn.commit()
    cur.close()
    conn.close()
    print("ETL completed.")

if __name__ == "__main__":
    main()