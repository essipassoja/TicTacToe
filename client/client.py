"""
Copyright: Essi Passoja
"""

import socket
import mysql.connector
from mysql.connector import Error
from tkinter import *

class Client:
    def __init__(self):
        self.db = None
        self.cursor = None
        self.photo = None
        self.player = None
        self.root = Tk()
        self.root.title("Tic-tac-toe")
        self.socket = socket.socket()
        self.transaction_in_progress = False

    ####################  MySQL  #######################

    def check_that_game_table_exists(self):
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

    #####################  Game GUI  #######################

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
        canvas = event.widget
        x, y = self.check_click_and_return_image_coordinates(event.x, event.y)
        if x != 0 and y != 0:
            if not self.transaction_in_progress:
                self.start_transaction()
            self.send_prepare_command_to_server(x, y)
            response = self.socket.recv(1024).decode()
            if response == "yes":
                self.send_commit_command_to_server()
                canvas.create_image(x, y, anchor=NW, image=self.photo)
                self.commit_transaction()
                self.transaction_in_progress = False
            elif response == "no":
                self.send_abort_command_to_server()
                self.rollback_transaction()
                self.transaction_in_progress = False

    @staticmethod
    def check_click_and_return_image_coordinates(x, y):
        if 63 < x < 226 and 135 < y < 275:
            return 65, 135
        elif 249 < x < 426 and 140 < y < 270:
            return 270, 136
        elif 450 < x < 630 and 141 < y < 280:
            return 470, 134
        elif 58 < x < 218 and 305 < y < 435:
            return 65, 310
        elif 240 < x < 444 and 296 < y < 440:
            return 270, 309
        elif 462 < x < 618 and 300 < y < 445:
            return 470, 311
        elif 61 < x < 215 and 463 < y < 595:
            return 65, 475
        elif 241 < x < 442 and 471 < y < 593:
            return 270, 475
        elif 466 < x < 617 and 467 < y < 587:
            return 470, 475
        else:
            return 0, 0
    
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
    
    #############  Server communication  #################
    
    def connect_to_server(self):
        port = 5000
        self.socket.connect(("server", port))
    
    def get_player_information(self):
        self.send_command_to_server("Who am I?")
    
    def send_command_to_server(self, command):
        self.socket.sendall(command.encode())
        response = self.socket.recv(1024).decode()
        print("Response from server: {}".format(response))

    def send_prepare_command_to_server(self, x, y):
        self.send_command_to_server("prepare -> {}, {}".format(x, y))
    
    def start_transaction(self):
        self.db.start_transaction()
    
    def send_commit_command_to_server(self):
        self.send_command_to_server("commit")
    
    def commit_transaction(self):
        self.db.commit()

    def send_abort_command_to_server(self):
        self.send_command_to_server("abort")
    
    def rollback_transaction(self):
        self.db.rollback()

    ####################  Main  #####################
    
    def main(self):
        self.connect_to_server()
        self.get_player_information()
        self.check_that_game_table_exists()
        self.create_gui()

if __name__ == '__main__':
    client = Client()
    client.main()
