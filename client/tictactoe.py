import re

def parse_requested_move(requested_move):
    location_regex = re.compile(r".*?(x|o).*?(\d), ?(\d).*")
    match = location_regex.match(requested_move)
    return match.group(1), int(match.group(2)), int(match.group(3))

def check_if_move_can_be_made(game_board, requested_move):
    _, row, column = parse_requested_move(requested_move)
    if game_board[row][column] == " ":
        return True
    return False

def add_move_to_game_board(game_board, requested_move):
    player, row, column = parse_requested_move(requested_move)
    game_board[row][column] = player
    print(game_board)
    player_won = check_win(game_board)
    print("Player won: {}".format(player_won))
    return game_board, player_won

def check_win(game_board):
    print("Checking win")
    for i, _ in enumerate(game_board):
        if ((game_board[i][0]
                == game_board[i][1]
                == game_board[i][2])
                and game_board[i][0] != " "):
            return True
        elif ((game_board[0][i]
                == game_board[1][i]
                == game_board[2][i])
                and game_board[0][i] != " "):
            return True
    if ((game_board[0][0]
            == game_board[1][1]
            == game_board[2][2])
            and game_board[0][0] != " "):
        return True
    if ((game_board[0][2]
            == game_board[1][1]
            == game_board[2][0]) 
            and game_board[0][2] != " "):
        return True
    return False

def coordinate_to_square_location(coordinates):
    if coordinates == (65, 135):
        return 0, 0
    elif coordinates == (270, 136):
        return 0, 1
    elif coordinates == (470, 134):
        return 0, 2
    elif coordinates == (65, 310):
        return 1, 0
    elif coordinates == (270, 309):
        return 1, 1
    elif coordinates == (470, 311):
        return 1, 2
    elif coordinates == (65, 475):
        return 2, 0
    elif coordinates == (270, 475):
        return 2, 1
    elif coordinates == (470, 475):
        return 2, 2

def square_location_to_coordinates(location):
    if location == (0, 0):
        return 65, 135
    elif location == (0, 1):
        return 270, 136
    elif location == (0, 2):
        return 470, 134
    elif location == (1, 0):
        return 65, 310
    elif location == (1, 1):
        return 270, 309
    elif location == (1, 2):
        return 470, 311
    elif location == (2, 0):
        return 65, 475
    elif location == (2, 1):
        return 270, 475
    elif location == (2, 2):
        return 470, 475

def check_click_and_return_image_coordinates(x, y):
    if 63 < x < 226 and 135 < y < 275:  # Square (1, 1)
        return 65, 135
    elif 249 < x < 426 and 140 < y < 270:  # Square (1, 2)
        return 270, 136
    elif 450 < x < 630 and 141 < y < 280:  # Square (1, 3)
        return 470, 134
    elif 58 < x < 218 and 305 < y < 435:  # Square (2, 1)
        return 65, 310
    elif 240 < x < 444 and 296 < y < 440:  # Square (2, 2)
        return 270, 309
    elif 462 < x < 618 and 300 < y < 445:  # Square (2, 3)
        return 470, 311
    elif 61 < x < 215 and 463 < y < 595:  # Square (3, 1)
        return 65, 475
    elif 241 < x < 442 and 471 < y < 593:  # Square (3, 2)
        return 270, 475
    elif 466 < x < 617 and 467 < y < 587:  # Square (3, 3)
        return 470, 475
    else:
        return 0, 0  # Outside the square grid
