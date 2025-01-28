import requests
import json
import subprocess
import time
from datetime import datetime
from db_operations import get_previous_price, insert_crypto_price, close_connection

def format_number(num):
    if num >= 10000:
        # 转换为k表示法，并四舍五入保留1位小数
        formatted_num = round(num / 1000, 1)
        return f"{formatted_num}k"
    else:
        return str(num)

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
        return f"Price moved {direction} to ${format_number(current_price)} (new grid: ${format_number(current_down)}-${format_number(current_up)})"
    return None

if __name__ == "__main__":
    try:
        # Main loop
        while True:
            # Load config on each iteration
            crypto_configs = get_config()
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

                # Check grid-based price change
                grid_size = crypto_configs[crypto_name]['grid_size']
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