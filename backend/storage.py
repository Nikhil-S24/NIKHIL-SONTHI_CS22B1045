import mysql.connector
from mysql.connector import Error

def create_connection():
    """Create and return a MySQL database connection."""
    try:
        connection = mysql.connector.connect(
            host="localhost",        
            user="root",             
            password="nikhil",
            database="quant_data"
        )
        if connection.is_connected():
            print("✅ Connected to MySQL database")
            return connection
    except Error as e:
        print(f"❌ Error connecting to MySQL: {e}")
        return None


def create_table(connection):
    """Create a table for tick data if not exists."""
    create_table_query = """
    CREATE TABLE IF NOT EXISTS ticks (
        id INT AUTO_INCREMENT PRIMARY KEY,
        symbol VARCHAR(20),
        price FLOAT,
        quantity FLOAT,
        timestamp DATETIME
    )
    """
    cursor = connection.cursor()
    cursor.execute(create_table_query)
    connection.commit()
    cursor.close()
    print("📊 Table 'ticks' is ready.")


def insert_tick(connection, tick):
    """Insert one tick record into the database."""
    try:
        cursor = connection.cursor()
        insert_query = """
        INSERT INTO ticks (symbol, price, quantity, timestamp)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(insert_query, (tick["symbol"], tick["price"], tick["quantity"], tick["timestamp"]))
        connection.commit()
        cursor.close()
    except Error as e:
        print(f"⚠️ Error inserting tick: {e}")
