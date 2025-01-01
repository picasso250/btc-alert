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

def validate_config(min_val, max_val):
    if not isinstance(min_val, (int, float)) or not isinstance(max_val, (int, float)):
        return False
    if min_val >= max_val:
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

def get_previous_price(crypto_name):
    """
    Gets the previous price from the database.
    :param crypto_name: Name of the cryptocurrency
    :return: Previous price or None if not found
    """
    cursor = conn.cursor()
    cursor.execute('''
        SELECT price FROM crypto_prices 
        WHERE crypto = ? 
        ORDER BY timestamp DESC 
        LIMIT 1 OFFSET 1
    ''', (crypto_name,))
    result = cursor.fetchone()
    return result[0] if result else None

def check_price_condition(price, min_val, max_val):
    """
    Checks if the price is outside the specified range.
    :param price: Current price
    :param min_val: Minimum price threshold
    :param max_val: Maximum price threshold
    :return: Result message if price is outside range, else None
    """
    if price < min_val:
        return f"${price} is below minimum ${min_val}."
    elif price > max_val:
        return f"${price} is above maximum ${max_val}."
    return None

def insert_crypto_price(crypto_name, price):
    """
    Inserts cryptocurrency price into the database.
    :param crypto_name: Name of the cryptocurrency
    :param price: Current price
    """
    cursor = conn.cursor()
    cursor.execute('INSERT INTO crypto_prices (crypto, price) VALUES (?, ?)', (crypto_name, price))
    conn.commit()

def get_up_down_grid(price, grid_size):
    """
    Calculates upper and lower grid bounds for a given price.
    :param price: Current price
    :param grid_size: Size of each grid
    :return: Tuple of (lower_bound, upper_bound)
    """
    down = int(price / grid_size) * grid_size
    up = down + grid_size
    return (down, up)
def check_grid_change(current_price, previous_price, grid_size):
    """
    Checks if price has moved to a different grid level.
    :param current_price: Current price
    :param previous_price: Previous price
    :param grid_size: Size of each grid
    :return: Alert message if grid level changed, else None
    """
    if previous_price is None:
        return None
        
    # Get current and previous grid bounds
    current_down, current_up = get_up_down_grid(current_price, grid_size)
    prev_down, prev_up = get_up_down_grid(previous_price, grid_size)
    
    # Check if grid bounds have changed
    if current_down != prev_down or current_up != prev_up:
        change = abs(current_price - previous_price)
        direction = "up" if current_price > previous_price else "down"
        return f"Price moved {direction} by ${change:.2f} (new grid: ${current_down}-${current_up})"
    return None

if __name__ == "__main__":
    try:
        crypto_configs = get_config()

        # Validate configuration
        for crypto_name in crypto_configs:
            crypto = crypto_configs[crypto_name]
            min_val = crypto['min']
            max_val = crypto['max']
            
            if not validate_config(min_val, max_val):
                raise ValueError("Invalid config")

        # Main loop
        while True:
            crypto_ids = [crypto for crypto in crypto_configs]

            # Fetch crypto prices
            prices = fetch_crypto_price(crypto_ids)

            for crypto_name, price in prices.items():
                # Insert price into database
                insert_crypto_price(crypto_name, price)

                # Log (optional)
                print(f'Logged {crypto_name} price: {price}')

                # Check conditions for each crypto
                min_val = crypto_configs[crypto_name]['min']
                max_val = crypto_configs[crypto_name]['max']
                grid_size = crypto_configs[crypto_name]['grid_size']
                
                # Check price range condition
                range_result = check_price_condition(price, min_val, max_val)
                if range_result:
                    show_msg(range_result, f"{crypto_name.upper()} Price Alert!")
                
                # Check grid-based price change
                previous_price = get_previous_price(crypto_name)
                grid_result = check_grid_change(price, previous_price, grid_size)
                if grid_result:
                    show_msg(grid_result, f"{crypto_name.upper()} Grid Alert!")

            # Wait half hour
            time.sleep(3600/2)

        # Close database connection (this is never reached theoretically)
        conn.close()

    except ValueError:
        print("Invalid input. Please enter a valid number for the price threshold.")
    except Exception as e:
        print(f"An error occurred: {e}")
