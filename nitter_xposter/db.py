import sqlite3


def setup_database(sqlite_file: str):
    # Connect to SQLite Database
    conn = sqlite3.connect(sqlite_file)
    cursor = conn.cursor()

    # Create table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS last_position (
        feed_name TEXT PRIMARY KEY,
        last_id TEXT
    )
    ''')
    conn.commit()
    conn.close()


def get_last_position(sqlite_file: str, feed_name: str):
    # Connect to the database
    conn = sqlite3.connect(sqlite_file)
    cursor = conn.cursor()

    # Get the last crawled position
    cursor.execute('SELECT last_id FROM last_position WHERE feed_name = ?', (feed_name,))
    last_id = cursor.fetchone()
    last_id = last_id[0] if last_id else None
    return last_id


def set_last_position(sqlite_file: str, feed_name: str, new_last_id: str):
    # Connect to SQLite Database
    conn = sqlite3.connect(sqlite_file)
    cursor = conn.cursor()

    cursor.execute('REPLACE INTO last_position (feed_name, last_id) VALUES (?, ?)', (feed_name, new_last_id))
    
    conn.commit()
    conn.close()
