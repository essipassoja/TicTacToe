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
        self.tic = None
        self.tac = None
        self.player = None
        self.socket = None
        self.requested_move = None

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
        canvas = Canvas(self.root)
        canvas.pack(fill=BOTH, expand=1)
        background = PhotoImage(file="tictactoe_background.png")
        self.tic = PhotoImage(file="tic.png")
        self.tac = PhotoImage(file="tac.png")
        canvas.create_image(0, 0, anchor=NW, image=background)
        self.root.wm_geometry("656x656")
        canvas.bind("<Button-1>", self.handle_click)
        self.root.mainloop()
    
    def handle_click(self, event):
        # canvas = event.widget
        x, y = tictactoe.check_click_and_return_image_coordinates(event.x, event.y)
        if x != 0 and y != 0:
            location = tictactoe.coordinate_to_square_location((x, y))
            self.send_prepare_request_to_server(location)
            # TODO: canvas.create_image(x, y, anchor=NW, image=self.photo)
    
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
            self.requested_move = tuple(
                tictactoe.parse_requested_move(message))
            print("Requested move: {}".format(self.requested_move))
            success = self.db.start_transaction()
            if not success:
                self.send_message_to_server(
                    "Not prepared", wait_response=False)
            else:
                self.send_message_to_server(
                    "Prepared", wait_response=False)
        elif message == "Request to commit":
            self.db.commit_transaction()
            self.send_commit_response_to_server()
        elif message == "Request to abort":
            self.db.rollback_transaction()
            self.send_abort_response_to_server()

    # ~~~~~~~~~~~~~~  Main  ~~~~~~~~~~~~~~~~
    
    def main(self):
        self.db.connect_to_database_and_check_tables()
        self.create_gui()

if __name__ == '__main__':
    client = Client()
    client.main()
