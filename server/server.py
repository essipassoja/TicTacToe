"""
Copyright: Essi Passoja
"""

import socket
import threading

PORT = 5000
HOST = ""
CLIENT_HOSTS = ["client1", "client2"]


class Server:
    def __init__(self):
        # Initialize db attributes
        self.db = None
        self.cursor = None
        self.connections = []
        self.game_board_update_required = False
        self.request_ongoing = False
        self.message_counter = 0

        #Initialize game play attributes
        self.current_player = "x"
        self.players = []

        # player_statuses collects the responses from clients, 
        # for example ["Prepared", "Prepared"]
        self.player_statuses = []

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
                    self.message_counter += 1
                    print("Traffic: {} messages".format(self.message_counter))
                # ~~~~ Start 2PC protocol ~~~~~~
                    if ("prepare" in message and 
                            " {} ".format(self.current_player) in message and 
                            len(self.players) == 2 and not self.request_ongoing):
                        self.game_board_update_required = True
                        self.request_ongoing = True
                        self.prepare_phase(message)
                    elif "prepare" in message:
                        # Game has not started or it's not the player's turn
                        reply = "Refusing to make the move"
                        connection.send(reply.encode())
                    elif ("Prepared" in message or "Not Prepared" in message or 
                        "Committed" in message or "Aborted" in message):
                        self.player_statuses.append(message)
                    # ~~~~~~~~~~~~~~~~~~~~~~~~~~
                    elif "Who am I" in message:
                        self.send_player_info(connection)
        except BrokenPipeError:
            print("Connection was probably closed by client.")
        finally:
            print("Closing the connection.")
            connection.close()
            self.remove_connection_from_connections(connection)
    
    def send_message_to_both_clients(self, message):
        print("Sending {}".format(message))
        for connection in self.connections:
            t = threading.Thread(
                target=self.send_message, 
                args=(connection, message))
            t.start()

    def send_message(self, connection, message):
        try:
            connection.sendall(message.encode())
            self.message_counter += 1
            print("Traffic: {} messages".format(self.message_counter))
        except BrokenPipeError:
            self.remove_connection_from_connections(connection)

    def remove_connection_from_connections(self, connection):
        try:
            self.connections.remove(connection)
        except ValueError:
            print("Connection already removed from list.")

    # ~~~~~~~~  Decice player marks  ~~~~~~~~~~~~

    def send_player_info(self, connection):
        if not self.players:
            message = "x"
            connection.send(message.encode())
            self.message_counter += 1
            print("Traffic: {} messages".format(self.message_counter))
            self.players.append("x")
        else:
            message = "o"
            connection.send(message.encode())
            self.message_counter += 1
            print("Traffic: {} messages".format(self.message_counter))
            self.players.append("o")
            self.game_started = True
        self.remove_connection_from_connections(connection)

    # ~~~~~~~~~~  2PC protocol  ~~~~~~~~~~~~~~
    
    def prepare_phase(self, request):
        message = "Request to {}".format(request)
        self.send_message_to_both_clients(message)
        while True:
            if self.player_statuses.count("Prepared") == 2:
                print("Both are prepared")
                self.player_statuses = []
                self.commit_phase()
                break
            elif ((self.player_statuses.count("Prepared") + 
                    self.player_statuses.count("Not prepared")) == 2
                    and self.player_statuses.count("Prepared") != 2):
                self.player_statuses = []
                self.abort_phase()
                break

    def commit_phase(self):
        message = "Request to commit"
        self.send_message_to_both_clients(message)
        while True:
            if self.player_statuses.count("Committed") == 2:
                print("Both committed")
                self.player_statuses = []
                if self.game_board_update_required:
                    self.game_board_update_required = False
                    print("Game board update no longer required")
                    self.update_boards()
                break

    def abort_phase(self):
        message = "Request to abort"
        self.send_message_to_both_clients(message)
        while True:
            if self.player_statuses.count("Aborted") == 2:
                print("Both aborted")
                self.player_statuses = []
                self.game_board_update_required = False
                self.request_ongoing = False
                break
    
    def update_boards(self):
        message = "Request to prepare update"
        self.send_message_to_both_clients(message)
        while True:
            if self.player_statuses.count("Prepared") == 2:
                self.player_statuses = []
                self.commit_phase()
                self.request_ongoing = False
                self.current_player = "x" if self.current_player == "o" else "o"
                print("Switched current player to {}".format(self.current_player))
                break
            elif ((self.player_statuses.count("Prepared") + 
                    self.player_statuses.count("Not prepared")) == 2
                    and self.player_statuses.count("Prepared") != 2):
                self.player_statuses = []
                self.abort_phase()
                self.current_player = "x" if self.current_player == "o" else "o"
                print("Switched current player to {}".format(self.current_player))
                break

    # ~~~~~~~~~~~~~~  Main  ~~~~~~~~~~~~~~~~

    def main(self):
        self.start_listening_to_port()

if __name__ == '__main__':
    server = Server()
    server.main()
