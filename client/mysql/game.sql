CREATE TABLE IF NOT EXISTS game (
  id INT AUTO_INCREMENT PRIMARY KEY,
  game_table JSON DEFAULT '[[" ", " ", " "], [" ", " ", " "], [" ", " ", " "]]',
  winner ENUM('None', 'tic', 'tac') DEFAULT 'None'
);
