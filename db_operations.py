import sqlite3
from datetime import datetime

# Initialize SQLite database
conn = sqlite3.connect('prices.db')
cursor = conn.cursor()

def initialize_db():
    """Initialize the database table if it doesn't exist"""
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS crypto_prices (
        id INTEGER PRIMARY KEY,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        crypto TEXT,
        price REAL
    )
    ''')
    conn.commit()

def get_previous_price(crypto_name):
    """
    Gets the previous price from the database.
    :param crypto_name: Name of the cryptocurrency
    :return: Previous price or None if not found
    """
    cursor.execute('''
        SELECT price FROM crypto_prices 
        WHERE crypto = ? 
        ORDER BY timestamp DESC 
        LIMIT 1 OFFSET 1
    ''', (crypto_name,))
    result = cursor.fetchone()
    return result[0] if result else None

def insert_crypto_price(crypto_name, price):
    """
    Inserts cryptocurrency price into the database.
    :param crypto_name: Name of the cryptocurrency
    :param price: Current price
    """
    cursor.execute('INSERT INTO crypto_prices (crypto, price, timestamp) VALUES (?, ?, ?)', 
                  (crypto_name, price, datetime.now()))
    conn.commit()

def close_connection():
    """Close the database connection"""
    conn.close()
