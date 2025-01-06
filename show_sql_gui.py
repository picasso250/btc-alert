import sqlite3
import tkinter as tk
from tkinter import ttk

class CryptoPriceViewer:
    # 字体定义
    title_font = ("Arial", 16, "bold")
    label_font = ("Arial", 12)

    def __init__(self, root):
        self.root = root
        self.root.title("Crypto Price Viewer")
        
        # 创建主容器
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 创建标题
        tk.Label(self.main_frame, text="Crypto Prices", font=self.title_font).pack(pady=10)
        
        # 创建数据容器
        self.data_frame = tk.Frame(self.main_frame)
        self.data_frame.pack(fill=tk.BOTH, expand=True)
        
        # 加载数据
        self.load_data()

    def load_data(self):
        try:
            # 连接数据库
            conn = sqlite3.connect('prices.db')
            cursor = conn.cursor()
            
            # 获取每种币的最新价格
            cursor.execute('''
                SELECT id, crypto, price, MAX(timestamp) 
                FROM crypto_prices 
                GROUP BY crypto
            ''')
            rows = cursor.fetchall()
            
            # 显示数据
            for row in rows:
                crypto_frame = tk.Frame(self.data_frame)
                crypto_frame.pack(fill=tk.X, pady=5)
                
                # 显示币种名称
                tk.Label(crypto_frame, text=row[1], font=self.label_font, width=15, anchor="w").pack(side=tk.LEFT)
                
                # 显示价格
                price_label = tk.Label(crypto_frame, text=f"${float(row[2]):.2f}", font=self.label_font, fg="green")
                price_label.pack(side=tk.LEFT, padx=10)
                
                # 显示时间
                tk.Label(crypto_frame, text=row[3], font=self.label_font, fg="gray").pack(side=tk.RIGHT)
                
            # 关闭连接
            conn.close()
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CryptoPriceViewer(root)
    root.geometry("800x600")
    root.mainloop()
