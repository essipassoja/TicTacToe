CREATE TABLE IF NOT EXISTS game (
  id INT AUTO_INCREMENT PRIMARY KEY,
  game_table TEXT,
  game_status ENUM('Not started', 'On-going', 'Finished') DEFAULT 'Not started',
  winner ENUM('None', 'tic', 'tac') DEFAULT 'None'
);
