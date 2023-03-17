# TicTacToe

Here comes some description of the system

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