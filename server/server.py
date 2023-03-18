"""
Copyright: Essi Passoja
"""

import socket
import threading
import mysql.connector
from mysql.connector import Error

PORT = 5000
HOST = ""
HOST_CLIENT1 = "client1"  # Docker container for client1
HOST_CLIENT2 = "client2"  # Docker container for client2

# https://stackoverflow.com/questions/57925492/how-to-listen-continuously-to-a-socket-for-data-in-python

class Server:
    def __init__(self):
        # Initialize db attributes
        self.db = None
        self.cursor = None
        self.transaction_in_progress = False

        #Initialize game play attributes
        self.current_player = "tic"
        self.requested_move = ""
        self.game_board = [
            [' ', ' ', ' '], 
            [' ', ' ', ' '], 
            [' ', ' ', ' ']]
        self.players = []

    # ~~~~~~~~  Client communication  ~~~~~~~~~~~~

    def start_listening_to_port(self):
        s = socket.socket()
        s.bind((HOST, PORT))
        s.listen(5)
        while True:
            connection, address = s.accept()
            print("Got connection from {}".format(address))
            t = threading.Thread(
                target=self.handle_client_messages, 
                args=(connection,))
            t.start()

    def handle_client_messages(self, connection):
        try:
            while True:
                message = bytes.decode(connection.recv(1024))
                ### Phase 1 ###
                if ("prepare" in message and 
                        self.current_player in message and 
                        len(self.players) == 2):
                    self.requested_move = message
                    self.prepare_phase(connection)
                elif "prepare" in message:
                    # Game has not started or it's not the player's turn
                    connection.send("Refusing to make the move".encode())
                ### Phase 2 ###
                elif "commit" in message and len(self.players) == 2:
                    self.commit_phase(connection)
                    self.read_move_location(message)
                elif "abort" in message and len(self.players) == 2:
                    self.abort_phase(connection)
                elif "Who am I" in message:
                    self.send_player_info(connection)
        except BrokenPipeError:
            print("Connection was probably closed by client.")
        finally:
            print("Closing the connection.")
            connection.close()

    # ~~~~~~~~  Decice player marks  ~~~~~~~~~~~~

    def send_player_info(self, connection):
        if not self.players:
            message = "tic"
            connection.send(message.encode())
            self.players.append("tic")
        else:
            message = "tac"
            connection.send(message.encode())
            self.players.append("tac")
            self.game_started = True

    # ~~~~~~~~  Two-phase protocol  ~~~~~~~~~~~~

    def prepare_phase(self, connection):
        if not self.transaction_in_progress:
            self.start_transaction()
        message = "Request to prepare"
        connection.sendall(message.encode())
        reply = bytes.decode(connection.recv(1024))
        if reply == "yes":
            message = "prepared"
            connection.sendall(message.encode())
        else:
            message = "not prepared"
            connection.sendall(message.encode())

    @staticmethod
    def commit_phase(self, connection):
        message = "Request to commit"
        connection.sendall(message.encode())
        reply = bytes.decode(connection.recv(1024))
        if reply == "yes":
            self.update_database()
            message = "commit confirmed"
            connection.sendall(message.encode())
        else:
            message = "commit aborted"
            connection.sendall(message.encode())

    @staticmethod
    def abort_phase(connection):
        message = "abort confirmed"
        connection.sendall(message.encode())

    def update_database(self):
        pass

    # ~~~~~~~~~~~~~~  MySQL  ~~~~~~~~~~~~~~~~

    def connect_to_database_and_check_tables(self):
        print("Checking the DB")  # debug
        self.connect_to_database()
        result = self.execute_query("SHOW TABLES LIKE 'game'")
        self.transaction_in_progress = True
        if not result:
            self.create_table()
    
    def execute_query(self, query):
        self.cursor.execute(query)
        result = self.cursor.fetchall()
        print("result: {}".format(result))  # debug
        return result
    
    def connect_to_database(self):
        self.db = mysql.connector.connect(
            host = "mysql",
            port="3306",
            user="root",
            password="root",
            database="tictactoe_db"
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

    def start_transaction(self):
        self.db.start_transaction()

    def commit_transaction(self):
        self.db.commit()
    
    def rollback_transaction(self):
        self.db.rollback()

    # ~~~~~~~~~~~~  Game logic  ~~~~~~~~~~~~~~

    def read_move_location(message):
        pass

    def check_game_status():
        pass

    # ~~~~~~~~~~~~~~  Main  ~~~~~~~~~~~~~~~~

    def main(self):
        self.connect_to_database_and_check_tables()
        self.start_listening_to_port()

if __name__ == '__main__':
    server = Server()
    server.main()
