import os
import psycopg2

def pg_conn():
    return psycopg2.connect(
        dbname=os.environ.get("DB_NAME", "musicdb"),
        user=os.environ.get("DB_USER", "music"),
        password=os.environ.get("DB_PASS", "music"),
        host=os.environ.get("DB_HOST", "localhost"),
        port=os.environ.get("DB_PORT", "5432")
    )

def main():
    conn = pg_conn()
    cur = conn.cursor()
    with open("sql/time_gaps.sql") as f:
        cur.execute(f.read())
        rows = cur.fetchall()
        print("User ID | Shortest Gap (s) | Longest Gap (s)")
        for row in rows:
            print(f"{row[0]} | {row[1]:.2f} | {row[2]:.2f}")
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()