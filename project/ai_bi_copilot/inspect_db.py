import sqlite3

conn = sqlite3.connect("ai_bi.db")

print("\nTABLES")
print("=" * 50)

tables = conn.execute(
    "SELECT name FROM sqlite_master WHERE type='table'"
).fetchall()

print(tables)

print("\nDATASETS TABLE")
print("=" * 50)

columns = conn.execute(
    "PRAGMA table_info(datasets)"
).fetchall()

for column in columns:
    print(column)

conn.close()