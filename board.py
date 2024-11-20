import random
from termcolor import colored

# Constants
SYMBOLS = ["B", "G", "P", "O"]
EMPTY = " "
SYMBOL_TO_INDEX = {symbol: i for i, symbol in enumerate([EMPTY] + SYMBOLS)}
COLORS = {
    "B": "blue", 
    "G": "green",
    "P": "magenta",
    "O": "yellow",
    " ": "black"
} 
BLOCK_CHAR = "■ "
CURSOR_CHAR = "▲ "

def is_within_bounds(board, x, y):
    return 0 <= y < len(board) and 0 <= x < len(board[0])

def print_board(board, x, y):
    # Print the board with a cursor at position (x, y)
    for i, row in enumerate(board):
        for j, block in enumerate(row):
            if i == y and j == x:
                print(colored(CURSOR_CHAR, "red"), end="")
            else:
                print(colored(BLOCK_CHAR, COLORS[block]), end="")
        print()

def print_game(board, moves):
    # Print the board with a sequence of moves
    for x, y in moves:
        board = step(board, x, y)
        print_board(board, x, y)
        print()

def generate_random_board(width, height):
    return [random.choices(SYMBOLS, k=width) for _ in range(height)]

def is_empty(board, x, y):
    return board[y][x] == EMPTY

def is_terminal(board):
    # Check if board is empty. Only need to check bottom row because gravity
    for block in board[-1]:
        if block != EMPTY:
            return False
    return True

def get_non_empty_blocks(board):
    # Return a list of coordinates for non-empty blocks
    return [(x, y) for y in range(len(board)) for x in range(len(board[0])) if board[y][x] != EMPTY]

def dfs(board, x, y, target_color):
    # Depth-first search to find connected blocks of the same color
    if not is_within_bounds(board, x, y) or board[y][x] != target_color:
        return []
    board[y][x] = EMPTY
    return [(x, y)] + dfs(board, x + 1, y, target_color) + dfs(board, x - 1, y, target_color) + dfs(board, x, y + 1, target_color) + dfs(board, x, y - 1, target_color)

def destroy_blocks(board, x, y):
    # Destroy a block and all connected blocks of the same color
    target_color = board[y][x]
    for x, y in dfs(board, x, y, target_color):
        board[y][x] = EMPTY
    return board

def get_connected_blocks(board, x, y):
    # Return a list of connected blocks starting from (x, y)
    target_color = board[y][x]
    return dfs(board, x, y, target_color)

def get_blobs(board):
    # Return a list of coordinates for each blob
    blobs = []
    visited = set()
    board_copy = copy_board(board)
    for y in range(len(board)):
        for x in range(len(board[0])):
            if (x, y) in visited or board_copy[y][x] == EMPTY:
                continue
            blob = get_connected_blocks(board_copy, x, y)
            visited.update(blob)
            x, y = blob[0]
            blobs.append((x, y)) 
    return blobs

def move_blocks_down(board):
    # Apply gravity to board
    for j in range(len(board[0])):
        new_column = [block for block in [row[j] for row in board] if block != EMPTY]
        new_column = [EMPTY] * (len(board) - len(new_column)) + new_column
        for i, block in enumerate(new_column):
            board[i][j] = block
    return board

def read_board_from_file(filename):
    with open(filename, "r") as f:
        board = [list(line.strip()) for line in f]
    if not all(all(block in SYMBOLS for block in row) for row in board):
        raise ValueError("Invalid board file: contains invalid symbols")
    if not all(len(row) == len(board[0]) for row in board):
        raise ValueError("Invalid board file: rows have different lengths")
    return board

def step(board, x, y):
    # Simulate a click on the board at position (x, y)
    if is_empty(board, x, y):
        return board
    board = destroy_blocks(board, x, y)
    board = move_blocks_down(board)
    return board

def playout(board):
    # Play a random game until the board is empty
    n_moves = 0
    while not is_terminal(board):
        x, y = random.choice(get_non_empty_blocks(board))
        board = step(board, x, y)
        n_moves += 1
    return n_moves

def copy_board(board):
    # Return a deep copy of the board (faster than deepcopy)
    return [row[:] for row in board]

