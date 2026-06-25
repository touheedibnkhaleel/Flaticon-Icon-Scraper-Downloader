# db.py
import sqlite3

connection = sqlite3.connect("/Users/touheed/Desktop/flaticon/scraper.db")
cursor = connection.cursor()

def setup_database():
    try:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS ICONS (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            TITLE TEXT NOT NULL,
            IMAGE_URL TEXT UNIQUE,
            LOCAL_PATH TEXT,
            DOWNLOADED BOOLEAN,
            CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS PROGRESS (
                LAST_PAGE INTEGER
            )
        """)
        try:
            cursor.execute("""ALTER TABLE ICONS ADD COLUMN FAILED BOOLEAN DEFAULT 0 """)
        except:
            pass
        connection.commit()
        print("Tables created successfully")

    except sqlite3.Error as e:
        print(f"Database error: {e}")

def add_icon(title: str, image_url: str):
    try:
        cursor.execute("""
            INSERT OR IGNORE INTO ICONS (TITLE, IMAGE_URL)
            VALUES (?, ?)
        """, (title, image_url))
        connection.commit()
    except sqlite3.Error as e:
        print(f"Error adding icon: {e}")

def get_undownloaded_icons(downloaded: bool = False):
    try:
        cursor.execute("SELECT ID, TITLE, IMAGE_URL FROM ICONS WHERE (DOWNLOADED = 0 OR DOWNLOADED IS NULL) AND (FAILED = 0 OR FAILED IS NULL) ")
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Error fetching icons: {e}")
        return []

def get_progress():
    try:
        cursor.execute("SELECT LAST_PAGE FROM PROGRESS")
        result = cursor.fetchone()
        if result is None:
            return None
        return result[0]
    except sqlite3.Error as e:
        print(f"Error getting progress: {e}")
        return None

def save_progress(last: int):
    try:
        cursor.execute("SELECT LAST_PAGE FROM PROGRESS")
        result = cursor.fetchone()
        if result is None:
            cursor.execute("INSERT INTO PROGRESS (LAST_PAGE) VALUES (?)", (last,))
        else:
            cursor.execute("UPDATE PROGRESS SET LAST_PAGE = ?", (last,))
        connection.commit()
    except sqlite3.Error as e:
        print(f"Error saving progress: {e}")

def clear_progress():
    try:
        cursor.execute("DELETE FROM PROGRESS")
        connection.commit()
    except sqlite3.Error as e:
        print(f"Error clearing progress: {e}")

def update_icon(local_path, id):
    try:
        local_connection = sqlite3.connect("/Users/touheed/Desktop/flaticon/scraper.db")
        local_cursor = local_connection.cursor()
        local_cursor.execute("""UPDATE ICONS SET DOWNLOADED = 1, LOCAL_PATH = ? WHERE ID = ?""", (local_path, id))
        local_connection.commit()
        local_connection.close()
    except Exception as e:
        print("Error ", e)

def mark_failed(id):
    try:
        local_connections = sqlite3.connect("/Users/touheed/Desktop/flaticon/scraper.db")
        local_cursors = local_connections.cursor()
        local_cursors.execute("UPDATE ICONS SET FAILED = 1 WHERE ID = ? ", (id, ))
        local_connections.commit()
        local_connections.close()
    except Exception as e:
        print("Error ", e)

        
setup_database()
