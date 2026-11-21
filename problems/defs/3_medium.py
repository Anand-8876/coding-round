from _util import arr, rand_arr, size, rand_word

ARRAY_IN = "The first line contains an integer `n`.\nThe second line contains `n` space-separated integers."


def nk(a, k):
    return f"{len(a)} {k}\n{' '.join(map(str, a))}"


def gen_rotated(r):
    a = sorted(r.sample(range(-10**6, 10**6), size(r)))
    p = r.randrange(len(a))
    a = a[p:] + a[:p]
    x = r.choice(a) if r.random() < 0.7 else r.randint(-10**6, 10**6)
    return nk(a, x)


def gen_intervals(r):
    n = size(r)
    lines = []
    for _ in range(n):
        s = r.randint(0, 10 * n)
        lines.append(f"{s} {s + r.randint(0, 20)}")
    return f"{n}\n" + "\n".join(lines)


def gen_rpn(r):
    """Random valid RPN expression whose intermediate values stay small."""
    def build(depth):
        if depth == 0 or r.random() < 0.3:
            return [str(r.randint(-20, 20))], None
        left, _ = build(depth - 1)
        right, _ = build(depth - 1)
        return left + right + [r.choice("+-*/")], None

    while True:
        toks, _ = build(r.randint(1, 8))
        # reject expressions that divide by zero or blow up (evaluate the same way the solutions do)
        st, ok = [], True
        for t in toks:
            if t in "+-*/" and len(t) == 1:
                b, a = st.pop(), st.pop()
                if t == "/" and b == 0:
                    ok = False
                    break
                v = a + b if t == "+" else a - b if t == "-" else a * b if t == "*" else abs(a) // abs(b) * (1 if (a < 0) == (b < 0) else -1)
                if abs(v) > 10**12:
                    ok = False
                    break
                st.append(v)
            else:
                st.append(int(t))
        if ok:
            return f"{len(toks)}\n{' '.join(toks)}"


PROBLEMS = [
    dict(
        slug="maximum-subarray", title="Maximum Subarray Sum", difficulty="medium",
        topics=["arrays", "dynamic programming", "kadane"],
        description="Find the contiguous (non-empty) subarray with the largest sum and print that sum.",
        input_format=ARRAY_IN,
        output_format="Print the maximum subarray sum.",
        constraints="- 1 ≤ n ≤ 10^5\n- -10^4 ≤ a[i] ≤ 10^4",
        samples=["9\n-2 1 -3 4 -1 2 1 -5 4", "1\n-7"],
        tests=["3\n-3 -1 -2", "5\n5 4 -1 7 8", "4\n0 0 0 0"],
        gen=lambda r: arr(rand_arr(r, size(r), -10**4, 10**4)),
        py=r'''
import sys
data = sys.stdin.read().split()
n = int(data[0])
best = cur = int(data[1])
for x in map(int, data[2:1 + n]):
    cur = max(x, cur + x)
    best = max(best, cur)
print(best)
''',
        js=r'''
const t = require('fs').readFileSync(0, 'utf8').split(/\s+/).filter(Boolean).map(Number);
let best = t[1], cur = t[1];
for (let i = 2; i <= t[0]; i++) { cur = Math.max(t[i], cur + t[i]); best = Math.max(best, cur); }
console.log(best);
''',
        explanation="**Kadane's algorithm**: `cur` is the best sum of a subarray ending at the current index — either "
                    "extend the previous one or start fresh (`max(x, cur + x)`). The answer is the best `cur` seen. "
                    "**O(n)** time, **O(1)** space.",
    ),
    dict(
        slug="longest-substring-without-repeating", title="Longest Substring Without Repeating Characters",
        difficulty="medium", topics=["strings", "sliding window", "hashing"],
        description="Find the length of the longest substring that contains no repeated characters.",
        input_format="A single line containing the string (lowercase letters and digits).",
        output_format="Print the length.",
        constraints="- 1 ≤ |s| ≤ 10^5",
        samples=["abcabcbb", "bbbbb"],
        tests=["a", "pwwkew", "abcdefghijklmnopqrstuvwxyz0123456789", "abba", "dvdf"],
        gen=lambda r: rand_word(r, size(r), "abcdefghijklmnopqrstuvwxyz0123456789"[: r.randint(2, 36)]),
        py=r'''
s = input().strip()
last = {}
best = start = 0
for i, c in enumerate(s):
    if c in last and last[c] >= start:
        start = last[c] + 1
    last[c] = i
    best = max(best, i - start + 1)
print(best)
''',
        js=r'''
const s = require('fs').readFileSync(0, 'utf8').trim();
const last = new Map();
let best = 0, start = 0;
for (let i = 0; i < s.length; i++) {
  const c = s[i];
  if (last.has(c) && last.get(c) >= start) start = last.get(c) + 1;
  last.set(c, i);
  best = Math.max(best, i - start + 1);
}
console.log(best);
''',
        explanation="**Sliding window**: keep a window `[start, i]` with no repeats and remember each character's "
                    "last index. When `s[i]` was already seen inside the window, move `start` just past that earlier "
                    "occurrence. **O(n)**.",
    ),
    dict(
        slug="three-sum", title="3Sum", difficulty="medium", topics=["arrays", "two pointers", "sorting"],
        description="Count the number of **distinct** triplets of values `(a, b, c)` taken from different positions "
                    "of the array such that `a + b + c = 0`. Triplets are distinct if their sorted value lists "
                    "differ.",
        input_format=ARRAY_IN,
        output_format="Print the number of distinct zero-sum triplets.",
        constraints="- 1 ≤ n ≤ 3000\n- -10^5 ≤ a[i] ≤ 10^5",
        samples=["6\n-1 0 1 2 -1 -4", "3\n0 1 1"],
        tests=["3\n0 0 0", "1\n0", "5\n0 0 0 0 0", "6\n-2 0 1 1 2 -1"],
        gen=lambda r: arr(rand_arr(r, size(r, 10, 500, 3000), -r.choice([5, 50, 10**5]), r.choice([5, 50, 10**5]))),
        time_limit_ms=3000,
        py=r'''
import sys
data = sys.stdin.read().split()
n = int(data[0])
a = sorted(map(int, data[1:1 + n]))
count = 0
for i in range(n - 2):
    if a[i] > 0:
        break
    if i and a[i] == a[i - 1]:
        continue
    lo, hi = i + 1, n - 1
    while lo < hi:
        s = a[i] + a[lo] + a[hi]
        if s < 0:
            lo += 1
        elif s > 0:
            hi -= 1
        else:
            count += 1
            lo += 1
            while lo < hi and a[lo] == a[lo - 1]:
                lo += 1
            hi -= 1
print(count)
''',
        js=r'''
const t = require('fs').readFileSync(0, 'utf8').split(/\s+/).filter(Boolean).map(Number);
const n = t[0];
const a = t.slice(1, 1 + n).sort((x, y) => x - y);
let count = 0;
for (let i = 0; i < n - 2 && a[i] <= 0; i++) {
  if (i && a[i] === a[i - 1]) continue;
  let lo = i + 1, hi = n - 1;
  while (lo < hi) {
    const s = a[i] + a[lo] + a[hi];
    if (s < 0) lo++;
    else if (s > 0) hi--;
    else {
      count++;
      lo++;
      while (lo < hi && a[lo] === a[lo - 1]) lo++;
      hi--;
    }
  }
}
console.log(count);
''',
        explanation="Sort the array. Fix the smallest element `a[i]` (skipping duplicates) and find pairs summing to "
                    "`-a[i]` with two pointers moving inward. After a hit, skip duplicate values so each triplet is "
                    "counted once. **O(n²)**.",
    ),
    dict(
        slug="container-with-most-water", title="Container With Most Water", difficulty="medium",
        topics=["arrays", "two pointers", "greedy"],
        description="`n` vertical lines stand at positions `1..n` with heights `h[i]`. Two lines and the x-axis "
                    "form a container holding `min(h[i], h[j]) × (j - i)` water. Print the maximum amount.",
        input_format=ARRAY_IN,
        output_format="Print the maximum area.",
        constraints="- 2 ≤ n ≤ 10^5\n- 0 ≤ h[i] ≤ 10^4",
        samples=["9\n1 8 6 2 5 4 8 3 7", "2\n1 1"],
        tests=["2\n0 5", "5\n1 2 3 4 5", "3\n10 1 10"],
        gen=lambda r: arr(rand_arr(r, max(2, size(r)), 0, 10**4)),
        py=r'''
import sys
data = sys.stdin.read().split()
n = int(data[0])
h = list(map(int, data[1:1 + n]))
i, j, best = 0, n - 1, 0
while i < j:
    best = max(best, min(h[i], h[j]) * (j - i))
    if h[i] < h[j]:
        i += 1
    else:
        j -= 1
print(best)
''',
        js=r'''
const t = require('fs').readFileSync(0, 'utf8').split(/\s+/).filter(Boolean).map(Number);
const n = t[0], h = t.slice(1, 1 + n);
let i = 0, j = n - 1, best = 0;
while (i < j) {
  best = Math.max(best, Math.min(h[i], h[j]) * (j - i));
  if (h[i] < h[j]) i++; else j--;
}
console.log(best);
''',
        explanation="Start with the widest container. The shorter line limits the area, and moving the taller line "
                    "inward can never help (width shrinks, height can't exceed the short side). So always move the "
                    "shorter side. **O(n)**.",
    ),
    dict(
        slug="product-except-self", title="Product of Array Except Self", difficulty="medium",
        topics=["arrays", "prefix sums"],
        description="For every index `i`, compute the product of all elements **except** `a[i]`, modulo "
                    "`1 000 000 007`. Do not use division (the modulus makes it unreliable anyway).",
        input_format=ARRAY_IN,
        output_format="Print the `n` products modulo 10^9 + 7.",
        constraints="- 2 ≤ n ≤ 10^5\n- 0 ≤ a[i] ≤ 10^9",
        samples=["4\n1 2 3 4", "5\n2 0 3 4 1"],
        tests=["2\n5 7", "3\n0 0 5", "3\n1000000000 1000000000 1000000000"],
        gen=lambda r: arr([x if r.random() < 0.97 else 0 for x in rand_arr(r, max(2, size(r)), 1, 10**9)]),
        py=r'''
import sys
MOD = 10**9 + 7
data = sys.stdin.read().split()
n = int(data[0])
a = list(map(int, data[1:1 + n]))
out = [1] * n
p = 1
for i in range(n):
    out[i] = p
    p = p * a[i] % MOD
p = 1
for i in range(n - 1, -1, -1):
    out[i] = out[i] * p % MOD
    p = p * a[i] % MOD
print(" ".join(map(str, out)))
''',
        js=r'''
const t = require('fs').readFileSync(0, 'utf8').split(/\s+/).filter(Boolean);
const MOD = 1000000007n;
const n = Number(t[0]);
const a = t.slice(1, 1 + n).map(BigInt);
const out = new Array(n);
let p = 1n;
for (let i = 0; i < n; i++) { out[i] = p; p = p * a[i] % MOD; }
p = 1n;
for (let i = n - 1; i >= 0; i--) { out[i] = out[i] * p % MOD; p = p * a[i] % MOD; }
console.log(out.join(' '));
''',
        explanation="`answer[i]` = (product of everything left of `i`) × (product of everything right of `i`). "
                    "Fill prefix products in a forward pass, then multiply by suffix products in a backward pass. "
                    "**O(n)** time, O(1) extra besides the output. In JavaScript, products of two values near 10^9 "
                    "exceed 2^53, so use `BigInt`.",
    ),
    dict(
        slug="group-anagrams", title="Group Anagrams", difficulty="medium", topics=["strings", "hashing", "sorting"],
        description="Group the words that are anagrams of each other.\n\nPrint the number of groups, then one line "
                    "per group with its words sorted alphabetically (duplicates kept). Order the groups by their "
                    "first word.",
        input_format="The first line contains `n`. The second line contains `n` lowercase words.",
        output_format="First line: number of groups. Then one line per group.",
        constraints="- 1 ≤ n ≤ 10^4\n- 1 ≤ |word| ≤ 10",
        samples=["6\neat tea tan ate nat bat", "1\na"],
        tests=["3\nab ba ab", "3\nabc def ghi", "4\naab aba baa abb"],
        gen=lambda r: (lambda ws: f"{len(ws)}\n{' '.join(ws)}")([rand_word(r, r.randint(1, 4), "abcd") for _ in range(size(r, 10, 500, 10000))]),
        py=r'''
import sys
from collections import defaultdict
data = sys.stdin.read().split()
words = data[1:1 + int(data[0])]
groups = defaultdict(list)
for w in words:
    groups["".join(sorted(w))].append(w)
res = sorted(sorted(g) for g in groups.values())
print(len(res))
print("\n".join(" ".join(g) for g in res))
''',
        js=r'''
const t = require('fs').readFileSync(0, 'utf8').split(/\s+/).filter(Boolean);
const words = t.slice(1, 1 + Number(t[0]));
const groups = new Map();
for (const w of words) {
  const key = [...w].sort().join('');
  if (!groups.has(key)) groups.set(key, []);
  groups.get(key).push(w);
}
const cmp = (a, b) => (a < b ? -1 : a > b ? 1 : 0);
const res = [...groups.values()].map((g) => g.sort(cmp));
res.sort((a, b) => {
  for (let i = 0; i < Math.min(a.length, b.length); i++) { const c = cmp(a[i], b[i]); if (c) return c; }
  return a.length - b.length;
});
console.log(res.length + '\n' + res.map((g) => g.join(' ')).join('\n'));
''',
        explanation="Two words are anagrams iff their sorted letters are equal, so use the sorted word as a hash-map "
                    "key. Then sort each group and sort the groups. **O(n · k log k)** for words of length `k`, plus "
                    "the final sort.",
    ),
    dict(
        slug="top-k-frequent-elements", title="Top K Frequent Elements", difficulty="medium",
        topics=["hashing", "heap", "sorting"],
        description="Print the `k` most frequent values, from most to least frequent. When frequencies tie, the "
                    "smaller value comes first.",
        input_format="The first line contains `n` and `k`.\nThe second line contains `n` integers.",
        output_format="Print `k` values.",
        constraints="- 1 ≤ n ≤ 10^5\n- 1 ≤ k ≤ number of distinct values\n- -10^4 ≤ a[i] ≤ 10^4",
        samples=["6 2\n1 1 1 2 2 3", "1 1\n1"],
        tests=["4 2\n5 5 4 4", "5 3\n-1 -1 2 3 3"],
        gen=lambda r: (lambda a: nk(a, r.randint(1, len(set(a)))))(rand_arr(r, size(r), -r.choice([5, 100, 10**4]), r.choice([5, 100, 10**4]))),
        py=r'''
import sys
from collections import Counter
data = sys.stdin.read().split()
n, k = int(data[0]), int(data[1])
cnt = Counter(map(int, data[2:2 + n]))
top = sorted(cnt.items(), key=lambda kv: (-kv[1], kv[0]))[:k]
print(" ".join(str(v) for v, _ in top))
''',
        js=r'''
const t = require('fs').readFileSync(0, 'utf8').split(/\s+/).filter(Boolean).map(Number);
const n = t[0], k = t[1];
const cnt = new Map();
for (let i = 0; i < n; i++) cnt.set(t[2 + i], (cnt.get(t[2 + i]) || 0) + 1);
const top = [...cnt.entries()].sort((a, b) => b[1] - a[1] || a[0] - b[0]).slice(0, k);
console.log(top.map((e) => e[0]).join(' '));
''',
        explanation="Count frequencies with a hash map, then sort the distinct values by (frequency desc, value asc) "
                    "and take the first `k`. **O(n + d log d)** for `d` distinct values. A size-`k` heap or bucket "
                    "sort brings it to O(n log k) / O(n).",
    ),
    dict(
        slug="subarray-sum-equals-k", title="Subarray Sum Equals K", difficulty="medium",
        topics=["arrays", "prefix sums", "hashing"],
        description="Count the contiguous subarrays whose sum equals `k`.",
        input_format="The first line contains `n` and `k`.\nThe second line contains `n` integers.",
        output_format="Print the count.",
        constraints="- 1 ≤ n ≤ 10^5\n- -1000 ≤ a[i] ≤ 1000\n- -10^7 ≤ k ≤ 10^7",
        samples=["3 2\n1 1 1", "3 3\n1 2 3"],
        tests=["1 0\n0", "5 0\n0 0 0 0 0", "4 -1\n1 -1 -1 1"],
        gen=lambda r: nk(rand_arr(r, size(r), -5, 5), r.randint(-5, 5)),
        py=r'''
import sys
data = sys.stdin.read().split()
n, k = int(data[0]), int(data[1])
seen = {0: 1}
s = count = 0
for x in map(int, data[2:2 + n]):
    s += x
    count += seen.get(s - k, 0)
    seen[s] = seen.get(s, 0) + 1
print(count)
''',
        js=r'''
const t = require('fs').readFileSync(0, 'utf8').split(/\s+/).filter(Boolean).map(Number);
const n = t[0], k = t[1];
const seen = new Map([[0, 1]]);
let s = 0, count = 0;
for (let i = 0; i < n; i++) {
  s += t[2 + i];
  count += seen.get(s - k) || 0;
  seen.set(s, (seen.get(s) || 0) + 1);
}
console.log(count);
''',
        explanation="A subarray `(j, i]` sums to `k` iff `prefix[i] - prefix[j] = k`. Scan once, keeping a hash map "
                    "from prefix-sum value → how many times it occurred; at each `i` add the count of "
                    "`prefix[i] - k`. Works with negatives (unlike sliding window). **O(n)**.",
    ),
    dict(
        slug="longest-consecutive-sequence", title="Longest Consecutive Sequence", difficulty="medium",
        topics=["hashing", "arrays"],
        description="Find the length of the longest run of consecutive integers (`x, x+1, x+2, …`) whose values all "
                    "appear in the array (in any order). Aim for O(n).",
        input_format=ARRAY_IN,
        output_format="Print the length.",
        constraints="- 1 ≤ n ≤ 10^5\n- -10^9 ≤ a[i] ≤ 10^9",
        samples=["6\n100 4 200 1 3 2", "10\n0 3 7 2 5 8 4 6 0 1"],
        tests=["1\n5", "3\n1 1 1", "4\n-1 -2 -3 10"],
        gen=lambda r: arr(rand_arr(r, size(r), -r.choice([10, 1000, 10**9]), r.choice([10, 1000, 10**9]))),
        py=r'''
import sys
data = sys.stdin.read().split()
s = set(map(int, data[1:1 + int(data[0])]))
best = 0
for x in s:
    if x - 1 not in s:
        y = x
        while y + 1 in s:
            y += 1
        best = max(best, y - x + 1)
print(best)
''',
        js=r'''
const t = require('fs').readFileSync(0, 'utf8').split(/\s+/).filter(Boolean).map(Number);
const s = new Set(t.slice(1, 1 + t[0]));
let best = 0;
for (const x of s) {
  if (s.has(x - 1)) continue;
  let y = x;
  while (s.has(y + 1)) y++;
  best = Math.max(best, y - x + 1);
}
console.log(best);
''',
        explanation="Put all values in a hash set. Only start counting from values `x` where `x - 1` is **not** in "
                    "the set (the start of a run), then walk `x+1, x+2, …`. Each value is visited at most twice, so "
                    "the total is **O(n)**.",
    ),
    dict(
        slug="sliding-window-maximum", title="Sliding Window Maximum", difficulty="medium",
        topics=["sliding window", "deque", "monotonic queue"],
        description="A window of size `k` slides from the left of the array to the right, one step at a time. "
                    "Print the maximum of each window.",
        input_format="The first line contains `n` and `k`.\nThe second line contains `n` integers.",
        output_format="Print `n - k + 1` values.",
        constraints="- 1 ≤ k ≤ n ≤ 10^5\n- -10^4 ≤ a[i] ≤ 10^4",
        samples=["8 3\n1 3 -1 -3 5 3 6 7", "1 1\n1"],
        tests=["4 4\n4 3 2 1", "4 1\n1 2 3 4", "5 2\n5 5 5 5 5"],
        gen=lambda r: (lambda a: nk(a, r.randint(1, len(a))))(rand_arr(r, size(r), -10**4, 10**4)),
        py=r'''
import sys
from collections import deque
data = sys.stdin.read().split()
n, k = int(data[0]), int(data[1])
a = list(map(int, data[2:2 + n]))
dq = deque()
out = []
for i, x in enumerate(a):
    while dq and a[dq[-1]] <= x:
        dq.pop()
    dq.append(i)
    if dq[0] <= i - k:
        dq.popleft()
    if i >= k - 1:
        out.append(a[dq[0]])
print(" ".join(map(str, out)))
''',
        js=r'''
const t = require('fs').readFileSync(0, 'utf8').split(/\s+/).filter(Boolean).map(Number);
const n = t[0], k = t[1], a = t.slice(2, 2 + n);
const dq = new Int32Array(n);
let head = 0, tail = 0;
const out = [];
for (let i = 0; i < n; i++) {
  while (tail > head && a[dq[tail - 1]] <= a[i]) tail--;
  dq[tail++] = i;
  if (dq[head] <= i - k) head++;
  if (i >= k - 1) out.push(a[dq[head]]);
}
console.log(out.join(' '));
''',
        explanation="Keep a **monotonic deque** of indices whose values are decreasing. When a new element arrives, "
                    "pop smaller elements from the back (they can never be a maximum again). Drop the front if it "
                    "left the window. The front is always the window's maximum. Each index is pushed and popped once: "
                    "**O(n)**.",
    ),
    dict(
        slug="minimum-size-subarray-sum", title="Minimum Size Subarray Sum", difficulty="medium",
        topics=["sliding window", "two pointers"],
        description="Given positive integers and a `target`, find the minimal length of a contiguous subarray whose "
                    "sum is **at least** `target`. Print `0` if there is none.",
        input_format="The first line contains `n` and `target`.\nThe second line contains `n` positive integers.",
        output_format="Print the minimal length, or `0`.",
        constraints="- 1 ≤ n ≤ 10^5\n- 1 ≤ a[i] ≤ 10^4\n- 1 ≤ target ≤ 10^9",
        samples=["6 7\n2 3 1 2 4 3", "3 100\n1 2 3"],
        tests=["1 1\n1", "1 2\n1", "5 15\n1 2 3 4 5"],
        gen=lambda r: (lambda a: nk(a, r.randint(1, sum(a) + 5)))(rand_arr(r, size(r), 1, r.choice([10, 10**4]))),
        py=r'''
import sys
data = sys.stdin.read().split()
n, target = int(data[0]), int(data[1])
a = list(map(int, data[2:2 + n]))
best = n + 1
s = lo = 0
for hi in range(n):
    s += a[hi]
    while s >= target:
        best = min(best, hi - lo + 1)
        s -= a[lo]
        lo += 1
print(best if best <= n else 0)
''',
        js=r'''
const t = require('fs').readFileSync(0, 'utf8').split(/\s+/).filter(Boolean).map(Number);
const n = t[0], target = t[1], a = t.slice(2, 2 + n);
let best = n + 1, s = 0, lo = 0;
for (let hi = 0; hi < n; hi++) {
  s += a[hi];
  while (s >= target) { best = Math.min(best, hi - lo + 1); s -= a[lo++]; }
}
console.log(best <= n ? best : 0);
''',
        explanation="Since all values are positive, extending a window only increases its sum. Grow the right end; "
                    "while the sum is ≥ target, record the length and shrink from the left. Each pointer moves at "
                    "most `n` times: **O(n)**.",
    ),
    dict(
        slug="search-rotated-sorted-array", title="Search in Rotated Sorted Array", difficulty="medium",
        topics=["binary search"],
        description="A sorted array of **distinct** integers was rotated at an unknown pivot (e.g. `[0,1,2,4,5,6,7]` "
                    "→ `[4,5,6,7,0,1,2]`). Print the 1-based index of `x`, or `-1`. Required: O(log n).",
        input_format="The first line contains `n` and `x`.\nThe second line contains the rotated array.",
        output_format="Print the index or `-1`.",
        constraints="- 1 ≤ n ≤ 10^5\n- -10^6 ≤ values ≤ 10^6",
        samples=["7 0\n4 5 6 7 0 1 2", "7 3\n4 5 6 7 0 1 2"],
        tests=["1 1\n1", "1 0\n1", "2 1\n3 1", "3 3\n1 2 3"],
        gen=gen_rotated,
        py=r'''
import sys
data = sys.stdin.read().split()
n, x = int(data[0]), int(data[1])
a = list(map(int, data[2:2 + n]))
lo, hi, ans = 0, n - 1, -1
while lo <= hi:
    mid = (lo + hi) // 2
    if a[mid] == x:
        ans = mid + 1
        break
    if a[lo] <= a[mid]:          # left half sorted
        if a[lo] <= x < a[mid]:
            hi = mid - 1
        else:
            lo = mid + 1
    else:                        # right half sorted
        if a[mid] < x <= a[hi]:
            lo = mid + 1
        else:
            hi = mid - 1
print(ans)
''',
        js=r'''
const t = require('fs').readFileSync(0, 'utf8').split(/\s+/).filter(Boolean).map(Number);
const n = t[0], x = t[1], a = t.slice(2, 2 + n);
let lo = 0, hi = n - 1, ans = -1;
while (lo <= hi) {
  const mid = (lo + hi) >> 1;
  if (a[mid] === x) { ans = mid + 1; break; }
  if (a[lo] <= a[mid]) {
    if (a[lo] <= x && x < a[mid]) hi = mid - 1; else lo = mid + 1;
  } else {
    if (a[mid] < x && x <= a[hi]) lo = mid + 1; else hi = mid - 1;
  }
}
console.log(ans);
''',
        explanation="At every step at least one half `[lo, mid]` or `[mid, hi]` is normally sorted. Check whether "
                    "`x` lies inside the sorted half's range; if so search there, otherwise search the other half. "
                    "**O(log n)**.",
    ),
    dict(
        slug="first-and-last-position", title="First and Last Position in Sorted Array", difficulty="medium",
        topics=["binary search"],
        description="Given a sorted array (with duplicates), print the 1-based indices of the first and last "
                    "occurrence of `x`, or `-1 -1` if absent. Required: O(log n).",
        input_format="The first line contains `n` and `x`.\nThe second line contains `n` sorted integers.",
        output_format="Print `first last`.",
        constraints="- 1 ≤ n ≤ 10^5\n- -10^9 ≤ values ≤ 10^9",
        samples=["6 8\n5 7 7 8 8 10", "6 6\n5 7 7 8 8 10"],
        tests=["1 1\n1", "1 0\n1", "5 2\n2 2 2 2 2"],
        gen=lambda r: (lambda a: nk(a, r.choice(a) if r.random() < 0.7 else r.randint(-30, 30)))(sorted(rand_arr(r, size(r), -20, 20))),
        py=r'''
import sys
from bisect import bisect_left, bisect_right
data = sys.stdin.read().split()
n, x = int(data[0]), int(data[1])
a = list(map(int, data[2:2 + n]))
l, r = bisect_left(a, x), bisect_right(a, x)
print(f"{l + 1} {r}" if l < r else "-1 -1")
''',
        js=r'''
const t = require('fs').readFileSync(0, 'utf8').split(/\s+/).filter(Boolean).map(Number);
const n = t[0], x = t[1], a = t.slice(2, 2 + n);
function lowerBound(v) { // first index with a[i] >= v
  let lo = 0, hi = n;
  while (lo < hi) { const m = (lo + hi) >> 1; if (a[m] < v) lo = m + 1; else hi = m; }
  return lo;
}
const l = lowerBound(x), r = lowerBound(x + 1);
console.log(l < r ? `${l + 1} ${r}` : '-1 -1');
''',
        explanation="Use two binary searches: **lower bound** (first index with `a[i] ≥ x`) and **upper bound** "
                    "(first index with `a[i] > x`). If they are equal, `x` is absent. **O(log n)**.",
    ),
    dict(
        slug="koko-eating-bananas", title="Koko Eating Bananas", difficulty="medium",
        topics=["binary search", "binary search on answer"],
        description="There are `n` piles of bananas. Koko eats at speed `s` bananas/hour: each hour she picks a pile "
                    "and eats `s` bananas from it (or the whole pile if it has fewer). Find the minimum integer `s` "
                    "that lets her finish all piles within `h` hours.",
        input_format="The first line contains `n` and `h`.\nThe second line contains the pile sizes.",
        output_format="Print the minimum speed.",
        constraints="- 1 ≤ n ≤ 10^4\n- n ≤ h ≤ 10^9\n- 1 ≤ pile ≤ 10^9",
        samples=["4 8\n3 6 7 11", "5 5\n30 11 23 4 20"],
        tests=["1 1\n1000000000", "1 1000000000\n1000000000", "3 6\n30 11 23"],
        gen=lambda r: (lambda a: nk(a, r.randint(len(a), len(a) * r.choice([1, 3, 1000]))))(rand_arr(r, size(r), 1, r.choice([100, 10**9]))),
        py=r'''
import sys
data = sys.stdin.read().split()
n, h = int(data[0]), int(data[1])
piles = list(map(int, data[2:2 + n]))
lo, hi = 1, max(piles)
while lo < hi:
    mid = (lo + hi) // 2
    hours = sum((p + mid - 1) // mid for p in piles)
    if hours <= h:
        hi = mid
    else:
        lo = mid + 1
print(lo)
''',
        js=r'''
const t = require('fs').readFileSync(0, 'utf8').split(/\s+/).filter(Boolean).map(Number);
const n = t[0], h = t[1], piles = t.slice(2, 2 + n);
let lo = 1, hi = Math.max(...piles);
while (lo < hi) {
  const mid = Math.floor((lo + hi) / 2);
  let hours = 0;
  for (const p of piles) hours += Math.ceil(p / mid);
  if (hours <= h) hi = mid; else lo = mid + 1;
}
console.log(lo);
''',
        explanation="**Binary search on the answer**: the hours needed decrease as speed increases (monotonic), so "
                    "binary search speed in `[1, max pile]` for the smallest one with `Σ ceil(p / s) ≤ h`. "
                    "**O(n log max)**.",
    ),
    dict(
        slug="merge-intervals", title="Merge Intervals", difficulty="medium", topics=["sorting", "intervals"],
        description="Merge all overlapping intervals and print the result sorted by start. Intervals that touch "
                    "(e.g. `[1,4]` and `[4,5]`) also merge.",
        input_format="The first line contains `n`. Each of the next `n` lines contains `start end`.",
        output_format="Print each merged interval as `start end` on its own line.",
        constraints="- 1 ≤ n ≤ 10^4\n- 0 ≤ start ≤ end ≤ 10^9",
        samples=["4\n1 3\n2 6\n8 10\n15 18", "2\n1 4\n4 5"],
        tests=["1\n5 5", "3\n1 10\n2 3\n4 5", "3\n7 8\n1 2\n4 5"],
        gen=gen_intervals,
        py=r'''
import sys
data = sys.stdin.read().split()
n = int(data[0])
iv = sorted((int(data[1 + 2 * i]), int(data[2 + 2 * i])) for i in range(n))
out = [list(iv[0])]
for s, e in iv[1:]:
    if s <= out[-1][1]:
        out[-1][1] = max(out[-1][1], e)
    else:
        out.append([s, e])
print("\n".join(f"{s} {e}" for s, e in out))
''',
        js=r'''
const t = require('fs').readFileSync(0, 'utf8').split(/\s+/).filter(Boolean).map(Number);
const n = t[0];
const iv = [];
for (let i = 0; i < n; i++) iv.push([t[1 + 2 * i], t[2 + 2 * i]]);
iv.sort((a, b) => a[0] - b[0] || a[1] - b[1]);
const out = [iv[0].slice()];
for (const [s, e] of iv.slice(1)) {
  const last = out[out.length - 1];
  if (s <= last[1]) last[1] = Math.max(last[1], e); else out.push([s, e]);
}
console.log(out.map((x) => x.join(' ')).join('\n'));
''',
        explanation="Sort by start. Walk through the intervals: if the current one starts before (or at) the end of "
                    "the last merged interval, extend that interval; otherwise start a new one. **O(n log n)**.",
    ),
    dict(
        slug="kth-largest-element", title="Kth Largest Element", difficulty="medium", topics=["heap", "sorting", "quickselect"],
        description="Print the `k`-th largest element in the array (counting duplicates — i.e. the element at "
                    "position `k` when sorted in descending order).",
        input_format="The first line contains `n` and `k`.\nThe second line contains `n` integers.",
        output_format="Print the k-th largest element.",
        constraints="- 1 ≤ k ≤ n ≤ 10^5\n- -10^4 ≤ a[i] ≤ 10^4",
        samples=["6 2\n3 2 1 5 6 4", "9 4\n3 2 3 1 2 4 5 5 6"],
        tests=["1 1\n-5", "3 3\n1 1 1", "4 1\n-1 -2 -3 -4"],
        gen=lambda r: (lambda a: nk(a, r.randint(1, len(a))))(rand_arr(r, size(r), -10**4, 10**4)),
        py=r'''
import sys
import heapq
data = sys.stdin.read().split()
n, k = int(data[0]), int(data[1])
heap = []
for x in map(int, data[2:2 + n]):
    heapq.heappush(heap, x)
    if len(heap) > k:
        heapq.heappop(heap)
print(heap[0])
''',
        js=r'''
const t = require('fs').readFileSync(0, 'utf8').split(/\s+/).filter(Boolean).map(Number);
const n = t[0], k = t[1];
// min-heap of size k
const h = [];
const up = (i) => { while (i > 0) { const p = (i - 1) >> 1; if (h[p] <= h[i]) break; [h[p], h[i]] = [h[i], h[p]]; i = p; } };
const down = (i) => {
  for (;;) {
    let m = i; const l = 2 * i + 1, r = l + 1;
    if (l < h.length && h[l] < h[m]) m = l;
    if (r < h.length && h[r] < h[m]) m = r;
    if (m === i) return;
    [h[m], h[i]] = [h[i], h[m]]; i = m;
  }
};
for (let i = 0; i < n; i++) {
  h.push(t[2 + i]); up(h.length - 1);
  if (h.length > k) { h[0] = h.pop(); down(0); }
}
console.log(h[0]);
''',
        explanation="Keep a **min-heap of size k** holding the k largest elements seen so far; when it grows past "
                    "k, pop the smallest. At the end the heap's top is the k-th largest. **O(n log k)**. "
                    "(Sorting is O(n log n); quickselect is O(n) on average.) JavaScript has no built-in heap, so "
                    "the solution implements one.",
    ),
    dict(
        slug="next-greater-element", title="Next Greater Element", difficulty="medium", topics=["stack", "monotonic stack"],
        description="For each element, print the first element to its **right** that is strictly greater. If there "
                    "is none, print `-1` for that position.",
        input_format=ARRAY_IN,
        output_format="Print `n` values.",
        constraints="- 1 ≤ n ≤ 10^5\n- -10^9 ≤ a[i] ≤ 10^9",
        samples=["4\n4 5 2 25", "4\n13 7 6 12"],
        tests=["1\n5", "4\n1 2 3 4", "4\n4 3 2 1", "3\n2 2 2"],
        gen=lambda r: arr(rand_arr(r, size(r), -r.choice([5, 10**9]), r.choice([5, 10**9]))),
        py=r'''
import sys
data = sys.stdin.read().split()
n = int(data[0])
a = list(map(int, data[1:1 + n]))
res = [-1] * n
stack = []  # indices waiting for a greater element
for i, x in enumerate(a):
    while stack and a[stack[-1]] < x:
        res[stack.pop()] = x
    stack.append(i)
print(" ".join(map(str, res)))
''',
        js=r'''
const t = require('fs').readFileSync(0, 'utf8').split(/\s+/).filter(Boolean).map(Number);
const n = t[0], a = t.slice(1, 1 + n);
const res = new Array(n).fill(-1), stack = [];
for (let i = 0; i < n; i++) {
  while (stack.length && a[stack[stack.length - 1]] < a[i]) res[stack.pop()] = a[i];
  stack.push(i);
}
console.log(res.join(' '));
''',
        explanation="Maintain a stack of indices that haven't found their next greater element yet (their values are "
                    "non-increasing from bottom to top). Each new element resolves all smaller elements on top of "
                    "the stack. Each index is pushed and popped once: **O(n)**.",
    ),
    dict(
        slug="evaluate-reverse-polish-notation", title="Evaluate Reverse Polish Notation", difficulty="medium",
        topics=["stack"],
        description="Evaluate an arithmetic expression in Reverse Polish (postfix) notation. Operators are `+ - * /`. "
                    "Division between integers **truncates toward zero** (e.g. `-7 / 2 = -3`). The expression is "
                    "valid and never divides by zero.",
        input_format="The first line contains the number of tokens `n`. The second line contains the tokens.",
        output_format="Print the result.",
        constraints="- 1 ≤ n ≤ 10^4\n- all intermediate values fit in a 64-bit signed integer (|v| ≤ 10^12)",
        samples=["5\n2 1 + 3 *", "13\n10 6 9 3 + -11 * / * 17 + 5 +"],
        tests=["1\n42", "3\n-7 2 /", "3\n7 -2 /", "5\n4 13 5 / +"],
        gen=gen_rpn,
        py=r'''
import sys
data = sys.stdin.read().split()
toks = data[1:1 + int(data[0])]
st = []
for t in toks:
    if t in ("+", "-", "*", "/"):
        b, a = st.pop(), st.pop()
        if t == "+":
            st.append(a + b)
        elif t == "-":
            st.append(a - b)
        elif t == "*":
            st.append(a * b)
        else:
            q = abs(a) // abs(b)
            st.append(q if (a < 0) == (b < 0) else -q)
    else:
        st.append(int(t))
print(st[-1])
''',
        js=r'''
const t = require('fs').readFileSync(0, 'utf8').split(/\s+/).filter(Boolean);
const toks = t.slice(1, 1 + Number(t[0]));
const st = [];
for (const tok of toks) {
  if (tok === '+' || tok === '-' || tok === '*' || tok === '/') {
    const b = st.pop(), a = st.pop();
    if (tok === '+') st.push(a + b);
    else if (tok === '-') st.push(a - b);
    else if (tok === '*') st.push(a * b);
    else st.push(Math.trunc(a / b));
  } else st.push(Number(tok));
}
console.log(String(st[st.length - 1]));
''',
        explanation="Push numbers onto a stack. On an operator, pop the right operand then the left operand, apply "
                    "the operator and push the result. Watch out: Python's `//` floors (`-7 // 2 = -4`), so compute "
                    "truncating division explicitly; in JavaScript use `Math.trunc(a / b)`. **O(n)**.",
    ),
]
