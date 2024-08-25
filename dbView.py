import sqlite3
import os

# Get the current working directory
current_dir = os.getcwd()

# Construct the full path to the database file
db_path = os.path.join(current_dir, 'schedules.db')

print(f"Attempting to open database at: {db_path}")

# Check if the file exists
if not os.path.exists(db_path):
    print(f"Database file not found at {db_path}")
else:
    print("Database file found. Attempting to read data...")

    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get the number of rows in the schedules table
        cursor.execute("SELECT COUNT(*) FROM schedules")
        row_count = cursor.fetchone()[0]
        print(f"Total number of rows in schedules table: {row_count}")

        # Fetch and print the first 5 rows
        cursor.execute("SELECT * FROM schedules LIMIT 50")
        rows = cursor.fetchall()
        
        print("\nFirst 5 rows of data:")
        for row in rows:
            print(row)

        # Close the connection
        conn.close()

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")