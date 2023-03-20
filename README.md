# TicTacToe

The game implements the two-phase commit -protocol. While initiating, the server starts listening to the socket and once prompted by clients, 
it gives them their mark, 'x' or 'o'. Once both players have prompted for their mark, the game can start.

Server is continuously listening to the socket, and it has a self.current_player attribute, which determines whether or not the
prompting client can make a move. If the current player requests to make a move, the 2PC -protocol is initiated. If both clients are
able to start the database transaction successfully, the current_player -client can save the new game_board to the database.

After both clients have sent the Commit -confirmation, the server/controller initiates the update game table -request, to update
the GUIs for both players. Once the update is done, the server again starts listening to the game move requests.

The game logic is not fully finished and the game does not end when one player wins. It is also possible to overwrite a made move,
but only after the move was successfully made during 2PC. The protocol itself works, but the game itself is not fully finished.
However, the goal of the course work is reached since the implementing and testing of the 2PC are done.

## How to run the game

You need to have MySQL and Docker installed.

Then run the commands:

*Create a user-defined network for container communication:*
> docker network create --subnet 172.168.1.0/24 tictactoe-network

*Add MySQL database to the network:*
> docker run -d --network tictactoe-network --network-alias mysql -v tictactoe-mysql-data:/var/lib/mysql -e MYSQL_ROOT_PASSWORD=root -e MYSQL_DATABASE=tictactoe_db mysql:latest

*Make the server and client -images:*
> docker build -t tictactoe-server ./server
> docker build -t tictactoe-client ./client

*Start the server container called **server** and add it to the network:*
> docker run -it --network tictactoe-network --name server tictactoe-server

**Open a new cmd:**

*Start the client container called **client1** and add it to the network:*
> docker run -it --network tictactoe-network --name client1 tictactoe-client

**Open a new cmd:**

*Start the client container called **client2** and add it to the network:*
> docker run -it --network tictactoe-network --name client2 tictactoe-client

## Testing the system with high payload:

The server is measuring the traffic and printing the output.
If you want to test with high payload, remove the commenting
from client.py, row 164.