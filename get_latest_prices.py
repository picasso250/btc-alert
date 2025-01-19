import sqlite3
import json
from datetime import datetime

def get_latest_prices():
    # 读取config.json
    with open('config.json') as f:
        coins = json.load(f)
    
    # 连接数据库
    conn = sqlite3.connect('prices.db')
    cursor = conn.cursor()
    
    prices = {}
    for coin in coins:
        # 查询每个币种的最新价格
        cursor.execute(
            "SELECT price, timestamp FROM crypto_prices WHERE crypto=? ORDER BY timestamp DESC LIMIT 1",
            (coin,)
        )
        result = cursor.fetchone()
        if result:
            prices[coin] = result[0]
            latest_timestamp = result[1]
    
    conn.close()
    
    # 格式化输出
    # Convert timestamp to datetime and format
    dt = datetime.strptime(latest_timestamp, "%Y-%m-%d %H:%M:%S.%f")
    lines = [f"Prices at {dt.strftime('%Y-%m-%d %H:%M')}"]
    lines.extend(f"{coin}: {price}" for coin, price in prices.items())
    return "\n".join(lines)

if __name__ == "__main__":
    try:
        print(get_latest_prices())
    except Exception as e:
        print(f"Error: {str(e)}")
