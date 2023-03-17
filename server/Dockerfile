FROM python:3.9

# Set the display environment variable
ENV DISPLAY=172.19.160.1:0.0

# Set up working directory
WORKDIR /TicTacToe/server

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000
EXPOSE 3306

# Copy project files
COPY server.py .

# Set default command
CMD ["python", "server.py"]