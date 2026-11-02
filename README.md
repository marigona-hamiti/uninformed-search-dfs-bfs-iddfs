# Uninformed Search: DFS, BFS, IDDFS

Detyra e parë semestrale – **Inteligjenca Artificiale 2026/27 (FIEK)**.

Probleme të zgjidhura me kërkim pa informacion shtesë (uninformed search) dhe backtracking.

| # | Problemi | Algoritmi | Kodi |
|---|----------|-----------|------|
| 1 | Social Golfers | DFS + backtracking | [social_golfers/social_golfers_dfs.py](social_golfers/social_golfers_dfs.py) |
| 2 | Sudoku Solver (Easy, Medium, Hard) | BFS + backtracking | [sudoku/sudoku_bfs.py](sudoku/sudoku_bfs.py) |
| 3 | Latin Square | IDDFS + backtracking | [latin_square/latin_square_iddfs.py](latin_square/latin_square_iddfs.py) |
| 4 | Pemët e kërkimit: 8-Puzzle, Missionaries & Cannibals, Rotating Workforce Scheduling | – | [search_trees/search_trees.md](search_trees/search_trees.md) |

Kërkohet vetëm Python 3 (pa librari të jashtme).

```bash
python latin_square/latin_square_iddfs.py 5
python sudoku/sudoku_bfs.py            # ose: sudoku_bfs.py easy
python social_golfers/social_golfers_dfs.py            # të gjitha rastet
python social_golfers/social_golfers_dfs.py 8 4 5 30   # g p javë kufiri_kohor_në_sekonda
```

---

## 1. Social Golfers (DFS)

**Problemi.** `n = g·p` golfistë luajnë çdo javë në `g` grupe me `p` lojtarë. Dy golfistë nuk lejohen të jenë në të njëjtin grup më shumë se një herë. Sa javë maksimale mund të luhet për `g = 8, p = 4` (32 golfistë)?

**Modelimi.**
- Variabla: grupi i secilit golfist në secilën javë; çdo javë është ndarje e golfistëve në `g` grupe me `p` anëtarë.
- Kufizime: (C1) çdo grup ka saktësisht `p` golfistë, çdo golfist luan një herë në javë; (C2) çdo çift takohet më së shumti një herë.
- Gjendja: grupet e caktuara deri tani. Veprimi: shtohet një grup i ri. Qëllimi: `w` javë të planifikuara.

**Funksioni objektiv.** `f = Σ_{çift {a,b}} max(0, takime(a,b) − 1)`, pra numri i takimeve të përsëritura; qëllimi është `f = 0`. Backtracking nuk e zgjeron kurrë një gjendje me `f > 0`.

**Hapësira e kërkimit.** Ndarjet e `n` golfistëve në `g` grupe me `p`: `n! / ((p!)^g · g!)`. Për `g=8, p=4` kjo është ≈ 1.1·10²⁴ për javë, pra ≈ (1.1·10²⁴)^w plane për `w` javë.

**Thyerja e simetrisë.** Java 1 fiksohet (`{0..3}, {4..7}, ...`), dhe çdo grup fillon me golfistin më të vogël të papërdorur, anëtarët shtohen në rend rritës. Kjo heq degët ekuivalente por e lë DFS-në të plotë.

**DFS.** Thellësia = (javë, grup, anëtar). Çdo kandidat që ka takuar tashmë një anëtar të grupit prehet menjëherë.

**Rezultatet (të matura).**

| Rasti | Rezultati |
|-------|-----------|
| 9 golfistë (3×3), 4 javë | zgjidhet (37 nyje); 5 javë: DFS e shteron hapësirën, **nuk ka zgjidhje** |
| 16 golfistë (4×4), 5 javë | zgjidhet (80 nyje) |
| 15 golfistë (5×3, Kirkman), 7 javë | **nuk gjendet** brenda 30 s (16 mln nyje); thellësia maksimale: 6 javë (7 javë ekzistojnë) |
| 32 golfistë (8×4), 5 javë | zgjidhet menjëherë (160 nyje) |
| 32 golfistë (8×4), 6–10 javë, renditje fikse | **nuk gjendet** brenda 40 s (8–20 milionë nyje); thellësia maksimale e arritur: 5 javë |
| 32 golfistë (8×4), 7 javë, renditje e rastësishme + rinisje (`run_restarts`) | zgjidhet në rinisjen e parë, ~0.2 s |
| 32 golfistë (8×4), 8 javë, renditje e rastësishme + rinisje | **nuk gjendet** në 60 s (~100 rinisje me 200 000 nyje) |

**Vëzhgim.** DFS-ja me renditje fikse arrin 5 javë për 32 golfistë dhe pastaj ngec: bën backtracking në javët e fundit pa e ndryshuar javën 2–3 që e bën problemin të pazgjidhshëm. Kur kandidatët provohen në renditje të rastësishme dhe kërkimi niset përsëri pas një buxheti nyjesh (rinisje), arrihen 7 javë. Algoritmi mbetet DFS + backtracking; ndryshon vetëm rendi i provës. Optimumi i njohur nga literatura është **10 javë**; arrihet me metoda algjebrike ose me kërkim lokal/metaheuristika (temat 5–6 të lëndës), jo me DFS të verbër. Ky është kufizimi kryesor i DFS në hapësira shumë të mëdha.

**Rasti i përgjithshëm `n = g × p`, `w` javë.** Kufiri i sipërm: një golfist takon `w·(p−1)` të tjerë, pra `w ≤ (n−1)/(p−1)`. Për 32 golfistë, `p=4`: `w ≤ 31/3`, pra `w ≤ 10`, dhe 10 arrihet. Për 9 golfistë, `p=3`: `w ≤ 4`, që përputhet me rezultatin e DFS.

---

## 2. Sudoku (BFS)

**Modelimi.** 81 variabla (qelizat), domen `{1..9}`, kufizime: vlera të ndryshme në çdo rresht, kolonë dhe kuti 3×3. Gjendja: tabelë e pjesshme; veprimi: një qelizë e zbrazët merr një vlerë të ligjshme; qëllimi: asnjë qelizë e zbrazët.

**Funksioni objektiv.** `f = numri i qelizave të zbrazëta` (qëllimi 0), me kufizimin e ngurtë që asnjë rresht/kolonë/kuti nuk ka dublikat. Vlerat e palejuara nuk vendosen kurrë (backtracking).

**Hapësira e kërkimit.** `9^e`, ku `e` = numri i qelizave të zbrazëta.

**BFS.** Radha FIFO mban të gjitha tabelat e pjesshme të nivelit aktual; zgjerohet një nivel i plotë para se të shkohet më thellë. Qeliza që zgjerohet është ajo me më pak vlera të ligjshme (MRV); nëse nuk ka vlerë të ligjshme, nyja hidhet (backtracking).

| Niveli | Qeliza të zbrazëta | Hapësira `9^e` | Nyje të zgjeruara | Madhësia max e radhës | Koha |
|--------|-------------------|----------------|-------------------|-----------------------|------|
| Easy | 51 | 4.6·10⁴⁸ | 52 | 1 | ~0.001 s |
| Medium | 45 | 8.7·10⁴² | 46 | 1 | <0.001 s |
| Hard | 53 | 3.8·10⁵⁰ | 206 | 9 | ~0.003 s |

Puzzle-t shtesë për provë stresi (`very_hard`, `escargot`; të njohura si të vështira për brute force):

| Niveli | Qeliza të zbrazëta | Nyje të zgjeruara | Madhësia max e radhës | Koha |
|--------|-------------------|-------------------|-----------------------|------|
| very_hard | 64 | 3 723 | 150 | ~0.09 s |
| escargot | 58 | 2 425 | 96 | ~0.03 s |

Të gjitha zgjidhjet verifikohen automatikisht (`is_valid_solution`). Me MRV radha mbetet e vogël, prandaj BFS nuk ka problem memorieje këtu. Pa MRV (p.sh. duke zgjeruar qelizën e parë të zbrazët) radha pritet të rritet shumë më shpejt, por këtë nuk e kam matur.

---

## 3. Latin Square (IDDFS)

**Modelimi.** `n×n` qeliza, domen `{1..n}`, kufizime: vlerat në çdo rresht dhe kolonë janë të ndryshme. Qelizat plotësohen rresht pas rreshti; thellësia = numri i qelizave të plotësuara.

**Funksioni objektiv.** `f = dublikatet në rreshta + dublikatet në kolona`; qëllimi `f = 0`.

**Hapësira e kërkimit.** `n^(n²)` tabela (5²⁵ ≈ 3·10¹⁷ për `n=5`); vetëm 161 280 janë katrorë latinë të vlefshëm për `n=5`.

**IDDFS.** DFS me kufi thellësie 1, 2, 3, … deri te `n²`. Zgjidhja është në thellësinë `n²`, ndaj iteracioni i fundit e gjen.

Rezultati për `n = 5` (i matur): iteracionet me kufi < 25 e shterojnë hapësirën pa zgjidhje; me kufirin 25 zgjidhja gjendet pas 38 nyjesh. Gjithsej 13 505 922 nyje, ~7.5 s.

```
1 2 3 4 5
2 1 4 5 3
3 4 5 1 2
4 5 2 3 1
5 3 1 2 4
```

---

## 4. Krahasimi i algoritmeve

Me `b` = faktori i degëzimit, `d` = thellësia e zgjidhjes, `m` = thellësia maksimale.

| Algoritmi | Kompletë | Optimal | Koha | Memoria |
|-----------|----------|---------|------|---------|
| DFS | jo (në pemë pa fund) | jo | O(b^m) | **O(b·m)** |
| BFS | po | po (kosto njësi) | O(b^d) | O(b^d) |
| IDDFS | po | po (kosto njësi) | O(b^d) | **O(b·d)** |

- **DFS**: memorie e vogël, përshtatet kur zgjidhja është në thellësi të njohur (Social Golfers), por mund të humbasë në degë të këqija.
- **BFS**: gjen zgjidhjen më të cekët, por kërkon memorie shumë të madhe; për Sudoku funksionon sepse MRV e mban radhën të vogël.
- **IDDFS**: memoria e DFS me plotësinë e BFS; kostoja është rinisja e niveleve të sipërme (te Latin Square ~13.5 mln nyje në total).

## 5. Pemët e kërkimit

Shih [search_trees/search_trees.md](search_trees/search_trees.md): 8-Puzzle, Missionaries & Cannibals dhe Rotating Workforce Scheduling.
