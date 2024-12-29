import sqlite3

# 打开数据库文件
conn = sqlite3.connect('prices.db')
cursor = conn.cursor()

# 执行 SELECT 语句
cursor.execute('SELECT * FROM crypto_prices')

# 获取所有结果
rows = cursor.fetchall()

# 处理结果（示例打印每行）
for row in rows:
    print(row)

# 关闭连接
conn.close()
