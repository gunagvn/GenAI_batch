import sqlite3

conn = sqlite3.connect(":memory:")
conn.enable_load_extension(True)
conn.load_extension(r"C:\Users\Asus-2024\sqlite\vec0.dll")

print("sqlite-vec loaded successfully!")
