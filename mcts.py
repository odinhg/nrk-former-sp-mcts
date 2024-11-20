"""
Single-Player Monte Carlo Tree Search (SP-MCTS) for the game NRK Former.

References:
    [1] Single-Player Monte-Carlo Tree Search, Schadd et al., 2008

"""

import math
import random
from time import time
from board import playout, step, is_terminal, get_blobs, copy_board

class Node:
    def __init__(self, board, depth, parent=None, move=None):
        self.board = [row[:] for row in board] # Copy of the board state
        self.parent = parent # Parent node
        self.move = move # (x, y) coordinates of the move that led to this node
        self.blobs = get_blobs(self.board) # List of blobs in the board (possible moves)
        self.children = [] # List of nodes that are children of this node
        self.n_visits = 0 # Number of times this node has been visited
        self.average_score = 0.0 # Average score of the node
        self.square_sum_score = 0.0 # Sum of the square of the scores
        self.depth = depth

    def is_leaf(self):
        return len(self.children) < len(self.blobs)

class MCTS:
    """
    Only use UTC for selection strategy if all children are explored
    """
    def __init__(self, board, seed=0, selection_threshold=1000, C=0.1, D=100):
        self.board = [row[:] for row in board]
        self.root = Node(board, depth=0)
        self.selection_threshold = selection_threshold
        self.C = C
        self.D = D
        self.solution_found = False
        self.best_solution = None
        self.rng = random.Random(seed)

    def search(self, time_limit=1.0):
        # Run the MCTS algorithm for a given time limit
        t0 = time()
        node = self.root
        iter_count = 0
        while time() - t0 < time_limit:# or not self.solution_found:
            node = self.select()
            if node.is_leaf():
                node = self.expand(node)
            score = self.simulate(node)
            self.backpropagate(node, score)
            iter_count += 1
        t1 = time()

        if self.best_solution is None:
            return []
        # Return the best solution found
        moves = []
        node = self.best_solution
        while node.parent is not None:
            moves.append(node.move)
            node = node.parent
        moves.reverse()
        print(f"Finished {iter_count} iterations in {t1 - t0:.2f} seconds. Found solution with {len(moves)} moves.")
        return moves

    def select(self):
        node = self.root
        while not node.is_leaf():
            if is_terminal(node.board):
                self.solution_found = True
                if self.best_solution is None or node.depth < self.best_solution.depth:
                    self.best_solution = node
                return node
            node = self.selection_strategy(node)
        return node

    def selection_strategy(self, node):
        if node.is_leaf():
            node = self.expand(node)
            return node

        if node.n_visits < self.selection_threshold:
            # pick a random child node 
            return self.rng.choice(node.children)
        child_uct_values = [self.uct(node, child) for child in node.children]
        max_uct_index = max(range(len(child_uct_values)), key=child_uct_values.__getitem__)
        max_uct_child = node.children[max_uct_index]
        return max_uct_child

    def uct(self, parent, child):
        # Modified UCT formula from equation (1) in [1]
        x_bar = child.average_score
        n = parent.n_visits
        n_i = child.n_visits
        x_ss = child.square_sum_score
        uct = x_bar + self.C * math.sqrt(math.log(n) / n_i) + math.sqrt((x_ss - n_i * x_bar**2 + self.D) / n_i)
        return uct

    def simulate(self, node):
        # Random playout from the current node
        board_copy = [row[:] for row in node.board]
        n_moves = playout(board_copy, self.rng) + node.depth
        score = self.score(n_moves)
        return score

    def score(self, n_moves):
        # Scoring function for the playout
        score = 10 * max(63 - n_moves, 0)
        return score
    
    def expand(self, node):
        blob = node.blobs[len(node.children)]
        board_copy = [row[:] for row in node.board]
        board_copy = step(board_copy, *blob)
        child = Node(board_copy, depth=node.depth + 1, parent=node, move=blob)
        node.children.append(child)
        return child

    def backpropagate(self, node, score):
        # Update the node and its ancestor's statistics 
        while node is not None:
            node.n_visits += 1
            node.average_score = (node.average_score * (node.n_visits - 1) + score) / node.n_visits
            node.square_sum_score += score**2
            node = node.parent

    def max_depth(self, node):
        # Get the maximum depth of the tree
        if not node.children:
            return 0
        return 1 + max(self.max_depth(child) for child in node.children)

