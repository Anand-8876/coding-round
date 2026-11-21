from _util import arr, rand_arr, size, rand_word, tree_input, random_tree, level_order, edges_input

TREE_IN = ("The first line contains `m`, the number of tokens. The second line contains the tree in **level order**: "
           "the root value, then for each present node its left and right child, with `-1` meaning no child "
           "(trailing `-1`s may be omitted). All node values are ≥ 0.")

TREE_PARSE_PY = r'''
def parse_tree(tok):
    """Level-order tokens -> (val, left, right) arrays; node 0 is the root, -1 = no child.
    Children always get larger ids than their parent (BFS order)."""
    val, left, right = [int(tok[0])], [-1], [-1]
    i, cur = 1, 0
    while i < len(tok):
        for side in (left, right):
            if i < len(tok) and tok[i] != "-1":
                side[cur] = len(val)
                val.append(int(tok[i]))
                left.append(-1)
                right.append(-1)
            i += 1
        cur += 1
    return val, left, right
'''

TREE_PARSE_JS = r'''
function parseTree(tok) {
  // Level-order tokens -> {val, left, right}; node 0 is the root, -1 = no child.
  // Children always get larger ids than their parent (BFS order).
  const val = [Number(tok[0])], left = [-1], right = [-1];
  let i = 1, cur = 0;
  while (i < tok.length) {
    for (const side of [left, right]) {
      if (i < tok.length && tok[i] !== '-1') {
        side[cur] = val.length;
        val.push(Number(tok[i])); left.push(-1); right.push(-1);
      }
      i++;
    }
    cur++;
  }
  return { val, left, right };
}
'''


def gen_bad_bst(r):
    n = size(r, 8, 200, 3000)
    root, ch = random_tree(r, n, 0, 10**6, bst=True)
    s = level_order(root, ch)
    if r.random() < 0.5 and n > 1:
        head, toks = s.split("\n")
        toks = toks.split()
        idx = [i for i, t in enumerate(toks) if t != "-1"]
        i, j = r.sample(idx, 2)
        if r.random() < 0.5:
            toks[i], toks[j] = toks[j], toks[i]
        else:
            toks[i] = toks[j]  # duplicate value -> not a strict BST
        s = head + "\n" + " ".join(toks)
    return s


def gen_lca(r):
    n = size(r, 8, 300, 3000)
    root, ch = random_tree(r, n, 0, 10**6, bst=True)
    nodes = list(ch)
    q = size(r, 5, 100, 2000)
    qs = [f"{r.choice(nodes)} {r.choice(nodes)}" for _ in range(q)]
    return level_order(root, ch) + f"\n{q}\n" + "\n".join(qs)


def gen_islands(r):
    R, C = r.randint(1, 60), r.randint(1, 60)
    p = r.random()
    return f"{R} {C}\n" + "\n".join("".join("1" if r.random() < p else "0" for _ in range(C)) for _ in range(R))


def gen_oranges(r):
    R, C = r.randint(1, 50), r.randint(1, 50)
    w = [r.random(), r.random(), r.random() * 0.1]
    rows = [" ".join(str(r.choices([0, 1, 2], w)[0]) for _ in range(C)) for _ in range(R)]
    return f"{R} {C}\n" + "\n".join(rows)


def gen_dag(r):
    n = size(r, 8, 300, 3000)
    m = r.randint(0, min(3 * n, 6000))
    order = list(range(1, n + 1))
    r.shuffle(order)
    pos = {v: i for i, v in enumerate(order)}
    edges = []
    for _ in range(m):
        a, b = r.randint(1, n), r.randint(1, n)
        if a == b:
            continue
        if pos[a] > pos[b]:
            a, b = b, a
        edges.append((b, a))  # "b requires a"
    if edges and r.random() < 0.5:
        a, b = edges[r.randrange(len(edges))]
        edges.append((b, a))  # create a cycle
    return edges_input(n, edges)


def gen_graph_path(r):
    n = size(r, 8, 300, 5000)
    m = r.randint(0, min(2 * n, 8000))
    edges = [(r.randint(1, n), r.randint(1, n)) for _ in range(m)]
    return edges_input(n, edges, f"{n} {m} {r.randint(1, n)} {r.randint(1, n)}")


def gen_obstacle_grid(r):
    R, C = r.randint(1, 100), r.randint(1, 100)
    p = r.choice([0.0, 0.05, 0.2, 0.4])
    g = [["1" if r.random() < p else "0" for _ in range(C)] for _ in range(R)]
    if r.random() < 0.8:
        g[0][0] = g[-1][-1] = "0"
    return f"{R} {C}\n" + "\n".join(" ".join(row) for row in g)


def gen_word_break(r):
    words = list({rand_word(r, r.randint(1, 4), "ab") for _ in range(r.randint(1, 8))})
    s = "".join(r.choice(words) for _ in range(r.randint(1, 60)))
    if r.random() < 0.5:
        s = s[:-1] + r.choice("abc") if len(s) > 1 else s
    return f"{s}\n{len(words)}\n{' '.join(words)}"


PROBLEMS = [
    dict(
        slug="decode-string", title="Decode String", difficulty="medium", topics=["stack", "strings", "recursion"],
        description="An encoded string uses the rule `k[text]`, meaning `text` repeated `k` times. Encodings can be "
                    "nested. Decode it.\n\nExamples: `3[a]2[bc]` → `aaabcbc`, `3[a2[c]]` → `accaccacc`.",
        input_format="A single line containing the encoded string (lowercase letters, digits and brackets).",
        output_format="Print the decoded string.",
        constraints="- 1 ≤ |s| ≤ 1000\n- 1 ≤ k ≤ 300\n- the decoded string has length ≤ 10^5",
        samples=["3[a]2[bc]", "3[a2[c]]"],
        tests=["abc", "2[abc]3[cd]ef", "10[z]", "1[1[1[x]]]", "2[a2[b2[c]]]d", "100[ab]", "3[z]2[2[y]pq4[2[jk]e1[f]]]ef",
               "abc3[cd]xyz"],
        py=r'''
s = input().strip()
stack = []  # (previous string, repeat count)
cur, num = [], 0
for c in s:
    if c.isdigit():
        num = num * 10 + int(c)
    elif c == "[":
        stack.append((cur, num))
        cur, num = [], 0
    elif c == "]":
        prev, k = stack.pop()
        prev.append("".join(cur) * k)
        cur = prev
    else:
        cur.append(c)
print("".join(cur))
''',
        js=r'''
const s = require('fs').readFileSync(0, 'utf8').trim();
const stack = [];
let cur = '', num = 0;
for (const c of s) {
  if (c >= '0' && c <= '9') num = num * 10 + Number(c);
  else if (c === '[') { stack.push([cur, num]); cur = ''; num = 0; }
  else if (c === ']') { const [prev, k] = stack.pop(); cur = prev + cur.repeat(k); }
  else cur += c;
}
console.log(cur);
''',
        explanation="Use a stack. On `[`, push the text built so far together with the repeat count and start a new "
                    "segment. On `]`, pop, repeat the current segment `k` times and append it to the popped text. "
                    "Multi-digit counts are accumulated digit by digit. **O(output length)**.",
    ),
    dict(
        slug="binary-tree-level-order", title="Binary Tree Level Order Traversal", difficulty="medium",
        topics=["trees", "bfs"],
        description="Print the values of a binary tree level by level, left to right, one level per line.",
        input_format=TREE_IN,
        output_format="One line per level containing that level's values.",
        constraints="- 1 ≤ nodes ≤ 10^4\n- 0 ≤ value ≤ 10^4",
        samples=["7\n3 9 20 -1 -1 15 7", "1\n1"],
        tests=["3\n1 -1 2", "5\n1 2 -1 3 -1"],
        gen=lambda r: tree_input(r, size(r, 8, 300, 5000)),
        py=TREE_PARSE_PY + r'''
import sys
data = sys.stdin.read().split()
val, left, right = parse_tree(data[1:1 + int(data[0])])
level, out = [0], []
while level:
    out.append(" ".join(str(val[v]) for v in level))
    level = [c for v in level for c in (left[v], right[v]) if c != -1]
print("\n".join(out))
''',
        js=TREE_PARSE_JS + r'''
const t = require('fs').readFileSync(0, 'utf8').split(/\s+/).filter(Boolean);
const { val, left, right } = parseTree(t.slice(1, 1 + Number(t[0])));
const out = [];
let level = [0];
while (level.length) {
  out.push(level.map((v) => val[v]).join(' '));
  const next = [];
  for (const v of level) { if (left[v] !== -1) next.push(left[v]); if (right[v] !== -1) next.push(right[v]); }
  level = next;
}
console.log(out.join('\n'));
''',
        explanation="**Breadth-first search** one level at a time: start with `[root]`; the next level is all "
                    "children of the current level, in order. **O(n)**.",
    ),
    dict(
        slug="diameter-of-binary-tree", title="Diameter of Binary Tree", difficulty="medium",
        topics=["trees", "dfs"],
        description="The diameter of a binary tree is the number of **edges** on the longest path between any two "
                    "nodes. Print it.",
        input_format=TREE_IN,
        output_format="Print the diameter.",
        constraints="- 1 ≤ nodes ≤ 10^4 (the tree may be very deep)",
        samples=["5\n1 2 3 4 5", "1\n1"],
        tests=["3\n1 2 -1", "7\n1 2 -1 3 -1 4 -1"],
        gen=lambda r: tree_input(r, size(r, 8, 300, 10000)),
        py=TREE_PARSE_PY + r'''
import sys
data = sys.stdin.read().split()
val, left, right = parse_tree(data[1:1 + int(data[0])])
n = len(val)
height = [0] * n  # edges from node down to its deepest leaf
best = 0
for v in range(n - 1, -1, -1):  # children have larger ids -> bottom-up order
    hl = height[left[v]] + 1 if left[v] != -1 else 0
    hr = height[right[v]] + 1 if right[v] != -1 else 0
    height[v] = max(hl, hr)
    best = max(best, hl + hr)
print(best)
''',
        js=TREE_PARSE_JS + r'''
const t = require('fs').readFileSync(0, 'utf8').split(/\s+/).filter(Boolean);
const { val, left, right } = parseTree(t.slice(1, 1 + Number(t[0])));
const n = val.length, height = new Array(n).fill(0);
let best = 0;
for (let v = n - 1; v >= 0; v--) {
  const hl = left[v] !== -1 ? height[left[v]] + 1 : 0;
  const hr = right[v] !== -1 ? height[right[v]] + 1 : 0;
  height[v] = Math.max(hl, hr);
  best = Math.max(best, hl + hr);
}
console.log(best);
''',
        explanation="For each node, the longest path that turns at that node is `height(left) + height(right)` (in "
                    "edges). Compute heights bottom-up (post-order) and take the maximum over all nodes. **O(n)**. "
                    "The tree can be 10^4 deep, so a recursive DFS may overflow the stack — process nodes in reverse "
                    "BFS order (or raise the recursion limit).",
    ),
    dict(
        slug="validate-bst", title="Validate Binary Search Tree", difficulty="medium", topics=["trees", "bst"],
        description="Print `YES` if the tree is a valid **binary search tree**: for every node, all values in its "
                    "left subtree are strictly smaller and all values in its right subtree are strictly larger. "
                    "Otherwise print `NO`.",
        input_format=TREE_IN,
        output_format="`YES` or `NO`.",
        constraints="- 1 ≤ nodes ≤ 10^4\n- 0 ≤ value ≤ 10^6",
        samples=["3\n2 1 3", "7\n5 1 4 -1 -1 3 6"],
        tests=["1\n0", "3\n1 1 -1", "7\n5 4 6 -1 -1 3 7", "3\n2 -1 3"],
        gen=gen_bad_bst,
        py=TREE_PARSE_PY + r'''
import sys
data = sys.stdin.read().split()
val, left, right = parse_tree(data[1:1 + int(data[0])])
ok = True
stack = [(0, float("-inf"), float("inf"))]
while stack and ok:
    v, lo, hi = stack.pop()
    if not lo < val[v] < hi:
        ok = False
        break
    if left[v] != -1:
        stack.append((left[v], lo, val[v]))
    if right[v] != -1:
        stack.append((right[v], val[v], hi))
print("YES" if ok else "NO")
''',
        js=TREE_PARSE_JS + r'''
const t = require('fs').readFileSync(0, 'utf8').split(/\s+/).filter(Boolean);
const { val, left, right } = parseTree(t.slice(1, 1 + Number(t[0])));
let ok = true;
const stack = [[0, -Infinity, Infinity]];
while (stack.length) {
  const [v, lo, hi] = stack.pop();
  if (!(lo < val[v] && val[v] < hi)) { ok = false; break; }
  if (left[v] !== -1) stack.push([left[v], lo, val[v]]);
  if (right[v] !== -1) stack.push([right[v], val[v], hi]);
}
console.log(ok ? 'YES' : 'NO');
''',
        explanation="Checking only each node against its direct children is **wrong** (see sample 2). Instead pass "
                    "down an allowed range `(lo, hi)`: the left child must lie in `(lo, node)` and the right child in "
                    "`(node, hi)`. **O(n)**.",
    ),
    dict(
        slug="lca-in-bst", title="Lowest Common Ancestor in a BST", difficulty="medium", topics=["trees", "bst"],
        description="Given a binary search tree with distinct values and `q` queries `u v` (both values exist in the "
                    "tree), print the value of their **lowest common ancestor** — the deepest node that has both as "
                    "descendants (a node is a descendant of itself).",
        input_format=TREE_IN + "\nThen a line with `q`, followed by `q` lines `u v`.",
        output_format="Print the LCA value for each query.",
        constraints="- 1 ≤ nodes ≤ 10^4\n- 1 ≤ q ≤ 10^4",
        samples=["11\n6 2 8 0 4 7 9 -1 -1 3 5\n3\n2 8\n2 4\n3 5", "1\n1\n1\n1 1"],
        tests=["3\n2 1 -1\n2\n1 2\n1 1", "7\n4 2 6 1 3 5 7\n4\n1 3\n5 7\n1 7\n6 5"],
        gen=gen_lca,
        py=TREE_PARSE_PY + r'''
import sys
data = sys.stdin.read().split()
m = int(data[0])
val, left, right = parse_tree(data[1:1 + m])
q = int(data[1 + m])
out = []
for i in range(q):
    u, v = int(data[2 + m + 2 * i]), int(data[3 + m + 2 * i])
    lo, hi = min(u, v), max(u, v)
    cur = 0
    while True:
        if hi < val[cur]:
            cur = left[cur]
        elif lo > val[cur]:
            cur = right[cur]
        else:
            break
    out.append(str(val[cur]))
print("\n".join(out))
''',
        js=TREE_PARSE_JS + r'''
const t = require('fs').readFileSync(0, 'utf8').split(/\s+/).filter(Boolean);
const m = Number(t[0]);
const { val, left, right } = parseTree(t.slice(1, 1 + m));
const q = Number(t[1 + m]), out = [];
for (let i = 0; i < q; i++) {
  const u = Number(t[2 + m + 2 * i]), v = Number(t[3 + m + 2 * i]);
  const lo = Math.min(u, v), hi = Math.max(u, v);
  let cur = 0;
  for (;;) {
    if (hi < val[cur]) cur = left[cur];
    else if (lo > val[cur]) cur = right[cur];
    else break;
  }
  out.push(val[cur]);
}
console.log(out.join('\n'));
''',
        explanation="Walk down from the root. If both values are smaller than the current node, the LCA is in the "
                    "left subtree; if both are larger, in the right subtree; otherwise the paths split here, so the "
                    "current node is the LCA. **O(h)** per query.",
    ),
    dict(
        slug="number-of-islands", title="Number of Islands", difficulty="medium", topics=["graphs", "bfs", "dfs", "matrix"],
        description="Given a grid of `1` (land) and `0` (water), count the islands. An island is a group of land "
                    "cells connected horizontally or vertically.",
        input_format="The first line contains `r c`. Each of the next `r` lines is a string of `c` characters "
                     "(`0` or `1`).",
        output_format="Print the number of islands.",
        constraints="- 1 ≤ r, c ≤ 300",
        samples=["4 5\n11110\n11010\n11000\n00000", "4 5\n11000\n11000\n00100\n00011"],
        tests=["1 1\n0", "1 1\n1", "3 3\n101\n010\n101"],
        gen=gen_islands,
        py=r'''
import sys
lines = sys.stdin.read().split()
R, C = int(lines[0]), int(lines[1])
g = [list(row) for row in lines[2:2 + R]]
count = 0
for i in range(R):
    for j in range(C):
        if g[i][j] == "1":
            count += 1
            g[i][j] = "0"
            stack = [(i, j)]
            while stack:
                x, y = stack.pop()
                for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                    if 0 <= nx < R and 0 <= ny < C and g[nx][ny] == "1":
                        g[nx][ny] = "0"
                        stack.append((nx, ny))
print(count)
''',
        js=r'''
const t = require('fs').readFileSync(0, 'utf8').split(/\s+/).filter(Boolean);
const R = Number(t[0]), C = Number(t[1]);
const g = t.slice(2, 2 + R).map((row) => row.split(''));
let count = 0;
for (let i = 0; i < R; i++) for (let j = 0; j < C; j++) {
  if (g[i][j] !== '1') continue;
  count++;
  g[i][j] = '0';
  const stack = [[i, j]];
  while (stack.length) {
    const [x, y] = stack.pop();
    for (const [nx, ny] of [[x + 1, y], [x - 1, y], [x, y + 1], [x, y - 1]]) {
      if (nx >= 0 && nx < R && ny >= 0 && ny < C && g[nx][ny] === '1') { g[nx][ny] = '0'; stack.push([nx, ny]); }
    }
  }
}
console.log(count);
''',
        explanation="Scan the grid; every time you find unvisited land, that's a new island — flood-fill it (DFS/BFS) "
                    "marking all connected land as visited. Use an explicit stack to avoid recursion limits on big "
                    "islands. **O(r·c)**.",
    ),
    dict(
        slug="rotting-oranges", title="Rotting Oranges", difficulty="medium", topics=["graphs", "bfs", "matrix"],
        description="Each cell is `0` (empty), `1` (fresh orange) or `2` (rotten orange). Every minute, fresh oranges "
                    "adjacent (up/down/left/right) to a rotten one become rotten. Print the minimum minutes until no "
                    "fresh orange remains, or `-1` if that is impossible.",
        input_format="The first line contains `r c`. Each of the next `r` lines contains `c` integers.",
        output_format="Print the number of minutes, or `-1`.",
        constraints="- 1 ≤ r, c ≤ 100",
        samples=["3 3\n2 1 1\n1 1 0\n0 1 1", "3 3\n2 1 1\n0 1 1\n1 0 1"],
        tests=["1 2\n0 2", "1 1\n1", "1 1\n0", "1 5\n2 1 1 1 1"],
        gen=gen_oranges,
        py=r'''
import sys
data = sys.stdin.read().split()
R, C = int(data[0]), int(data[1])
g = [[int(data[2 + i * C + j]) for j in range(C)] for i in range(R)]
frontier = [(i, j) for i in range(R) for j in range(C) if g[i][j] == 2]
fresh = sum(row.count(1) for row in g)
minutes = 0
while frontier and fresh:
    nxt = []
    for x, y in frontier:
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= nx < R and 0 <= ny < C and g[nx][ny] == 1:
                g[nx][ny] = 2
                fresh -= 1
                nxt.append((nx, ny))
    frontier = nxt
    minutes += 1
print(minutes if fresh == 0 else -1)
''',
        js=r'''
const t = require('fs').readFileSync(0, 'utf8').split(/\s+/).filter(Boolean).map(Number);
const R = t[0], C = t[1];
const g = [];
for (let i = 0; i < R; i++) g.push(t.slice(2 + i * C, 2 + (i + 1) * C));
let frontier = [], fresh = 0;
for (let i = 0; i < R; i++) for (let j = 0; j < C; j++) {
  if (g[i][j] === 2) frontier.push([i, j]);
  else if (g[i][j] === 1) fresh++;
}
let minutes = 0;
while (frontier.length && fresh) {
  const next = [];
  for (const [x, y] of frontier) {
    for (const [nx, ny] of [[x + 1, y], [x - 1, y], [x, y + 1], [x, y - 1]]) {
      if (nx >= 0 && nx < R && ny >= 0 && ny < C && g[nx][ny] === 1) { g[nx][ny] = 2; fresh--; next.push([nx, ny]); }
    }
  }
  frontier = next;
  minutes++;
}
console.log(fresh === 0 ? minutes : -1);
''',
        explanation="**Multi-source BFS**: start with all rotten oranges in the queue at once. Each BFS layer is one "
                    "minute. Count fresh oranges; if any remain when the BFS ends, return -1. **O(r·c)**.",
    ),
    dict(
        slug="course-schedule", title="Course Schedule", difficulty="medium",
        topics=["graphs", "topological sort", "cycle detection"],
        description="There are `n` courses labelled `1..n` and `m` prerequisite pairs `a b`, meaning you must take "
                    "course `b` before course `a`. Print `YES` if it is possible to finish all courses, otherwise "
                    "`NO`.",
        input_format="The first line contains `n m`. Each of the next `m` lines contains `a b`.",
        output_format="`YES` or `NO`.",
        constraints="- 1 ≤ n ≤ 10^4\n- 0 ≤ m ≤ 2·10^4",
        samples=["2 1\n2 1", "2 2\n2 1\n1 2"],
        tests=["1 0", "3 3\n2 1\n3 2\n1 3", "4 3\n2 1\n3 1\n4 3", "1 1\n1 1"],
        gen=gen_dag,
        py=r'''
import sys
from collections import deque
data = sys.stdin.read().split()
n, m = int(data[0]), int(data[1])
adj = [[] for _ in range(n + 1)]
indeg = [0] * (n + 1)
for i in range(m):
    a, b = int(data[2 + 2 * i]), int(data[3 + 2 * i])
    adj[b].append(a)
    indeg[a] += 1
q = deque(v for v in range(1, n + 1) if indeg[v] == 0)
done = 0
while q:
    v = q.popleft()
    done += 1
    for w in adj[v]:
        indeg[w] -= 1
        if indeg[w] == 0:
            q.append(w)
print("YES" if done == n else "NO")
''',
        js=r'''
const t = require('fs').readFileSync(0, 'utf8').split(/\s+/).filter(Boolean).map(Number);
const n = t[0], m = t[1];
const adj = Array.from({ length: n + 1 }, () => []);
const indeg = new Array(n + 1).fill(0);
for (let i = 0; i < m; i++) { const a = t[2 + 2 * i], b = t[3 + 2 * i]; adj[b].push(a); indeg[a]++; }
const q = [];
for (let v = 1; v <= n; v++) if (indeg[v] === 0) q.push(v);
let done = 0;
for (let h = 0; h < q.length; h++) {
  done++;
  for (const w of adj[q[h]]) if (--indeg[w] === 0) q.push(w);
}
console.log(done === n ? 'YES' : 'NO');
''',
        explanation="Courses and prerequisites form a directed graph; all courses can be finished iff it has **no "
                    "cycle**. **Kahn's algorithm**: repeatedly take a course with no remaining prerequisites "
                    "(in-degree 0) and remove its outgoing edges. If every course gets taken, there is no cycle. "
                    "**O(n + m)**.",
    ),
    dict(
        slug="shortest-path-unweighted", title="Shortest Path in an Unweighted Graph", difficulty="medium",
        topics=["graphs", "bfs"],
        description="Given an undirected graph with `n` vertices and `m` edges, print the minimum number of edges on "
                    "a path from `s` to `t`, or `-1` if `t` is unreachable.",
        input_format="The first line contains `n m s t`. Each of the next `m` lines contains an edge `u v`.",
        output_format="Print the distance or `-1`.",
        constraints="- 1 ≤ n ≤ 10^5\n- 0 ≤ m ≤ 2·10^5\n- self-loops and repeated edges may appear",
        samples=["5 5 1 5\n1 2\n2 3\n3 5\n1 4\n4 3", "3 1 1 3\n1 2"],
        tests=["1 0 1 1", "2 1 2 1\n1 2", "3 2 1 3\n1 1\n2 3"],
        gen=gen_graph_path,
        py=r'''
import sys
from collections import deque
data = sys.stdin.buffer.read().split()
n, m, s, t = map(int, data[:4])
adj = [[] for _ in range(n + 1)]
for i in range(m):
    u, v = int(data[4 + 2 * i]), int(data[5 + 2 * i])
    adj[u].append(v)
    adj[v].append(u)
dist = [-1] * (n + 1)
dist[s] = 0
q = deque([s])
while q:
    u = q.popleft()
    for v in adj[u]:
        if dist[v] == -1:
            dist[v] = dist[u] + 1
            q.append(v)
print(dist[t])
''',
        js=r'''
const d = require('fs').readFileSync(0, 'utf8').split(/\s+/).filter(Boolean).map(Number);
const [n, m, s, t] = d;
const adj = Array.from({ length: n + 1 }, () => []);
for (let i = 0; i < m; i++) { const u = d[4 + 2 * i], v = d[5 + 2 * i]; adj[u].push(v); adj[v].push(u); }
const dist = new Array(n + 1).fill(-1);
dist[s] = 0;
const q = [s];
for (let h = 0; h < q.length; h++) {
  const u = q[h];
  for (const v of adj[u]) if (dist[v] === -1) { dist[v] = dist[u] + 1; q.push(v); }
}
console.log(dist[t]);
''',
        explanation="In an unweighted graph, **BFS** from `s` visits vertices in order of distance, so the first time "
                    "a vertex is reached is via a shortest path. **O(n + m)**. (Use an index pointer instead of "
                    "`shift()` in JavaScript — `shift()` is O(n).)",
    ),
    dict(
        slug="coin-change", title="Coin Change", difficulty="medium", topics=["dynamic programming"],
        description="Given coin denominations (unlimited supply of each) and an `amount`, print the fewest coins "
                    "needed to make exactly that amount, or `-1` if it is impossible.",
        input_format="The first line contains `n` and `amount`. The second line contains the `n` coin values.",
        output_format="Print the minimum number of coins, or `-1`.",
        constraints="- 1 ≤ n ≤ 12\n- 1 ≤ coin ≤ 10^4\n- 0 ≤ amount ≤ 10^4",
        samples=["3 11\n1 2 5", "1 3\n2"],
        tests=["1 0\n1", "2 6\n4 3", "3 7\n2 4 6", "2 10000\n9999 7"],
        gen=lambda r: (lambda c: f"{len(c)} {r.randint(0, 10**4)}\n{' '.join(map(str, c))}")(rand_arr(r, r.randint(1, 12), 1, r.choice([20, 500, 10**4]))),
        py=r'''
import sys
data = sys.stdin.read().split()
n, amount = int(data[0]), int(data[1])
coins = list(map(int, data[2:2 + n]))
INF = amount + 1
dp = [0] + [INF] * amount
for c in coins:
    for x in range(c, amount + 1):
        if dp[x - c] + 1 < dp[x]:
            dp[x] = dp[x - c] + 1
print(dp[amount] if dp[amount] <= amount else -1)
''',
        js=r'''
const t = require('fs').readFileSync(0, 'utf8').split(/\s+/).filter(Boolean).map(Number);
const n = t[0], amount = t[1], coins = t.slice(2, 2 + n);
const INF = amount + 1;
const dp = new Array(amount + 1).fill(INF);
dp[0] = 0;
for (const c of coins) for (let x = c; x <= amount; x++) if (dp[x - c] + 1 < dp[x]) dp[x] = dp[x - c] + 1;
console.log(dp[amount] <= amount ? dp[amount] : -1);
''',
        explanation="Greedy (always take the largest coin) fails, e.g. coins `{1, 3, 4}` for 6. Use DP: "
                    "`dp[x]` = fewest coins for amount `x`, `dp[x] = min(dp[x - c] + 1)` over coins `c`. "
                    "**O(n · amount)**.",
    ),
    dict(
        slug="longest-increasing-subsequence", title="Longest Increasing Subsequence", difficulty="medium",
        topics=["dynamic programming", "binary search"],
        description="Print the length of the longest **strictly** increasing subsequence (not necessarily "
                    "contiguous). O(n²) is too slow for the largest tests.",
        input_format="The first line contains `n`.\nThe second line contains `n` integers.",
        output_format="Print the length.",
        constraints="- 1 ≤ n ≤ 10^5\n- -10^9 ≤ a[i] ≤ 10^9",
        samples=["8\n10 9 2 5 3 7 101 18", "6\n7 7 7 7 7 7"],
        tests=["1\n5", "5\n1 2 3 4 5", "5\n5 4 3 2 1", "7\n0 1 0 3 2 3 4"],
        gen=lambda r: arr(rand_arr(r, size(r), -r.choice([10, 10**9]), r.choice([10, 10**9]))),
        py=r'''
import sys
from bisect import bisect_left
data = sys.stdin.read().split()
tails = []  # tails[k] = smallest tail of an increasing subsequence of length k+1
for x in map(int, data[1:1 + int(data[0])]):
    i = bisect_left(tails, x)
    if i == len(tails):
        tails.append(x)
    else:
        tails[i] = x
print(len(tails))
''',
        js=r'''
const t = require('fs').readFileSync(0, 'utf8').split(/\s+/).filter(Boolean).map(Number);
const tails = [];
for (let i = 1; i <= t[0]; i++) {
  const x = t[i];
  let lo = 0, hi = tails.length;
  while (lo < hi) { const m = (lo + hi) >> 1; if (tails[m] < x) lo = m + 1; else hi = m; }
  tails[lo] = x;
}
console.log(tails.length);
''',
        explanation="Maintain `tails[k]` = the smallest possible last element of an increasing subsequence of length "
                    "`k + 1`. This array is sorted, so for each `x` binary-search the first tail `≥ x` and replace "
                    "it (or append if none). The answer is `len(tails)`. **O(n log n)** (the classic DP is O(n²)).",
    ),
    dict(
        slug="longest-common-subsequence", title="Longest Common Subsequence", difficulty="medium",
        topics=["dynamic programming", "strings"],
        description="Print the length of the longest common subsequence of two strings.",
        input_format="Two lines, each containing a string of lowercase letters.",
        output_format="Print the length.",
        constraints="- 1 ≤ |a|, |b| ≤ 1000",
        samples=["abcde\nace", "abc\ndef"],
        tests=["a\na", "a\nb", "abcba\nabcbcba", "aaaa\naa"],
        gen=lambda r: rand_word(r, r.choice([5, 100, 1000]), "abcd"[: r.randint(1, 4)]) + "\n" + rand_word(r, r.choice([5, 100, 1000]), "abcd"[: r.randint(1, 4)]),
        time_limit_ms=3000,
        py=r'''
a = input().strip()
b = input().strip()
m = len(b)
prev = [0] * (m + 1)
for ca in a:
    cur = [0] * (m + 1)
    for j in range(m):
        cur[j + 1] = prev[j] + 1 if ca == b[j] else max(prev[j + 1], cur[j])
    prev = cur
print(prev[m])
''',
        js=r'''
const [a, b] = require('fs').readFileSync(0, 'utf8').split('\n').map((s) => s.trim());
const m = b.length;
let prev = new Int32Array(m + 1);
for (const ca of a) {
  const cur = new Int32Array(m + 1);
  for (let j = 0; j < m; j++) cur[j + 1] = ca === b[j] ? prev[j] + 1 : Math.max(prev[j + 1], cur[j]);
  prev = cur;
}
console.log(prev[m]);
''',
        explanation="`dp[i][j]` = LCS of the first `i` chars of `a` and first `j` of `b`. If the characters match, "
                    "`dp[i][j] = dp[i-1][j-1] + 1`, otherwise `max(dp[i-1][j], dp[i][j-1])`. Only the previous row "
                    "is needed, giving **O(|a|·|b|)** time and **O(|b|)** space.",
    ),
    dict(
        slug="unique-paths-with-obstacles", title="Unique Paths with Obstacles", difficulty="medium",
        topics=["dynamic programming", "matrix"],
        description="A robot starts at the top-left cell of a grid and must reach the bottom-right cell, moving only "
                    "**right** or **down**. Cells with `1` are obstacles. Count the number of distinct paths modulo "
                    "`1 000 000 007`.",
        input_format="The first line contains `r c`. Each of the next `r` lines contains `c` values (`0` or `1`).",
        output_format="Print the number of paths modulo 10^9 + 7.",
        constraints="- 1 ≤ r, c ≤ 100",
        samples=["3 3\n0 0 0\n0 1 0\n0 0 0", "2 2\n0 1\n1 0"],
        tests=["1 1\n0", "1 1\n1", "1 5\n0 0 0 0 0", "2 2\n1 0\n0 0"],
        gen=gen_obstacle_grid,
        py=r'''
import sys
MOD = 10**9 + 7
data = sys.stdin.read().split()
R, C = int(data[0]), int(data[1])
g = data[2:]
dp = [0] * C
dp[0] = 1
for i in range(R):
    for j in range(C):
        if g[i * C + j] == "1":
            dp[j] = 0
        elif j:
            dp[j] = (dp[j] + dp[j - 1]) % MOD
print(dp[C - 1])
''',
        js=r'''
const t = require('fs').readFileSync(0, 'utf8').split(/\s+/).filter(Boolean);
const R = Number(t[0]), C = Number(t[1]), g = t.slice(2);
const MOD = 1000000007;
const dp = new Array(C).fill(0);
dp[0] = 1;
for (let i = 0; i < R; i++) for (let j = 0; j < C; j++) {
  if (g[i * C + j] === '1') dp[j] = 0;
  else if (j) dp[j] = (dp[j] + dp[j - 1]) % MOD;
}
console.log(dp[C - 1]);
''',
        explanation="Paths into a free cell = paths into the cell above + paths into the cell to the left; obstacle "
                    "cells have 0. Iterate row by row with a single 1-D array (`dp[j]` already holds the value from "
                    "the row above). **O(r·c)**.",
    ),
    dict(
        slug="house-robber", title="House Robber", difficulty="medium", topics=["dynamic programming"],
        description="Houses along a street hold `a[i]` money each. You cannot rob two **adjacent** houses. Print the "
                    "maximum amount you can rob.",
        input_format="The first line contains `n`.\nThe second line contains `n` integers.",
        output_format="Print the maximum amount.",
        constraints="- 1 ≤ n ≤ 10^5\n- 0 ≤ a[i] ≤ 10^4",
        samples=["4\n1 2 3 1", "5\n2 7 9 3 1"],
        tests=["1\n5", "2\n1 2", "3\n2 1 1", "4\n0 0 0 0"],
        gen=lambda r: arr(rand_arr(r, size(r), 0, 10**4)),
        py=r'''
import sys
data = sys.stdin.read().split()
take = skip = 0
for x in map(int, data[1:1 + int(data[0])]):
    take, skip = skip + x, max(take, skip)
print(max(take, skip))
''',
        js=r'''
const t = require('fs').readFileSync(0, 'utf8').split(/\s+/).filter(Boolean).map(Number);
let take = 0, skip = 0;
for (let i = 1; i <= t[0]; i++) [take, skip] = [skip + t[i], Math.max(take, skip)];
console.log(Math.max(take, skip));
''',
        explanation="For each house keep two values: the best total if we rob it (`skip_prev + a[i]`) and if we "
                    "skip it (`max(take_prev, skip_prev)`). **O(n)** time, **O(1)** space.",
    ),
    dict(
        slug="word-break", title="Word Break", difficulty="medium", topics=["dynamic programming", "strings", "hashing"],
        description="Print `YES` if the string `s` can be split into a sequence of one or more dictionary words "
                    "(words may be reused), otherwise `NO`.",
        input_format="Line 1: `s`. Line 2: `n`, the dictionary size. Line 3: `n` words.",
        output_format="`YES` or `NO`.",
        constraints="- 1 ≤ |s| ≤ 1000\n- 1 ≤ n ≤ 1000\n- 1 ≤ |word| ≤ 20",
        samples=["leetcode\n2\nleet code", "catsandog\n5\ncats dog sand and cat"],
        tests=["a\n1\na", "a\n1\nb", "applepenapple\n2\napple pen",
               "a" * 999 + "b\n5\na aa aaa aaaa aaaaa", "a" * 1000 + "\n2\naa aaa"],
        gen=gen_word_break,
        py=r'''
import sys
data = sys.stdin.read().split()
s = data[0]
words = set(data[2:2 + int(data[1])])
lens = sorted({len(w) for w in words})
n = len(s)
dp = [False] * (n + 1)
dp[0] = True
for i in range(1, n + 1):
    for L in lens:
        if L > i:
            break
        if dp[i - L] and s[i - L:i] in words:
            dp[i] = True
            break
print("YES" if dp[n] else "NO")
''',
        js=r'''
const t = require('fs').readFileSync(0, 'utf8').split(/\s+/).filter(Boolean);
const s = t[0];
const words = new Set(t.slice(2, 2 + Number(t[1])));
const lens = [...new Set([...words].map((w) => w.length))].sort((a, b) => a - b);
const n = s.length;
const dp = new Array(n + 1).fill(false);
dp[0] = true;
for (let i = 1; i <= n; i++) {
  for (const L of lens) {
    if (L > i) break;
    if (dp[i - L] && words.has(s.slice(i - L, i))) { dp[i] = true; break; }
  }
}
console.log(dp[n] ? 'YES' : 'NO');
''',
        explanation="`dp[i]` is true if the prefix `s[0:i]` can be segmented: it is true when some word of length "
                    "`L` ends at `i` and `dp[i - L]` is true. Plain recursion without memoization is exponential on "
                    "inputs like `aaaa…ab`. **O(|s| · distinct word lengths · L)**.",
    ),
    dict(
        slug="subsets", title="Subsets", difficulty="medium", topics=["backtracking", "recursion", "bit manipulation"],
        description="Given `n` distinct integers, print **all** subsets. Write each subset with its elements in "
                    "increasing order inside square brackets, e.g. `[1 3]`, and the empty subset as `[]`.\n\n"
                    "Print the subsets in **lexicographic order** (compare element by element; a proper prefix comes "
                    "first).",
        input_format="The first line contains `n`.\nThe second line contains `n` distinct integers.",
        output_format="Print `2^n` lines.",
        constraints="- 1 ≤ n ≤ 12\n- -100 ≤ a[i] ≤ 100",
        samples=["3\n1 2 3", "1\n0"],
        tests=["2\n5 -5", "4\n4 3 2 1"],
        gen=lambda r: arr(r.sample(range(-100, 101), r.randint(1, 12))),
        py=r'''
import sys
data = sys.stdin.read().split()
a = sorted(map(int, data[1:1 + int(data[0])]))
out, cur = [], []


def go(start):
    out.append("[" + " ".join(map(str, cur)) + "]")
    for i in range(start, len(a)):
        cur.append(a[i])
        go(i + 1)
        cur.pop()


go(0)
print("\n".join(out))
''',
        js=r'''
const t = require('fs').readFileSync(0, 'utf8').split(/\s+/).filter(Boolean).map(Number);
const a = t.slice(1, 1 + t[0]).sort((x, y) => x - y);
const out = [], cur = [];
function go(start) {
  out.push('[' + cur.join(' ') + ']');
  for (let i = start; i < a.length; i++) { cur.push(a[i]); go(i + 1); cur.pop(); }
}
go(0);
console.log(out.join('\n'));
''',
        explanation="Sort the input, then **backtrack**: record the current subset, and for each later element try "
                    "adding it and recursing. Because we record before extending and try elements in increasing "
                    "order, subsets come out in lexicographic order. **O(n · 2^n)**.",
    ),
    dict(
        slug="permutations", title="Permutations", difficulty="medium", topics=["backtracking", "recursion"],
        description="Given `n` distinct integers, print all their permutations in lexicographic order, one per line.",
        input_format="The first line contains `n`.\nThe second line contains `n` distinct integers.",
        output_format="Print `n!` lines, each a space-separated permutation.",
        constraints="- 1 ≤ n ≤ 8\n- -100 ≤ a[i] ≤ 100",
        samples=["3\n1 2 3", "1\n7"],
        tests=["2\n2 1", "4\n-1 0 1 2", "8\n1 2 3 4 5 6 7 8"],
        gen=lambda r: arr(r.sample(range(-100, 101), r.randint(1, 7))),
        py=r'''
import sys
data = sys.stdin.read().split()
a = sorted(map(int, data[1:1 + int(data[0])]))
n = len(a)
used = [False] * n
cur, out = [], []


def go():
    if len(cur) == n:
        out.append(" ".join(map(str, cur)))
        return
    for i in range(n):
        if not used[i]:
            used[i] = True
            cur.append(a[i])
            go()
            cur.pop()
            used[i] = False


go()
print("\n".join(out))
''',
        js=r'''
const t = require('fs').readFileSync(0, 'utf8').split(/\s+/).filter(Boolean).map(Number);
const a = t.slice(1, 1 + t[0]).sort((x, y) => x - y);
const n = a.length, used = new Array(n).fill(false), cur = [], out = [];
function go() {
  if (cur.length === n) { out.push(cur.join(' ')); return; }
  for (let i = 0; i < n; i++) {
    if (used[i]) continue;
    used[i] = true; cur.push(a[i]);
    go();
    cur.pop(); used[i] = false;
  }
}
go();
console.log(out.join('\n'));
''',
        explanation="Sort, then backtrack: at each position try every unused element in increasing order, recurse, "
                    "then undo the choice. Trying candidates in sorted order yields permutations in lexicographic "
                    "order. **O(n · n!)**.",
    ),
]
