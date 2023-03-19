import mysql.connector
from mysql.connector import Error, ProgrammingError

class DataBase:
    def __init__(self):
        self.db = None
        # self.cursor = None

    def connect_to_database_and_check_tables(self):
        print("Checking the DB")  # debug
        self.connect_to_database()
        self.delete_table()  # debug
        result = self.execute_query("SHOW TABLES LIKE 'game'")
        if not result:
            self.create_table()
        self.commit_transaction()
    
    def execute_query(self, query, *args):
        cursor = self.db.cursor()
        if args:
            cursor.execute(query, args)
        else:
            cursor.execute(query)
        result = cursor.fetchall()
        print("result: {}".format(result))  # debug
        return result
    
    def connect_to_database(self):
        self.db = mysql.connector.connect(
            host = "mysql",
            port = "3306",
            user = "root",
            password = "root",
            database = "tictactoe_db"
        )
        # self.cursor = self.db.cursor()

    def create_table(self):
        try:
            with open('game.sql', 'r') as file:
                script = file.read()
                print("Found table script: {}".format(script))
            self.execute_query(script)
            game_board = '[[" ", " ", " "], [" ", " ", " "], [" ", " ", " "]]'
            # Put the game_board to database
            query = "INSERT INTO game (game_board) VALUES (%s)"
            params = game_board
            self.execute_query(query, params)
            query = "SELECT * FROM game"
            self.execute_query(query)
            print("Table created successfully.")
        except Error as e:
            print(f"The error '{e}' occurred while creating the table.")

    def delete_table(self):
        self.execute_query("DROP TABLE game;")

    def update_game_board(self, game_board):
        print("Putting a game board to database: {}".format(game_board))
        query = "UPDATE game SET game_board = %s WHERE game_id = 1"
        params = str(game_board)
        self.execute_query(query, params)
    
    def get_game_board(self):
        query = "SELECT game_board FROM game WHERE game_id = 1"
        b = self.execute_query(query)
        b = b[0][0]
        return [[b[3], b[8], b[13]], 
                [b[20], b[25], b[30]],
                [b[37], b[42], b[47]]]
    
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