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

def is_within_bounds(board, x, y):
    return 0 <= y < len(board) and 0 <= x < len(board[0])

def print_board(board):
    for row in board:
        for block in row:
            print(colored(BLOCK_CHAR, COLORS[block]), end="")
        print()
    print()

def generate_random_board(width, height):
    return [random.choices(SYMBOLS, k=width) for _ in range(height)]

def is_empty(board, x, y):
    return board[y][x] == EMPTY

def is_terminal(board):
    # Only need to check bottom row because gravity
    for block in board[-1]:
        if block != EMPTY:
            return False
    return True

def get_non_empty_blocks(board):
    return [(x, y) for y in range(len(board)) for x in range(len(board[0])) if board[y][x] != EMPTY]

def dfs(board, x, y, target_color):
    if not is_within_bounds(board, x, y) or board[y][x] != target_color:
        return []
    board[y][x] = EMPTY
    return [(x, y)] + dfs(board, x + 1, y, target_color) + dfs(board, x - 1, y, target_color) + dfs(board, x, y + 1, target_color) + dfs(board, x, y - 1, target_color)

def destroy_blocks(board, x, y):
    target_color = board[y][x]
    for x, y in dfs(board, x, y, target_color):
        board[y][x] = EMPTY
    return board

def get_connected_blocks(board, x, y):
    target_color = board[y][x]
    return dfs(board, x, y, target_color)

def get_blobs(board):
    # Return a list of coordinates for each blob
    blobs = []
    visited = set()
    board_copy = [row[:] for row in board] # Faster than deepcop
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
    # Apply gravity
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
    if is_empty(board, x, y):
        return board

    board = destroy_blocks(board, x, y)
    board = move_blocks_down(board)
    return board

def playout(board):
    n_moves = 0
    while not is_terminal(board):
        x, y = random.choice(get_non_empty_blocks(board))
        board = step(board, x, y)
        n_moves += 1
    return n_moves

if __name__ == "__main__":
    from time import time
    from tqdm import tqdm
    times = []
    moves_per_game = []
    original_board = read_board_from_file("board.txt")
    original_board = step(original_board, 1, 1)
    original_board = step(original_board, 2, 2)
    for _ in tqdm(range(1000)):
        board = [row[:] for row in original_board]
        t0 = time()
        n_moves = playout(board)
        t1 = time()
        times.append(t1 - t0)
        moves_per_game.append(n_moves)
    print(f"Average time: {1000 * sum(times) / len(times):.2f} ms")
    print(f"Min moves: {min(moves_per_game)}")
    print(f"Average moves: {sum(moves_per_game) / len(moves_per_game):.2f}")
    print(f"Max moves: {max(moves_per_game)}")
        
