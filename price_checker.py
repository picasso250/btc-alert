import requests
import json
import subprocess
import time
from datetime import datetime
from db_operations import get_previous_price, insert_crypto_price, close_connection

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
    # If both are None, config is valid
    if min_val is None and max_val is None:
        return True
    # If only one is None, config is invalid
    if min_val is None or max_val is None:
        return False
    # Both have values - validate them
    if not isinstance(min_val, (int, float)) or not isinstance(max_val, (int, float)):
        return False
    if min_val >= max_val:
        return False
    return True

def fetch_crypto_price(crypto_ids):
    """
    Fetches the current price for the specified cryptocurrencies using the CoinGecko API.
    :param crypto_ids: List of cryptocurrency IDs to fetch prices for
    :return: Dictionary of {crypto: price} or raises an exception if the API call fails
    """
    ids = ','.join(crypto_ids)
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd"
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for HTTP errors
    try:
        data = response.json()
        return {crypto: data[crypto]["usd"] for crypto in crypto_ids}
    except KeyError:
        print("Unexpected response format.")
        raise

def check_price_condition(price, min_val, max_val):
    """
    Checks if the price is outside the specified range.
    :param price: Current price
    :param min_val: Minimum price threshold (optional)
    :param max_val: Maximum price threshold (optional)
    :return: Result message if price is outside range, else None
    """
    # Skip check if either value is None
    if min_val is None or max_val is None:
        return None
    if price < min_val:
        return f"${price} is below ${min_val}."
    elif price > max_val:
        return f"${price} is above ${max_val}."
    return None

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
        return f"Price moved {direction} to ${current_price:.2f} (new grid: ${current_down}-${current_up})"
    return None

if __name__ == "__main__":
    try:
        # Main loop
        while True:
            # Load and validate config on each iteration
            crypto_configs = get_config()
            for crypto_name in crypto_configs:
                crypto = crypto_configs[crypto_name]
                min_val = crypto.get('min')  # Use get() to handle missing key
                max_val = crypto.get('max')  # Use get() to handle missing key
                
                if not validate_config(min_val, max_val):
                    print(f"Invalid config detected for {crypto_name}")
                    time.sleep(600)  # Sleep for 10 minutes
                    continue

            crypto_ids = [crypto for crypto in crypto_configs]

            # Fetch crypto prices
            try:
                prices = fetch_crypto_price(crypto_ids)
            except requests.exceptions.RequestException as e:
                print(f"API request failed: {e}")
                time.sleep(600)  # Sleep for 10 minutes
                continue

            # Initialize combined message
            combined_msg = ""
            
            for crypto_name, price in prices.items():
                # Insert price into database
                insert_crypto_price(crypto_name, price)

                # Log (optional)
                print(f'Logged {crypto_name} price: {price}')

                # Check conditions for each crypto
                min_val = crypto_configs[crypto_name].get('min')
                max_val = crypto_configs[crypto_name].get('max') 
                grid_size = crypto_configs[crypto_name]['grid_size']
                
                # Check price range condition
                range_result = check_price_condition(price, min_val, max_val)
                if range_result:
                    combined_msg += f"{crypto_name.upper()}: {range_result}\n"
                
                # Check grid-based price change
                previous_price = get_previous_price(crypto_name)
                grid_result = check_grid_change(price, previous_price, grid_size)
                if grid_result:
                    combined_msg += f"{crypto_name.upper()}: {grid_result}\n"

            # Show combined message if there are any alerts
            if len(combined_msg) > 0:
                show_msg(combined_msg, "Crypto Price Alerts")

            # Wait half hour
            time.sleep(3600/2)

    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        close_connection()
        print("Database connection closed")
