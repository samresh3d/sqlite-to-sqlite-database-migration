import sqlite3

# Connect to the source and destination databases
source_conn = sqlite3.connect('data-s.db')
destination_conn = sqlite3.connect('data-d.db')

# Get the list of table names from the source database
source_cursor = source_conn.cursor()
source_cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = source_cursor.fetchall()
table_names = [table[0] for table in tables if table[0] != 'sqlite_sequence']

# Iterate over each table
for table_name in table_names:
    # Retrieve the table schema from the source database
    source_cursor.execute(f"PRAGMA table_info({table_name})")
    columns = source_cursor.fetchall()

    # Check if the table exists in the destination database
    destination_cursor = destination_conn.cursor()
    destination_cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    table_exists = destination_cursor.fetchone()

    if table_exists:
        # Update the data in the destination table from the source table
        destination_cursor.execute(f"DELETE FROM `{table_name}`")
    else:
        # Create the table in the destination database using the retrieved schema
        create_table_query = f"CREATE TABLE `{table_name}` ({', '.join([f'`{column[1]}` {column[2]}' for column in columns])})"
        destination_cursor.execute(create_table_query)

    # Migrate the data from the source table to the destination table
    source_cursor.execute(f"SELECT * FROM `{table_name}`")
    data = source_cursor.fetchall()
    destination_cursor.executemany(f"INSERT INTO `{table_name}` VALUES ({', '.join(['?' for _ in columns])})", data)

# Commit and close the connections
destination_conn.commit()
destination_conn.close()
source_conn.close()
