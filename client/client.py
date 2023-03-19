"""
Copyright: Essi Passoja
"""

import socket
import threading
from tkinter import *
import tictactoe
import database as db

HOST = "server"
PORT = 5000

class Client:
    def __init__(self):
        # Initialize attributes
        self.x = None
        self.o = None
        self.player = None
        self.socket = None
        self.requested_board = None
        self.game_board = [[" ", " ", " "], 
                           [" ", " ", " "], 
                           [" ", " ", " "]]
        self.update_ongoing = False

        # Initialize GUI
        self.root = Tk()
        self.root.title("Tic-tac-toe")

        # Initialize database
        self.db = db.DataBase()

        # Start listening to the server and ask for player info
        self.get_player_role()
        self.listen_server = threading.Thread(
            target=self.server_listener)
        self.listen_server.start()

    # ~~~~~~~~~~~~~~  Game GUI  ~~~~~~~~~~~~~~~~

    def create_gui(self):
        self.canvas = Canvas(self.root)
        self.canvas.pack(fill=BOTH, expand=1)
        background = PhotoImage(file="tictactoe_background.png")
        self.x = PhotoImage(file="tic.png")
        self.o = PhotoImage(file="tac.png")
        self.canvas.create_image(0, 0, anchor=NW, image=background)
        self.root.wm_geometry("656x656")
        self.canvas.bind("<Button-1>", self.handle_click)
        self.root.mainloop()
    
    def handle_click(self, event):
        x, y = tictactoe.check_click_and_return_image_coordinates(event.x, event.y)
        if x != 0 and y != 0:  # TODO add checks if the square is already marked
            location = tictactoe.coordinate_to_square_location((x, y))
            self.requested_board = self.game_board
            self.requested_board[location[0]][location[1]] = self.player
            self.send_prepare_request_to_server(location)
    
    def update_gui(self):
        # Go through all squares:
        for row, _ in enumerate(self.game_board):
            for column, _ in enumerate(self.game_board):
                x, y = tictactoe.square_location_to_coordinates((row, column))
                if self.game_board[row][column] == 'x':
                    self.canvas.create_image(x, y, anchor=NW, image=self.x)
                elif self.game_board[row][column] == 'o':
                    self.canvas.create_image(x, y, anchor=NW, image=self.o)

    # ~~~~~~~~~~~  Server communication  ~~~~~~~~~~~~~

    @staticmethod
    def connect_to_server():
        s = socket.socket()
        s.connect((HOST, PORT))
        return s
    
    def send_message_to_server(self, message, wait_response=True):
        print("Sending message '{}' to server.".format(message))
        s = self.connect_to_server()
        s.sendall(message.encode())
        if wait_response:
            response = s.recv(1024).decode()
            s.close()
            if response:
                print("Received a response from server: {}".format(response))
                return response
        s.close()
        return ""

    def get_player_role(self):
        player_role = self.send_message_to_server("Who am I?")
        self.player = player_role

    def send_prepare_request_to_server(self, location):
        self.send_message_to_server(
            "prepare {} -> {}".format(self.player, location), 
            wait_response=False)
    
    def send_commit_response_to_server(self):
        self.send_message_to_server("Committed", wait_response=False)

    def send_abort_response_to_server(self):
        self.send_message_to_server("Aborted", wait_response=False)
    
    def server_listener(self):
        self.socket = self.connect_to_server()
        while True:
            message = self.socket.recv(1024).decode()
            if message:
                print("Received a message from "
                      "server: {}".format(message))
                self.handle_message(message)
    
    def handle_message(self, message):
        if "Request to prepare" in message:
            if " {} ".format(self.player) not in message:
                self.requested_board = None 
            if "update" in message:
                self.update_ongoing = True
            # print("Requested board: {}".format(self.requested_board))
            success = self.db.start_transaction()
            if not success:
                self.send_message_to_server(
                    "Not prepared", wait_response=False)
            else:
                self.send_message_to_server(
                    "Prepared", wait_response=False)
        elif message == "Request to commit":
            if self.requested_board:
                print("Adding mark to game board")
                self.db.update_game_board(self.requested_board)
            if self.update_ongoing:
                self.game_board = self.db.get_game_board()
                print("Got game board!! {}".format(self.game_board))
                self.update_gui()
                self.update_ongoing = False
            self.db.commit_transaction()
            self.send_commit_response_to_server()
            self.requested_board = None
        elif message == "Request to abort":
            self.db.rollback_transaction()
            self.send_abort_response_to_server()
            self.requested_board = None
        elif "Refusing" in message:
            self.requested_board = None
    
    def start_tester(self):
        t = threading.Thread(target=self.tester, daemon=True)
        t. start()

    def tester(self):
        if self.player == "o":
            while True:
                self.send_prepare_request_to_server((0, 0))

    # ~~~~~~~~~~~~~~  Main  ~~~~~~~~~~~~~~~~
    
    def main(self):
        self.db.connect_to_database_and_check_tables()
        # self.start_tester()
        self.create_gui()


if __name__ == '__main__':
    client = Client()
    client.main()
