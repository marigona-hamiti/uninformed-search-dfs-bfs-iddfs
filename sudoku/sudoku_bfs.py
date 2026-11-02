"""Sudoku solver using Breadth-First Search (BFS) + backtracking.

Modeling
    Variables : the 81 cells.
    Domain    : {1..9}; given cells have a single-value domain.
    Constraints (hard): all values in a row / column / 3x3 box are different.
    State     : a partially filled 9x9 board.
    Action    : choose an empty cell and assign one of its legal values.
    Goal test : no empty cells left (constraints are never violated, because
                only legal values are placed -> backtracking prunes the rest).

Objective function
    f(board) = number of empty cells (to minimise, goal f = 0), with the
    additional hard constraint "no duplicate in any row/column/box".
    Equivalent view: f = number of constraint violations of a complete board.

Search space (landscape)
    Without constraints: 9^e boards, where e = number of empty cells
    (for e = 55 that is ~ 1.3e52). Constraint checking prunes it drastically.

BFS
    A FIFO queue holds all partial boards of the current depth; depth d means
    d cells have been filled. Expanding the whole level before going deeper
    guarantees the shallowest solution (all solutions of a valid puzzle lie at
    the same depth = number of empty cells). The price is memory: the queue
    can hold a whole level of the tree.
    To keep the queue small the expanded cell is always the empty cell with the
    fewest legal values (minimum remaining values), and cells with a single
    legal value are filled in place without creating new nodes.
"""

import sys
import time
from collections import deque

PUZZLES = {
    "easy": (
        "530070000"
        "600195000"
        "098000060"
        "800060003"
        "400803001"
        "700020006"
        "060000280"
        "000419005"
        "000080079"
    ),
    "medium": (
        "000260701"
        "680070090"
        "190004500"
        "820100040"
        "004602900"
        "050003028"
        "009300074"
        "040050036"
        "703018000"
    ),
    "hard": (
        "000000907"
        "000420180"
        "000705026"
        "100904000"
        "050000040"
        "000507009"
        "920108000"
        "034059000"
        "507000000"
    ),
    # extra stress tests (known to be hard for brute force)
    "very_hard": (
        "400000805"
        "030000000"
        "000700000"
        "020000060"
        "000080400"
        "000010000"
        "000603070"
        "500200000"
        "104000000"
    ),
    "escargot": (
        "100007090"
        "030020008"
        "009600500"
        "005300900"
        "010080002"
        "600004000"
        "300000010"
        "040000007"
        "007000300"
    ),
}


def candidates(board, r, c):
    """Legal values for the empty cell (r, c)."""
    used = set(board[r * 9 : r * 9 + 9])
    used.update(board[c::9])
    br, bc = r - r % 3, c - c % 3
    for i in range(br, br + 3):
        used.update(board[i * 9 + bc : i * 9 + bc + 3])
    return [v for v in range(1, 10) if v not in used]


def most_constrained_cell(board):
    """Return (index, candidates) of the empty cell with fewest legal values,
    or (None, None) if the board is full."""
    best_idx, best_cands = None, None
    for idx, v in enumerate(board):
        if v:
            continue
        cands = candidates(board, idx // 9, idx % 9)
        if best_cands is None or len(cands) < len(best_cands):
            best_idx, best_cands = idx, cands
            if len(cands) <= 1:
                break
    return best_idx, best_cands


def is_valid_solution(board):
    full = set(range(1, 10))
    rows = all(set(board[r * 9 : r * 9 + 9]) == full for r in range(9))
    cols = all(set(board[c::9]) == full for c in range(9))
    boxes = all(
        {board[(br + i) * 9 + bc + j] for i in range(3) for j in range(3)} == full
        for br in (0, 3, 6)
        for bc in (0, 3, 6)
    )
    return rows and cols and boxes


def first_empty_cell(board):
    """Return (index, candidates) of the first empty cell (no MRV heuristic)."""
    for idx, v in enumerate(board):
        if not v:
            return idx, candidates(board, idx // 9, idx % 9)
    return None, None


def solve_bfs(puzzle, max_nodes=5_000_000, use_mrv=True):
    """BFS over partial boards. Returns (solution or None, stats dict).

    use_mrv=False expands the first empty cell instead of the most constrained
    one, which makes the BFS queue grow much faster (see the README)."""
    choose_cell = most_constrained_cell if use_mrv else first_empty_cell
    start = [int(ch) for ch in puzzle]
    queue = deque([start])
    nodes = 0
    max_queue = 1
    while queue:
        board = queue.popleft()
        nodes += 1
        if nodes > max_nodes:
            return None, {"nodes": nodes, "max_queue": max_queue, "aborted": True}
        idx, cands = choose_cell(board)
        if idx is None:  # goal: board is complete
            return board, {"nodes": nodes, "max_queue": max_queue, "aborted": False}
        for v in cands:  # empty list -> dead end -> backtrack (node is dropped)
            child = board.copy()
            child[idx] = v
            queue.append(child)
        max_queue = max(max_queue, len(queue))
    return None, {"nodes": nodes, "max_queue": max_queue, "aborted": False}


def print_board(board):
    for r in range(9):
        if r and r % 3 == 0:
            print("------+-------+------")
        row = board[r * 9 : r * 9 + 9]
        print(" ".join(
            ("." if v == 0 else str(v)) + (" |" if c in (2, 5) else "")
            for c, v in enumerate(row)
        ))


def main():
    levels = sys.argv[1:] or list(PUZZLES)
    for level in levels:
        puzzle = PUZZLES[level]
        empty = puzzle.count("0")
        print(f"=== {level.upper()}  ({empty} empty cells, search space 9^{empty} ~ {9**empty:.2e}) ===")
        print_board([int(ch) for ch in puzzle])
        start = time.perf_counter()
        solution, stats = solve_bfs(puzzle)
        elapsed = time.perf_counter() - start
        print()
        if solution is None:
            print("No solution found" + (" (node limit reached)" if stats["aborted"] else ""))
        else:
            print_board(solution)
            print(f"\nvalid solution : {is_valid_solution(solution)}")
        print(f"nodes expanded : {stats['nodes']}")
        print(f"max queue size : {stats['max_queue']}")
        print(f"time           : {elapsed:.3f}s\n")


if __name__ == "__main__":
    main()
