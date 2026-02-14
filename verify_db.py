
import sqlite3
import os

db_path = os.path.join("instance", "cinego.db")
if not os.path.exists(db_path):
    print("DB file not found!")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

with open("verify_result_phase3.txt", "w") as f:
    # Check series count
    cursor.execute("SELECT COUNT(*) FROM series")
    try:
        count = cursor.fetchone()[0]
        f.write(f"Series count: {count}\n")
    except:
        f.write("Error counting series\n")
    
    # Check series with trailers protection
    try:
        cursor.execute("SELECT COUNT(*) FROM series WHERE trailer_url IS NOT NULL AND trailer_url != ''")
        trailer_count = cursor.fetchone()[0]
        f.write(f"Series with trailers: {trailer_count}\n")
    except Exception as e:
        f.write(f"Error checking trailers: {e}\n")

    # Sample series
    try:
        cursor.execute("SELECT title, trailer_url FROM series WHERE trailer_url != '' LIMIT 1")
        sample = cursor.fetchone()
        if sample:
            f.write(f"\nSample Series with Trailer:\nTitle: {sample[0]}\nURL: {sample[1]}\n")
    except Exception as e:
        f.write(f"Error fetching sample: {e}\n")

conn.close()
