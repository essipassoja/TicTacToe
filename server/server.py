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

        #Initialize game play attributes
        self.current_player = "tic"
        self.requested_move = ""
        self.game_board = [
            [' ', ' ', ' '], 
            [' ', ' ', ' '], 
            [' ', ' ', ' ']]
        self.players = []
        # Game status follows the responses from clients, 
        # for example ["Prepared", "Prepared"]
        self.game_status = []

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
                # ~~~~ Start 2PC protocol ~~~~~~
                if ("prepare" in message and 
                        self.current_player in message and 
                        len(self.players) == 2):
                    self.requested_move = message
                    self.prepare_phase()
                elif "prepare" in message:
                    # Game has not started or it's not the player's turn
                    connection.send("Refusing to make the move".encode())
                elif ("Prepared" in message or "Not Prepared" in message or 
                      "Committed" in message or "Aborted" in message):
                    self.game_status.append(message)
                # ~~~~~~~~~~~~~~~~~~~~~~~~~~
                elif "Who am I" in message:
                    self.send_player_info(connection)
        except BrokenPipeError:
            print("Connection was probably closed by client.")
        finally:
            print("Closing the connection.")
            connection.close()
            try:
                self.connections.remove(connection)
            except ValueError:
                print("Connection already removed from list.")

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
        try:
            self.connections.remove(connection)
        except ValueError:
            print("Connection already removed from list.")

    # ~~~~~~~~~~  2PC protocol  ~~~~~~~~~~~~~~

    def send_message_to_both_clients(self, message):
        for connection in self.connections:
            t = threading.Thread(
                target=self.send_message, 
                args=(connection, message))
            t.start()

    def send_message(self, connection, message):
        print("Sending a message {}".format(message))
        try:
            connection.sendall(message.encode())
        except BrokenPipeError:
            pass
        else:
            reply = bytes.decode(connection.recv(1024))
            try:
                self.connections.remove(connection)
            except ValueError:
                print("Connection already removed from list.")
            print(reply)
            self.game_status.append(reply)
    
    def prepare_phase(self):
        ok = self.check_if_move_can_be_made()
        if not ok:
            print("Cannot make move, the square is already taken")
            return
        message = "Request to {}".format(self.requested_move)
        self.send_message_to_both_clients(message)
        while True:
            if self.game_status.count("Prepared") == 2:
                self.game_status = []
                self.commit_phase()
                break
            elif ((self.game_status.count("Prepared") + 
                    self.game_status.count("Not prepared")) == 2
                    and self.game_status.count("Prepared") != 2):
                self.game_status = []
                self.abort_phase()
                break

    def commit_phase(self):
        message = "Request to commit"
        self.send_message_to_both_clients(message)
        while True:
            if self.game_status.count("Committed") == 2:
                print("Both committed")
                self.game_status = []
                self.add_move_to_game_board()
                break

    def abort_phase(self):
        message = "Request to abort"
        self.send_message_to_both_clients(message)
        while True:
            if self.game_status.count("Aborted") == 2:
                print("Both aborted")
                self.game_status = []
                break

    # ~~~~~~~~~~~~  Game logic  ~~~~~~~~~~~~~~

    def get_location(self):
        location_regex = re.compile(r".*?(\d), ?(\d).*")
        match = location_regex.match(self.requested_move)
        return int(match.group(1)), int(match.group(2))
    
    def check_if_move_can_be_made(self):
        row, column = self.get_location()
        if self.game_board[row][column] == " ":
            return True
        return False
    
    def add_move_to_game_board(self):
        row, column = self.get_location()
        self.game_board[row][column] = ("x" if "tic" in self.current_player 
                                        else "o")
        print(self.game_board)
        player_won = self.check_win()
        print("Player won: {}".format(player_won))
        self.current_player = "tic" if self.current_player == "tac" else "tac"

    def check_win(self):
        print("Checking win")
        for i, _ in enumerate(self.game_board):
            if ((self.game_board[i][0]
                    == self.game_board[i][1]
                    == self.game_board[i][2])
                    and self.game_board[i][0] != " "):
                return True
            elif ((self.game_board[0][i]
                    == self.game_board[1][i]
                    == self.game_board[2][i])
                    and self.game_board[0][i] != " "):
                return True
        if ((self.game_board[0][0]
                == self.game_board[1][1]
                == self.game_board[2][2])
                and self.game_board[0][0] != " "):
            return True
        if ((self.game_board[0][2]
                == self.game_board[1][1]
                == self.game_board[2][0]) 
                and self.game_board[0][2] != " "):
            return True
        return False

    # ~~~~~~~~~~~~~~  Main  ~~~~~~~~~~~~~~~~

    def main(self):
        self.start_listening_to_port()

if __name__ == '__main__':
    server = Server()
    server.main()
