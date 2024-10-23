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

        # Get all distinct room names from the schedules table
        cursor.execute("SELECT DISTINCT room FROM schedules")
        rooms = cursor.fetchall()
        
        print("\nDistinct room names:")
        for room in rooms:
            print(room[0])

        # Close the connection
        conn.close()

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
