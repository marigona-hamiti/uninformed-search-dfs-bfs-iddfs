# Uninformed Search: DFS, BFS, IDDFS

Semester Assignment 1 – **Artificial Intelligence 2026/27 (FIEK)**.

Problems solved with uninformed search and backtracking.

| # | Problem | Algorithm | Code |
|---|---------|-----------|------|
| 1 | Social Golfers | DFS + backtracking | [social_golfers/social_golfers_dfs.py](social_golfers/social_golfers_dfs.py) |
| 2 | Sudoku Solver (Easy, Medium, Hard) | BFS + backtracking | [sudoku/sudoku_bfs.py](sudoku/sudoku_bfs.py) |
| 3 | Latin Square | IDDFS + backtracking | [latin_square/latin_square_iddfs.py](latin_square/latin_square_iddfs.py) |
| 4 | Search trees: 8-Puzzle, Missionaries & Cannibals, Rotating Workforce Scheduling | – | [search_trees/search_trees.md](search_trees/search_trees.md) |

Only Python 3 is required (no external libraries).

```bash
python latin_square/latin_square_iddfs.py 5
python sudoku/sudoku_bfs.py                              # or: sudoku_bfs.py easy
python social_golfers/social_golfers_dfs.py              # all cases
python social_golfers/social_golfers_dfs.py 8 4 5 30     # groups players weeks time_limit_seconds
```

---

## 1. Social Golfers (DFS)

**Problem.** `n = g·p` golfers play every week in `g` groups of `p` players. Two golfers may not be in the same group more than once. What is the maximum number of weeks for `g = 8, p = 4` (32 golfers)?

**Modeling.**
- Variables: the group of each golfer in each week; every week is a partition of the golfers into `g` groups of `p` members.
- Constraints: (C1) every group has exactly `p` golfers and every golfer plays once a week; (C2) every pair of golfers meets at most once.
- State: the groups assigned so far. Action: add a new group. Goal: `w` weeks scheduled.

**Objective function.** `f = Σ over pairs {a,b} of max(0, meetings(a,b) − 1)`, i.e. the number of repeated meetings; the goal is `f = 0`. Backtracking never extends a state with `f > 0`.

**Search space.** Partitions of `n` golfers into `g` groups of `p`: `n! / ((p!)^g · g!)`. For `g=8, p=4` this is ≈ 1.1·10²⁴ per week, so ≈ (1.1·10²⁴)^w schedules for `w` weeks.

**Symmetry breaking.** Week 1 is fixed (`{0..3}, {4..7}, ...`), and every group starts with the smallest golfer not yet placed, with members added in increasing order. This removes equivalent branches and keeps the DFS complete.

**DFS.** Depth = (week, group, member). A candidate that has already met a member of the group is pruned immediately.

**Results (measured).**

| Case | Result |
|------|--------|
| 9 golfers (3×3), 4 weeks | solved (37 nodes); 5 weeks: DFS exhausts the space, **no solution exists** |
| 16 golfers (4×4), 5 weeks | solved (80 nodes) |
| 15 golfers (5×3, Kirkman), 7 weeks | **not found** within 30 s (16 M nodes); deepest reached: 6 weeks (7 weeks exist) |
| 32 golfers (8×4), 5 weeks | solved immediately (160 nodes) |
| 32 golfers (8×4), 6–10 weeks, fixed order | **not found** within 40 s (8–20 M nodes); deepest reached: 5 weeks |
| 32 golfers (8×4), 7 weeks, random order + restarts (`run_restarts`) | solved in the first restart, ~0.2 s |
| 32 golfers (8×4), 8 weeks, random order + restarts | **not found** in 60 s (~100 restarts of 200 000 nodes) |

**Observation.** DFS with a fixed order reaches 5 weeks for 32 golfers and then gets stuck: it backtracks through the last weeks without changing weeks 2–3, which are what make the problem unsolvable. When candidates are tried in random order and the search restarts after a node budget, 7 weeks are reached. The algorithm is still DFS + backtracking; only the order of trial changes. The best known value in the literature is **10 weeks**, reached with algebraic constructions or local search / metaheuristics (topics 5–6 of the course), not with blind DFS. This is the main limitation of DFS in very large search spaces.

**General case `n = g × p`, `w` weeks.** Upper bound: a golfer meets `w·(p−1)` others, so `w ≤ (n−1)/(p−1)`. For 32 golfers with `p=4`: `w ≤ 31/3`, so `w ≤ 10`. For 9 golfers with `p=3`: `w ≤ 4`, which matches the DFS result.

---

## 2. Sudoku (BFS)

**Modeling.** 81 variables (the cells), domain `{1..9}`, constraints: different values in every row, column and 3×3 box. State: a partial board; action: an empty cell receives a legal value; goal: no empty cells.

**Objective function.** `f = number of empty cells` (goal 0), with the hard constraint that no row/column/box contains a duplicate. Illegal values are never placed (backtracking).

**Search space.** `9^e`, where `e` is the number of empty cells.

**BFS.** A FIFO queue holds all partial boards of the current level; a whole level is expanded before going deeper. The expanded cell is the one with the fewest legal values (MRV); if a cell has no legal value the node is dropped (backtracking).

| Level | Empty cells | Space `9^e` | Nodes expanded | Max queue size | Time |
|-------|-------------|-------------|----------------|----------------|------|
| Easy | 51 | 4.6·10⁴⁸ | 52 | 1 | ~0.001 s |
| Medium | 45 | 8.7·10⁴² | 46 | 1 | <0.001 s |
| Hard | 53 | 3.8·10⁵⁰ | 206 | 9 | ~0.003 s |

Extra stress-test puzzles (`very_hard`, `escargot`; known to be hard for brute force):

| Level | Empty cells | Nodes expanded | Max queue size | Time |
|-------|-------------|----------------|----------------|------|
| very_hard | 64 | 3 723 | 150 | ~0.09 s |
| escargot | 58 | 2 425 | 96 | ~0.03 s |

All solutions are verified automatically (`is_valid_solution`).

**Effect of MRV (measured, `solve_bfs(puzzle, use_mrv=False)` expands the first empty cell instead, node limit 300 000).**

| Level | Nodes with MRV | Max queue with MRV | Nodes without MRV | Max queue without MRV |
|-------|----------------|--------------------|-------------------|-----------------------|
| easy | 52 | 1 | 4 632 | 738 |
| medium | 46 | 1 | 69 | 5 |
| hard | 206 | 9 | 22 919 | 3 616 |
| very_hard | 3 723 | 150 | not solved (limit reached) | 137 964 |
| escargot | 2 425 | 96 | 18 885 | 1 716 |

Without MRV BFS expands up to ~100× more nodes and the queue grows to thousands (and on `very_hard` to over 100 000 boards before the limit stops it), which is the memory weakness of BFS. With MRV the queue stays small, so BFS has no memory problem on these puzzles.

## Running the tests and the demo

```bash
python run_all.py                        # runs all three solvers (quick demo)
python -m unittest discover -s tests -v  # 13 unit tests
```

---

## 3. Latin Square (IDDFS)

**Modeling.** `n×n` cells, domain `{1..n}`, constraints: the values in every row and column are different. Cells are filled row by row; depth = number of filled cells.

**Objective function.** `f = duplicates in rows + duplicates in columns`; goal `f = 0`.

**Search space.** `n^(n²)` grids (5²⁵ ≈ 3·10¹⁷ for `n=5`); only 161 280 of them are valid Latin squares for `n=5`.

**IDDFS.** DFS with depth limit 1, 2, 3, … up to `n²`. The solution is at depth `n²`, so the last iteration finds it.

Result for `n = 5` (measured): iterations with a limit < 25 exhaust the space without a solution; with limit 25 the solution is found after 38 nodes. In total 13 505 922 nodes, ~7.5 s.

```
1 2 3 4 5
2 1 4 5 3
3 4 5 1 2
4 5 2 3 1
5 3 1 2 4
```

---

## 4. Algorithm comparison

With `b` = branching factor, `d` = solution depth, `m` = maximum depth.

| Algorithm | Complete | Optimal | Time | Memory |
|-----------|----------|---------|------|--------|
| DFS | no (in infinite trees) | no | O(b^m) | **O(b·m)** |
| BFS | yes | yes (unit cost) | O(b^d) | O(b^d) |
| IDDFS | yes | yes (unit cost) | O(b^d) | **O(b·d)** |

- **DFS**: small memory; suits problems whose solution depth is known (Social Golfers), but can get lost in bad branches.
- **BFS**: finds the shallowest solution but needs a lot of memory; works for Sudoku because MRV keeps the queue small.
- **IDDFS**: the memory of DFS with the completeness of BFS; the cost is re-visiting the upper levels (about 13.5 M nodes in total for the Latin Square).

## 5. Search trees

See [search_trees/search_trees.md](search_trees/search_trees.md): 8-Puzzle, Missionaries & Cannibals and Rotating Workforce Scheduling.
