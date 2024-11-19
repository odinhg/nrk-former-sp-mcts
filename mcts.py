"""
Single-Player Monte Carlo Tree Search (SP-MCTS) for the game NRK Former.

References:
    [1] Single-Player Monte-Carlo Tree Search, Schadd et al., 2008

"""

import math
import random
from time import time
from board import read_board_from_file, playout, step, is_terminal, get_blobs, print_board

# import deepcopy from copy module
from copy import deepcopy


class Node:
    def __init__(self, board, parent=None, move=None):
        self.board = [row[:] for row in board] # Copy of the board state
        self.parent = parent # Parent node
        self.move = move # (x, y) coordinates of the move that led to this node
        self.blobs = get_blobs(self.board) # List of blobs in the board (possible moves)
        self.children = [] # List of nodes that are children of this node
        self.n_visits = 0 # Number of times this node has been visited
        self.average_score = 0.0 # Average score of the node
        self.square_sum_score = 0.0 # Sum of the square of the scores

    def is_leaf(self):
        return len(self.children) < len(self.blobs)

class MCTS:
    def __init__(self, board, selection_threshold=100):
        self.root = Node(board)
        self.selection_threshold = selection_threshold
        self.found_solution = False

    def search(self, time_limit=30.0):
        t0 = time()
        t1 = time()
        while time() - t0 < time_limit or not self.found_solution:
            node = self.select()
            if node.is_leaf():
                node = self.expand(node)
            score = self.simulate(node)
            self.backpropagate(node, score)

            if time() - t1 > 0.5 and self.found_solution:
                print("Best solution so far:")
                self.print_solution(print_boards=False)
                t1 = time()

    def select(self):
        node = self.root
        while not node.is_leaf():
            if is_terminal(node.board):
                self.found_solution = True
                return node
            node = self.selection_strategy(node)
        return node

    def selection_strategy(self, node):
        if node.n_visits < self.selection_threshold:
            # pick a random child node 
            return random.choice(node.children)
        child_uct_values = [self.uct(node, child) for child in node.children]
        max_uct_index = max(range(len(child_uct_values)), key=child_uct_values.__getitem__)
        max_uct_child = node.children[max_uct_index]
        return max_uct_child

    #def uct(self, parent, child, C=0.5, D=1000):
    def uct(self, parent, child, C=0.01, D=10000):
        # Modified UCT formula from equation (1) in [1]
        x_bar = child.average_score
        n = parent.n_visits
        n_i = child.n_visits
        x_ss = child.square_sum_score
        uct = x_bar + C * math.sqrt(math.log(n) / n_i) + math.sqrt((x_ss - n_i * x_bar**2 + D) / n_i)
        return uct

    def simulate(self, node):
        # Random playout from the current node
        board_copy = [row[:] for row in node.board]
        n_moves = playout(board_copy)
        score = self.score(n_moves)
        return score

    def score(self, n_moves):
        # Scoring function for the playout
        score = 1000 * math.exp(-n_moves / 20) 
        return score
    
    def expand(self, node):
        blob = node.blobs[len(node.children)]
        board_copy = [row[:] for row in node.board]
        board_copy = step(board_copy, *blob)
        child = Node(board_copy, parent=node, move=blob)
        node.children.append(child)
        return child

    def backpropagate(self, node, score):
        # Update the node and its ancestor's average scores, visit counts, and square sum scores
        while node is not None:
            node.n_visits += 1
            node.average_score = (node.average_score * (node.n_visits - 1) + score) / node.n_visits
            node.square_sum_score += score**2
            node = node.parent

    def print_tree(self, node, depth=0):
        print("  " * depth, node.move, node.average_score, node.n_visits)
        for child in node.children:
            self.print_tree(child, depth + 1)

    def max_depth(self, node):
        if not node.children:
            return 0
        return 1 + max(self.max_depth(child) for child in node.children)

    def print_solution(self, print_boards=True):
        # Print the best path and the board state after each move
        moves = []
        node = self.root
        while node.children:
            if print_boards:
                print_board(node.board)
            node = max(node.children, key=lambda child: child.average_score)
            moves.append(node.move)
            if print_boards:
                print(node.move)
                print()
        print("Moves:", moves)
        print("Number of moves:", len(moves))


if __name__ == "__main__":
    board = read_board_from_file("board.txt")
    mcts = MCTS(board)
    mcts.search()
    mcts.print_solution()
