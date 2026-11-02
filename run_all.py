"""Run all three solvers one after another (quick demo, about 15 seconds).

    python run_all.py
"""

import os
import sys
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
for folder in ("latin_square", "sudoku", "social_golfers"):
    sys.path.insert(0, os.path.join(ROOT, folder))

import latin_square_iddfs  # noqa: E402
import social_golfers_dfs  # noqa: E402
import sudoku_bfs  # noqa: E402


def section(title):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def main():
    start = time.perf_counter()

    section("1. Latin Square (IDDFS), n = 4")
    grid, nodes = latin_square_iddfs.LatinSquareIDDFS(4).solve()
    for row in grid:
        print(" ".join(f"{v:>2}" for v in row))
    print(f"valid: {latin_square_iddfs.is_latin_square(grid)}, nodes: {nodes}")

    section("2. Sudoku (BFS): easy, medium, hard")
    for level in ("easy", "medium", "hard"):
        solution, stats = sudoku_bfs.solve_bfs(sudoku_bfs.PUZZLES[level])
        print(f"{level:<7} valid={sudoku_bfs.is_valid_solution(solution)}  "
              f"nodes={stats['nodes']}  max_queue={stats['max_queue']}")

    section("3. Social Golfers (DFS): 9 and 16 golfers, 32 golfers with restarts")
    social_golfers_dfs.run(3, 3, 4)
    social_golfers_dfs.run(4, 4, 5)
    social_golfers_dfs.run_restarts(8, 4, 7, time_limit=20)

    print(f"Total time: {time.perf_counter() - start:.1f}s")


if __name__ == "__main__":
    main()
