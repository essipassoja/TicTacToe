To run the game you need to have a MySQL server on called TicTacToe and Docker installed.

Run the commands:

docker run --name TicTacToe -e MYSQL_ROOT_PASSWORD=root -d mysql:latest

docker build -t tictactoe .

docker run -p 8000:8000 tictactoe
