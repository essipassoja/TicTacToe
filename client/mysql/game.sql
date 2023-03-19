CREATE TABLE IF NOT EXISTS game (
  game_id INT AUTO_INCREMENT PRIMARY KEY,
  game_board TEXT,
  winner ENUM('None', 'x', 'o') DEFAULT 'None'
);
