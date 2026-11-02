"""Social Golfers Problem solved with DFS + backtracking.

Problem
    n = g * p golfers play once a week in g groups of p players. Over w weeks
    no two golfers may share a group more than once. What is the maximum
    number of weeks w for g = 8, p = 4 (32 golfers)?

Modeling
    Variables : x[w][i] = group (0..g-1) of golfer i in week w.
                Equivalent view used here: each week is a partition of the
                golfers into g groups of p players.
    Domain    : group index 0..g-1 (with exactly p golfers per group).
    Constraints (hard):
        C1  every group has exactly p golfers (each golfer plays once a week);
        C2  every pair of golfers meets at most once in all weeks.
    State     : the first k groups (k // g complete weeks + part of a week).
    Action    : add one group (p golfers) to the current week.
    Goal test : w weeks scheduled.

Objective function
    f(schedule) = sum over pairs {a, b} of max(0, meetings(a, b) - 1)
    (number of repeated meetings). Goal f = 0. Backtracking only keeps states
    with f = 0, so every visited state satisfies C2 by construction.

Search space (landscape)
    Partitions of n golfers into g groups of p: P = n! / ((p!)^g * g!).
    For g = 8, p = 4: P ~ 1.1e24 per week, so ~ P^w schedules for w weeks.

Symmetry breaking (keeps DFS complete but prunes equivalent branches)
    * golfers are interchangeable -> week 1 is fixed to {0..p-1}, {p..2p-1}, ...
    * groups inside a week are unordered -> a group always starts with the
      smallest golfer that is not placed yet, the others are added in
      increasing order.

DFS
    Depth-first search over (week, group, member) choices, backtracking as
    soon as a candidate golfer has already met a member of the group.
"""

import random
import sys
import time


class SocialGolfersDFS:
    def __init__(self, groups, size, weeks, time_limit=None, rng=None, node_limit=None):
        self.g = groups
        self.p = size
        self.n = groups * size
        self.weeks = weeks
        self.time_limit = time_limit
        self.rng = rng              # if set, candidates are tried in random order
        self.node_limit = node_limit  # per-run node budget (used by restarts)
        self.met = [[False] * self.n for _ in range(self.n)]
        self.schedule = []        # list of weeks, each a list of groups
        self.nodes = 0
        self.best_weeks = 0       # deepest number of complete weeks reached
        self.best_schedule = []
        self.deadline = None
        self.timed_out = False

    # --- helpers -----------------------------------------------------------
    def _meet(self, group, flag):
        for i, a in enumerate(group):
            for b in group[i + 1:]:
                self.met[a][b] = self.met[b][a] = flag

    def _record(self):
        done = len(self.schedule) - (0 if self._week_complete() else 1)
        if done > self.best_weeks:
            self.best_weeks = done
            self.best_schedule = [[g[:] for g in wk] for wk in self.schedule[:done]]

    def _week_complete(self):
        return bool(self.schedule) and len(self.schedule[-1]) == self.g

    # --- search ------------------------------------------------------------
    def solve(self):
        if self.time_limit:
            self.deadline = time.perf_counter() + self.time_limit
        # week 1 is fixed by symmetry breaking
        week1 = [list(range(k * self.p, (k + 1) * self.p)) for k in range(self.g)]
        for grp in week1:
            self._meet(grp, True)
        self.schedule.append(week1)
        self.best_weeks, self.best_schedule = 1, [week1]
        if self.weeks == 1:
            return True
        self.schedule.append([])
        return self._fill_group(used=set(), group=[])

    def _fill_group(self, used, group):
        """Extend the current group of the current week (DFS step)."""
        self.nodes += 1
        if self.deadline and self.nodes % 4096 == 0 and time.perf_counter() > self.deadline:
            self.timed_out = True
        if self.node_limit and self.nodes > self.node_limit:
            self.timed_out = True
        if self.timed_out:
            return False

        week = self.schedule[-1]
        if len(group) == self.p:
            # group complete: record it and start the next group / week
            self._meet(group, True)
            week.append(group[:])
            used_next = used | set(group)
            result = self._next_group(used_next)
            if result:
                return True
            week.pop()
            self._meet(group, False)
            return False

        # candidates: not used this week, not met any member, increasing order
        if not group:
            first = min(set(range(self.n)) - used)
            return self._fill_group(used, [first])
        start = group[-1] + 1
        cands = [c for c in range(start, self.n)
                 if c not in used and not any(self.met[c][m] for m in group)]
        if self.rng:
            self.rng.shuffle(cands)
        for cand in cands:  # candidates that would meet someone twice are already pruned
            group.append(cand)
            if self._fill_group(used, group):
                return True
            group.pop()
        return False

    def _next_group(self, used):
        week = self.schedule[-1]
        if len(week) < self.g:
            return self._fill_group(used, [])
        # week complete
        self._record()
        if len(self.schedule) == self.weeks:
            return True
        self.schedule.append([])
        if self._fill_group(set(), []):
            return True
        self.schedule.pop()
        return False


def verify(schedule, g, p):
    n = g * p
    seen = set()
    for week in schedule:
        if sorted(x for grp in week for x in grp) != list(range(n)):
            return False
        for grp in week:
            if len(grp) != p:
                return False
            for i, a in enumerate(grp):
                for b in grp[i + 1:]:
                    pair = (min(a, b), max(a, b))
                    if pair in seen:
                        return False
                    seen.add(pair)
    return True


def print_schedule(schedule):
    for w, week in enumerate(schedule, 1):
        print(f"  week {w:>2}: " + "  ".join("[" + " ".join(f"{x:>2}" for x in grp) + "]" for grp in week))


def run(g, p, weeks, time_limit=None):
    print(f"--- g={g} groups, p={p} players ({g * p} golfers), target weeks={weeks} ---")
    solver = SocialGolfersDFS(g, p, weeks, time_limit)
    start = time.perf_counter()
    found = solver.solve()
    elapsed = time.perf_counter() - start
    if found:
        sched = solver.schedule
        print(f"SOLVED  nodes={solver.nodes}  time={elapsed:.2f}s  valid={verify(sched, g, p)}")
        print_schedule(sched)
    else:
        reason = "time limit reached" if solver.timed_out else "search space exhausted, no solution"
        print(f"NOT SOLVED ({reason})  nodes={solver.nodes}  time={elapsed:.2f}s")
        print(f"  deepest valid schedule found: {solver.best_weeks} week(s), valid={verify(solver.best_schedule, g, p)}")
    print()
    return solver


def run_restarts(g, p, weeks, time_limit=60, node_limit=200_000):
    """DFS with random candidate order and restarts: each restart is a normal
    DFS + backtracking run with a node budget; when it is exhausted the search
    starts again with a different random order."""
    print(f"--- g={g}, p={p} ({g * p} golfers), target weeks={weeks}, random-order DFS with restarts ---")
    start = time.perf_counter()
    restarts, solver = 0, None
    while time.perf_counter() - start < time_limit:
        restarts += 1
        solver = SocialGolfersDFS(g, p, weeks, rng=random.Random(restarts), node_limit=node_limit)
        if solver.solve():
            print(f"SOLVED  restarts={restarts}  time={time.perf_counter() - start:.2f}s  valid={verify(solver.schedule, g, p)}")
            print_schedule(solver.schedule)
            print()
            return solver
    print(f"NOT SOLVED within {time_limit}s  restarts={restarts}\n")
    return None


def main():
    if len(sys.argv) >= 4:
        g, p, w = map(int, sys.argv[1:4])
        limit = float(sys.argv[4]) if len(sys.argv) > 4 else None
        run(g, p, w, limit)
        return
    # small instances where a complete DFS finishes quickly
    run(3, 3, 4)      # 9 golfers: affine plane of order 3 -> 4 weeks possible, 5 impossible
    run(3, 3, 5)
    run(4, 4, 5)      # 16 golfers: affine plane of order 4 -> 5 weeks possible
    run(5, 3, 7, time_limit=30)  # 15 golfers: Kirkman's schoolgirl problem (7 weeks exist, DFS may time out)
    # the assignment instance: 32 golfers, 8 groups of 4 (known optimum: 10 weeks)
    # plain DFS finds 5 weeks instantly but cannot reach 6+ within the time limit
    for weeks in (5, 6):
        run(8, 4, weeks, time_limit=30)
    # random candidate order + restarts reaches further than the fixed order
    for weeks in (7, 8):
        run_restarts(8, 4, weeks, time_limit=60)


if __name__ == "__main__":
    main()
