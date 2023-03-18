"""
Copyright: Essi Passoja
"""

import re
import socket
import threading

PORT = 5000
HOST = ""
CLIENT_HOSTS = ["client1", "client2"]

# https://stackoverflow.com/questions/57925492/how-to-listen-continuously-to-a-socket-for-data-in-python

class Server:
    def __init__(self):
        # Initialize db attributes
        self.db = None
        self.cursor = None
        self.connections = []
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
            self.connections.append(connection)
            print("Got connection from {}".format(address))
            t = threading.Thread(
                target=self.handle_client_messages, 
                args=(connection,))
            t.start()

    def handle_client_messages(self, connection):
        try:
            while True:
                message = bytes.decode(connection.recv(1024))
                if message:
                    print("Received a message: {}".format(message))
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
                    self.add_move_to_game_board()
                elif "abort" in message and len(self.players) == 2:
                    self.abort_phase(connection)
                    self.requested_move = None
                elif "Who am I" in message:
                    self.send_player_info(connection)
        except BrokenPipeError:
            print("Connection was probably closed by client.")
        finally:
            print("Closing the connection.")
            connection.close()
            self.connections.remove(connection)

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

    # ~~~~~~~~~~  2PC protocol  ~~~~~~~~~~~~~~

    def prepare_phase(self, connection):
        message = "Request to prepare"
        for connection in self.connections:
            t = threading.Thread(
                target=self.send_message, 
                args=(connection, message))
            t.start()
    
    def send_message(self, connection, message):
        print("Sending a message {}".format(message))
        connection.sendall(message.encode())
        reply = bytes.decode(connection.recv(1024))
        print(reply)

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

    # ~~~~~~~~~~~~  Game logic  ~~~~~~~~~~~~~~

    def add_move_to_game_board(self):
        location_regex = re.compile(r".*?(\d), ?(\d).*")
        match = location_regex.match(self.requested_move)
        row = match.group(1)
        column = match.group(2)
        self.game_board[row][column] = ("x" if "tic" in self.current_player 
                                        else "o")
        print(self.game_board)

    def check_win(self):
        for i in enumerate(len(self.game_board)):
            if (self.game_board[i][0]
                    == self.game_board[i][1]
                    == self.game_board[i][2]):
                return True
            elif (self.game_board[0][i]
                    == self.game_board[1][i]
                    == self.game_board[2][i]):
                return True
        if (self.game_board[0][0]
                == self.game_board[1][1]
                == self.game_board[2][2]):
            return True
        if (self.game_board[0][2]
                == self.game_board[1][1]
                == self.game_board[2][0]):
            return True
        return False

    # ~~~~~~~~~~~~~~  Main  ~~~~~~~~~~~~~~~~

    def main(self):
        self.start_listening_to_port()

if __name__ == '__main__':
    server = Server()
    server.main()
