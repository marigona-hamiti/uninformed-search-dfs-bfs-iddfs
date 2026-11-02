# Search Trees (Task 4)

Each tree is drawn with Mermaid (GitHub renders it directly). Nodes are states,
edges are actions. Only the first levels are drawn; repeated states are marked.

---

## 1. 8-Puzzle

**State:** 3x3 board, `_` is the blank. **Actions:** move the blank Up / Down / Left / Right.
**Goal:** `1 2 3 / 4 5 6 / 7 8 _`. **Step cost:** 1.
**Branching factor:** 2 (corner blank), 3 (edge blank), 4 (centre blank); about 2.67 on average.
**State space:** 9!/2 = 181 440 reachable states.

```mermaid
graph TD
    S["1 2 3<br/>4 _ 6<br/>7 5 8<br/>(initial)"]
    S -->|Up| A["1 _ 3<br/>4 2 6<br/>7 5 8"]
    S -->|Down| B["1 2 3<br/>4 5 6<br/>7 _ 8"]
    S -->|Left| C["1 2 3<br/>_ 4 6<br/>7 5 8"]
    S -->|Right| D["1 2 3<br/>4 6 _<br/>7 5 8"]
    B -->|Right| G["1 2 3<br/>4 5 6<br/>7 8 _<br/>GOAL"]
    B -->|Up| R["1 2 3<br/>4 _ 6<br/>7 5 8<br/>(repeat of initial)"]
    B -->|Left| E["1 2 3<br/>4 5 6<br/>_ 7 8"]
    A -->|Left| F["_ 1 3<br/>4 2 6<br/>7 5 8"]
    A -->|Right| H["1 3 _<br/>4 2 6<br/>7 5 8"]
    A -->|Down| R2["1 2 3<br/>4 _ 6<br/>7 5 8<br/>(repeat of initial)"]
    C -->|Up| I["_ 2 3<br/>1 4 6<br/>7 5 8"]
    C -->|Down| J["1 2 3<br/>7 4 6<br/>_ 5 8"]
    C -->|Right| R3["1 2 3<br/>4 _ 6<br/>7 5 8<br/>(repeat of initial)"]
    D -->|Up| K["1 2 _<br/>4 6 3<br/>7 5 8"]
    D -->|Down| L["1 2 3<br/>4 6 8<br/>7 5 _"]
    D -->|Left| R4["1 2 3<br/>4 _ 6<br/>7 5 8<br/>(repeat of initial)"]
```

Worst-case nodes for depth d (b ~ 3, no repeated-state check): about 3^d.
With a closed list the tree is bounded by the 181 440 states.

---

## 2. Missionaries and Cannibals

**State:** `(M, C, B)` = missionaries and cannibals on the **left** bank, boat side `B` (L/R). Start `(3,3,L)`, goal `(0,0,R)`.
**Actions:** the boat carries 1 or 2 people: `1M`, `2M`, `1C`, `2C`, `1M1C`.
**Constraint:** on neither bank may cannibals outnumber missionaries (if missionaries are present). Illegal states are pruned.

```mermaid
graph TD
    S["(3,3,L)<br/>start"]
    S -->|1C| A["(3,2,R)"]
    S -->|2C| B["(3,1,R)"]
    S -->|1M1C| C["(2,2,R)"]
    S -->|1M| X1["(2,3,R)<br/>illegal: 3C > 2M on left"]
    S -->|2M| X2["(1,3,R)<br/>illegal"]
    A -->|1C back| R1["(3,3,L)<br/>(repeat)"]
    B -->|1C back| D["(3,2,L)"]
    B -->|2C back| R2["(3,3,L)<br/>(repeat)"]
    C -->|1M1C back| R3["(3,3,L)<br/>(repeat)"]
    C -->|1M back| E["(3,2,L)"]
    D -->|2C| F["(3,0,R)"]
    D -->|1M1C| X3["(2,1,R)<br/>illegal: 2C > 1M on right"]
    F -->|1C back| G["(3,1,L)"]
    G -->|2M| H["(1,1,R)"]
    H -->|1M1C back| I["(2,2,L)"]
    I -->|2M| J["(0,2,R)"]
    J -->|1C back| K["(0,3,L)"]
    K -->|2C| L["(0,1,R)"]
    L -->|1C back| M["(0,2,L)"]
    M -->|2C| N["(0,0,R)<br/>GOAL"]
```

The long branch `(3,3,L) -> (3,1,R) -> (3,2,L) -> (3,0,R) -> ... -> (0,0,R)` is the shortest solution (11 crossings).
State space: 4 x 4 x 2 = 32 combinations, 16 of them legal; branching factor <= 5.

---

## 3. Rotating Workforce Scheduling

**Problem:** build a cyclic schedule for `n` employees over a cycle of `n` weeks (`7n` days). Each day has a shift from
`{D (day), A (afternoon), N (night), - (off)}`; each day needs the required number of staff per shift, the number of working
days in a row, free days in a row, allowed shift transitions (e.g. N must not be followed by D) and the schedule must wrap around
(the last day connects to the first).

**State:** the sequence of shifts assigned to the days `1..k` of one employee's row (the other employees use the same row shifted by one week, which is what makes it "rotating").
**Action:** assign a shift to day `k+1`.
**Branching factor:** 4 (D, A, N, off), reduced by the constraints.
**Search space:** 4^(7n) rows, for example 4^21 ~ 4.4e12 for `n = 3`.

Example with three weeks (`n = 3`), first levels of the tree for the first days of the row:

```mermaid
graph TD
    S["empty row"]
    S -->|D| D1["D"]
    S -->|A| A1["A"]
    S -->|N| N1["N"]
    S -->|off| O1["-"]
    D1 -->|D| DD["D D"]
    D1 -->|A| DA["D A"]
    D1 -->|N| DN["D N"]
    D1 -->|off| DO["D -"]
    N1 -->|D| X1["N D<br/>illegal: forbidden transition"]
    N1 -->|A| X2["N A<br/>illegal: forbidden transition"]
    N1 -->|N| NN["N N"]
    N1 -->|off| NO["N -"]
    A1 -->|D| X3["A D<br/>illegal: forbidden transition"]
    A1 -->|A| AA["A A"]
    A1 -->|N| AN["A N"]
    A1 -->|off| AO["A -"]
    DD --> DDD["D D D ..."]
    DD --> DDO["D D - ..."]
    DDD --> L["... depth 7n: check coverage per day, rest rules and wrap-around -> goal / dead end"]
```

Nodes at depth `k` that violate a transition or max-consecutive rule are pruned (backtracking); a leaf at depth `7n` is a goal only if the daily
coverage requirement is met and the last day connects legally to the first.
