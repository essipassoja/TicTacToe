"""
Copyright: Essi Passoja
"""

import socket
import threading
from tkinter import *
import mysql.connector

HOST = "server"
PORT = 5000

class Client:
    def __init__(self):
        # Initialize attributes
        self.cursor = None
        self.db = None
        self.photo = None
        self.player = None
        self.socket = None

        # Initialize GUI
        self.root = Tk()
        self.root.title("Tic-tac-toe")

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
        self.photo = (PhotoImage(file="tic.png") if self.player == "tic" 
                      else PhotoImage(file="tac.png"))
        canvas.create_image(0, 0, anchor=NW, image=background)
        self.root.wm_geometry("656x656")
        canvas.bind("<Button-1>", self.handle_click)
        self.root.mainloop()
    
    def handle_click(self, event):
        # canvas = event.widget
        x, y = self.check_click_and_return_image_coordinates(event.x, event.y)
        if x != 0 and y != 0:
            location = self.coordinate_to_square_location((x, y))
            self.send_prepare_command_to_server(location)
            # TODO: canvas.create_image(x, y, anchor=NW, image=self.photo)

    @staticmethod
    def check_click_and_return_image_coordinates(x, y):
        if 63 < x < 226 and 135 < y < 275:  # Square (1, 1)
            return 65, 135
        elif 249 < x < 426 and 140 < y < 270:  # Square (1, 2)
            return 270, 136
        elif 450 < x < 630 and 141 < y < 280:  # Square (1, 3)
            return 470, 134
        elif 58 < x < 218 and 305 < y < 435:  # Square (2, 1)
            return 65, 310
        elif 240 < x < 444 and 296 < y < 440:  # Square (2, 2)
            return 270, 309
        elif 462 < x < 618 and 300 < y < 445:  # Square (2, 3)
            return 470, 311
        elif 61 < x < 215 and 463 < y < 595:  # Square (3, 1)
            return 65, 475
        elif 241 < x < 442 and 471 < y < 593:  # Square (3, 2)
            return 270, 475
        elif 466 < x < 617 and 467 < y < 587:  # Square (3, 3)
            return 470, 475
        else:
            return 0, 0  # Outside the square grid

    @staticmethod
    def coordinate_to_square_location(coordinates):
        if coordinates == (65, 135):
            return 1, 1
        elif coordinates == (270, 136):
            return 1, 2
        elif coordinates == (470, 134):
            return 1, 3
        elif coordinates == (65, 310):
            return 2, 1
        elif coordinates == (270, 309):
            return 2, 2
        elif coordinates == (470, 311):
            return 2, 3
        elif coordinates == (65, 475):
            return 3, 1
        elif coordinates == (270, 475):
            return 3, 2
        elif coordinates == (470, 475):
            return 3, 3
    
    @staticmethod
    def square_location_to_coordinates(location):
        if location == (1, 1):
            return 65, 135
        elif location == (1, 2):
            return 270, 136
        elif location == (1, 3):
            return 470, 134
        elif location == (2, 1):
            return 65, 310
        elif location == (2, 2):
            return 270, 309
        elif location == (2, 3):
            return 470, 311
        elif location == (3, 1):
            return 65, 475
        elif location == (3, 2):
            return 270, 475
        elif location == (3, 3):
            return 470, 475
    
    # ~~~~~~~~~~~  Server communication  ~~~~~~~~~~~~~

    @staticmethod
    def connect_to_server():
        s = socket.socket()
        s.connect((HOST, PORT))
        return s
    
    def send_message_to_server(self, command):
        print("Sending command '{}' to server.".format(command))
        s = self.connect_to_server()
        s.sendall(command.encode())
        response = s.recv(1024).decode()
        s.close()
        if response:
            print("Received a response from server: {}".format(response))
            return response
        return ""

    def get_player_role(self):
        player_role = self.send_message_to_server("Who am I?")
        self.player = player_role

    def send_prepare_command_to_server(self, location):
        self.send_message_to_server(
            "prepare {} -> {}".format(self.player, location))
    
    def send_commit_command_to_server(self):
        self.send_message_to_server("commit")

    def send_abort_command_to_server(self):
        self.send_message_to_server("abort")
    
    def server_listener(self):
        self.socket = self.connect_to_server()
        while True:
            message = self.socket.recv(1024).decode()
            if message:
                print("Received a message from server: {}".format(message))
                self.handle_message(message)
    
    def handle_message(self, message):
        if message == "Request to prepare":
            # TODO: When is this no?
            self.send_message_to_server("yes")
        elif message == "prepared":
            self.send_commit_command_to_server()

    # ~~~~~~~~~~~~~~  MySQL  ~~~~~~~~~~~~~~~~
    
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

    # ~~~~~~~~~~~~~~  Main  ~~~~~~~~~~~~~~~~
    
    def main(self):
        self.connect_to_database()
        self.create_gui()

if __name__ == '__main__':
    client = Client()
    client.main()
