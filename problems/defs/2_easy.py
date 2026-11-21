from _util import arr, rand_arr, size, rand_word

ARRAY_IN = "The first line contains an integer `n`.\nThe second line contains `n` space-separated integers."


def gen_missing(r):
    n = size(r, 10, 1000, 100000)
    nums = list(range(n + 1))
    nums.remove(r.randint(0, n))
    r.shuffle(nums)
    return arr(nums)


def gen_single(r):
    k = size(r, 5, 500, 50000)
    vals = r.sample(range(-10**9, 10**9), k + 1)
    nums = vals[:k] * 2 + [vals[k]]
    r.shuffle(nums)
    return arr(nums)


def gen_majority(r):
    n = size(r, 9, 1000, 100000)
    maj = r.randint(-10**9, 10**9)
    cnt = n // 2 + 1 + r.randint(0, n // 4)
    nums = [maj] * cnt + rand_arr(r, n - cnt, -10**9, 10**9)
    r.shuffle(nums)
    return arr(nums)


def gen_range_sum(r):
    n = size(r, 10, 1000, 50000)
    q = size(r, 10, 1000, 50000)
    a = rand_arr(r, n, -10**4, 10**4)
    qs = []
    for _ in range(q):
        lo, hi = sorted((r.randint(1, n), r.randint(1, n)))
        qs.append(f"{lo} {hi}")
    return f"{n} {q}\n{' '.join(map(str, a))}\n" + "\n".join(qs)


def gen_min_stack(r):
    q = size(r, 10, 1000, 50000)
    ops, depth = [], 0
    for _ in range(q):
        c = r.random()
        if c < 0.4 or depth == 0 and c < 0.6:
            ops.append(f"push {r.randint(-10**9, 10**9)}")
            depth += 1
        elif c < 0.6:
            ops.append("pop")
            depth = max(0, depth - 1)
        elif c < 0.8:
            ops.append("top")
        else:
            ops.append("getMin")
    ops[-1] = "getMin"  # guarantee at least one line of output
    return f"{q}\n" + "\n".join(ops)


PROBLEMS = [
    dict(
        slug="missing-number", title="Missing Number", difficulty="easy", topics=["arrays", "math", "bit manipulation"],
        description="An array contains `n` distinct numbers taken from `0, 1, …, n`. Exactly one number in that range "
                    "is missing. Find it.",
        input_format=ARRAY_IN,
        output_format="Print the missing number.",
        constraints="- 1 ≤ n ≤ 10^5",
        samples=["3\n3 0 1", "2\n0 1"],
        tests=["1\n0", "1\n1", "4\n4 2 3 1"],
        gen=gen_missing,
        py=r'''
import sys
data = sys.stdin.read().split()
n = int(data[0])
print(n * (n + 1) // 2 - sum(map(int, data[1:1 + n])))
''',
        js=r'''
const t = require('fs').readFileSync(0, 'utf8').split(/\s+/).filter(Boolean).map(Number);
const n = t[0];
let s = n * (n + 1) / 2;
for (let i = 1; i <= n; i++) s -= t[i];
console.log(s);
''',
        explanation="The sum of `0..n` is `n(n+1)/2`. Subtract the array's sum to get the missing number. "
                    "**O(n)** time, **O(1)** space. (XOR-ing all indices and values also works.)",
    ),
    dict(
        slug="single-number", title="Single Number", difficulty="easy", topics=["bit manipulation", "arrays"],
        description="Every element appears exactly twice except for one, which appears once. Find that one. "
                    "Try to use O(1) extra memory.",
        input_format=ARRAY_IN,
        output_format="Print the single element.",
        constraints="- 1 ≤ n ≤ 10^5 (n is odd)\n- -10^9 ≤ a[i] ≤ 10^9",
        samples=["3\n2 2 1", "5\n4 1 2 1 2"],
        tests=["1\n7", "3\n-1 5 -1", "5\n0 0 -3 9 9"],
        gen=gen_single,
        py=r'''
import sys
data = sys.stdin.read().split()
n = int(data[0])
x = 0
for v in map(int, data[1:1 + n]):
    x ^= v
print(x)
''',
        js=r'''
const t = require('fs').readFileSync(0, 'utf8').split(/\s+/).filter(Boolean).map(Number);
let x = 0;
for (let i = 1; i <= t[0]; i++) x ^= t[i];
console.log(x);
''',
        explanation="`a ^ a = 0` and `a ^ 0 = a`, and XOR is commutative. XOR-ing every element cancels the pairs "
                    "and leaves the single number. **O(n)** time, **O(1)** space.",
    ),
    dict(
        slug="majority-element", title="Majority Element", difficulty="easy", topics=["arrays", "hashing"],
        description="Find the element that appears **more than** `n / 2` times. It is guaranteed to exist.",
        input_format=ARRAY_IN,
        output_format="Print the majority element.",
        constraints="- 1 ≤ n ≤ 10^5\n- -10^9 ≤ a[i] ≤ 10^9",
        samples=["3\n3 2 3", "7\n2 2 1 1 1 2 2"],
        tests=["1\n5", "2\n9 9", "5\n-1 -1 -1 2 3"],
        gen=gen_majority,
        py=r'''
import sys
data = sys.stdin.read().split()
n = int(data[0])
cand, cnt = None, 0
for x in data[1:1 + n]:
    if cnt == 0:
        cand = x
    cnt += 1 if x == cand else -1
print(cand)
''',
        js=r'''
const t = require('fs').readFileSync(0, 'utf8').split(/\s+/).filter(Boolean).map(Number);
let cand = null, cnt = 0;
for (let i = 1; i <= t[0]; i++) {
  if (cnt === 0) cand = t[i];
  cnt += t[i] === cand ? 1 : -1;
}
console.log(cand);
''',
        explanation="**Boyer–Moore voting**: keep a candidate and a counter. Matching elements increment, others "
                    "decrement; when the counter hits 0, adopt the current element. The majority survives because "
                    "it outnumbers everything else combined. **O(n)** time, **O(1)** space.",
    ),
    dict(
        slug="rotate-array", title="Rotate Array", difficulty="easy", topics=["arrays"],
        description="Rotate the array to the right by `k` steps. For example `[1,2,3,4,5]` rotated by 2 is "
                    "`[4,5,1,2,3]`.",
        input_format="The first line contains `n` and `k`.\nThe second line contains `n` integers.",
        output_format="Print the rotated array.",
        constraints="- 1 ≤ n ≤ 10^5\n- 0 ≤ k ≤ 10^9",
        samples=["5 2\n1 2 3 4 5", "3 4\n1 2 3"],
        tests=["1 100\n7", "4 0\n1 2 3 4", "4 4\n1 2 3 4", "3 1000000000\n1 2 3"],
        gen=lambda r: (lambda a: f"{len(a)} {r.randint(0, 10**9)}\n{' '.join(map(str, a))}")(rand_arr(r, size(r), -1000, 1000)),
        py=r'''
import sys
data = sys.stdin.read().split()
n, k = int(data[0]), int(data[1])
a = data[2:2 + n]
k %= n
print(" ".join(a[n - k:] + a[:n - k]))
''',
        js=r'''
const t = require('fs').readFileSync(0, 'utf8').split(/\s+/).filter(Boolean);
const n = Number(t[0]), k = Number(t[1]) % n;
const a = t.slice(2, 2 + n);
console.log(a.slice(n - k).concat(a.slice(0, n - k)).join(' '));
''',
        explanation="Rotating by `n` gives the same array, so reduce `k %= n` first (k can be 10^9). The last `k` "
                    "elements move to the front. In-place alternative: reverse the whole array, then reverse the "
                    "first `k` and the remaining `n-k`. **O(n)**.",
    ),
    dict(
        slug="character-frequency", title="Character Frequency", difficulty="easy", topics=["strings", "hashing"],
        description="Given a string of lowercase letters, print each distinct character and how many times it "
                    "occurs, in alphabetical order.",
        input_format="A single line containing the string.",
        output_format="For each distinct character, a line `c count`, sorted by character.",
        constraints="- 1 ≤ |s| ≤ 10^5",
        samples=["banana", "abc"],
        tests=["z", "zzzzzz", "thequickbrownfoxjumpsoverthelazydog"],
        gen=lambda r: rand_word(r, size(r, 10, 1000, 100000), "abcdefghijklmnopqrstuvwxyz"[: r.randint(1, 26)]),
        py=r'''
from collections import Counter
s = input().strip()
print("\n".join(f"{c} {n}" for c, n in sorted(Counter(s).items())))
''',
        js=r'''
const s = require('fs').readFileSync(0, 'utf8').trim();
const cnt = new Array(26).fill(0);
for (const c of s) cnt[c.charCodeAt(0) - 97]++;
const out = [];
cnt.forEach((n, i) => { if (n) out.push(String.fromCharCode(97 + i) + ' ' + n); });
console.log(out.join('\n'));
''',
        explanation="Count occurrences with a hash map (or a 26-slot array), then output the keys in sorted order. "
                    "**O(n)**.",
    ),
    dict(
        slug="range-sum-queries", title="Range Sum Queries", difficulty="easy", topics=["arrays", "prefix sums"],
        description="Given an array and `q` queries `l r` (1-based, inclusive), answer each query with "
                    "`a[l] + a[l+1] + … + a[r]`.",
        input_format="Line 1: `n q`. Line 2: `n` integers.\nNext `q` lines: `l r`.",
        output_format="Print the answer to each query on its own line.",
        constraints="- 1 ≤ n, q ≤ 10^5\n- -10^4 ≤ a[i] ≤ 10^4\n- 1 ≤ l ≤ r ≤ n",
        samples=["5 3\n1 2 3 4 5\n1 5\n2 3\n4 4", "3 1\n-1 -2 -3\n1 2"],
        tests=["1 1\n5\n1 1", "4 2\n0 0 0 0\n1 4\n2 2"],
        gen=gen_range_sum,
        py=r'''
import sys
data = sys.stdin.buffer.read().split()
n, q = int(data[0]), int(data[1])
pre = [0] * (n + 1)
for i in range(n):
    pre[i + 1] = pre[i] + int(data[2 + i])
out = []
p = 2 + n
for _ in range(q):
    l, r = int(data[p]), int(data[p + 1])
    p += 2
    out.append(pre[r] - pre[l - 1])
print("\n".join(map(str, out)))
''',
        js=r'''
const t = require('fs').readFileSync(0, 'utf8').split(/\s+/).filter(Boolean).map(Number);
const n = t[0], q = t[1];
const pre = new Array(n + 1).fill(0);
for (let i = 0; i < n; i++) pre[i + 1] = pre[i] + t[2 + i];
const out = [];
for (let i = 0, p = 2 + n; i < q; i++, p += 2) out.push(pre[t[p + 1]] - pre[t[p] - 1]);
console.log(out.join('\n'));
''',
        explanation="Summing each range directly is O(n·q) — too slow. Build prefix sums `pre[i] = a[1] + … + a[i]` "
                    "once; then each query is `pre[r] - pre[l-1]`. **O(n + q)**.",
    ),
    dict(
        slug="string-compression", title="String Compression", difficulty="easy", topics=["strings", "two pointers"],
        description="Compress a string by replacing each run of identical consecutive characters with the "
                    "character followed by the run length. `aaabbc` becomes `a3b2c1`.",
        input_format="A single line containing a string of lowercase letters.",
        output_format="Print the compressed string.",
        constraints="- 1 ≤ |s| ≤ 10^5",
        samples=["aaabbc", "abcd"],
        tests=["a", "zzzzzzzzzzzz", "aabbaa"],
        gen=lambda r: "".join(r.choice("abc") * r.randint(1, r.choice([3, 30])) for _ in range(size(r, 5, 200, 5000))),
        py=r'''
s = input().strip()
out = []
i = 0
while i < len(s):
    j = i
    while j < len(s) and s[j] == s[i]:
        j += 1
    out.append(s[i] + str(j - i))
    i = j
print("".join(out))
''',
        js=r'''
const s = require('fs').readFileSync(0, 'utf8').trim();
const out = [];
for (let i = 0; i < s.length;) {
  let j = i;
  while (j < s.length && s[j] === s[i]) j++;
  out.push(s[i] + (j - i));
  i = j;
}
console.log(out.join(''));
''',
        explanation="Walk the string; from each position extend a second pointer while the character repeats. Emit "
                    "the character and the run length, then jump to the end of the run. Build with a list/array and "
                    "join once (string concatenation in a loop can be quadratic). **O(n)**.",
    ),
    dict(
        slug="first-unique-character", title="First Unique Character", difficulty="easy", topics=["strings", "hashing"],
        description="Find the first character in the string that occurs exactly once and print its 1-based index. "
                    "If there is none, print `-1`.",
        input_format="A single line containing a string of lowercase letters.",
        output_format="Print the index or `-1`.",
        constraints="- 1 ≤ |s| ≤ 10^5",
        samples=["leetcode", "aabb"],
        tests=["z", "aabbc", "abcabcx"],
        gen=lambda r: rand_word(r, size(r), "abcdefghij"[: r.randint(1, 10)]) + (r.choice("xyz") if r.random() < 0.5 else ""),
        py=r'''
from collections import Counter
s = input().strip()
cnt = Counter(s)
print(next((i + 1 for i, c in enumerate(s) if cnt[c] == 1), -1))
''',
        js=r'''
const s = require('fs').readFileSync(0, 'utf8').trim();
const cnt = {};
for (const c of s) cnt[c] = (cnt[c] || 0) + 1;
let ans = -1;
for (let i = 0; i < s.length; i++) if (cnt[s[i]] === 1) { ans = i + 1; break; }
console.log(ans);
''',
        explanation="Two passes: first count every character, then find the first position whose count is 1. "
                    "**O(n)**.",
    ),
    dict(
        slug="power-of-two", title="Power of Two", difficulty="easy", topics=["bit manipulation", "math"],
        description="For each query number `x`, print `YES` if `x` is a power of two (1, 2, 4, 8, …), otherwise "
                    "`NO`.",
        input_format="The first line contains `q`. Each of the next `q` lines contains an integer `x`.",
        output_format="`YES` or `NO` for each query.",
        constraints="- 1 ≤ q ≤ 10^4\n- 0 ≤ x ≤ 10^18",
        samples=["4\n1\n16\n3\n0", "2\n1024\n1000"],
        tests=["1\n576460752303423488", "1\n576460752303423487", "3\n2\n4\n6"],
        gen=lambda r: (lambda xs: f"{len(xs)}\n" + "\n".join(map(str, xs)))(
            [(2 ** r.randint(0, 59)) + (0 if r.random() < 0.5 else r.choice([-1, 1, 2])) for _ in range(size(r, 10, 100, 10000))]),
        py=r'''
import sys
data = sys.stdin.read().split()
out = []
for x in map(int, data[1:1 + int(data[0])]):
    out.append("YES" if x > 0 and x & (x - 1) == 0 else "NO")
print("\n".join(out))
''',
        js=r'''
const t = require('fs').readFileSync(0, 'utf8').split(/\s+/).filter(Boolean);
const out = [];
for (let i = 1; i <= Number(t[0]); i++) {
  const x = BigInt(t[i]);
  out.push(x > 0n && (x & (x - 1n)) === 0n ? 'YES' : 'NO');
}
console.log(out.join('\n'));
''',
        explanation="A power of two has exactly one set bit. `x & (x - 1)` clears the lowest set bit, so it equals 0 "
                    "exactly when `x` is a power of two (and `x > 0`). Values up to 10^18 need `BigInt` in "
                    "JavaScript, because bitwise ops on Numbers are 32-bit. **O(1)** per query.",
    ),
    dict(
        slug="gcd-and-lcm", title="GCD and LCM", difficulty="easy", topics=["math"],
        description="Given two positive integers `a` and `b`, print their greatest common divisor and least common "
                    "multiple.",
        input_format="A single line with `a` and `b`.",
        output_format="Print `gcd lcm`.",
        constraints="- 1 ≤ a, b ≤ 10^9",
        samples=["12 18", "7 13"],
        tests=["1 1", "1000000000 999999999", "5 5", "6 1000000000"],
        gen=lambda r: f"{r.randint(1, 10**9)} {r.randint(1, 10**9)}" if r.random() < 0.5 else (lambda g: f"{g * r.randint(1, 1000)} {g * r.randint(1, 1000)}")(r.randint(1, 10**6)),
        py=r'''
a, b = map(int, input().split())
x, y = a, b
while y:
    x, y = y, x % y
print(x, a // x * b)
''',
        js=r'''
const [a, b] = require('fs').readFileSync(0, 'utf8').trim().split(/\s+/).map(BigInt);
let x = a, y = b;
while (y) [x, y] = [y, x % y];
console.log(`${x} ${a / x * b}`);
''',
        explanation="**Euclid's algorithm**: `gcd(a, b) = gcd(b, a mod b)` until `b = 0`. Then "
                    "`lcm = a / gcd × b` (divide first to keep numbers small). The LCM can reach 10^18, so "
                    "JavaScript needs `BigInt`. **O(log min(a, b))**.",
    ),
    dict(
        slug="count-primes", title="Count Primes", difficulty="easy", topics=["math", "sieve"],
        description="Count the prime numbers less than or equal to `n`.",
        input_format="A single integer `n`.",
        output_format="Print the count.",
        constraints="- 1 ≤ n ≤ 10^6",
        samples=["10", "2"],
        tests=["1", "3", "100", "1000000", "999983", "4"],
        gen=lambda r: str(r.randint(1, 10**6)),
        gen_count=3,
        py=r'''
n = int(input())
if n < 2:
    print(0)
else:
    is_p = bytearray([1]) * (n + 1)
    is_p[0] = is_p[1] = 0
    i = 2
    while i * i <= n:
        if is_p[i]:
            is_p[i * i::i] = bytearray(len(range(i * i, n + 1, i)))
        i += 1
    print(sum(is_p))
''',
        js=r'''
const n = Number(require('fs').readFileSync(0, 'utf8').trim());
const comp = new Uint8Array(n + 1);
let c = 0;
for (let i = 2; i <= n; i++) {
  if (comp[i]) continue;
  c++;
  for (let j = i * i; j <= n; j += i) comp[j] = 1;
}
console.log(c);
''',
        explanation="**Sieve of Eratosthenes**: for each prime `p`, mark its multiples starting from `p²` as "
                    "composite. Whatever stays unmarked is prime. **O(n log log n)** time.",
    ),
    dict(
        slug="reverse-words", title="Reverse Words in a Sentence", difficulty="easy", topics=["strings"],
        description="Reverse the order of the words in a sentence. Words are separated by one or more spaces; the "
                    "output must separate words by a single space.",
        input_format="A single line of text (letters and spaces, at least one word).",
        output_format="Print the words in reverse order.",
        constraints="- 1 ≤ length ≤ 10^5",
        samples=["the sky is blue", "  hello   world  "],
        tests=["a", "one two", "x  y  z"],
        gen=lambda r: (" " * r.randint(0, 2)).join(rand_word(r, r.randint(1, 8)) for _ in range(size(r, 5, 500, 10000))),
        py=r'''
import sys
print(" ".join(reversed(sys.stdin.readline().split())))
''',
        js=r'''
const line = require('fs').readFileSync(0, 'utf8').split('\n')[0];
console.log(line.split(' ').filter(Boolean).reverse().join(' '));
''',
        explanation="Split on whitespace (dropping empty pieces), reverse the list, join with single spaces. "
                    "**O(n)**.",
    ),
    dict(
        slug="intersection-of-two-arrays", title="Intersection of Two Arrays", difficulty="easy",
        topics=["arrays", "hashing"],
        description="Print the distinct values that appear in **both** arrays, in increasing order. If there are "
                    "none, print `-1`.",
        input_format="Line 1: `n`. Line 2: `n` integers.\nLine 3: `m`. Line 4: `m` integers.",
        output_format="Print the common values in increasing order, or `-1`.",
        constraints="- 1 ≤ n, m ≤ 10^5\n- -10^9 ≤ values ≤ 10^9",
        samples=["4\n1 2 2 1\n2\n2 2", "3\n4 9 5\n5\n9 4 9 8 4"],
        tests=["1\n1\n1\n2", "3\n-1 0 1\n3\n1 0 -1"],
        gen=lambda r: arr(rand_arr(r, size(r), 0, 200)) + arr(rand_arr(r, size(r), 100, 300)),
        py=r'''
import sys
data = sys.stdin.read().split()
n = int(data[0]); a = set(map(int, data[1:1 + n]))
m = int(data[1 + n]); b = set(map(int, data[2 + n:2 + n + m]))
common = sorted(a & b)
print(" ".join(map(str, common)) if common else -1)
''',
        js=r'''
const t = require('fs').readFileSync(0, 'utf8').split(/\s+/).filter(Boolean).map(Number);
const n = t[0], a = new Set(t.slice(1, 1 + n));
const m = t[1 + n], b = new Set(t.slice(2 + n, 2 + n + m));
const common = [...a].filter((x) => b.has(x)).sort((x, y) => x - y);
console.log(common.length ? common.join(' ') : '-1');
''',
        explanation="Put one array in a hash set, keep the distinct elements of the other that are in the set, and "
                    "sort the result. **O((n + m) + k log k)**. Note: JavaScript's default `sort()` compares as "
                    "strings — pass `(x, y) => x - y`.",
    ),
    dict(
        slug="climbing-stairs", title="Climbing Stairs", difficulty="easy", topics=["dynamic programming"],
        description="You climb a staircase with `n` steps, taking 1 or 2 steps at a time. In how many distinct ways "
                    "can you reach the top? Print the answer modulo `1 000 000 007`.",
        input_format="A single integer `n`.",
        output_format="Print the number of ways modulo 10^9 + 7.",
        constraints="- 1 ≤ n ≤ 10^5",
        samples=["2", "3"],
        tests=["1", "4", "45", "100000", "50", "1000"],
        gen=lambda r: str(r.randint(1, 10**5)),
        gen_count=3,
        py=r'''
n = int(input())
MOD = 10**9 + 7
a, b = 1, 1
for _ in range(n - 1):
    a, b = b, (a + b) % MOD
print(b)
''',
        js=r'''
const n = Number(require('fs').readFileSync(0, 'utf8').trim());
const MOD = 1000000007;
let a = 1, b = 1;
for (let i = 1; i < n; i++) [a, b] = [b, (a + b) % MOD];
console.log(b);
''',
        explanation="To reach step `i` your last move came from `i-1` or `i-2`, so `ways(i) = ways(i-1) + ways(i-2)` "
                    "— the Fibonacci recurrence. Keep two variables and take the modulo each step. **O(n)**.",
    ),
    dict(
        slug="pascals-triangle-row", title="Pascal's Triangle Row", difficulty="easy", topics=["math", "dynamic programming"],
        description="Print row `k` (0-indexed) of Pascal's triangle. Row 0 is `1`, row 1 is `1 1`, row 2 is `1 2 1`.",
        input_format="A single integer `k`.",
        output_format="Print the `k + 1` numbers of the row.",
        constraints="- 0 ≤ k ≤ 30",
        samples=["3", "0"],
        tests=["1", "2", "30", "10", "29", "15", "5", "20"],
        py=r'''
k = int(input())
row = [1]
for _ in range(k):
    row = [1] + [row[i] + row[i + 1] for i in range(len(row) - 1)] + [1]
print(" ".join(map(str, row)))
''',
        js=r'''
const k = Number(require('fs').readFileSync(0, 'utf8').trim());
const row = new Array(k + 1).fill(1);
for (let i = 2; i <= k; i++) for (let j = i - 1; j >= 1; j--) row[j] += row[j - 1];
console.log(row.join(' '));
''',
        explanation="Each entry is the sum of the two above it. Build rows iteratively, or update a single array "
                    "from right to left so values are not overwritten early. **O(k²)** time, **O(k)** space.",
    ),
    dict(
        slug="matrix-transpose", title="Matrix Transpose", difficulty="easy", topics=["matrix", "arrays"],
        description="Print the transpose of an `r × c` matrix (rows become columns).",
        input_format="Line 1: `r c`. Next `r` lines: `c` integers each.",
        output_format="Print the `c × r` transposed matrix.",
        constraints="- 1 ≤ r, c ≤ 300\n- -10^9 ≤ values ≤ 10^9",
        samples=["2 3\n1 2 3\n4 5 6", "1 1\n7"],
        tests=["1 4\n1 2 3 4", "4 1\n1\n2\n3\n4", "2 2\n1 2\n3 4"],
        gen=lambda r: (lambda R, C: f"{R} {C}\n" + "\n".join(" ".join(str(r.randint(-99, 99)) for _ in range(C)) for _ in range(R)))(r.randint(1, 120), r.randint(1, 120)),
        py=r'''
import sys
lines = sys.stdin.read().split("\n")
r, c = map(int, lines[0].split())
m = [lines[1 + i].split() for i in range(r)]
print("\n".join(" ".join(m[i][j] for i in range(r)) for j in range(c)))
''',
        js=r'''
const lines = require('fs').readFileSync(0, 'utf8').split('\n');
const [r, c] = lines[0].trim().split(/\s+/).map(Number);
const m = [];
for (let i = 0; i < r; i++) m.push(lines[1 + i].trim().split(/\s+/));
const out = [];
for (let j = 0; j < c; j++) { const row = []; for (let i = 0; i < r; i++) row.push(m[i][j]); out.push(row.join(' ')); }
console.log(out.join('\n'));
''',
        explanation="Element `(i, j)` moves to `(j, i)`. Loop over columns of the original to produce rows of the "
                    "result. **O(r·c)**.",
    ),
    dict(
        slug="longest-common-prefix", title="Longest Common Prefix", difficulty="easy", topics=["strings"],
        description="Find the longest string that is a prefix of all `n` given words. If it is empty, print `-1`.",
        input_format="The first line contains `n`. Each of the next `n` lines contains one word.",
        output_format="Print the longest common prefix, or `-1`.",
        constraints="- 1 ≤ n ≤ 10^4\n- 1 ≤ |word| ≤ 100, lowercase letters",
        samples=["3\nflower\nflow\nflight", "3\ndog\nracecar\ncar"],
        tests=["1\nalone", "2\nabc\nabc", "2\na\nab", "3\nprefix\npre\npref"],
        gen=lambda r: (lambda p, k: f"{k}\n" + "\n".join(p + rand_word(r, r.randint(0, 5), "ab") for _ in range(k)))(rand_word(r, r.randint(0, 20)), size(r, 5, 100, 10000)),
        py=r'''
import sys
data = sys.stdin.read().split()
words = data[1:1 + int(data[0])]
prefix = words[0]
for w in words[1:]:
    i = 0
    while i < len(prefix) and i < len(w) and prefix[i] == w[i]:
        i += 1
    prefix = prefix[:i]
print(prefix or -1)
''',
        js=r'''
const t = require('fs').readFileSync(0, 'utf8').split(/\s+/).filter(Boolean);
const words = t.slice(1, 1 + Number(t[0]));
let prefix = words[0];
for (const w of words) {
  let i = 0;
  while (i < prefix.length && i < w.length && prefix[i] === w[i]) i++;
  prefix = prefix.slice(0, i);
}
console.log(prefix || '-1');
''',
        explanation="Start with the first word as the candidate prefix and shrink it against each following word. "
                    "**O(total characters)**.",
    ),
    dict(
        slug="squares-of-sorted-array", title="Squares of a Sorted Array", difficulty="easy",
        topics=["arrays", "two pointers"],
        description="Given an array sorted in non-decreasing order (may contain negatives), print the squares of "
                    "each number, also sorted in non-decreasing order. Try for O(n).",
        input_format=ARRAY_IN,
        output_format="Print the sorted squares.",
        constraints="- 1 ≤ n ≤ 10^5\n- -10^4 ≤ a[i] ≤ 10^4",
        samples=["5\n-4 -1 0 3 10", "5\n-7 -3 2 3 11"],
        tests=["1\n-5", "3\n-3 -2 -1", "3\n0 0 0"],
        gen=lambda r: arr(sorted(rand_arr(r, size(r), -10**4, 10**4))),
        py=r'''
import sys
data = sys.stdin.read().split()
n = int(data[0])
a = list(map(int, data[1:1 + n]))
out = [0] * n
lo, hi = 0, n - 1
for k in range(n - 1, -1, -1):
    if abs(a[lo]) > abs(a[hi]):
        out[k] = a[lo] * a[lo]; lo += 1
    else:
        out[k] = a[hi] * a[hi]; hi -= 1
print(" ".join(map(str, out)))
''',
        js=r'''
const t = require('fs').readFileSync(0, 'utf8').split(/\s+/).filter(Boolean).map(Number);
const n = t[0], a = t.slice(1, 1 + n), out = new Array(n);
let lo = 0, hi = n - 1;
for (let k = n - 1; k >= 0; k--) {
  if (Math.abs(a[lo]) > Math.abs(a[hi])) { out[k] = a[lo] * a[lo]; lo++; }
  else { out[k] = a[hi] * a[hi]; hi--; }
}
console.log(out.join(' '));
''',
        explanation="The largest square is at one of the two ends. Use two pointers from both ends and fill the "
                    "output from the back with the larger square. **O(n)** instead of O(n log n) with sorting.",
    ),
    dict(
        slug="remove-nth-node-from-end", title="Remove Nth Node From End of List", difficulty="easy",
        topics=["linked list", "two pointers"],
        description="A singly linked list is given by its values from head to tail. Remove the `k`-th node from the "
                    "**end** and print the remaining list. If the list becomes empty print `EMPTY`.\n\n"
                    "Try to build an actual linked list and solve it in a single pass with two pointers.",
        input_format="Line 1: `n k`. Line 2: the `n` node values from head to tail.",
        output_format="Print the remaining values, or `EMPTY`.",
        constraints="- 1 ≤ k ≤ n ≤ 10^5\n- -10^9 ≤ values ≤ 10^9",
        samples=["5 2\n1 2 3 4 5", "1 1\n1"],
        tests=["2 1\n1 2", "2 2\n1 2", "3 3\n7 8 9"],
        gen=lambda r: (lambda a: f"{len(a)} {r.randint(1, len(a))}\n{' '.join(map(str, a))}")(rand_arr(r, size(r), -100, 100)),
        py=r'''
import sys


class Node:
    __slots__ = ("val", "next")

    def __init__(self, val, nxt=None):
        self.val, self.next = val, nxt


data = sys.stdin.read().split()
n, k = int(data[0]), int(data[1])
dummy = Node(0)
cur = dummy
for v in data[2:2 + n]:
    cur.next = Node(v)
    cur = cur.next

fast = slow = dummy
for _ in range(k):
    fast = fast.next
while fast.next:
    fast, slow = fast.next, slow.next
slow.next = slow.next.next

out = []
cur = dummy.next
while cur:
    out.append(cur.val)
    cur = cur.next
print(" ".join(out) if out else "EMPTY")
''',
        js=r'''
const t = require('fs').readFileSync(0, 'utf8').split(/\s+/).filter(Boolean);
const n = Number(t[0]), k = Number(t[1]);
const dummy = { val: 0, next: null };
let cur = dummy;
for (let i = 0; i < n; i++) { cur.next = { val: t[2 + i], next: null }; cur = cur.next; }

let fast = dummy, slow = dummy;
for (let i = 0; i < k; i++) fast = fast.next;
while (fast.next) { fast = fast.next; slow = slow.next; }
slow.next = slow.next.next;

const out = [];
for (cur = dummy.next; cur; cur = cur.next) out.push(cur.val);
console.log(out.length ? out.join(' ') : 'EMPTY');
''',
        explanation="Move a `fast` pointer `k` nodes ahead, then move `fast` and `slow` together until `fast` reaches "
                    "the last node. `slow` now sits just before the node to delete. A dummy head node handles "
                    "removing the first node. **O(n)**, one pass.",
    ),
    dict(
        slug="min-stack", title="Min Stack", difficulty="easy", topics=["stack", "design"],
        description="Implement a stack that supports these operations, all in O(1):\n\n"
                    "- `push x` — push `x`\n- `pop` — remove the top element\n- `top` — print the top element\n"
                    "- `getMin` — print the minimum element in the stack\n\n"
                    "If `top` or `getMin` is called on an empty stack print `EMPTY`. `pop` on an empty stack does "
                    "nothing.",
        input_format="The first line contains `q`. Each of the next `q` lines contains an operation.",
        output_format="For each `top` and `getMin`, print the result on its own line.",
        constraints="- 1 ≤ q ≤ 10^5 (at least one `top` or `getMin`)\n- -10^9 ≤ x ≤ 10^9",
        samples=["6\npush -2\npush 0\npush -3\ngetMin\npop\ntop", "3\ntop\npush 5\ngetMin"],
        tests=["1\ngetMin", "5\npush 1\npush 1\npop\ngetMin\ntop", "4\npush 3\npop\npop\ntop"],
        gen=gen_min_stack,
        py=r'''
import sys
lines = sys.stdin.read().split("\n")
q = int(lines[0])
stack = []  # pairs (value, min so far)
out = []
for i in range(1, q + 1):
    op = lines[i].split()
    if not op:
        continue
    if op[0] == "push":
        x = int(op[1])
        stack.append((x, min(x, stack[-1][1]) if stack else x))
    elif op[0] == "pop":
        if stack:
            stack.pop()
    elif op[0] == "top":
        out.append(str(stack[-1][0]) if stack else "EMPTY")
    else:
        out.append(str(stack[-1][1]) if stack else "EMPTY")
print("\n".join(out))
''',
        js=r'''
const lines = require('fs').readFileSync(0, 'utf8').split('\n');
const q = Number(lines[0]);
const vals = [], mins = [], out = [];
for (let i = 1; i <= q; i++) {
  const op = lines[i].trim().split(' ');
  if (op[0] === 'push') {
    const x = Number(op[1]);
    vals.push(x);
    mins.push(mins.length ? Math.min(x, mins[mins.length - 1]) : x);
  } else if (op[0] === 'pop') {
    vals.pop(); mins.pop();
  } else if (op[0] === 'top') {
    out.push(vals.length ? vals[vals.length - 1] : 'EMPTY');
  } else if (op[0] === 'getMin') {
    out.push(mins.length ? mins[mins.length - 1] : 'EMPTY');
  }
}
console.log(out.join('\n'));
''',
        explanation="Store alongside each element the minimum of the stack **at the time it was pushed**. The "
                    "current minimum is then always the value stored with the top element. Every operation is "
                    "**O(1)**.",
    ),
]
