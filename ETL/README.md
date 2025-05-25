# Extract, Transform, Load (ETL)

An ETL or (ELT) Python script that processes your data, loads it into PostgreSQL (running in Docker Compose), and includes SQL scripts to answer your business questions.

Create project structure folders:

    project_folder/
    ├── data/
    │   └── ... (data files)
    ├── app/
    │   ├── main.py
    │   └── requirements.txt
    ├── sql/
    │   └── queries.sql
    ├── docker-compose.yml
    └── .env

Create requirements.txt file.

    psycopg2-binary
    python-dotenv


## Python scripts

Here is a Python script for execution within a Docker container, which extracts data from local JSON files, transforms it, and loads it into an SQL database.

import json
import psycopg2
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def process_date(date_str):
    """Processes data for a given date."""
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        raise ValueError("Incorrect date format, should be YYYY-MM-DD")

    # Placeholder for data loading and transformation logic
    # This part should read the data files, parse them, and prepare for database insertion
    print(f"Processing data for {date_obj}")
    return date_obj  # Return the date object for later use

def load_data_to_db(date_obj):
    """Loads processed data into PostgreSQL."""
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )
        cur = conn.cursor()

        # Create tables if they don't exist
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id VARCHAR(24) PRIMARY KEY,
                signup_date DATE,
                country VARCHAR(50)
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS songs (
                song_id SERIAL PRIMARY KEY,
                title VARCHAR(255),
                artist VARCHAR(255),
                publisher VARCHAR(255)
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS streams (
                stream_id SERIAL PRIMARY KEY,
                user_id VARCHAR(24) REFERENCES users(user_id),
                song_id INTEGER REFERENCES songs(song_id),
                event_time TIMESTAMP
            );
        """)

        # Placeholder for inserting data
        # Example:
        # cur.execute("INSERT INTO users (user_id, signup_date, country) VALUES (%s, %s, %s) ON CONFLICT (user_id) DO NOTHING;", ('user1', date_obj, 'USA'))
        # cur.execute("INSERT INTO songs (title, artist, publisher) VALUES (%s, %s, %s) ON CONFLICT (title) DO NOTHING;", ('Song1', 'Artist1', 'Global Artists Songs United Company'))
        # cur.execute("INSERT INTO streams (user_id, song_id, event_time) VALUES (%s, %s, %s);", ('user1', 1, datetime.now()))

        conn.commit()
        cur.close()
        conn.close()
        print("Data loaded into PostgreSQL.")

    except psycopg2.Error as e:
        print(f"Database error: {e}")

def execute_sql_queries():
    """Executes SQL queries and prints the results."""
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )
        cur = conn.cursor()

        # Time gaps in song streams
        cur.execute("""
            SELECT 
                s1.user_id,
                MIN(EXTRACT(EPOCH FROM (s1.event_time - s2.event_time))) AS shortest_interval,
                MAX(EXTRACT(EPOCH FROM (s1.event_time - s2.event_time))) AS longest_interval
            FROM streams s1
            JOIN streams s2 ON s1.user_id = s2.user_id AND s1.stream_id != s2.stream_id
            JOIN users u ON s1.user_id = u.user_id
            JOIN songs sg ON s1.song_id = sg.song_id
            WHERE u.signup_date >= '2024-03-01' AND sg.publisher = 'Global Artists Songs United Company'
            GROUP BY s1.user_id;
        """)
        print("Time Gaps in Song Streams:")
        for row in cur.fetchall():
            print(row)

        # Top hits in a country
        cur.execute("""
            SELECT sg.artist, COUNT(*) AS stream_count
            FROM streams s
            JOIN users u ON s.user_id = u.user_id
            JOIN songs sg ON s.song_id = sg.song_id
            WHERE u.country = 'USA'  -- Replace 'USA' with the desired country
            GROUP BY sg.artist
            ORDER BY stream_count DESC
            LIMIT 5;
        """)
        print("\nTop Hits in a Country:")
        for row in cur.fetchall():
            print(row)

        cur.close()
        conn.close()

    except psycopg2.Error as e:
        print(f"Database error: {e}")

if __name__ == "__main__":
    date_input = input("Enter the date to process (YYYY-MM-DD): ")
    try:
        processed_date = process_date(date_input)
        load_data_to_db(processed_date)
        execute_sql_queries()
    except ValueError as e:
        print(e)

## SQL queries

Python scripts to run SQL queries for the described analytics.

## Dockerfile, Docker and environment variables

Instructions to run and test the solution with Python, Dockerfile and Docker

Set up Docker and Docker Compose:

Install Docker and Docker Compose on your machine.

Create Dockerfile

    FROM python:3.9
    WORKDIR /app
    COPY app/requirements.txt .
    RUN pip install --no-cache-dir -r requirements.txt
    COPY app .
    CMD ["python", "main.py"]


Create docker-compose.yml file.

    version: '3.8'
    services:
      db:
        image: postgres:13
        environment:
          POSTGRES_USER: ${DB_USER}
          POSTGRES_PASSWORD: ${DB_PASSWORD}
          POSTGRES_DB: ${DB_NAME}
        ports:
          - "5432:5432"
        volumes:
          - db_data:/var/lib/postgresql/data
      app:
        build: ./app
        depends_on:
          - db
        environment:
          DB_USER: ${DB_USER}
          DB_PASSWORD: ${DB_PASSWORD}
          DB_NAME: ${DB_NAME}
          DB_HOST: db
          DB_PORT: 5432
        volumes:
          - ./app:/app
    volumes:
      db_data:

Create .env file.

    DB_USER=your_db_user
    DB_PASSWORD=your_db_password
    DB_NAME=your_db_name
    DB_HOST=db 
    DB_PORT=5432

Run the application:

Open a terminal shell in the project directory and run the command:

	docker-compose up --build

The script will prompt for the date, process data, load it to the database, and execute the queries.

Test the solution:

You can test the solution by inspecting the database using a PostgreSQL client or by running the script multiple times with different dates and data.


### Run the application without Docker:

Install requirements

	pip install -r requirements.txt

Set environment variables.

 	export DB_USER=your_db_user
    export DB_PASSWORD=your_db_password
    export DB_NAME=your_db_name
    export DB_HOST=localhost
    export DB_PORT=5432

Run the application.

    python app/main.py
