FROM python:3.9

# Set up working directory
WORKDIR /TicTacToe

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000 32000 3306

# Copy project files
COPY game.sql .
COPY server.py .
COPY client.py .
COPY tictactoe.py .

# Set default command
CMD ["python", "server.py"]