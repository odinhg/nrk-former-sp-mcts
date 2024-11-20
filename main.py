from multiprocessing import Pool 
from functools import partial

from mcts import MCTS
from board import read_board_from_file, print_board

# Parameters
n_processes = 32 
board_file = "board.txt"
time_limit = 10 

# MCTS parameters
selection_threshold = 10
C = 10.0
D = 1.0

def run_mcts(seed, board, selection_threshold, C, D):
    mcts = MCTS(board, seed, selection_threshold, C, D)
    return mcts.search(time_limit)

board = read_board_from_file(board_file)
solutions = []

func = partial(run_mcts, board=board, selection_threshold=selection_threshold, C=C, D=D)
with Pool(n_processes) as p:
    seeds = list(range(n_processes))
    solutions += p.map(func, seeds)

best_solution = []
for solution in solutions:
    if len(solution) == 0:
        continue
    if len(solution) < len(best_solution) or len(best_solution) == 0:
        best_solution = solution

print(f"Best solution: {best_solution}")
print(f"Number of moves: {len(best_solution)}")

