import json
import os
import sqlite3

def extract_data(data_folder='data'):
    """Extracts data from JSON files in the specified folder.

    Args:
        data_folder (str, optional): Path to the folder containing JSON files. Defaults to 'data'.

    Returns:
        list: A list of dictionaries, each representing a record extracted from the JSON files.
    """
    all_data = []
    for filename in os.listdir(data_folder):
        if filename.endswith('.json'):
            filepath = os.path.join(data_folder, filename)
            with open(filepath, 'r') as f:
                data = json.load(f)
                all_data.extend(data)
    return all_data

def transform_data(data):
    """Transforms the extracted data (example transformation).

    Args:
        data (list): A list of dictionaries representing the data.

    Returns:
        list: A list of tuples, where each tuple represents a transformed record.
    """
    transformed_data = []
    for item in data:
      # Example transformation: converting values to uppercase
        transformed_item = tuple(str(value).upper() if isinstance(value, str) else value for value in item.values())
        transformed_data.append(transformed_item)
    return transformed_data

def load_data(data, db_name='mydatabase.db', table_name='my_table'):
    """Loads the transformed data into an SQLite database.

    Args:
        data (list): A list of tuples representing the transformed data.
        db_name (str, optional): Name of the SQLite database file. Defaults to 'mydatabase.db'.
        table_name (str, optional): Name of the table to create and load data into. Defaults to 'my_table'.
    """
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Assuming all JSON files have the same structure, use the first item to create table
    if data:
        columns = list(extract_data()[0].keys())
        # Create table with appropriate data types (example: TEXT for all)
        create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join([f'{col} TEXT' for col in columns])})"
        cursor.execute(create_table_query)

        # Insert data
        placeholders = ', '.join(['?'] * len(columns))
        insert_query = f"INSERT INTO {table_name} VALUES ({placeholders})"
        cursor.executemany(insert_query, data)
        conn.commit()
    
    conn.close()

if __symbol__name__ == "__main__":
    extracted_data = extract_data()
    transformed_data = transform_data(extracted_data)
    load_data(transformed_data)
    print("ETL process completed successfully.")
