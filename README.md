# Using Monte-Carlo Tree Search to Solve NRK's Former

This repository contains the code for solving [NRK's "Former"](https://www.nrk.no/former-1.17105310) puzzle game using a Monte-Carlo Tree Search (MCTS) algorithm. 

The game is a 2D grid-based puzzle game where the goal is to remove all the blocks using as few moves as possible. The game is played on a 9x7 grid where each cell can contain a block of one of the four colors: pink, green, blue, and orange. When a block is clicked, all blocks of the same color that are connected are also removed. The game is won when all blocks are removed.

The algorithm is based on the paper "Single-Player Monte-Carlo Tree Search" by Schadd et al. (2008). The algorithm is used to find the best move to make in a game by simulating possible future moves and selecting the move that leads to the best outcome based on random simulations/playouts.

The board is loaded from the file `board.txt` which contains the initial state of the board. The board is a 9x7 grid where each cell contains a block of one of the four colors. The colors are represented by the following characters: pink [P], green [G], blue [B], and orange [O].

To find the best solution, run `python main.py`. The algorithm will find the best move to make and print the sequence of moves to solve the game. Feel free to play around with the hyper-parameters in `main.py` to see how they affect the performance of the algorithm. In particular, the constants `C` and `D` are used in the UCT (Upper Confidence Bound for Trees) formula to balance exploration and exploitation.

The environment/game is implemented in `board.py` and the MCTS algorithm is implemented in `mcts.py`.
