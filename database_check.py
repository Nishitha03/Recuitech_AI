import sqlite3
import pandas as pd

# 1. Connect to the database
# Replace 'your_database.db' with your actual database file path
conn = sqlite3.connect('recruitment.db')
cursor = conn.cursor()

# 2. Explore the database structure

# Get list of all tables
def list_tables():
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables in the database:")
    for table in tables:
        print(f"- {table[0]}")
    return [table[0] for table in tables]

# Get table schema (column names and types)
def get_table_schema(table_name):
    cursor.execute(f"PRAGMA table_info({table_name});")
    schema = cursor.fetchall()
    print(f"\nSchema for table '{table_name}':")
    for column in schema:
        print(f"- {column[1]} ({column[2]})")

# Preview table data
def preview_table(table_name, limit=5):
    cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit};")
    rows = cursor.fetchall()
    
    # Get column names
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = [column[1] for column in cursor.fetchall()]
    
    print(f"\nPreview of '{table_name}' (first {limit} rows):")
    # Create a DataFrame for nicer display
    df = pd.DataFrame(rows, columns=columns)
    print(df)
    return df

# 3. Example database operations

# Basic SELECT query
def run_query(query):
    cursor.execute(query)
    results = cursor.fetchall()
    
    # Try to get column names if it's a SELECT query
    if query.strip().upper().startswith('SELECT'):
        column_names = [description[0] for description in cursor.description]
        df = pd.DataFrame(results, columns=column_names)
        return df
    return results

# INSERT data
def insert_data(table_name, data_dict):
    columns = ', '.join(data_dict.keys())
    placeholders = ', '.join(['?'] * len(data_dict))
    values = tuple(data_dict.values())
    
    query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
    cursor.execute(query, values)
    conn.commit()
    print(f"Inserted data into {table_name}")

# UPDATE data
def update_data(table_name, data_dict, condition):
    set_clause = ', '.join([f"{column} = ?" for column in data_dict.keys()])
    values = tuple(data_dict.values())
    
    query = f"UPDATE {table_name} SET {set_clause} WHERE {condition}"
    cursor.execute(query, values)
    conn.commit()
    print(f"Updated {cursor.rowcount} rows in {table_name}")

# DELETE data
def delete_data(table_name, condition):
    query = f"DELETE FROM {table_name} WHERE {condition}"
    cursor.execute(query)
    conn.commit()
    print(f"Deleted {cursor.rowcount} rows from {table_name}")

# Create a new table
def create_table(table_name, columns_with_types):
    columns_definition = ', '.join(columns_with_types)
    query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_definition})"
    cursor.execute(query)
    conn.commit()
    print(f"Created table '{table_name}'")

# 4. Example usage

# List all tables in the database
tables = list_tables()

# If there are tables, explore the first one
if tables:
    first_table = tables[0]
    
    # Get schema of the first table
    get_table_schema(first_table)
    
    # Preview data in the first table
    preview_df = preview_table(first_table)
    
    # Run a custom query
    custom_query = f"SELECT * FROM {first_table} WHERE rowid < 10"
    result_df = run_query(custom_query)
    print("\nCustom query result:")
    print(result_df)
    
    # Example of inserting data (uncomment to use)
    # new_data = {'column1': 'value1', 'column2': 'value2'}
    # insert_data(first_table, new_data)
    
    # Example of updating data (uncomment to use)
    # update_values = {'column1': 'updated_value'}
    # update_data(first_table, update_values, "column2 = 'value2'")
    
    # Example of deleting data (uncomment to use)
    # delete_data(first_table, "column1 = 'updated_value'")

# 5. Creating a new table example (uncomment to use)
# new_table_name = 'new_table'
# columns = [
#     'id INTEGER PRIMARY KEY',
#     'name TEXT NOT NULL',
#     'age INTEGER',
#     'email TEXT UNIQUE'
# ]
# create_table(new_table_name, columns)

# Always close the connection when done
conn.close()