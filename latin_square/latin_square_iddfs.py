"""Latin Square solved with Iterative Deepening DFS (IDDFS) + backtracking.

Problem
    Fill an n x n grid with the numbers 1..n so that every number appears
    exactly once in every row and in every column.

Modeling
    Variables : n*n cells, filled in row-major order (cell k = (k // n, k % n)).
    Domain    : {1, ..., n} for every cell.
    Constraints (hard): all values in a row differ, all values in a column differ.
    State     : a partial grid in which the first `depth` cells are filled.
    Action    : assign a value to the next empty cell (only values that do not
                break a constraint are tried -> backtracking).
    Goal test : depth == n*n (all cells filled, no constraint violated).

Objective function
    f(grid) = number of constraint violations
            = (number of duplicate values in rows) + (number of duplicate values in columns)
    The goal is f = 0. Backtracking never extends a state with f > 0, so every
    visited state has f = 0 and the search stops at the first complete state.

Search space (landscape)
    Without constraints: n^(n*n) grids (5^25 ~ 3.0e17 for n = 5).
    Only valid ones: L(n) Latin squares (161 280 for n = 5, 12 for n = 3).

IDDFS
    Run a depth-limited DFS with limit 1, 2, 3, ... until the goal is found.
    The goal is at depth n*n, so the final iteration uses limit n*n.
"""

import sys
import time


class LatinSquareIDDFS:
    def __init__(self, n):
        self.n = n
        self.grid = [[0] * n for _ in range(n)]
        self.row_used = [set() for _ in range(n)]
        self.col_used = [set() for _ in range(n)]
        self.nodes = 0  # nodes visited in the current iteration

    def _dls(self, depth, limit):
        """Depth-limited DFS with backtracking. Returns True if a solution is found."""
        self.nodes += 1
        n = self.n
        if depth == n * n:
            return True
        if depth == limit:
            return False
        r, c = divmod(depth, n)
        for v in range(1, n + 1):
            if v in self.row_used[r] or v in self.col_used[c]:
                continue
            self.grid[r][c] = v
            self.row_used[r].add(v)
            self.col_used[c].add(v)
            if self._dls(depth + 1, limit):
                return True
            self.grid[r][c] = 0  # backtrack
            self.row_used[r].discard(v)
            self.col_used[c].discard(v)
        return False

    def solve(self):
        total_nodes = 0
        for limit in range(1, self.n * self.n + 1):
            self.nodes = 0
            found = self._dls(0, limit)
            total_nodes += self.nodes
            print(f"  limit={limit:>3}  nodes visited={self.nodes:>9}  solution={'yes' if found else 'no'}")
            if found:
                return self.grid, total_nodes
        return None, total_nodes


def is_latin_square(grid):
    n = len(grid)
    expected = set(range(1, n + 1))
    rows_ok = all(set(row) == expected for row in grid)
    cols_ok = all({grid[r][c] for r in range(n)} == expected for c in range(n))
    return rows_ok and cols_ok


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    print(f"Latin Square n={n} with IDDFS + backtracking")
    start = time.perf_counter()
    grid, total_nodes = LatinSquareIDDFS(n).solve()
    elapsed = time.perf_counter() - start
    if grid is None:
        print("No solution found.")
        return
    print()
    for row in grid:
        print(" ".join(f"{v:>2}" for v in row))
    print()
    print(f"valid Latin square : {is_latin_square(grid)}")
    print(f"total nodes visited: {total_nodes}")
    print(f"time               : {elapsed:.3f}s")


if __name__ == "__main__":
    main()
