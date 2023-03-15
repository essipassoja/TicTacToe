import client
import tictactoe
import mysql.connector
from mysql.connector import errorcode

# Establish a connection to the MySQL database
try:
    tictactoe_db = mysql.connector.connect(
      host="172.17.0.2",
      user="root",
      password="root",
      database="mysql"
    )
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your username or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
    else:
        print(err)
else:
    # Create a cursor object to interact with the database
    mycursor = tictactoe_db.cursor()

    # Read SQL file
    with open('game.sql', 'r') as f:
        create_table_query = f.read()

        # Execute SQL query
        mycursor.execute(create_table_query)

    # Execute a query
    mycursor.execute("SELECT * FROM game")

    # Fetch the results
    results = mycursor.fetchall()

    # Print the results
    for result in results:
        print(result)


    print("Making a server")

    client.make_a_new_client(1)
    client.make_a_new_client(2)
    tictactoe.run_game_logic()

    tictactoe_db.close()