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
            "SELECT price FROM crypto_prices WHERE crypto=? ORDER BY timestamp DESC LIMIT 1",
            (coin,)
        )
        result = cursor.fetchone()
        if result:
            prices[coin] = result[0]
    
    conn.close()
    
    # 格式化输出
    tip_text = f"Prices at {datetime.now().strftime('%H:%M')}\n"
    for coin, price in prices.items():
        tip_text += f"{coin}: {price}\n"
    
    return tip_text.strip()

if __name__ == "__main__":
    try:
        print(get_latest_prices())
    except Exception as e:
        print(f"Error: {str(e)}")
