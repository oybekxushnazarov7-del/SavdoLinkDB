import json
import pypyodbc as odbc

with open('config/settings.json','r') as f:
    config = json.load(f)

DRIVER_NAME = config["DRIVER_NAME"]
SERVER_NAME = config["SERVER_NAME"]
DATABASE_NAME = config["DATABASE_NAME"]

connection_string = f"""
DRIVER={{{DRIVER_NAME}}};
SERVER={SERVER_NAME};
DATABASE={DATABASE_NAME};
Trusted_Connection=yes;
"""

conn = odbc.connect(connection_string)
cursor = conn.cursor()


sql_query = "SELECT * FROM mart.FactDailySales"
cursor.execute(sql_query)

# 4. Fetch and display results
for row in cursor.fetchall():
    print(row)

conn.close()