import requests
import json
import subprocess
from datetime import datetime
import time
import sqlite3

# Initialize SQLite database
conn = sqlite3.connect('prices.db')
cursor = conn.cursor()

# Create table (if it doesn't exist)
cursor.execute('''
CREATE TABLE IF NOT EXISTS crypto_prices (
    id INTEGER PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    crypto TEXT,
    price REAL
)
''')

def show_msg(param1, param2):
    # Define AutoHotkey script path
    ahk_script_path = 'show_msg.ahk'

    # Construct command
    auto_hotkey_path = r'C:\Program Files\AutoHotkey\v2\AutoHotkey64.exe'
    command = [auto_hotkey_path, ahk_script_path, param1, param2]

    # Invoke AutoHotkey script
    subprocess.run(command)

def get_config():
    with open('config.json', 'r') as f:
        return json.load(f)

def validate_config(condition, threshold):
    if condition not in ['<', '>']:
        return False
    if not isinstance(threshold, (int, float)):
        return False
    return True

def fetch_crypto_price(crypto_ids):
    """
    Fetches the current price for the specified cryptocurrencies using the CoinGecko API.
    :param crypto_ids: List of cryptocurrency IDs to fetch prices for.
    :return: Dictionary of {crypto: price} or raises an exception if the API call fails.
    """
    ids = ','.join(crypto_ids)
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        return {crypto: data[crypto]["usd"] for crypto in crypto_ids}
    except requests.exceptions.RequestException as e:
        print(f"Error fetching crypto prices: {e}")
        raise
    except KeyError:
        print("Unexpected response format.")
        raise

def check_price_condition(price, threshold, condition):
    """
    Checks if the price meets the specified condition.
    :param price: Current price
    :param threshold: Price threshold to compare against
    :param condition: Condition to check ('>' or '<')
    :return: Result message
    """
    if condition == '>':
        if price > threshold:
            return f"${price} is greater than ${threshold}."
        else:
            return None
    elif condition == '<':
        if price < threshold:
            return f"${price} is less than ${threshold}."
        else:
            return None
    else:
        return None

if __name__ == "__main__":
    try:
        config = get_config()
        crypto_configs = config

        # Validate configuration
        for crypto_name in crypto_configs:
            crypto = crypto_configs[crypto_name]
            for c in crypto:
                condition = c['condition']
                threshold = c['threshold']

                if not validate_config(condition, threshold):
                    raise ValueError("Invalid config")

        # Main loop
        while True:
            crypto_ids = [crypto for crypto in crypto_configs]

            # Fetch crypto prices
            prices = fetch_crypto_price(crypto_ids)

            for crypto_name, price in prices.items():
                # Insert price into database
                cursor.execute('INSERT INTO crypto_prices (crypto, price) VALUES (?, ?)', (crypto_name, price))
                conn.commit()

                # Log (optional)
                print(f'Logged {crypto_name} price: {price}')

                # Check conditions for each crypto
                for c in crypto_configs[crypto_name]:
                    condition = c['condition']
                    threshold = c['threshold']

                    result = check_price_condition(price, threshold, condition)

                    if result:
                        show_msg(result, f"{crypto.upper()} Price Alert!")

            # Wait 1 hour
            time.sleep(3600)

        # Close database connection (this is never reached theoretically)
        conn.close()

    except ValueError:
        print("Invalid input. Please enter a valid number for the price threshold.")
    except Exception as e:
        print(f"An error occurred: {e}")
