import requests
import json
import subprocess
from datetime import datetime
def show_msg(param1, param2):
    # 定义AutoHotkey脚本路径
    ahk_script_path = 'show_msg.ahk'

    # 构建命令
    auto_hotkey_path = r'C:\Program Files\AutoHotkey\v2\AutoHotkey64.exe'
    command = [auto_hotkey_path, ahk_script_path, param1, param2]

    # 调用AutoHotkey脚本
    result = subprocess.run(command)

def get_config():
    json_config = json.load(open('config.json', 'r'))
    return json_config

def validate_config(condition, threshold):
    if condition not in ['<', '>']:
        return False
    if not isinstance(threshold, (int, float)):
        return False
    return True

def fetch_btc_price():
    """
    Fetches the current BTC price using the CoinGecko API.
    Returns the price in USD or raises an exception if the API call fails.
    """
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        return data["bitcoin"]["usd"]
    except requests.exceptions.RequestException as e:
        print(f"Error fetching BTC price: {e}")
        raise
    except KeyError:
        print("Unexpected response format.")
        raise

def check_price_condition(price, threshold, condition):
    """
    Checks if the price meets the specified condition.
    :param price: Current BTC price
    :param threshold: Price threshold to compare against
    :param condition: Condition to check ('>' or '<')
    :return: Result message
    """
    if condition == '>':
        if price > threshold:
            return f"BTC price (${price}) is greater than ${threshold}."
        else:
            return None
    elif condition == '<':
        if price < threshold:
            return f"BTC price (${price}) is less than ${threshold}."
        else:
            return None
    else:
        return None

if __name__ == "__main__":
    try:
        config = get_config()['BTC']
        for item in config:
            condition = item['condition']
            threshold = item['threshold']

            if not validate_config(condition, threshold):
                raise ValueError("Invalid config")

        btc_price = fetch_btc_price()
        print(btc_price)
        with open("btc_price.txt", "a") as f:
            f.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " " + str(btc_price) + "\n")

        for item in config:
            condition = item['condition']   
            threshold = item['threshold']

            result = check_price_condition(btc_price, threshold, condition)

            if result:
                show_msg(result, "BTC Price Out of Range!")
    except ValueError:
        print("Invalid input. Please enter a valid number for the price threshold.")
    except Exception as e:
        print(f"An error occurred: {e}")

