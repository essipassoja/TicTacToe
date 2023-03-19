CREATE TABLE IF NOT EXISTS game (
  id INT AUTO_INCREMENT PRIMARY KEY,
  game_table TEXT,
  winner ENUM('None', 'tic', 'tac') DEFAULT 'None'
);
