"""
Copyright: Essi Passoja
"""

import socket

class Server:
    def __init__(self):
        self.game_board = [[' ', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']]
        self.game_started = False
        self.players = []
        self.socket = socket.socket()

    def start_listening_socket(self):
        port = 5000
        self.socket.bind(("", port))
        self.socket.listen(5)

        while True:
            connection, address = self.socket.accept()
            print("Got connection from {}".format(address))
            message = bytes.decode(connection.recv(1024))
            print(message)
            if not self.game_started:
                self.check_for_players(connection, message)
            ### Phase 1 ###
            if "prepare" in message:
                self.prepare_phase(connection)
            ### Phase 2 ###
            elif "commit" in message:
                self.commit_phase(connection)
                # TODO check if current player is winner
            elif "abort" in message:
                self.abort_phase(connection)

    def check_for_players(self, connection, message):
        if "Who am I?" in message:
            if not self.players:
                message = "tic"
                connection.sendall(message.encode())
                self.players.append("tic")
            else:
                message = "tac"
                connection.sendall(message.encode())
                self.players.append("tac")
                self.game_started = True
    
    def prepare_phase(self, connection):
        message = "Request to prepare"
        connection.sendall(message.encode())
        reply = bytes.decode(connection.recv(1024))  # Optios: Prepared/Not Prepared
        if reply == "yes":
            message = "prepared"
            connection.sendall(message.encode())
        else:
            message = "not prepared"
            connection.sendall(message.encode())


    def commit_phase(self, connection):
        message = "commit?"
        connection.sendall(message.encode())
        reply = bytes.decode(connection.recv(1024))
        if reply == "yes":
            self.update_database()
            message = "commit confirmed"
            connection.sendall(message.encode())
        else:
            message = "commit aborted"
            connection.sendall(message.encode())

    def abort_phase(self, connection):
        message = "abort confirmed"
        connection.sendall(message.encode())

    def update_database(self):
        pass

    def main(self):
        self.start_listening_socket()

if __name__ == '__main__':
    server = Server()
    server.main()
