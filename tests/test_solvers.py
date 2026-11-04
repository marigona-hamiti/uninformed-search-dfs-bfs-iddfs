"""Unit tests for the three solvers.

    python -m unittest discover -s tests -v
"""

import os
import random
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for folder in ("latin_square", "sudoku", "social_golfers"):
    sys.path.insert(0, os.path.join(ROOT, folder))

import latin_square_iddfs as ls  # noqa: E402
import social_golfers_dfs as sg  # noqa: E402
import sudoku_bfs as sd  # noqa: E402


class LatinSquareTests(unittest.TestCase):
    def test_solutions_are_valid_for_small_n(self):
        for n in (1, 2, 3, 4):
            grid, _ = ls.LatinSquareIDDFS(n).solve()
            self.assertTrue(ls.is_latin_square(grid), f"n={n}")

    def test_checker_rejects_duplicate_in_row(self):
        self.assertFalse(ls.is_latin_square([[1, 1], [2, 2]]))

    def test_checker_rejects_duplicate_in_column(self):
        self.assertFalse(ls.is_latin_square([[1, 2], [1, 2]]))


class SudokuTests(unittest.TestCase):
    def test_all_levels_solved_and_valid(self):
        for level, puzzle in sd.PUZZLES.items():
            solution, _ = sd.solve_bfs(puzzle)
            self.assertIsNotNone(solution, level)
            self.assertTrue(sd.is_valid_solution(solution), level)

    def test_solution_keeps_given_cells(self):
        puzzle = sd.PUZZLES["easy"]
        solution, _ = sd.solve_bfs(puzzle)
        for given, solved in zip(puzzle, solution):
            if given != "0":
                self.assertEqual(int(given), solved)

    def test_bfs_without_mrv_still_solves_easy_but_expands_more_nodes(self):
        with_mrv, stats_mrv = sd.solve_bfs(sd.PUZZLES["easy"])
        without_mrv, stats_plain = sd.solve_bfs(sd.PUZZLES["easy"], use_mrv=False)
        self.assertTrue(sd.is_valid_solution(without_mrv))
        self.assertEqual(with_mrv, without_mrv)  # the solution is unique
        self.assertGreater(stats_plain["nodes"], stats_mrv["nodes"])

    def test_unsolvable_puzzle_returns_none(self):
        # row 0 holds 1..8 and a 9 sits below its last cell, so cell (0, 8) has no legal value
        puzzle = "12345678" + "0" + "00000000" + "9" + "0" * 63
        solution, stats = sd.solve_bfs(puzzle)
        self.assertIsNone(solution)
        self.assertFalse(stats["aborted"])


class SocialGolfersTests(unittest.TestCase):
    def test_nine_golfers_four_weeks_solvable(self):
        solver = sg.SocialGolfersDFS(3, 3, 4)
        self.assertTrue(solver.solve())
        self.assertTrue(sg.verify(solver.schedule, 3, 3))

    def test_nine_golfers_five_weeks_impossible(self):
        solver = sg.SocialGolfersDFS(3, 3, 5)
        self.assertFalse(solver.solve())
        self.assertFalse(solver.timed_out)  # the whole space was searched

    def test_sixteen_golfers_five_weeks(self):
        solver = sg.SocialGolfersDFS(4, 4, 5)
        self.assertTrue(solver.solve())
        self.assertTrue(sg.verify(solver.schedule, 4, 4))

    def test_thirty_two_golfers_five_weeks(self):
        solver = sg.SocialGolfersDFS(8, 4, 5)
        self.assertTrue(solver.solve())
        self.assertTrue(sg.verify(solver.schedule, 8, 4))

    def test_random_order_restarts_reach_seven_weeks(self):
        solver = sg.SocialGolfersDFS(8, 4, 7, rng=random.Random(1), node_limit=200_000)
        self.assertTrue(solver.solve())
        self.assertTrue(sg.verify(solver.schedule, 8, 4))

    def test_verify_rejects_repeated_pair(self):
        bad = [[[0, 1, 2], [3, 4, 5], [6, 7, 8]], [[0, 1, 3], [2, 4, 6], [5, 7, 8]]]
        self.assertFalse(sg.verify(bad, 3, 3))


if __name__ == "__main__":
    unittest.main()
