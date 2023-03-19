FROM python:3.9

# Set the display environment variable
ENV DISPLAY=172.19.160.1:0.0

# Set up working directory
WORKDIR /TicTacToe/client

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000
EXPOSE 3306

# Copy project files
COPY client.py .
COPY tictactoe.py .
COPY /mysql/database.py .
COPY /mysql/game.sql .
COPY /graphics/tictactoe_background.png .
COPY /graphics/tic.png .
COPY /graphics/tac.png .

# Set default command
CMD ["python", "client.py"]