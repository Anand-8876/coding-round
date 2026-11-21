from _util import arr, rand_arr, size, rand_word, edges_input

HEAP_JS = r'''
class MinHeap {
  // Binary heap ordered by `less(a, b)`.
  constructor(less = (a, b) => a < b) { this.a = []; this.less = less; }
  get size() { return this.a.length; }
  peek() { return this.a[0]; }
  push(x) {
    const a = this.a; a.push(x);
    let i = a.length - 1;
    while (i > 0) { const p = (i - 1) >> 1; if (!this.less(a[i], a[p])) break; [a[i], a[p]] = [a[p], a[i]]; i = p; }
  }
  pop() {
    const a = this.a, top = a[0], last = a.pop();
    if (a.length) {
      a[0] = last;
      let i = 0;
      for (;;) {
        const l = 2 * i + 1, r = l + 1;
        let m = i;
        if (l < a.length && this.less(a[l], a[m])) m = l;
        if (r < a.length && this.less(a[r], a[m])) m = r;
        if (m === i) break;
        [a[i], a[m]] = [a[m], a[i]]; i = m;
      }
    }
    return top;
  }
}
'''


def gen_min_window(r):
    alpha = "abcdef"[: r.randint(1, 6)]
    s = rand_word(r, size(r, 10, 500, 10000), alpha)
    t = rand_word(r, r.randint(1, 8), alpha + ("z" if r.random() < 0.15 else ""))
    return f"{s}\n{t}"


def gen_k_lists(r):
    k = r.randint(1, 50)
    lines = [str(k)]
    for _ in range(k):
        L = r.randint(0, r.choice([5, 50, 400]))
        lines.append(" ".join(map(str, [L] + sorted(rand_arr(r, L, -10**4, 10**4)))))
    return "\n".join(lines)


def gen_regex(r):
    q = r.randint(5, 40)
    out = [str(q)]
    for _ in range(q):
        s = rand_word(r, r.randint(1, 20), "ab")
        p = []
        for _ in range(r.randint(1, 12)):
            p.append(r.choice("ab."))
            if r.random() < 0.4:
                p.append("*")
        out.append(f"{s} {''.join(p)}")
    return "\n".join(out)


def gen_knapsack(r):
    n = r.randint(1, 100)
    W = r.randint(0, 10**4)
    items = [f"{r.randint(1, max(1, W // r.choice([1, 5, 20]) or 1))} {r.randint(0, 10**6)}" for _ in range(n)]
    return f"{n} {W}\n" + "\n".join(items)


def gen_weighted(r, directed):
    n = size(r, 8, 300, 5000)
    m = r.randint(0, min(3 * n, 10000))
    edges = []
    if not directed and r.random() < 0.6:  # usually connected
        for v in range(2, n + 1):
            edges.append((r.randint(1, v - 1), v, r.randint(0, 10**4)))
    edges += [(r.randint(1, n), r.randint(1, n), r.randint(0, 10**4)) for _ in range(m)]
    r.shuffle(edges)
    return n, edges


def gen_dijkstra(r):
    n, edges = gen_weighted(r, True)
    return edges_input(n, edges, f"{n} {len(edges)} {r.randint(1, n)}")


def gen_mst(r):
    n, edges = gen_weighted(r, False)
    return edges_input(n, edges)


def gen_dsu(r):
    n = size(r, 8, 300, 10000)
    q = size(r, 10, 1000, 10000)
    ops = []
    for _ in range(q):
        c = r.random()
        if c < 0.45:
            ops.append(f"union {r.randint(1, n)} {r.randint(1, n)}")
        elif c < 0.9:
            ops.append(f"find {r.randint(1, n)} {r.randint(1, n)}")
        else:
            ops.append("count")
    ops[-1] = "count"
    return f"{n} {q}\n" + "\n".join(ops)


def gen_topo(r):
    n = size(r, 8, 300, 5000)
    order = list(range(1, n + 1))
    r.shuffle(order)
    pos = {v: i for i, v in enumerate(order)}
    edges = set()
    for _ in range(r.randint(0, min(2 * n, 8000))):
        a, b = r.randint(1, n), r.randint(1, n)
        if a != b:
            edges.add((a, b) if pos[a] < pos[b] else (b, a))
    edges = list(edges)
    if edges and r.random() < 0.3:
        a, b = r.choice(edges)
        edges.append((b, a))
    r.shuffle(edges)
    return edges_input(n, edges)


PROBLEMS = [
    dict(
        slug="trapping-rain-water", title="Trapping Rain Water", difficulty="hard", topics=["two pointers", "arrays", "stack"],
        description="`n` bars of width 1 have heights `h[i]`. Compute how much rain water is trapped between the bars "
                    "after it rains.",
        input_format="The first line contains `n`.\nThe second line contains `n` heights.",
        output_format="Print the total trapped water.",
        constraints="- 1 ≤ n ≤ 10^5\n- 0 ≤ h[i] ≤ 10^5",
        samples=["12\n0 1 0 2 1 0 1 3 2 1 2 1", "6\n4 2 0 3 2 5"],
        tests=["1\n5", "3\n1 2 3", "3\n3 0 3", "5\n5 4 3 4 5"],
        gen=lambda r: arr(rand_arr(r, size(r), 0, r.choice([5, 10**5]))),
        py=r'''
import sys
data = sys.stdin.read().split()
n = int(data[0])
h = list(map(int, data[1:1 + n]))
i, j = 0, n - 1
left_max = right_max = water = 0
while i < j:
    if h[i] < h[j]:
        left_max = max(left_max, h[i])
        water += left_max - h[i]
        i += 1
    else:
        right_max = max(right_max, h[j])
        water += right_max - h[j]
        j -= 1
print(water)
''',
        js=r'''
const t = require('fs').readFileSync(0, 'utf8').split(/\s+/).filter(Boolean).map(Number);
const n = t[0], h = t.slice(1, 1 + n);
let i = 0, j = n - 1, lm = 0, rm = 0, water = 0;
while (i < j) {
  if (h[i] < h[j]) { lm = Math.max(lm, h[i]); water += lm - h[i]; i++; }
  else { rm = Math.max(rm, h[j]); water += rm - h[j]; j--; }
}
console.log(water);
''',
        explanation="Water above bar `i` is `min(maxLeft, maxRight) - h[i]`. With two pointers, always advance the "
                    "side with the smaller height: its water level is determined by its own running max, because the "
                    "other side is known to have something at least as tall. **O(n)** time, **O(1)** space.",
    ),
    dict(
        slug="largest-rectangle-in-histogram", title="Largest Rectangle in Histogram", difficulty="hard",
        topics=["stack", "monotonic stack"],
        description="Given bar heights of a histogram (each bar width 1), print the area of the largest rectangle "
                    "that fits inside it.",
        input_format="The first line contains `n`.\nThe second line contains `n` heights.",
        output_format="Print the largest area.",
        constraints="- 1 ≤ n ≤ 10^5\n- 0 ≤ h[i] ≤ 10^4",
        samples=["6\n2 1 5 6 2 3", "2\n2 4"],
        tests=["1\n0", "1\n7", "5\n1 2 3 4 5", "5\n3 3 3 3 3", "4\n0 0 0 0"],
        gen=lambda r: arr(rand_arr(r, size(r), 0, r.choice([5, 10**4]))),
        py=r'''
import sys
data = sys.stdin.read().split()
n = int(data[0])
h = list(map(int, data[1:1 + n])) + [0]
stack, best = [], 0
for i, x in enumerate(h):
    start = i
    while stack and stack[-1][1] >= x:
        j, hj = stack.pop()
        best = max(best, hj * (i - j))
        start = j
    stack.append((start, x))
print(best)
''',
        js=r'''
const t = require('fs').readFileSync(0, 'utf8').split(/\s+/).filter(Boolean).map(Number);
const n = t[0], h = t.slice(1, 1 + n).concat([0]);
const stack = [];
let best = 0;
for (let i = 0; i < h.length; i++) {
  let start = i;
  while (stack.length && stack[stack.length - 1][1] >= h[i]) {
    const [j, hj] = stack.pop();
    best = Math.max(best, hj * (i - j));
    start = j;
  }
  stack.push([start, h[i]]);
}
console.log(best);
''',
        explanation="Keep a stack of `(start index, height)` with increasing heights. When a shorter bar arrives, "
                    "every taller bar on the stack can't extend further right — pop it and compute its rectangle "
                    "`height × (i - start)`. The new bar inherits the start of the last popped bar. A sentinel 0 at "
                    "the end flushes the stack. **O(n)**.",
    ),
    dict(
        slug="minimum-window-substring", title="Minimum Window Substring", difficulty="hard",
        topics=["sliding window", "hashing", "strings"],
        description="Find the shortest substring of `s` that contains every character of `t` (including "
                    "duplicates). If several have the same length, print the **leftmost**. If none exists print `-1`.",
        input_format="Two lines: `s` and `t` (lowercase letters).",
        output_format="Print the window, or `-1`.",
        constraints="- 1 ≤ |s|, |t| ≤ 10^5",
        samples=["adobecodebanc\nabc", "a\naa"],
        tests=["a\na", "ab\nb", "aaflslflsldkalskaaa\naaa", "abc\nd", "bba\nab"],
        gen=gen_min_window,
        py=r'''
from collections import Counter
s = input().strip()
t = input().strip()
need = Counter(t)
missing = len(t)
best_len, best_start = float("inf"), 0
lo = 0
for hi, c in enumerate(s):
    if need[c] > 0:
        missing -= 1
    need[c] -= 1
    while missing == 0:
        if hi - lo + 1 < best_len:
            best_len, best_start = hi - lo + 1, lo
        need[s[lo]] += 1
        if need[s[lo]] > 0:
            missing += 1
        lo += 1
print(s[best_start:best_start + best_len] if best_len != float("inf") else -1)
''',
        js=r'''
const [s, t] = require('fs').readFileSync(0, 'utf8').split('\n').map((x) => x.trim());
const need = new Array(128).fill(0);
for (const c of t) need[c.charCodeAt(0)]++;
let missing = t.length, bestLen = Infinity, bestStart = 0, lo = 0;
for (let hi = 0; hi < s.length; hi++) {
  const c = s.charCodeAt(hi);
  if (need[c] > 0) missing--;
  need[c]--;
  while (missing === 0) {
    if (hi - lo + 1 < bestLen) { bestLen = hi - lo + 1; bestStart = lo; }
    const d = s.charCodeAt(lo);
    need[d]++;
    if (need[d] > 0) missing++;
    lo++;
  }
}
console.log(bestLen === Infinity ? '-1' : s.slice(bestStart, bestStart + bestLen));
''',
        explanation="Sliding window with a count of still-`missing` characters. Expand the right end; once nothing "
                    "is missing, shrink from the left as far as possible, recording the window each time. Using "
                    "strict `<` when comparing lengths keeps the leftmost window. **O(|s| + |t|)**.",
    ),
    dict(
        slug="median-of-data-stream", title="Find Median from Data Stream", difficulty="hard",
        topics=["heap", "design"],
        description="Numbers arrive one at a time. After each number, print the **lower median** of all numbers so "
                    "far — the element at position `⌊(k-1)/2⌋` (0-based) when the `k` numbers are sorted.",
        input_format="The first line contains `n`.\nThe second line contains the `n` numbers in arrival order.",
        output_format="Print `n` values, space-separated.",
        constraints="- 1 ≤ n ≤ 10^5\n- -10^9 ≤ x ≤ 10^9",
        samples=["5\n5 15 1 3 2", "3\n1 1 1"],
        tests=["1\n-7", "4\n4 3 2 1", "4\n1 2 3 4"],
        gen=lambda r: arr(rand_arr(r, size(r), -r.choice([10, 10**9]), r.choice([10, 10**9]))),
        py=r'''
import sys
import heapq
data = sys.stdin.read().split()
low, high = [], []  # low: max-heap (negated), high: min-heap; len(low) == len(high) or len(high) + 1
out = []
for x in map(int, data[1:1 + int(data[0])]):
    if low and x > -low[0]:
        heapq.heappush(high, x)
    else:
        heapq.heappush(low, -x)
    if len(low) > len(high) + 1:
        heapq.heappush(high, -heapq.heappop(low))
    elif len(high) > len(low):
        heapq.heappush(low, -heapq.heappop(high))
    out.append(-low[0])
print(" ".join(map(str, out)))
''',
        js=HEAP_JS + r'''
const t = require('fs').readFileSync(0, 'utf8').split(/\s+/).filter(Boolean).map(Number);
const low = new MinHeap((a, b) => a > b);  // max-heap
const high = new MinHeap();                // min-heap
const out = [];
for (let i = 1; i <= t[0]; i++) {
  const x = t[i];
  if (low.size && x > low.peek()) high.push(x); else low.push(x);
  if (low.size > high.size + 1) high.push(low.pop());
  else if (high.size > low.size) low.push(high.pop());
  out.push(low.peek());
}
console.log(out.join(' '));
''',
        explanation="Keep the smaller half in a **max-heap** and the larger half in a **min-heap**, rebalancing so "
                    "the max-heap has the same size or one more. Its top is always the lower median. **O(log n)** "
                    "per insertion.",
    ),
    dict(
        slug="merge-k-sorted-lists", title="Merge K Sorted Lists", difficulty="hard", topics=["heap", "linked list", "divide and conquer"],
        description="Merge `k` sorted lists into one sorted list. If the result is empty print `EMPTY`.",
        input_format="The first line contains `k`. Each of the next `k` lines starts with the list length `L`, "
                     "followed by `L` sorted integers.",
        output_format="Print the merged list, or `EMPTY`.",
        constraints="- 1 ≤ k ≤ 10^4\n- total elements ≤ 10^5",
        samples=["3\n3 1 4 5\n3 1 3 4\n2 2 6", "2\n0\n0"],
        tests=["1\n1 5", "3\n0\n2 -1 1\n0", "2\n3 1 1 1\n2 1 1"],
        gen=gen_k_lists,
        py=r'''
import sys
import heapq
data = sys.stdin.read().split()
k = int(data[0])
lists, p = [], 1
for _ in range(k):
    L = int(data[p])
    lists.append(list(map(int, data[p + 1:p + 1 + L])))
    p += 1 + L
heap = [(lst[0], i, 0) for i, lst in enumerate(lists) if lst]
heapq.heapify(heap)
out = []
while heap:
    v, i, j = heapq.heappop(heap)
    out.append(v)
    if j + 1 < len(lists[i]):
        heapq.heappush(heap, (lists[i][j + 1], i, j + 1))
print(" ".join(map(str, out)) if out else "EMPTY")
''',
        js=HEAP_JS + r'''
const t = require('fs').readFileSync(0, 'utf8').split(/\s+/).filter(Boolean).map(Number);
const k = t[0], lists = [];
let p = 1;
for (let i = 0; i < k; i++) { const L = t[p]; lists.push(t.slice(p + 1, p + 1 + L)); p += 1 + L; }
const heap = new MinHeap((a, b) => a[0] < b[0] || (a[0] === b[0] && a[1] < b[1]));
lists.forEach((l, i) => { if (l.length) heap.push([l[0], i, 0]); });
const out = [];
while (heap.size) {
  const [v, i, j] = heap.pop();
  out.push(v);
  if (j + 1 < lists[i].length) heap.push([lists[i][j + 1], i, j + 1]);
}
console.log(out.length ? out.join(' ') : 'EMPTY');
''',
        explanation="Put the head of each list in a **min-heap**. Repeatedly pop the smallest element, output it, and "
                    "push the next element from the same list. **O(N log k)** for `N` total elements.",
    ),
    dict(
        slug="edit-distance", title="Edit Distance", difficulty="hard", topics=["dynamic programming", "strings"],
        description="Print the minimum number of single-character operations (insert, delete, replace) needed to "
                    "turn string `a` into string `b`.",
        input_format="Two lines: `a` and `b` (lowercase letters, at least one character each).",
        output_format="Print the edit distance.",
        constraints="- 1 ≤ |a|, |b| ≤ 1000",
        samples=["horse\nros", "intention\nexecution"],
        tests=["a\na", "a\nb", "abc\nabcdef", "kitten\nsitting"],
        gen=lambda r: rand_word(r, r.choice([5, 50, 1000]), "abc") + "\n" + rand_word(r, r.choice([5, 50, 1000]), "abc"),
        time_limit_ms=3000,
        py=r'''
a = input().strip()
b = input().strip()
m = len(b)
prev = list(range(m + 1))
for i, ca in enumerate(a, 1):
    cur = [i] + [0] * m
    for j in range(1, m + 1):
        if ca == b[j - 1]:
            cur[j] = prev[j - 1]
        else:
            cur[j] = 1 + min(prev[j - 1], prev[j], cur[j - 1])
    prev = cur
print(prev[m])
''',
        js=r'''
const [a, b] = require('fs').readFileSync(0, 'utf8').split('\n').map((s) => s.trim());
const m = b.length;
let prev = Int32Array.from({ length: m + 1 }, (_, j) => j);
for (let i = 1; i <= a.length; i++) {
  const cur = new Int32Array(m + 1);
  cur[0] = i;
  for (let j = 1; j <= m; j++) {
    cur[j] = a[i - 1] === b[j - 1] ? prev[j - 1] : 1 + Math.min(prev[j - 1], prev[j], cur[j - 1]);
  }
  prev = cur;
}
console.log(prev[m]);
''',
        explanation="`dp[i][j]` = edits to turn `a[:i]` into `b[:j]`. If the last characters match, "
                    "`dp[i-1][j-1]`; otherwise `1 + min(replace dp[i-1][j-1], delete dp[i-1][j], insert dp[i][j-1])`. "
                    "Base cases: `dp[i][0] = i`, `dp[0][j] = j`. **O(|a|·|b|)** time, one row of memory.",
    ),
    dict(
        slug="palindrome-partitioning-min-cuts", title="Palindrome Partitioning (Minimum Cuts)", difficulty="hard",
        topics=["dynamic programming", "strings"],
        description="Partition `s` so that every piece is a palindrome. Print the minimum number of cuts needed.",
        input_format="A single line containing `s` (lowercase letters).",
        output_format="Print the minimum number of cuts.",
        constraints="- 1 ≤ |s| ≤ 1500",
        samples=["aab", "a"],
        tests=["ab", "abba", "abcde", "aaaaaaaaaaaaaaaaaaaaaaaaa", "abacdcaba", "banana"],
        gen=lambda r: rand_word(r, r.choice([5, 100, 1500]), "ab"[: r.randint(1, 2)] + ("c" if r.random() < 0.5 else "")),
        gen_count=5,
        time_limit_ms=3000,
        py=r'''
s = input().strip()
n = len(s)
cuts = list(range(-1, n))  # cuts[i] = min cuts for s[:i]; cuts[0] = -1
for c in range(n):
    # odd-length palindromes centred at c
    i = j = c
    while i >= 0 and j < n and s[i] == s[j]:
        cuts[j + 1] = min(cuts[j + 1], cuts[i] + 1)
        i -= 1
        j += 1
    # even-length palindromes centred between c and c+1
    i, j = c, c + 1
    while i >= 0 and j < n and s[i] == s[j]:
        cuts[j + 1] = min(cuts[j + 1], cuts[i] + 1)
        i -= 1
        j += 1
print(cuts[n])
''',
        js=r'''
const s = require('fs').readFileSync(0, 'utf8').trim();
const n = s.length;
const cuts = Array.from({ length: n + 1 }, (_, i) => i - 1);
for (let c = 0; c < n; c++) {
  for (const [i0, j0] of [[c, c], [c, c + 1]]) {
    let i = i0, j = j0;
    while (i >= 0 && j < n && s[i] === s[j]) { cuts[j + 1] = Math.min(cuts[j + 1], cuts[i] + 1); i--; j++; }
  }
}
console.log(cuts[n]);
''',
        explanation="`cuts[i]` = minimum cuts for the prefix `s[:i]` (with `cuts[0] = -1`). Expand around every "
                    "centre; whenever `s[i..j]` is a palindrome, `cuts[j+1] = min(cuts[j+1], cuts[i] + 1)`. "
                    "Each expansion step is O(1), so the total is **O(n²)** with O(n) memory.",
    ),
    dict(
        slug="regular-expression-matching", title="Regular Expression Matching", difficulty="hard",
        topics=["dynamic programming", "strings", "recursion"],
        description="Implement pattern matching with `.` (matches any single character) and `*` (matches zero or "
                    "more of the **preceding** element). The pattern must match the **entire** string.\n\n"
                    "Answer `q` independent queries.",
        input_format="The first line contains `q`. Each of the next `q` lines contains `s p`.",
        output_format="`YES` or `NO` for each query.",
        constraints="- 1 ≤ q ≤ 100\n- 1 ≤ |s|, |p| ≤ 30\n- `s` has lowercase letters; `p` has lowercase letters, "
                    "`.` and `*`; every `*` follows a letter or `.`",
        samples=["3\naa a\naa a*\nab .*", "2\naab c*a*b\nmississippi mis*is*p*."],
        tests=["1\na .", "2\nab .*c\naaa a*a", "3\na ab*\nbbbba .*a*a\nabcd d*"],
        gen=gen_regex,
        py=r'''
import sys


def match(s, p):
    n, m = len(s), len(p)
    dp = [[False] * (m + 1) for _ in range(n + 1)]
    dp[n][m] = True
    for i in range(n, -1, -1):
        for j in range(m - 1, -1, -1):
            first = i < n and p[j] in (s[i], ".")
            if j + 1 < m and p[j + 1] == "*":
                dp[i][j] = dp[i][j + 2] or (first and dp[i + 1][j])
            else:
                dp[i][j] = first and dp[i + 1][j + 1]
    return dp[0][0]


lines = sys.stdin.read().split("\n")
q = int(lines[0])
out = []
for k in range(1, q + 1):
    s, p = lines[k].split()
    out.append("YES" if match(s, p) else "NO")
print("\n".join(out))
''',
        js=r'''
function match(s, p) {
  const n = s.length, m = p.length;
  const dp = Array.from({ length: n + 1 }, () => new Array(m + 1).fill(false));
  dp[n][m] = true;
  for (let i = n; i >= 0; i--) {
    for (let j = m - 1; j >= 0; j--) {
      const first = i < n && (p[j] === s[i] || p[j] === '.');
      if (j + 1 < m && p[j + 1] === '*') dp[i][j] = dp[i][j + 2] || (first && dp[i + 1][j]);
      else dp[i][j] = first && dp[i + 1][j + 1];
    }
  }
  return dp[0][0];
}
const lines = require('fs').readFileSync(0, 'utf8').split('\n');
const q = Number(lines[0]), out = [];
for (let k = 1; k <= q; k++) { const [s, p] = lines[k].trim().split(/\s+/); out.push(match(s, p) ? 'YES' : 'NO'); }
console.log(out.join('\n'));
''',
        explanation="`dp[i][j]` = does `s[i:]` match `p[j:]`? If `p[j+1]` is `*`, either skip `x*` entirely "
                    "(`dp[i][j+2]`) or, if the first characters match, consume one character of `s` and stay on the "
                    "same pattern (`dp[i+1][j]`). Otherwise the first characters must match and both advance. "
                    "**O(|s|·|p|)** per query.",
    ),
    dict(
        slug="knapsack-01", title="0/1 Knapsack", difficulty="hard", topics=["dynamic programming"],
        description="There are `n` items with weight `w[i]` and value `v[i]`. Each item can be taken at most once. "
                    "Print the maximum total value with total weight ≤ `W`.",
        input_format="The first line contains `n W`. Each of the next `n` lines contains `w v`.",
        output_format="Print the maximum value.",
        constraints="- 1 ≤ n ≤ 100\n- 0 ≤ W ≤ 10^4\n- 1 ≤ w ≤ 10^4\n- 0 ≤ v ≤ 10^6",
        samples=["3 50\n10 60\n20 100\n30 120", "1 5\n10 100"],
        tests=["1 0\n1 5", "2 10\n10 5\n10 6", "4 7\n1 1\n3 4\n4 5\n5 7"],
        gen=gen_knapsack,
        time_limit_ms=3000,
        py=r'''
import sys
data = sys.stdin.read().split()
n, W = int(data[0]), int(data[1])
dp = [0] * (W + 1)
for i in range(n):
    w, v = int(data[2 + 2 * i]), int(data[3 + 2 * i])
    if w > W:
        continue
    # iterate capacity downwards so each item is used at most once
    for c in range(W, w - 1, -1):
        if dp[c - w] + v > dp[c]:
            dp[c] = dp[c - w] + v
print(dp[W])
''',
        js=r'''
const t = require('fs').readFileSync(0, 'utf8').split(/\s+/).filter(Boolean).map(Number);
const n = t[0], W = t[1];
const dp = new Float64Array(W + 1);
for (let i = 0; i < n; i++) {
  const w = t[2 + 2 * i], v = t[3 + 2 * i];
  for (let c = W; c >= w; c--) if (dp[c - w] + v > dp[c]) dp[c] = dp[c - w] + v;
}
console.log(dp[W]);
''',
        explanation="`dp[c]` = best value with capacity `c`. For each item, update capacities from **high to low** "
                    "(`dp[c] = max(dp[c], dp[c - w] + v)`) — iterating downwards ensures the item is counted at most "
                    "once. Greedy by value/weight ratio does not work. **O(n·W)**.",
    ),
    dict(
        slug="dijkstra-shortest-paths", title="Dijkstra's Shortest Paths", difficulty="hard",
        topics=["graphs", "shortest path", "heap"],
        description="Given a **directed** graph with non-negative edge weights and a source `s`, print the shortest "
                    "distance from `s` to every vertex `1..n` (`-1` if unreachable).",
        input_format="The first line contains `n m s`. Each of the next `m` lines contains `u v w` (edge u → v with "
                     "weight w).",
        output_format="Print `n` distances, space-separated.",
        constraints="- 1 ≤ n ≤ 10^5\n- 0 ≤ m ≤ 2·10^5\n- 0 ≤ w ≤ 10^4",
        samples=["4 5 1\n1 2 4\n1 3 1\n3 2 2\n2 4 1\n3 4 5", "3 1 2\n1 2 5"],
        tests=["1 0 1", "2 2 1\n1 2 0\n2 1 0", "3 3 1\n1 2 10\n1 2 3\n2 3 1"],
        gen=gen_dijkstra,
        py=r'''
import sys
import heapq
data = sys.stdin.buffer.read().split()
n, m, s = int(data[0]), int(data[1]), int(data[2])
adj = [[] for _ in range(n + 1)]
for i in range(m):
    u, v, w = int(data[3 + 3 * i]), int(data[4 + 3 * i]), int(data[5 + 3 * i])
    adj[u].append((v, w))
INF = float("inf")
dist = [INF] * (n + 1)
dist[s] = 0
pq = [(0, s)]
while pq:
    d, u = heapq.heappop(pq)
    if d > dist[u]:
        continue
    for v, w in adj[u]:
        if d + w < dist[v]:
            dist[v] = d + w
            heapq.heappush(pq, (dist[v], v))
print(" ".join(str(d) if d < INF else "-1" for d in dist[1:]))
''',
        js=HEAP_JS + r'''
const t = require('fs').readFileSync(0, 'utf8').split(/\s+/).filter(Boolean).map(Number);
const n = t[0], m = t[1], s = t[2];
const adj = Array.from({ length: n + 1 }, () => []);
for (let i = 0; i < m; i++) adj[t[3 + 3 * i]].push([t[4 + 3 * i], t[5 + 3 * i]]);
const dist = new Array(n + 1).fill(Infinity);
dist[s] = 0;
const pq = new MinHeap((a, b) => a[0] < b[0]);
pq.push([0, s]);
while (pq.size) {
  const [d, u] = pq.pop();
  if (d > dist[u]) continue;
  for (const [v, w] of adj[u]) if (d + w < dist[v]) { dist[v] = d + w; pq.push([dist[v], v]); }
}
console.log(dist.slice(1).map((d) => (d === Infinity ? -1 : d)).join(' '));
''',
        explanation="**Dijkstra**: repeatedly take the unvisited vertex with the smallest tentative distance (via a "
                    "min-heap) and relax its outgoing edges. Stale heap entries (distance larger than the recorded "
                    "one) are skipped. Needs non-negative weights. **O((n + m) log n)**.",
    ),
    dict(
        slug="minimum-spanning-tree", title="Minimum Spanning Tree", difficulty="hard",
        topics=["graphs", "union find", "greedy"],
        description="Given a weighted **undirected** graph, print the total weight of a minimum spanning tree. If the "
                    "graph is not connected, print `-1`.",
        input_format="The first line contains `n m`. Each of the next `m` lines contains `u v w`.",
        output_format="Print the MST weight or `-1`.",
        constraints="- 1 ≤ n ≤ 10^5\n- 0 ≤ m ≤ 2·10^5\n- 0 ≤ w ≤ 10^4 (self-loops and parallel edges may appear)",
        samples=["4 5\n1 2 1\n2 3 2\n3 4 3\n1 4 4\n1 3 5", "3 1\n1 2 1"],
        tests=["1 0", "2 1\n1 1 5", "2 3\n1 2 5\n2 1 3\n1 2 4"],
        gen=gen_mst,
        py=r'''
import sys
data = sys.stdin.buffer.read().split()
n, m = int(data[0]), int(data[1])
edges = sorted((int(data[4 + 3 * i]), int(data[2 + 3 * i]), int(data[3 + 3 * i])) for i in range(m))
parent = list(range(n + 1))


def find(x):
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x


total, used = 0, 0
for w, u, v in edges:
    ru, rv = find(u), find(v)
    if ru != rv:
        parent[ru] = rv
        total += w
        used += 1
print(total if used == n - 1 else -1)
''',
        js=r'''
const t = require('fs').readFileSync(0, 'utf8').split(/\s+/).filter(Boolean).map(Number);
const n = t[0], m = t[1];
const edges = [];
for (let i = 0; i < m; i++) edges.push([t[4 + 3 * i], t[2 + 3 * i], t[3 + 3 * i]]);
edges.sort((a, b) => a[0] - b[0]);
const parent = Array.from({ length: n + 1 }, (_, i) => i);
const find = (x) => { while (parent[x] !== x) { parent[x] = parent[parent[x]]; x = parent[x]; } return x; };
let total = 0, used = 0;
for (const [w, u, v] of edges) {
  const ru = find(u), rv = find(v);
  if (ru !== rv) { parent[ru] = rv; total += w; used++; }
}
console.log(used === n - 1 ? total : -1);
''',
        explanation="**Kruskal's algorithm**: sort edges by weight and add each edge that connects two different "
                    "components, tracked with a **union-find** structure. If fewer than `n - 1` edges get added the "
                    "graph is disconnected. **O(m log m)**.",
    ),
    dict(
        slug="union-find-connectivity", title="Dynamic Connectivity (Union-Find)", difficulty="hard",
        topics=["union find", "design"],
        description="There are `n` isolated vertices. Process `q` operations:\n\n"
                    "- `union a b` — connect `a` and `b`\n- `find a b` — print `YES` if `a` and `b` are connected, "
                    "else `NO`\n- `count` — print the current number of connected components",
        input_format="The first line contains `n q`. Each of the next `q` lines contains an operation.",
        output_format="Print the answer for each `find` and `count`.",
        constraints="- 1 ≤ n, q ≤ 2·10^5 (at least one `find` or `count`)",
        samples=["5 6\nfind 1 2\nunion 1 2\nfind 1 2\nunion 3 4\nunion 2 4\ncount", "1 1\ncount"],
        tests=["3 3\nunion 1 1\ncount\nfind 2 2", "4 4\nunion 1 2\nunion 2 1\ncount\nfind 1 3"],
        gen=gen_dsu,
        py=r'''
import sys
lines = sys.stdin.read().split("\n")
n, q = map(int, lines[0].split())
parent = list(range(n + 1))
rank = [0] * (n + 1)
comps = n


def find(x):
    root = x
    while parent[root] != root:
        root = parent[root]
    while parent[x] != root:          # path compression
        parent[x], x = root, parent[x]
    return root


out = []
for k in range(1, q + 1):
    op = lines[k].split()
    if op[0] == "union":
        a, b = find(int(op[1])), find(int(op[2]))
        if a != b:
            if rank[a] < rank[b]:
                a, b = b, a
            parent[b] = a
            if rank[a] == rank[b]:
                rank[a] += 1
            comps -= 1
    elif op[0] == "find":
        out.append("YES" if find(int(op[1])) == find(int(op[2])) else "NO")
    else:
        out.append(str(comps))
print("\n".join(out))
''',
        js=r'''
const lines = require('fs').readFileSync(0, 'utf8').split('\n');
const [n, q] = lines[0].trim().split(/\s+/).map(Number);
const parent = Int32Array.from({ length: n + 1 }, (_, i) => i);
const rank = new Int32Array(n + 1);
let comps = n;
function find(x) {
  let root = x;
  while (parent[root] !== root) root = parent[root];
  while (parent[x] !== root) { const nx = parent[x]; parent[x] = root; x = nx; }
  return root;
}
const out = [];
for (let k = 1; k <= q; k++) {
  const op = lines[k].trim().split(/\s+/);
  if (op[0] === 'union') {
    let a = find(Number(op[1])), b = find(Number(op[2]));
    if (a !== b) {
      if (rank[a] < rank[b]) [a, b] = [b, a];
      parent[b] = a;
      if (rank[a] === rank[b]) rank[a]++;
      comps--;
    }
  } else if (op[0] === 'find') out.push(find(Number(op[1])) === find(Number(op[2])) ? 'YES' : 'NO');
  else out.push(comps);
}
console.log(out.join('\n'));
''',
        explanation="A **disjoint set union** stores a parent pointer per vertex; the root identifies the component. "
                    "With **union by rank** and **path compression**, each operation is nearly O(1) (amortised "
                    "inverse-Ackermann). Decrement the component count on every successful union.",
    ),
    dict(
        slug="lexicographic-topological-sort", title="Smallest Topological Order", difficulty="hard",
        topics=["graphs", "topological sort", "heap"],
        description="Given a directed graph with vertices `1..n`, print the **lexicographically smallest** "
                    "topological ordering (for every edge `u → v`, `u` comes before `v`). If the graph has a cycle, "
                    "print `-1`.",
        input_format="The first line contains `n m`. Each of the next `m` lines contains an edge `u v`.",
        output_format="Print the ordering, or `-1`.",
        constraints="- 1 ≤ n ≤ 10^5\n- 0 ≤ m ≤ 2·10^5",
        samples=["4 3\n1 2\n4 3\n2 3", "2 2\n1 2\n2 1"],
        tests=["1 0", "3 0", "3 2\n3 1\n3 2", "2 1\n1 1"],
        gen=gen_topo,
        py=r'''
import sys
import heapq
data = sys.stdin.buffer.read().split()
n, m = int(data[0]), int(data[1])
adj = [[] for _ in range(n + 1)]
indeg = [0] * (n + 1)
for i in range(m):
    u, v = int(data[2 + 2 * i]), int(data[3 + 2 * i])
    adj[u].append(v)
    indeg[v] += 1
pq = [v for v in range(1, n + 1) if indeg[v] == 0]
heapq.heapify(pq)
order = []
while pq:
    u = heapq.heappop(pq)
    order.append(u)
    for v in adj[u]:
        indeg[v] -= 1
        if indeg[v] == 0:
            heapq.heappush(pq, v)
print(" ".join(map(str, order)) if len(order) == n else -1)
''',
        js=HEAP_JS + r'''
const t = require('fs').readFileSync(0, 'utf8').split(/\s+/).filter(Boolean).map(Number);
const n = t[0], m = t[1];
const adj = Array.from({ length: n + 1 }, () => []);
const indeg = new Int32Array(n + 1);
for (let i = 0; i < m; i++) { adj[t[2 + 2 * i]].push(t[3 + 2 * i]); indeg[t[3 + 2 * i]]++; }
const pq = new MinHeap();
for (let v = 1; v <= n; v++) if (indeg[v] === 0) pq.push(v);
const order = [];
while (pq.size) {
  const u = pq.pop();
  order.push(u);
  for (const v of adj[u]) if (--indeg[v] === 0) pq.push(v);
}
console.log(order.length === n ? order.join(' ') : '-1');
''',
        explanation="Kahn's algorithm with a **min-heap** instead of a queue: always output the smallest vertex whose "
                    "in-degree is 0. That greedy choice gives the lexicographically smallest order. If not all "
                    "vertices are output, a cycle exists. **O((n + m) log n)**.",
    ),
]
