import mysql.connector
from mysql.connector import Error, ProgrammingError

class DataBase:
    def __init__(self):
        self.db = None
        self.cursor = None

    def connect_to_database_and_check_tables(self):
        print("Checking the DB")  # debug
        self.connect_to_database()
        # self.delete_table()  # reset table
        result = self.execute_query("SHOW TABLES LIKE 'game'")
        if not result:
            self.create_table()
    
    def execute_query(self, query):
        self.cursor.execute(query)
        result = self.cursor.fetchall()
        print("result: {}".format(result))  # debug
        self.commit_transaction()
        return result
    
    def connect_to_database(self):
        self.db = mysql.connector.connect(
            host = "mysql",
            port = "3306",
            user = "root",
            password = "root",
            database = "tictactoe_db"
        )
        self.cursor = self.db.cursor()

    def create_table(self):
        try:
            with open('game.sql', 'r') as file:
                script = file.read()
                print("Found table script: {}".format(script))
            self.execute_query(script)
            print("Table created successfully.")
        except Error as e:
            print(f"The error '{e}' occurred while creating the table.")

    def delete_table(self):
        self.execute_query("DROP TABLE game;")
    
    def start_transaction(self):
        try:
            self.db.start_transaction()
        except ProgrammingError:
            return False
        return True

    def commit_transaction(self):
        self.db.commit()
    
    def rollback_transaction(self):
        self.db.rollback()