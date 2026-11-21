import random

from _util import arr, rand_arr, size, rand_word, edges_input


# ---------- sudoku puzzle generator (guarantees a unique solution) ----------

def _count_solutions(g, limit=2):
    rows, cols, boxes = [0] * 9, [0] * 9, [0] * 9
    empty = []
    for i in range(81):
        r, c = divmod(i, 9)
        if g[i]:
            b = 1 << g[i]
            rows[r] |= b; cols[c] |= b; boxes[r // 3 * 3 + c // 3] |= b
        else:
            empty.append(i)
    count = 0

    def go():
        nonlocal count
        best, best_opts = -1, None
        for i in empty:
            if g[i]:
                continue
            r, c = divmod(i, 9)
            opts = [d for d in range(1, 10) if not ((rows[r] | cols[c] | boxes[r // 3 * 3 + c // 3]) >> d) & 1]
            if best_opts is None or len(opts) < len(best_opts):
                best, best_opts = i, opts
                if len(opts) <= 1:
                    break
        if best == -1:
            count += 1
            return
        r, c = divmod(best, 9)
        bx = r // 3 * 3 + c // 3
        for d in best_opts:
            b = 1 << d
            g[best] = d; rows[r] |= b; cols[c] |= b; boxes[bx] |= b
            go()
            g[best] = 0; rows[r] ^= b; cols[c] ^= b; boxes[bx] ^= b
            if count >= limit:
                return

    go()
    return count


def gen_sudoku(r):
    digits = list(range(1, 10))
    r.shuffle(digits)
    bands = r.sample(range(3), 3)
    rows = [b * 3 + x for b in bands for x in r.sample(range(3), 3)]
    stacks = r.sample(range(3), 3)
    cols = [s * 3 + x for s in stacks for x in r.sample(range(3), 3)]
    full = [digits[(3 * (rr % 3) + rr // 3 + cc) % 9] for rr in rows for cc in cols]
    g = full[:]
    target = r.randint(24, 40)  # number of clues to aim for
    cells = list(range(81))
    r.shuffle(cells)
    clues = 81
    for i in cells:
        if clues <= target:
            break
        keep = g[i]
        g[i] = 0
        if _count_solutions(g[:]) != 1:
            g[i] = keep
        else:
            clues -= 1
    return "\n".join("".join(map(str, g[k * 9:(k + 1) * 9])) for k in range(9))


_WIKI_SUDOKU = "530070000600195000098000060800060003400803001700020006060000280000419005000080079"
assert _count_solutions([int(c) for c in _WIKI_SUDOKU]) == 1


def gen_ladder(r):
    L = r.randint(2, 4)
    alpha = "abcde"[: r.randint(2, 5)]
    words = list({rand_word(r, L, alpha) for _ in range(size(r, 20, 300, 3000))})
    begin = rand_word(r, L, alpha)
    end = r.choice(words) if r.random() < 0.9 else rand_word(r, L, alpha)
    return f"{begin} {end}\n{len(words)}\n{' '.join(words)}"


def gen_simple_graph(r, directed):
    n = size(r, 8, 300, 5000)
    target = r.randint(0, min(2 * n, 10000))
    edges = set()
    if not directed and r.random() < 0.5:  # tree-like graphs have many bridges
        for v in range(2, n + 1):
            edges.add((r.randint(1, v - 1), v))
    for _ in range(target):
        a, b = r.randint(1, n), r.randint(1, n)
        if a == b:
            continue
        if not directed and (b, a) in edges:
            continue
        edges.add((a, b))
    edges = list(edges)
    r.shuffle(edges)
    return edges_input(n, edges)


def gen_grid_elim(r):
    R, C = r.randint(1, 40), r.randint(1, 40)
    p = r.choice([0.1, 0.3, 0.5])
    g = [["1" if r.random() < p else "0" for _ in range(C)] for _ in range(R)]
    g[0][0] = g[-1][-1] = "0"
    return f"{R} {C} {r.randint(0, 10)}\n" + "\n".join(" ".join(row) for row in g)


def gen_fenwick(r):
    n = size(r, 10, 1000, 10000)
    q = size(r, 10, 1000, 10000)
    a = rand_arr(r, n, -10**9, 10**9)
    ops = []
    for _ in range(q):
        if r.random() < 0.5:
            ops.append(f"1 {r.randint(1, n)} {r.randint(-10**9, 10**9)}")
        else:
            lo, hi = sorted((r.randint(1, n), r.randint(1, n)))
            ops.append(f"2 {lo} {hi}")
    ops[-1] = "2 1 " + str(n)
    return f"{n} {q}\n{' '.join(map(str, a))}\n" + "\n".join(ops)


PROBLEMS = [
    dict(
        slug="n-queens", title="N-Queens", difficulty="hard", topics=["backtracking", "bit manipulation"],
        description="Count the ways to place `n` queens on an `n × n` chessboard so that no two queens attack each "
                    "other (same row, column or diagonal).",
        input_format="A single integer `n`.",
        output_format="Print the number of solutions.",
        constraints="- 1 ≤ n ≤ 11",
        samples=["4", "1"],
        tests=["2", "3", "5", "6", "7", "8", "9", "10", "11"],
        py=r'''
n = int(input())
full = (1 << n) - 1


def solve(cols, d1, d2):
    if cols == full:
        return 1
    count = 0
    free = full & ~(cols | d1 | d2)
    while free:
        bit = free & -free
        free ^= bit
        count += solve(cols | bit, ((d1 | bit) << 1) & full, (d2 | bit) >> 1)
    return count


print(solve(0, 0, 0))
''',
        js=r'''
const n = Number(require('fs').readFileSync(0, 'utf8').trim());
const full = (1 << n) - 1;
function solve(cols, d1, d2) {
  if (cols === full) return 1;
  let count = 0, free = full & ~(cols | d1 | d2);
  while (free) {
    const bit = free & -free;
    free ^= bit;
    count += solve(cols | bit, ((d1 | bit) << 1) & full, (d2 | bit) >> 1);
  }
  return count;
}
console.log(solve(0, 0, 0));
''',
        explanation="Place one queen per row with **backtracking**. Track attacked columns and both diagonals as "
                    "**bitmasks**: when moving to the next row, the diagonal masks shift left/right by one. "
                    "`free & -free` extracts the lowest free column. Exponential, but pruning makes n ≤ 11 fast.",
    ),
    dict(
        slug="sudoku-solver", title="Sudoku Solver", difficulty="hard", topics=["backtracking", "bit manipulation"],
        description="Solve a 9×9 Sudoku: fill the empty cells (`0`) so that every row, column and 3×3 box contains "
                    "the digits 1–9 exactly once. Every puzzle has exactly one solution.",
        input_format="9 lines, each with 9 digits (`0` = empty cell).",
        output_format="Print the solved grid as 9 lines of 9 digits.",
        constraints="- the puzzle has a unique solution",
        samples=["530070000\n600195000\n098000060\n800060003\n400803001\n700020006\n060000280\n000419005\n000080079",
                 gen_sudoku(random.Random("sudoku-sample-2"))],
        gen=gen_sudoku,
        gen_count=8,
        py=r'''
import sys
rows_in = sys.stdin.read().split()
g = [int(ch) for row in rows_in[:9] for ch in row]
rows, cols, boxes = [0] * 9, [0] * 9, [0] * 9
for i, d in enumerate(g):
    if d:
        r, c = divmod(i, 9)
        rows[r] |= 1 << d; cols[c] |= 1 << d; boxes[r // 3 * 3 + c // 3] |= 1 << d
empty = [i for i in range(81) if g[i] == 0]


def solve():
    # pick the empty cell with the fewest candidates (MRV heuristic)
    best, best_mask, best_cnt = -1, 0, 10
    for i in empty:
        if g[i]:
            continue
        r, c = divmod(i, 9)
        mask = ~(rows[r] | cols[c] | boxes[r // 3 * 3 + c // 3]) & 0x3FE
        cnt = bin(mask).count("1")
        if cnt < best_cnt:
            best, best_mask, best_cnt = i, mask, cnt
            if cnt <= 1:
                break
    if best == -1:
        return True
    r, c = divmod(best, 9)
    bx = r // 3 * 3 + c // 3
    for d in range(1, 10):
        if best_mask >> d & 1:
            b = 1 << d
            g[best] = d; rows[r] |= b; cols[c] |= b; boxes[bx] |= b
            if solve():
                return True
            g[best] = 0; rows[r] ^= b; cols[c] ^= b; boxes[bx] ^= b
    return False


solve()
print("\n".join("".join(map(str, g[k * 9:(k + 1) * 9])) for k in range(9)))
''',
        js=r'''
const rowsIn = require('fs').readFileSync(0, 'utf8').split(/\s+/).filter(Boolean);
const g = [];
for (let k = 0; k < 9; k++) for (const ch of rowsIn[k]) g.push(Number(ch));
const rows = new Array(9).fill(0), cols = new Array(9).fill(0), boxes = new Array(9).fill(0);
const box = (r, c) => Math.floor(r / 3) * 3 + Math.floor(c / 3);
g.forEach((d, i) => {
  if (d) { const r = Math.floor(i / 9), c = i % 9; rows[r] |= 1 << d; cols[c] |= 1 << d; boxes[box(r, c)] |= 1 << d; }
});
const empty = [];
for (let i = 0; i < 81; i++) if (!g[i]) empty.push(i);
const popcount = (x) => { let c = 0; while (x) { x &= x - 1; c++; } return c; };
function solve() {
  let best = -1, bestMask = 0, bestCnt = 10;
  for (const i of empty) {
    if (g[i]) continue;
    const r = Math.floor(i / 9), c = i % 9;
    const mask = ~(rows[r] | cols[c] | boxes[box(r, c)]) & 0x3fe;
    const cnt = popcount(mask);
    if (cnt < bestCnt) { best = i; bestMask = mask; bestCnt = cnt; if (cnt <= 1) break; }
  }
  if (best === -1) return true;
  const r = Math.floor(best / 9), c = best % 9, bx = box(r, c);
  for (let d = 1; d <= 9; d++) {
    if (!((bestMask >> d) & 1)) continue;
    const b = 1 << d;
    g[best] = d; rows[r] |= b; cols[c] |= b; boxes[bx] |= b;
    if (solve()) return true;
    g[best] = 0; rows[r] ^= b; cols[c] ^= b; boxes[bx] ^= b;
  }
  return false;
}
solve();
const out = [];
for (let k = 0; k < 9; k++) out.push(g.slice(k * 9, k * 9 + 9).join(''));
console.log(out.join('\n'));
''',
        explanation="**Backtracking** with constraint bitmasks for each row, column and box (bit `d` set = digit `d` "
                    "used). At every step choose the empty cell with the **fewest** candidates (MRV heuristic) — "
                    "this prunes the search tree dramatically compared with filling cells left to right.",
    ),
    dict(
        slug="maximum-xor-pair", title="Maximum XOR of Two Numbers", difficulty="hard", topics=["trie", "bit manipulation"],
        description="Print the maximum value of `a[i] XOR a[j]` over all pairs `i ≠ j`. O(n²) is too slow.",
        input_format="The first line contains `n`.\nThe second line contains `n` integers.",
        output_format="Print the maximum XOR.",
        constraints="- 2 ≤ n ≤ 2·10^4\n- 0 ≤ a[i] < 2^30",
        samples=["6\n3 10 5 25 2 8", "2\n0 0"],
        tests=["2\n1 2", "3\n7 7 7", "4\n1073741823 0 5 6"],
        gen=lambda r: arr(rand_arr(r, max(2, size(r, 10, 1000, 20000)), 0, r.choice([15, 2**30 - 1]))),
        py=r'''
import sys
data = sys.stdin.read().split()
nums = list(map(int, data[1:1 + int(data[0])]))
# binary trie stored in flat lists: child[node*2 + bit]
child = [-1, -1]
best = 0
for idx, x in enumerate(nums):
    if idx:
        node, cur = 0, 0
        for b in range(29, -1, -1):
            want = ((x >> b) & 1) ^ 1
            if child[node * 2 + want] != -1:
                cur |= 1 << b
                node = child[node * 2 + want]
            else:
                node = child[node * 2 + (want ^ 1)]
        best = max(best, cur)
    node = 0
    for b in range(29, -1, -1):
        bit = (x >> b) & 1
        if child[node * 2 + bit] == -1:
            child[node * 2 + bit] = len(child) // 2
            child += [-1, -1]
        node = child[node * 2 + bit]
print(best)
''',
        js=r'''
const t = require('fs').readFileSync(0, 'utf8').split(/\s+/).filter(Boolean).map(Number);
const n = t[0];
const child = new Int32Array((n * 31 + 1) * 2).fill(-1);
let nodes = 1, best = 0;
for (let i = 1; i <= n; i++) {
  const x = t[i];
  if (i > 1) {
    let node = 0, cur = 0;
    for (let b = 29; b >= 0; b--) {
      const want = ((x >> b) & 1) ^ 1;
      if (child[node * 2 + want] !== -1) { cur |= 1 << b; node = child[node * 2 + want]; }
      else node = child[node * 2 + (want ^ 1)];
    }
    best = Math.max(best, cur);
  }
  let node = 0;
  for (let b = 29; b >= 0; b--) {
    const bit = (x >> b) & 1;
    if (child[node * 2 + bit] === -1) child[node * 2 + bit] = nodes++;
    node = child[node * 2 + bit];
  }
}
console.log(best);
''',
        explanation="Insert numbers bit by bit (most significant first) into a **binary trie**. For each number, walk "
                    "the trie greedily choosing the **opposite** bit whenever possible — a 1 in a higher bit beats "
                    "anything in lower bits. **O(n · 30)**.",
    ),
    dict(
        slug="longest-increasing-path-in-matrix", title="Longest Increasing Path in a Matrix", difficulty="hard",
        topics=["dynamic programming", "graphs", "matrix", "memoization"],
        description="From each cell you may move up, down, left or right to a cell with a **strictly larger** value. "
                    "Print the length (number of cells) of the longest such path.",
        input_format="The first line contains `r c`. Each of the next `r` lines contains `c` integers.",
        output_format="Print the length of the longest increasing path.",
        constraints="- 1 ≤ r, c ≤ 150\n- 0 ≤ values ≤ 10^6",
        samples=["3 3\n9 9 4\n6 6 8\n2 1 1", "3 3\n3 4 5\n3 2 6\n2 2 1"],
        tests=["1 1\n7", "1 5\n1 2 3 4 5", "2 2\n1 1\n1 1"],
        gen=lambda r: (lambda R, C, hi: f"{R} {C}\n" + "\n".join(" ".join(str(r.randint(0, hi)) for _ in range(C)) for _ in range(R)))(r.randint(1, 100), r.randint(1, 100), r.choice([3, 100, 10**6])),
        py=r'''
import sys
data = sys.stdin.buffer.read().split()
R, C = int(data[0]), int(data[1])
a = list(map(int, data[2:2 + R * C]))
best = [1] * (R * C)
# process cells from largest to smallest value: all neighbours we can move to are already final
for idx in sorted(range(R * C), key=a.__getitem__, reverse=True):
    x, y = divmod(idx, C)
    v = a[idx]
    b = 1
    if x > 0 and a[idx - C] > v: b = max(b, best[idx - C] + 1)
    if x < R - 1 and a[idx + C] > v: b = max(b, best[idx + C] + 1)
    if y > 0 and a[idx - 1] > v: b = max(b, best[idx - 1] + 1)
    if y < C - 1 and a[idx + 1] > v: b = max(b, best[idx + 1] + 1)
    best[idx] = b
print(max(best))
''',
        js=r'''
const t = require('fs').readFileSync(0, 'utf8').split(/\s+/).filter(Boolean).map(Number);
const R = t[0], C = t[1], a = t.slice(2, 2 + R * C);
const order = Array.from({ length: R * C }, (_, i) => i).sort((i, j) => a[j] - a[i]);
const best = new Int32Array(R * C).fill(1);
for (const idx of order) {
  const x = Math.floor(idx / C), y = idx % C, v = a[idx];
  let b = 1;
  if (x > 0 && a[idx - C] > v) b = Math.max(b, best[idx - C] + 1);
  if (x < R - 1 && a[idx + C] > v) b = Math.max(b, best[idx + C] + 1);
  if (y > 0 && a[idx - 1] > v) b = Math.max(b, best[idx - 1] + 1);
  if (y < C - 1 && a[idx + 1] > v) b = Math.max(b, best[idx + 1] + 1);
  best[idx] = b;
}
let ans = 0;
for (const b of best) ans = Math.max(ans, b);
console.log(ans);
''',
        explanation="Moves always go to larger values, so the graph is a DAG. `best[cell] = 1 + max(best[neighbour])` "
                    "over larger neighbours. Either DFS with memoization, or — avoiding deep recursion — process "
                    "cells in **decreasing value order** so neighbours are computed first. **O(rc log rc)**.",
    ),
    dict(
        slug="burst-balloons", title="Burst Balloons", difficulty="hard", topics=["dynamic programming", "interval dp"],
        description="`n` balloons have numbers `a[0..n-1]`. Bursting balloon `i` earns `left × a[i] × right`, where "
                    "`left`/`right` are its current neighbours (treat missing neighbours as 1). After bursting, its "
                    "neighbours become adjacent. Print the maximum total coins from bursting all balloons.",
        input_format="The first line contains `n`.\nThe second line contains `n` integers.",
        output_format="Print the maximum coins.",
        constraints="- 1 ≤ n ≤ 150\n- 0 ≤ a[i] ≤ 100",
        samples=["4\n3 1 5 8", "2\n1 5"],
        tests=["1\n7", "3\n0 0 0", "5\n9 76 64 21 97"],
        gen=lambda r: arr(rand_arr(r, r.choice([r.randint(1, 10), r.randint(10, 150)]), 0, 100)),
        time_limit_ms=3000,
        py=r'''
import sys
data = sys.stdin.read().split()
n = int(data[0])
a = [1] + list(map(int, data[1:1 + n])) + [1]
m = n + 2
# dp[l][r] = best coins from bursting every balloon strictly between l and r
dp = [[0] * m for _ in range(m)]
for length in range(2, m):
    for l in range(0, m - length):
        r = l + length
        edge = a[l] * a[r]
        row_l = dp[l]
        best = 0
        for k in range(l + 1, r):   # k = last balloon burst in (l, r)
            v = row_l[k] + dp[k][r] + edge * a[k]
            if v > best:
                best = v
        row_l[r] = best
print(dp[0][m - 1])
''',
        js=r'''
const t = require('fs').readFileSync(0, 'utf8').split(/\s+/).filter(Boolean).map(Number);
const n = t[0], a = [1, ...t.slice(1, 1 + n), 1], m = n + 2;
const dp = Array.from({ length: m }, () => new Array(m).fill(0));
for (let len = 2; len < m; len++) {
  for (let l = 0; l + len < m; l++) {
    const r = l + len;
    let best = 0;
    for (let k = l + 1; k < r; k++) best = Math.max(best, dp[l][k] + dp[k][r] + a[l] * a[k] * a[r]);
    dp[l][r] = best;
  }
}
console.log(dp[0][m - 1]);
''',
        explanation="Think about which balloon is burst **last** in an interval `(l, r)`: if it is `k`, its neighbours "
                    "at that moment are exactly `l` and `r`, and the two sides are independent subproblems. Pad the "
                    "array with 1s and fill `dp[l][r] = max(dp[l][k] + dp[k][r] + a[l]·a[k]·a[r])` by increasing "
                    "interval length. **O(n³)**.",
    ),
    dict(
        slug="matrix-chain-multiplication", title="Matrix Chain Multiplication", difficulty="hard",
        topics=["dynamic programming", "interval dp"],
        description="Matrix `i` has dimensions `p[i-1] × p[i]`. Multiplying a `x × y` matrix by a `y × z` matrix "
                    "costs `x·y·z` scalar multiplications. Print the minimum total cost to multiply the whole chain "
                    "(you choose the parenthesisation).",
        input_format="The first line contains `n` (number of matrices). The second line contains `n + 1` integers "
                     "`p[0..n]`.",
        output_format="Print the minimum cost.",
        constraints="- 1 ≤ n ≤ 150\n- 1 ≤ p[i] ≤ 100",
        samples=["3\n10 30 5 60", "1\n5 10"],
        tests=["2\n1 2 3", "4\n40 20 30 10 30", "5\n1 2 3 4 3 1"],
        gen=lambda r: (lambda n: f"{n}\n{' '.join(str(r.randint(1, 100)) for _ in range(n + 1))}")(r.choice([r.randint(1, 10), r.randint(10, 150)])),
        time_limit_ms=3000,
        py=r'''
import sys
data = sys.stdin.read().split()
n = int(data[0])
p = list(map(int, data[1:2 + n]))
INF = float("inf")
dp = [[0] * n for _ in range(n)]  # dp[i][j] = min cost for matrices i..j (0-based)
for length in range(2, n + 1):
    for i in range(n - length + 1):
        j = i + length - 1
        best = INF
        pi, pj = p[i], p[j + 1]
        row = dp[i]
        for k in range(i, j):
            v = row[k] + dp[k + 1][j] + pi * p[k + 1] * pj
            if v < best:
                best = v
        row[j] = best
print(dp[0][n - 1])
''',
        js=r'''
const t = require('fs').readFileSync(0, 'utf8').split(/\s+/).filter(Boolean).map(Number);
const n = t[0], p = t.slice(1, 2 + n);
const dp = Array.from({ length: n }, () => new Array(n).fill(0));
for (let len = 2; len <= n; len++) {
  for (let i = 0; i + len - 1 < n; i++) {
    const j = i + len - 1;
    let best = Infinity;
    for (let k = i; k < j; k++) best = Math.min(best, dp[i][k] + dp[k + 1][j] + p[i] * p[k + 1] * p[j + 1]);
    dp[i][j] = best;
  }
}
console.log(dp[0][n - 1]);
''',
        explanation="Try every split point `k` for the last multiplication: "
                    "`dp[i][j] = min(dp[i][k] + dp[k+1][j] + p[i]·p[k+1]·p[j+1])`. Fill by increasing chain length. "
                    "**O(n³)** time, **O(n²)** space.",
    ),
    dict(
        slug="count-inversions", title="Count Inversions", difficulty="hard", topics=["divide and conquer", "sorting", "fenwick tree"],
        description="An inversion is a pair `i < j` with `a[i] > a[j]`. Count the inversions. O(n²) is too slow.",
        input_format="The first line contains `n`.\nThe second line contains `n` integers.",
        output_format="Print the number of inversions.",
        constraints="- 1 ≤ n ≤ 10^5\n- -10^9 ≤ a[i] ≤ 10^9",
        samples=["5\n2 4 1 3 5", "5\n5 4 3 2 1"],
        tests=["1\n1", "4\n1 1 1 1", "4\n1 2 3 4"],
        gen=lambda r: arr(sorted(rand_arr(r, size(r, 10, 1000, 10000), -10**9, 10**9), reverse=True)) if r.random() < 0.15 else arr(rand_arr(r, size(r, 10, 1000, 10000), -r.choice([5, 10**9]), r.choice([5, 10**9]))),
        py=r'''
import sys
data = sys.stdin.read().split()
a = list(map(int, data[1:1 + int(data[0])]))


def sort_count(arr):
    if len(arr) <= 1:
        return arr, 0
    mid = len(arr) // 2
    left, x = sort_count(arr[:mid])
    right, y = sort_count(arr[mid:])
    merged, inv = [], x + y
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            merged.append(left[i]); i += 1
        else:
            merged.append(right[j]); j += 1
            inv += len(left) - i   # every remaining left element is greater
    merged += left[i:]
    merged += right[j:]
    return merged, inv


print(sort_count(a)[1])
''',
        js=r'''
const t = require('fs').readFileSync(0, 'utf8').split(/\s+/).filter(Boolean).map(Number);
let a = t.slice(1, 1 + t[0]);
const n = a.length;
let buf = new Array(n), inv = 0;
// bottom-up merge sort
for (let width = 1; width < n; width *= 2) {
  for (let lo = 0; lo < n; lo += 2 * width) {
    const mid = Math.min(lo + width, n), hi = Math.min(lo + 2 * width, n);
    let i = lo, j = mid, k = lo;
    while (i < mid && j < hi) {
      if (a[i] <= a[j]) buf[k++] = a[i++];
      else { buf[k++] = a[j++]; inv += mid - i; }
    }
    while (i < mid) buf[k++] = a[i++];
    while (j < hi) buf[k++] = a[j++];
  }
  [a, buf] = [buf, a];
}
console.log(inv);
''',
        explanation="Modify **merge sort**: while merging two sorted halves, whenever an element from the right half is "
                    "taken before remaining elements of the left half, it forms an inversion with each of them "
                    "(`len(left) - i`). **O(n log n)**. A Fenwick tree over compressed values also works.",
    ),
    dict(
        slug="range-sum-with-updates", title="Range Sum with Point Updates", difficulty="hard",
        topics=["fenwick tree", "segment tree"],
        description="Process `q` operations on an array:\n\n- `1 i x` — set `a[i] = x`\n"
                    "- `2 l r` — print `a[l] + … + a[r]`\n\nIndices are 1-based. Both operations must be fast.",
        input_format="Line 1: `n q`. Line 2: `n` integers. Next `q` lines: operations.",
        output_format="Print the answer to each type-2 operation.",
        constraints="- 1 ≤ n, q ≤ 10^5 (at least one query of type 2)\n- -10^9 ≤ a[i], x ≤ 10^9",
        samples=["5 4\n1 2 3 4 5\n2 1 5\n1 3 10\n2 2 4\n2 3 3", "1 1\n-5\n2 1 1"],
        tests=["3 3\n0 0 0\n1 1 5\n1 1 7\n2 1 3", "2 3\n1000000000 1000000000\n2 1 2\n1 2 -1000000000\n2 1 2"],
        gen=gen_fenwick,
        py=r'''
import sys
data = sys.stdin.buffer.read().split()
n, q = int(data[0]), int(data[1])
a = [0] + [int(x) for x in data[2:2 + n]]
tree = [0] * (n + 1)
for i in range(1, n + 1):          # O(n) Fenwick build
    tree[i] += a[i]
    j = i + (i & -i)
    if j <= n:
        tree[j] += tree[i]


def prefix(i):
    s = 0
    while i > 0:
        s += tree[i]
        i -= i & -i
    return s


out = []
p = 2 + n
for _ in range(q):
    t, x, y = int(data[p]), int(data[p + 1]), int(data[p + 2])
    p += 3
    if t == 1:
        delta = y - a[x]
        a[x] = y
        while x <= n:
            tree[x] += delta
            x += x & -x
    else:
        out.append(prefix(y) - prefix(x - 1))
print("\n".join(map(str, out)))
''',
        js=r'''
const t = require('fs').readFileSync(0, 'utf8').split(/\s+/).filter(Boolean).map(Number);
const n = t[0], q = t[1];
const a = [0, ...t.slice(2, 2 + n)];
const tree = new Float64Array(n + 1);
for (let i = 1; i <= n; i++) {
  tree[i] += a[i];
  const j = i + (i & -i);
  if (j <= n) tree[j] += tree[i];
}
const prefix = (i) => { let s = 0; for (; i > 0; i -= i & -i) s += tree[i]; return s; };
const out = [];
for (let k = 0, p = 2 + n; k < q; k++, p += 3) {
  const typ = t[p], x = t[p + 1], y = t[p + 2];
  if (typ === 1) {
    const delta = y - a[x];
    a[x] = y;
    for (let i = x; i <= n; i += i & -i) tree[i] += delta;
  } else out.push(prefix(y) - prefix(x - 1));
}
console.log(out.join('\n'));
''',
        explanation="Prefix sums alone make updates O(n). A **Fenwick tree (Binary Indexed Tree)** stores partial sums "
                    "so that both a point update and a prefix-sum query take **O(log n)**: move by `i & -i` (the "
                    "lowest set bit). Range sum = `prefix(r) - prefix(l - 1)`. A segment tree works too.",
    ),
    dict(
        slug="shortest-path-with-obstacle-elimination", title="Shortest Path with Obstacle Elimination",
        difficulty="hard", topics=["graphs", "bfs", "matrix"],
        description="In a grid, `0` is free and `1` is an obstacle. Moving up/down/left/right takes one step. You may "
                    "walk through **at most `k` obstacles** in total. Print the minimum steps from the top-left to "
                    "the bottom-right cell, or `-1` if impossible. Both corners are free.",
        input_format="The first line contains `r c k`. Each of the next `r` lines contains `c` values.",
        output_format="Print the minimum steps or `-1`.",
        constraints="- 1 ≤ r, c ≤ 40\n- 0 ≤ k ≤ r·c",
        samples=["5 3 1\n0 0 0\n1 1 0\n0 0 0\n0 1 1\n0 0 0", "3 3 1\n0 1 1\n1 1 1\n1 0 0"],
        tests=["1 1 0\n0", "1 3 0\n0 1 0", "1 3 1\n0 1 0"],
        gen=gen_grid_elim,
        py=r'''
import sys
from collections import deque
data = sys.stdin.read().split()
R, C, K = int(data[0]), int(data[1]), int(data[2])
g = [int(x) for x in data[3:3 + R * C]]
K = min(K, R + C)  # a shortest path never needs more eliminations than its length
# best[cell] = the most eliminations left with which we've reached this cell
best = [-1] * (R * C)
best[0] = K
q = deque([(0, K, 0)])
ans = -1
while q:
    cell, k, d = q.popleft()
    if cell == R * C - 1:
        ans = d
        break
    x, y = divmod(cell, C)
    for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
        if 0 <= nx < R and 0 <= ny < C:
            nc = nx * C + ny
            nk = k - g[nc]
            if nk > best[nc]:
                best[nc] = nk
                q.append((nc, nk, d + 1))
print(ans)
''',
        js=r'''
const t = require('fs').readFileSync(0, 'utf8').split(/\s+/).filter(Boolean).map(Number);
const R = t[0], C = t[1], K = Math.min(t[2], R + C);
const g = t.slice(3, 3 + R * C);
const best = new Int32Array(R * C).fill(-1);
best[0] = K;
const q = [[0, K, 0]];
let ans = -1;
for (let h = 0; h < q.length; h++) {
  const [cell, k, d] = q[h];
  if (cell === R * C - 1) { ans = d; break; }
  const x = Math.floor(cell / C), y = cell % C;
  for (const [nx, ny] of [[x + 1, y], [x - 1, y], [x, y + 1], [x, y - 1]]) {
    if (nx < 0 || nx >= R || ny < 0 || ny >= C) continue;
    const nc = nx * C + ny, nk = k - g[nc];
    if (nk > best[nc]) { best[nc] = nk; q.push([nc, nk, d + 1]); }
  }
}
console.log(ans);
''',
        explanation="BFS over states `(cell, eliminations left)`. A plain visited-per-cell BFS is wrong: reaching a "
                    "cell later but with **more** eliminations left can still be better. Keep, per cell, the maximum "
                    "eliminations left seen so far and only revisit when that improves. **O(r·c·k)** worst case.",
    ),
    dict(
        slug="bridges-in-graph", title="Bridges in a Graph", difficulty="hard", topics=["graphs", "dfs", "tarjan"],
        description="A **bridge** is an edge whose removal increases the number of connected components. Find all "
                    "bridges of an undirected simple graph (no self-loops or repeated edges).\n\n"
                    "Print the number of bridges, then each bridge as `u v` with `u < v`, sorted.",
        input_format="The first line contains `n m`. Each of the next `m` lines contains an edge `u v`.",
        output_format="First line: the count. Then one bridge per line.",
        constraints="- 1 ≤ n ≤ 10^5\n- 0 ≤ m ≤ 2·10^5",
        samples=["5 5\n1 2\n2 3\n3 1\n3 4\n4 5", "3 3\n1 2\n2 3\n3 1"],
        tests=["1 0", "2 1\n2 1", "6 7\n1 2\n2 3\n3 1\n3 4\n4 5\n5 6\n6 4"],
        gen=lambda r: gen_simple_graph(r, directed=False),
        py=r'''
import sys
data = sys.stdin.buffer.read().split()
n, m = int(data[0]), int(data[1])
adj = [[] for _ in range(n + 1)]
for i in range(m):
    u, v = int(data[2 + 2 * i]), int(data[3 + 2 * i])
    adj[u].append((v, i))
    adj[v].append((u, i))
tin = [0] * (n + 1)
low = [0] * (n + 1)
timer = 1
bridges = []
for s in range(1, n + 1):
    if tin[s]:
        continue
    tin[s] = low[s] = timer; timer += 1
    stack = [(s, -1, 0)]  # (vertex, edge id used to enter it, next neighbour index)
    while stack:
        v, pe, i = stack[-1]
        if i < len(adj[v]):
            stack[-1] = (v, pe, i + 1)
            to, eid = adj[v][i]
            if eid == pe:
                continue
            if tin[to]:
                low[v] = min(low[v], tin[to])
            else:
                tin[to] = low[to] = timer; timer += 1
                stack.append((to, eid, 0))
        else:
            stack.pop()
            if stack:
                p = stack[-1][0]
                low[p] = min(low[p], low[v])
                if low[v] > tin[p]:
                    bridges.append((min(p, v), max(p, v)))
bridges.sort()
print(len(bridges))
if bridges:
    print("\n".join(f"{u} {v}" for u, v in bridges))
''',
        js=r'''
const t = require('fs').readFileSync(0, 'utf8').split(/\s+/).filter(Boolean).map(Number);
const n = t[0], m = t[1];
const adj = Array.from({ length: n + 1 }, () => []);
for (let i = 0; i < m; i++) { const u = t[2 + 2 * i], v = t[3 + 2 * i]; adj[u].push([v, i]); adj[v].push([u, i]); }
const tin = new Int32Array(n + 1), low = new Int32Array(n + 1);
let timer = 1;
const bridges = [];
for (let s = 1; s <= n; s++) {
  if (tin[s]) continue;
  tin[s] = low[s] = timer++;
  const stack = [[s, -1, 0]];
  while (stack.length) {
    const top = stack[stack.length - 1];
    const [v, pe] = top;
    if (top[2] < adj[v].length) {
      const [to, eid] = adj[v][top[2]++];
      if (eid === pe) continue;
      if (tin[to]) low[v] = Math.min(low[v], tin[to]);
      else { tin[to] = low[to] = timer++; stack.push([to, eid, 0]); }
    } else {
      stack.pop();
      if (stack.length) {
        const p = stack[stack.length - 1][0];
        low[p] = Math.min(low[p], low[v]);
        if (low[v] > tin[p]) bridges.push([Math.min(p, v), Math.max(p, v)]);
      }
    }
  }
}
bridges.sort((a, b) => a[0] - b[0] || a[1] - b[1]);
console.log([bridges.length, ...bridges.map((b) => b.join(' '))].join('\n'));
''',
        explanation="**Tarjan's bridge algorithm**: DFS assigning entry times `tin`, and `low[v]` = the earliest entry "
                    "time reachable from `v`'s subtree using at most one back edge. Tree edge `p → v` is a bridge iff "
                    "`low[v] > tin[p]` (the subtree can't reach `p` or above without it). Iterative DFS avoids stack "
                    "overflow on long paths. **O(n + m)**.",
    ),
    dict(
        slug="strongly-connected-components", title="Strongly Connected Components", difficulty="hard",
        topics=["graphs", "dfs", "kosaraju"],
        description="In a directed graph, a strongly connected component (SCC) is a maximal set of vertices where "
                    "every vertex can reach every other. Print the number of SCCs and the size of the largest one.",
        input_format="The first line contains `n m`. Each of the next `m` lines contains a directed edge `u v`.",
        output_format="Print `count largest`.",
        constraints="- 1 ≤ n ≤ 10^5\n- 0 ≤ m ≤ 2·10^5",
        samples=["5 5\n1 2\n2 3\n3 1\n3 4\n4 5", "3 0"],
        tests=["1 0", "2 2\n1 2\n2 1", "4 4\n1 2\n2 3\n3 4\n4 1"],
        gen=lambda r: gen_simple_graph(r, directed=True),
        py=r'''
import sys
data = sys.stdin.buffer.read().split()
n, m = int(data[0]), int(data[1])
adj = [[] for _ in range(n + 1)]
radj = [[] for _ in range(n + 1)]
for i in range(m):
    u, v = int(data[2 + 2 * i]), int(data[3 + 2 * i])
    adj[u].append(v)
    radj[v].append(u)

# pass 1: order vertices by DFS finish time (iterative)
seen = [False] * (n + 1)
order = []
for s in range(1, n + 1):
    if seen[s]:
        continue
    seen[s] = True
    stack = [(s, 0)]
    while stack:
        v, i = stack[-1]
        if i < len(adj[v]):
            stack[-1] = (v, i + 1)
            w = adj[v][i]
            if not seen[w]:
                seen[w] = True
                stack.append((w, 0))
        else:
            stack.pop()
            order.append(v)

# pass 2: DFS on the reversed graph in decreasing finish time
comp = [0] * (n + 1)
count = largest = 0
for s in reversed(order):
    if comp[s]:
        continue
    count += 1
    comp[s] = count
    stack, sz = [s], 0
    while stack:
        v = stack.pop()
        sz += 1
        for w in radj[v]:
            if not comp[w]:
                comp[w] = count
                stack.append(w)
    largest = max(largest, sz)
print(count, largest)
''',
        js=r'''
const t = require('fs').readFileSync(0, 'utf8').split(/\s+/).filter(Boolean).map(Number);
const n = t[0], m = t[1];
const adj = Array.from({ length: n + 1 }, () => []), radj = Array.from({ length: n + 1 }, () => []);
for (let i = 0; i < m; i++) { const u = t[2 + 2 * i], v = t[3 + 2 * i]; adj[u].push(v); radj[v].push(u); }
const seen = new Uint8Array(n + 1), order = [];
for (let s = 1; s <= n; s++) {
  if (seen[s]) continue;
  seen[s] = 1;
  const stack = [[s, 0]];
  while (stack.length) {
    const top = stack[stack.length - 1], v = top[0];
    if (top[1] < adj[v].length) {
      const w = adj[v][top[1]++];
      if (!seen[w]) { seen[w] = 1; stack.push([w, 0]); }
    } else { stack.pop(); order.push(v); }
  }
}
const comp = new Int32Array(n + 1);
let count = 0, largest = 0;
for (let k = order.length - 1; k >= 0; k--) {
  const s = order[k];
  if (comp[s]) continue;
  comp[s] = ++count;
  const stack = [s];
  let sz = 0;
  while (stack.length) {
    const v = stack.pop();
    sz++;
    for (const w of radj[v]) if (!comp[w]) { comp[w] = count; stack.push(w); }
  }
  largest = Math.max(largest, sz);
}
console.log(`${count} ${largest}`);
''',
        explanation="**Kosaraju's algorithm**: (1) DFS the graph and record vertices in order of finishing time. "
                    "(2) On the **reversed** graph, run DFS from vertices in decreasing finish time; each DFS tree is "
                    "exactly one SCC. Both passes are iterative to handle 10^5-long paths. **O(n + m)**.",
    ),
    dict(
        slug="word-ladder", title="Word Ladder", difficulty="hard", topics=["graphs", "bfs", "strings", "hashing"],
        description="Transform `begin` into `end` by changing one letter at a time; every intermediate word **and** "
                    "`end` must be in the word list (`begin` need not be). Print the number of words in the "
                    "shortest transformation sequence (including `begin` and `end`), or `0` if impossible.",
        input_format="Line 1: `begin end`. Line 2: `n`. Line 3: the `n` words. All words have the same length.",
        output_format="Print the sequence length, or `0`.",
        constraints="- 1 ≤ n ≤ 5000\n- 1 ≤ word length ≤ 10, lowercase letters",
        samples=["hit cog\n6\nhot dot dog lot log cog", "hit cog\n5\nhot dot dog lot log"],
        tests=["a c\n3\na b c", "ab ab\n1\nab", "ab cd\n1\ncd", "abc abd\n1\nabd"],
        gen=gen_ladder,
        py=r'''
import sys
from collections import deque
data = sys.stdin.read().split()
begin, end = data[0], data[1]
words = set(data[3:3 + int(data[2])])
if end not in words:
    print(0)
elif begin == end:
    print(1)
else:
    letters = "abcdefghijklmnopqrstuvwxyz"
    dist = {begin: 1}
    q = deque([begin])
    ans = 0
    while q and not ans:
        w = q.popleft()
        for i in range(len(w)):
            for ch in letters:
                if ch == w[i]:
                    continue
                nw = w[:i] + ch + w[i + 1:]
                if nw in words and nw not in dist:
                    dist[nw] = dist[w] + 1
                    if nw == end:
                        ans = dist[nw]
                        break
                    q.append(nw)
            if ans:
                break
    print(ans)
''',
        js=r'''
const t = require('fs').readFileSync(0, 'utf8').split(/\s+/).filter(Boolean);
const begin = t[0], end = t[1];
const words = new Set(t.slice(3, 3 + Number(t[2])));
let ans = 0;
if (!words.has(end)) ans = 0;
else if (begin === end) ans = 1;
else {
  const dist = new Map([[begin, 1]]);
  const q = [begin];
  outer: for (let h = 0; h < q.length; h++) {
    const w = q[h];
    for (let i = 0; i < w.length; i++) {
      for (let c = 97; c < 123; c++) {
        const ch = String.fromCharCode(c);
        if (ch === w[i]) continue;
        const nw = w.slice(0, i) + ch + w.slice(i + 1);
        if (words.has(nw) && !dist.has(nw)) {
          dist.set(nw, dist.get(w) + 1);
          if (nw === end) { ans = dist.get(nw); break outer; }
          q.push(nw);
        }
      }
    }
  }
}
console.log(ans);
''',
        explanation="Words are vertices, and two words are connected if they differ in one letter. The shortest "
                    "sequence is a **BFS** from `begin`. Rather than comparing every pair of words (O(n²·L)), "
                    "generate each word's neighbours by trying all 26 letters at each position and checking the "
                    "hash set. **O(n · L · 26)**.",
    ),
]
