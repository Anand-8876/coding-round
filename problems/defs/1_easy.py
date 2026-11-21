from _util import arr, rand_arr, size, rand_word

def gen_brackets(r):
    """Balanced bracket string, sometimes with one character corrupted."""
    out, stack = [], []
    for _ in range(r.choice([6, 50, 20000])):
        if stack and r.random() < 0.5:
            out.append(stack.pop())
        else:
            o, c = r.choice(["()", "[]", "{}"])
            out.append(o)
            stack.append(c)
    out.extend(reversed(stack))
    if r.random() < 0.5:
        out[r.randrange(len(out))] = r.choice("()[]{}")
    return "".join(out)


ARRAY_IN = "The first line contains an integer `n`.\nThe second line contains `n` space-separated integers."

PROBLEMS = [
    dict(
        slug="sum-of-array", title="Sum of Array", difficulty="easy", topics=["arrays"],
        description="Given an array of `n` integers, print the sum of all its elements.",
        input_format=ARRAY_IN,
        output_format="Print a single integer: the sum.",
        constraints="- 1 ≤ n ≤ 10^5\n- -10^9 ≤ a[i] ≤ 10^9",
        samples=["5\n1 2 3 4 5", "3\n-1 5 -7"],
        tests=["1\n0", "1\n-1000000000", arr([10**9] * 1000)],
        gen=lambda r: arr(rand_arr(r, size(r), -10**9, 10**9)),
        py=r'''
import sys
data = sys.stdin.read().split()
n = int(data[0])
print(sum(map(int, data[1:1 + n])))
''',
        js=r'''
const t = require('fs').readFileSync(0, 'utf8').split(/\s+/).filter(Boolean);
const n = Number(t[0]);
let s = 0n;
for (let i = 1; i <= n; i++) s += BigInt(t[i]);
console.log(s.toString());
''',
        explanation="Walk through the array once and keep a running total. **O(n)** time, **O(1)** space.\n\n"
                    "In JavaScript the total can go past `Number.MAX_SAFE_INTEGER` (up to 10^14 here is fine, but "
                    "using `BigInt` is a good habit when sums can overflow).",
    ),
    dict(
        slug="maximum-element", title="Maximum Element", difficulty="easy", topics=["arrays"],
        description="Given an array of `n` integers, print the largest element.",
        input_format=ARRAY_IN,
        output_format="Print the maximum value.",
        constraints="- 1 ≤ n ≤ 10^5\n- -10^9 ≤ a[i] ≤ 10^9",
        samples=["5\n3 9 2 7 4", "3\n-5 -2 -9"],
        tests=["1\n42", "4\n-1 -1 -1 -1", "2\n1000000000 -1000000000"],
        gen=lambda r: arr(rand_arr(r, size(r), -10**9, 10**9)),
        py=r'''
import sys
data = sys.stdin.read().split()
n = int(data[0])
print(max(map(int, data[1:1 + n])))
''',
        js=r'''
const t = require('fs').readFileSync(0, 'utf8').split(/\s+/).filter(Boolean).map(Number);
const n = t[0];
let best = -Infinity;
for (let i = 1; i <= n; i++) if (t[i] > best) best = t[i];
console.log(best);
''',
        explanation="Keep the largest value seen so far while scanning. Start from the first element (or -∞), "
                    "not from 0, because all values may be negative. **O(n)** time.",
    ),
    dict(
        slug="reverse-array", title="Reverse Array", difficulty="easy", topics=["arrays", "two pointers"],
        description="Given an array of `n` integers, print it in reverse order.",
        input_format=ARRAY_IN,
        output_format="Print the `n` elements in reverse order, space-separated.",
        constraints="- 1 ≤ n ≤ 10^5\n- -10^9 ≤ a[i] ≤ 10^9",
        samples=["5\n1 2 3 4 5", "2\n10 -3"],
        tests=["1\n7", "3\n5 5 5", "4\n1 2 2 1"],
        gen=lambda r: arr(rand_arr(r, size(r), -10**9, 10**9)),
        py=r'''
import sys
data = sys.stdin.read().split()
n = int(data[0])
a = data[1:1 + n]
i, j = 0, n - 1
while i < j:
    a[i], a[j] = a[j], a[i]
    i += 1
    j -= 1
print(" ".join(a))
''',
        js=r'''
const t = require('fs').readFileSync(0, 'utf8').split(/\s+/).filter(Boolean);
const n = Number(t[0]);
const a = t.slice(1, 1 + n);
for (let i = 0, j = n - 1; i < j; i++, j--) [a[i], a[j]] = [a[j], a[i]];
console.log(a.join(' '));
''',
        explanation="Two pointers: swap the first and last elements, then move both pointers inward until they meet. "
                    "**O(n)** time, **O(1)** extra space.",
    ),
    dict(
        slug="count-even-numbers", title="Count Even Numbers", difficulty="easy", topics=["arrays", "math"],
        description="Given an array of `n` integers, count how many of them are even.",
        input_format=ARRAY_IN,
        output_format="Print the number of even elements.",
        constraints="- 1 ≤ n ≤ 10^5\n- -10^9 ≤ a[i] ≤ 10^9",
        samples=["5\n1 2 3 4 5", "4\n-2 0 7 -9"],
        tests=["1\n1", "1\n0", "3\n-4 -6 -8"],
        gen=lambda r: arr(rand_arr(r, size(r), -10**9, 10**9)),
        py=r'''
import sys
data = sys.stdin.read().split()
n = int(data[0])
print(sum(1 for x in data[1:1 + n] if int(x) % 2 == 0))
''',
        js=r'''
const t = require('fs').readFileSync(0, 'utf8').split(/\s+/).filter(Boolean).map(Number);
let c = 0;
for (let i = 1; i <= t[0]; i++) if (t[i] % 2 === 0) c++;
console.log(c);
''',
        explanation="A number is even when `x % 2 == 0`. Careful: in JavaScript `-3 % 2` is `-1`, so test for "
                    "`=== 0` rather than `=== 1` for odd. **O(n)**.",
    ),
    dict(
        slug="palindrome-string", title="Palindrome String", difficulty="easy", topics=["strings", "two pointers"],
        description="Given a string `s` of lowercase English letters, print `YES` if it reads the same forwards and "
                    "backwards, otherwise print `NO`.",
        input_format="A single line containing `s`.",
        output_format="`YES` or `NO`.",
        constraints="- 1 ≤ |s| ≤ 10^5",
        samples=["racecar", "hello"],
        tests=["a", "ab", "aa", "abba", "abca"],
        gen=lambda r: (lambda w: w + (w[::-1] if r.random() < 0.5 else rand_word(r, len(w))))(rand_word(r, r.randint(1, 5000), "ab")),
        py=r'''
s = input().strip()
i, j = 0, len(s) - 1
ok = True
while i < j:
    if s[i] != s[j]:
        ok = False
        break
    i += 1
    j -= 1
print("YES" if ok else "NO")
''',
        js=r'''
const s = require('fs').readFileSync(0, 'utf8').trim();
let ok = true;
for (let i = 0, j = s.length - 1; i < j; i++, j--) if (s[i] !== s[j]) { ok = false; break; }
console.log(ok ? 'YES' : 'NO');
''',
        explanation="Compare characters from both ends moving inward; stop at the first mismatch. **O(n)** time, "
                    "**O(1)** space. (`s == s[::-1]` also works but uses O(n) extra memory.)",
    ),
    dict(
        slug="fizzbuzz", title="FizzBuzz", difficulty="easy", topics=["math", "simulation"],
        description="For every integer `i` from 1 to `n` print:\n\n- `FizzBuzz` if `i` is divisible by 3 and 5\n"
                    "- `Fizz` if `i` is divisible by 3 only\n- `Buzz` if `i` is divisible by 5 only\n- `i` otherwise",
        input_format="A single integer `n`.",
        output_format="`n` lines as described.",
        constraints="- 1 ≤ n ≤ 10^4",
        samples=["5", "15"],
        tests=["1", "3", "30", "10000", "99", "7", "45", "2"],
        py=r'''
n = int(input())
out = []
for i in range(1, n + 1):
    if i % 15 == 0:
        out.append("FizzBuzz")
    elif i % 3 == 0:
        out.append("Fizz")
    elif i % 5 == 0:
        out.append("Buzz")
    else:
        out.append(str(i))
print("\n".join(out))
''',
        js=r'''
const n = Number(require('fs').readFileSync(0, 'utf8').trim());
const out = [];
for (let i = 1; i <= n; i++) {
  if (i % 15 === 0) out.push('FizzBuzz');
  else if (i % 3 === 0) out.push('Fizz');
  else if (i % 5 === 0) out.push('Buzz');
  else out.push(String(i));
}
console.log(out.join('\n'));
''',
        explanation="Check divisibility by 15 **first** — otherwise multiples of 15 would print `Fizz`. Build the "
                    "output in a list and print once; printing line by line is much slower for large `n`.",
    ),
    dict(
        slug="factorial", title="Factorial", difficulty="easy", topics=["math", "recursion"],
        description="Print `n!` (the product 1 × 2 × … × n). By definition `0! = 1`.",
        input_format="A single integer `n`.",
        output_format="Print `n!`.",
        constraints="- 0 ≤ n ≤ 20",
        samples=["5", "0"],
        tests=["1", "2", "10", "19", "20", "13", "3", "12"],
        py=r'''
n = int(input())
f = 1
for i in range(2, n + 1):
    f *= i
print(f)
''',
        js=r'''
const n = Number(require('fs').readFileSync(0, 'utf8').trim());
let f = 1n;
for (let i = 2n; i <= BigInt(n); i++) f *= i;
console.log(f.toString());
''',
        explanation="Multiply 1..n in a loop. `20!` ≈ 2.4 × 10^18, which is larger than JavaScript's safe integer "
                    "limit (2^53), so the JavaScript solution must use `BigInt`. Python integers never overflow.",
    ),
    dict(
        slug="fibonacci-number", title="Fibonacci Number", difficulty="easy", topics=["math", "dynamic programming"],
        description="The Fibonacci sequence is `F(0) = 0`, `F(1) = 1`, `F(n) = F(n-1) + F(n-2)`. Print `F(n)`.",
        input_format="A single integer `n`.",
        output_format="Print `F(n)`.",
        constraints="- 0 ≤ n ≤ 90",
        samples=["10", "1"],
        tests=["0", "2", "50", "90", "78", "79", "30", "5"],
        py=r'''
n = int(input())
a, b = 0, 1
for _ in range(n):
    a, b = b, a + b
print(a)
''',
        js=r'''
const n = Number(require('fs').readFileSync(0, 'utf8').trim());
let a = 0n, b = 1n;
for (let i = 0; i < n; i++) [a, b] = [b, a + b];
console.log(a.toString());
''',
        explanation="Naive recursion is exponential. Iterate instead, keeping only the last two values: **O(n)** "
                    "time, **O(1)** space. `F(90)` exceeds 2^53, so use `BigInt` in JavaScript.",
    ),
    dict(
        slug="count-vowels", title="Count Vowels", difficulty="easy", topics=["strings"],
        description="Given a line of text, count the vowels (`a e i o u`, upper or lower case).",
        input_format="A single line of text containing letters and spaces.",
        output_format="Print the number of vowels.",
        constraints="- 1 ≤ length ≤ 10^5",
        samples=["Hello World", "rhythm"],
        tests=["A", "AEIOU aeiou", "z", "The Quick Brown Fox Jumps Over The Lazy Dog"],
        gen=lambda r: " ".join(rand_word(r, r.randint(1, 10), "abcdeiouxyzAEIOUBCD") for _ in range(r.randint(1, 3000))),
        py=r'''
import sys
s = sys.stdin.readline().rstrip("\n")
print(sum(1 for c in s if c in "aeiouAEIOU"))
''',
        js=r'''
const s = require('fs').readFileSync(0, 'utf8').split('\n')[0];
let c = 0;
for (const ch of s) if ('aeiouAEIOU'.includes(ch)) c++;
console.log(c);
''',
        explanation="Scan each character and check membership in the vowel set (both cases). **O(n)**.",
    ),
    dict(
        slug="second-largest", title="Second Largest Element", difficulty="easy", topics=["arrays"],
        description="Given an array of `n` integers, print the second largest **distinct** value. If it does not "
                    "exist (all elements are equal), print `-1`.",
        input_format=ARRAY_IN,
        output_format="Print the second largest distinct value, or `-1`.",
        constraints="- 2 ≤ n ≤ 10^5\n- 0 ≤ a[i] ≤ 10^9",
        samples=["5\n3 9 2 9 4", "3\n7 7 7"],
        tests=["2\n1 2", "2\n5 5", "4\n0 0 0 1", "5\n10 9 8 7 6"],
        gen=lambda r: arr(rand_arr(r, max(2, size(r)), 0, r.choice([3, 10**9]))),
        py=r'''
import sys
data = sys.stdin.read().split()
n = int(data[0])
first = second = -1
for x in map(int, data[1:1 + n]):
    if x > first:
        first, second = x, first
    elif first > x > second:
        second = x
print(second)
''',
        js=r'''
const t = require('fs').readFileSync(0, 'utf8').split(/\s+/).filter(Boolean).map(Number);
let first = -1, second = -1;
for (let i = 1; i <= t[0]; i++) {
  const x = t[i];
  if (x > first) { second = first; first = x; }
  else if (x < first && x > second) second = x;
}
console.log(second);
''',
        explanation="Track the largest and second largest in one pass. When a new maximum appears, the old maximum "
                    "becomes the second. Ignore values equal to the maximum so the answer is distinct. **O(n)**.",
    ),
    dict(
        slug="linear-search", title="Linear Search", difficulty="easy", topics=["arrays", "searching"],
        description="Given an array and a value `x`, print the 1-based index of the **first** occurrence of `x`, "
                    "or `-1` if it does not appear.",
        input_format="The first line contains `n` and `x`.\nThe second line contains `n` integers.",
        output_format="Print the index or `-1`.",
        constraints="- 1 ≤ n ≤ 10^5\n- -10^9 ≤ a[i], x ≤ 10^9",
        samples=["5 7\n1 7 3 7 5", "3 4\n1 2 3"],
        tests=["1 1\n1", "1 2\n1", "4 9\n1 2 3 9"],
        gen=lambda r: (lambda a: f"{len(a)} {r.choice(a + [10**9 + 0])}\n{' '.join(map(str, a))}")(rand_arr(r, size(r), 0, 50)),
        py=r'''
import sys
data = sys.stdin.read().split()
n, x = int(data[0]), data[1]
ans = -1
for i in range(n):
    if data[2 + i] == x:
        ans = i + 1
        break
print(ans)
''',
        js=r'''
const t = require('fs').readFileSync(0, 'utf8').split(/\s+/).filter(Boolean).map(Number);
const n = t[0], x = t[1];
let ans = -1;
for (let i = 0; i < n; i++) if (t[2 + i] === x) { ans = i + 1; break; }
console.log(ans);
''',
        explanation="Check each element in order and stop at the first match. **O(n)** time.",
    ),
    dict(
        slug="check-sorted", title="Is It Sorted?", difficulty="easy", topics=["arrays"],
        description="Print `YES` if the array is sorted in non-decreasing order, otherwise `NO`.",
        input_format=ARRAY_IN,
        output_format="`YES` or `NO`.",
        constraints="- 1 ≤ n ≤ 10^5\n- -10^9 ≤ a[i] ≤ 10^9",
        samples=["5\n1 2 2 4 9", "3\n3 1 2"],
        tests=["1\n5", "2\n2 1", "3\n4 4 4", "4\n1 2 3 2"],
        gen=lambda r: arr(sorted(rand_arr(r, size(r), -1000, 1000)) if r.random() < 0.5 else rand_arr(r, size(r), 1, 3)),
        py=r'''
import sys
data = sys.stdin.read().split()
n = int(data[0])
a = list(map(int, data[1:1 + n]))
print("YES" if all(a[i] <= a[i + 1] for i in range(n - 1)) else "NO")
''',
        js=r'''
const t = require('fs').readFileSync(0, 'utf8').split(/\s+/).filter(Boolean).map(Number);
const n = t[0];
let ok = true;
for (let i = 1; i < n; i++) if (t[i] > t[i + 1]) { ok = false; break; }
console.log(ok ? 'YES' : 'NO');
''',
        explanation="An array is sorted iff every adjacent pair satisfies `a[i] ≤ a[i+1]`. **O(n)**.",
    ),
    dict(
        slug="remove-duplicates-sorted", title="Remove Duplicates from Sorted Array", difficulty="easy",
        topics=["arrays", "two pointers"],
        description="Given a sorted array, remove the duplicates so each value appears once. Print the number of "
                    "unique values `k`, then the unique values in order.",
        input_format=ARRAY_IN + " The array is sorted in non-decreasing order.",
        output_format="First line: `k`. Second line: the `k` unique values.",
        constraints="- 1 ≤ n ≤ 10^5\n- -10^9 ≤ a[i] ≤ 10^9",
        samples=["6\n1 1 2 3 3 3", "3\n5 5 5"],
        tests=["1\n0", "4\n1 2 3 4", "5\n-2 -2 -1 -1 0"],
        gen=lambda r: arr(sorted(rand_arr(r, size(r), -50, 50))),
        py=r'''
import sys
data = sys.stdin.read().split()
n = int(data[0])
a = list(map(int, data[1:1 + n]))
k = 1
for i in range(1, n):
    if a[i] != a[k - 1]:
        a[k] = a[i]
        k += 1
print(k)
print(" ".join(map(str, a[:k])))
''',
        js=r'''
const t = require('fs').readFileSync(0, 'utf8').split(/\s+/).filter(Boolean).map(Number);
const n = t[0], a = t.slice(1, 1 + n);
let k = 1;
for (let i = 1; i < n; i++) if (a[i] !== a[k - 1]) a[k++] = a[i];
console.log(k + '\n' + a.slice(0, k).join(' '));
''',
        explanation="Use a slow pointer `k` marking the end of the unique prefix and a fast pointer `i`. Whenever "
                    "`a[i]` differs from the last unique value, copy it to `a[k]`. **O(n)** time, **O(1)** space.",
    ),
    dict(
        slug="two-sum", title="Two Sum", difficulty="easy", topics=["arrays", "hashing"],
        description="Given an array and a `target`, find indices `i < j` with `a[i] + a[j] = target`.\n\n"
                    "If there are several pairs, print the one with the **smallest `j`**; among those, the smallest "
                    "`i`. If no pair exists print `-1`.",
        input_format="The first line contains `n` and `target`.\nThe second line contains `n` integers.",
        output_format="Print the 1-based indices `i j`, or `-1`.",
        constraints="- 2 ≤ n ≤ 10^5\n- -10^9 ≤ a[i], target ≤ 10^9",
        samples=["4 9\n2 7 11 15", "3 10\n1 2 3"],
        tests=["2 2\n1 1", "5 6\n3 3 3 3 3", "4 0\n-1 1 -2 2", "2 5\n1 1"],
        gen=lambda r: (lambda a: f"{len(a)} {r.choice(a) + r.choice(a)}\n{' '.join(map(str, a))}")(rand_arr(r, max(2, size(r)), -10**6, 10**6)),
        py=r'''
import sys
data = sys.stdin.read().split()
n, target = int(data[0]), int(data[1])
a = list(map(int, data[2:2 + n]))
seen = {}
ans = "-1"
for j, x in enumerate(a):
    if target - x in seen:
        ans = f"{seen[target - x] + 1} {j + 1}"
        break
    if x not in seen:
        seen[x] = j
print(ans)
''',
        js=r'''
const t = require('fs').readFileSync(0, 'utf8').split(/\s+/).filter(Boolean).map(Number);
const n = t[0], target = t[1];
const seen = new Map();
let ans = '-1';
for (let j = 0; j < n; j++) {
  const x = t[2 + j];
  if (seen.has(target - x)) { ans = `${seen.get(target - x) + 1} ${j + 1}`; break; }
  if (!seen.has(x)) seen.set(x, j);
}
console.log(ans);
''',
        explanation="Scan left to right with a hash map from value → first index seen. For each `j`, check whether "
                    "`target - a[j]` has been seen. The first hit gives the smallest `j`, and storing only the first "
                    "index of each value gives the smallest `i`. **O(n)** time and space, versus O(n²) brute force.",
    ),
    dict(
        slug="valid-anagram", title="Valid Anagram", difficulty="easy", topics=["strings", "hashing"],
        description="Given two strings `s` and `t` of lowercase letters, print `YES` if `t` is an anagram of `s` "
                    "(same letters with the same counts), otherwise `NO`.",
        input_format="Two lines: `s` and `t`.",
        output_format="`YES` or `NO`.",
        constraints="- 1 ≤ |s|, |t| ≤ 10^5",
        samples=["listen\nsilent", "rat\ncar"],
        tests=["a\na", "a\nb", "ab\na", "aab\nabb"],
        gen=lambda r: (lambda w: w + "\n" + ("".join(r.sample(w, len(w))) if r.random() < 0.6 else rand_word(r, len(w), "abc")))(rand_word(r, r.randint(1, 20000), "abc")),
        py=r'''
from collections import Counter
s = input().strip()
t = input().strip()
print("YES" if Counter(s) == Counter(t) else "NO")
''',
        js=r'''
const [s, t] = require('fs').readFileSync(0, 'utf8').split('\n').map((x) => x.trim());
const cnt = new Array(26).fill(0);
for (const c of s) cnt[c.charCodeAt(0) - 97]++;
for (const c of t) cnt[c.charCodeAt(0) - 97]--;
console.log(s.length === t.length && cnt.every((x) => x === 0) ? 'YES' : 'NO');
''',
        explanation="Count letters in `s`, subtract counts from `t`; they are anagrams iff every count ends at zero. "
                    "**O(n)** time, **O(1)** space (26 counters). Sorting both strings works too in O(n log n).",
    ),
    dict(
        slug="move-zeroes", title="Move Zeroes", difficulty="easy", topics=["arrays", "two pointers"],
        description="Move all zeros in the array to the end while keeping the relative order of the non-zero "
                    "elements. Print the resulting array.",
        input_format=ARRAY_IN,
        output_format="Print the `n` elements after moving zeros.",
        constraints="- 1 ≤ n ≤ 10^5\n- -10^9 ≤ a[i] ≤ 10^9",
        samples=["5\n0 1 0 3 12", "1\n0"],
        tests=["3\n1 2 3", "3\n0 0 0", "4\n-1 0 0 -2"],
        gen=lambda r: arr([x if r.random() < 0.6 else 0 for x in rand_arr(r, size(r), -100, 100)]),
        py=r'''
import sys
data = sys.stdin.read().split()
n = int(data[0])
a = list(map(int, data[1:1 + n]))
k = 0
for i in range(n):
    if a[i] != 0:
        a[k], a[i] = a[i], a[k]
        k += 1
print(" ".join(map(str, a)))
''',
        js=r'''
const t = require('fs').readFileSync(0, 'utf8').split(/\s+/).filter(Boolean).map(Number);
const n = t[0], a = t.slice(1, 1 + n);
let k = 0;
for (let i = 0; i < n; i++) if (a[i] !== 0) { [a[k], a[i]] = [a[i], a[k]]; k++; }
console.log(a.join(' '));
''',
        explanation="Pointer `k` marks where the next non-zero belongs. Swap each non-zero into position `k`. "
                    "Zeros naturally collect at the end. **O(n)** time, **O(1)** space.",
    ),
    dict(
        slug="best-time-to-buy-and-sell-stock", title="Best Time to Buy and Sell Stock", difficulty="easy",
        topics=["arrays", "greedy"],
        description="`prices[i]` is a stock's price on day `i`. Choose one day to buy and a **later** day to sell. "
                    "Print the maximum profit, or `0` if no profit is possible.",
        input_format=ARRAY_IN,
        output_format="Print the maximum profit.",
        constraints="- 1 ≤ n ≤ 10^5\n- 0 ≤ prices[i] ≤ 10^4",
        samples=["6\n7 1 5 3 6 4", "5\n7 6 4 3 1"],
        tests=["1\n5", "2\n1 2", "2\n2 1", "4\n3 3 3 3"],
        gen=lambda r: arr(rand_arr(r, size(r), 0, 10**4)),
        py=r'''
import sys
data = sys.stdin.read().split()
n = int(data[0])
best, low = 0, float("inf")
for p in map(int, data[1:1 + n]):
    low = min(low, p)
    best = max(best, p - low)
print(best)
''',
        js=r'''
const t = require('fs').readFileSync(0, 'utf8').split(/\s+/).filter(Boolean).map(Number);
let best = 0, low = Infinity;
for (let i = 1; i <= t[0]; i++) { low = Math.min(low, t[i]); best = Math.max(best, t[i] - low); }
console.log(best);
''',
        explanation="For each day, the best sale ends today and buys at the minimum price seen so far. Track that "
                    "minimum and the best difference in one pass. **O(n)**.",
    ),
    dict(
        slug="valid-parentheses", title="Valid Parentheses", difficulty="easy", topics=["stack", "strings"],
        description="Given a string of brackets `()[]{}`, print `YES` if every bracket is closed by the same type in "
                    "the correct order, otherwise `NO`.",
        input_format="A single line containing the string.",
        output_format="`YES` or `NO`.",
        constraints="- 1 ≤ |s| ≤ 10^5",
        samples=["()[]{}", "([)]"],
        tests=["(", ")", "{[]}", "((((", "(()", "[{()}]"],
        gen=gen_brackets,
        py=r'''
s = input().strip()
pairs = {")": "(", "]": "[", "}": "{"}
stack = []
ok = True
for c in s:
    if c in "([{":
        stack.append(c)
    elif not stack or stack.pop() != pairs[c]:
        ok = False
        break
print("YES" if ok and not stack else "NO")
''',
        js=r'''
const s = require('fs').readFileSync(0, 'utf8').trim();
const pairs = { ')': '(', ']': '[', '}': '{' };
const stack = [];
let ok = true;
for (const c of s) {
  if ('([{'.includes(c)) stack.push(c);
  else if (stack.pop() !== pairs[c]) { ok = false; break; }
}
console.log(ok && stack.length === 0 ? 'YES' : 'NO');
''',
        explanation="Push opening brackets onto a stack. For a closing bracket, the top of the stack must be the "
                    "matching opener. At the end the stack must be empty. **O(n)**.",
    ),
    dict(
        slug="binary-search", title="Binary Search", difficulty="easy", topics=["binary search"],
        description="Given a sorted array of **distinct** integers and a value `x`, print the 1-based index of `x`, "
                    "or `-1` if absent. Aim for O(log n).",
        input_format="The first line contains `n` and `x`.\nThe second line contains `n` sorted distinct integers.",
        output_format="Print the index or `-1`.",
        constraints="- 1 ≤ n ≤ 10^5\n- -10^9 ≤ a[i], x ≤ 10^9",
        samples=["5 9\n-1 0 3 5 9", "5 2\n-1 0 3 5 9"],
        tests=["1 5\n5", "1 4\n5", "2 1\n1 2", "3 100\n1 2 3"],
        gen=lambda r: (lambda a: f"{len(a)} {r.choice(a) if r.random() < 0.7 else r.randint(-10**6, 10**6)}\n{' '.join(map(str, a))}")(sorted(r.sample(range(-10**6, 10**6), size(r)))),
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
    if a[mid] < x:
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
  if (a[mid] < x) lo = mid + 1; else hi = mid - 1;
}
console.log(ans);
''',
        explanation="Keep a search window `[lo, hi]`. Compare the middle element with `x` and discard the half that "
                    "cannot contain it. **O(log n)** comparisons.",
    ),
    dict(
        slug="merge-sorted-arrays", title="Merge Two Sorted Arrays", difficulty="easy",
        topics=["arrays", "two pointers", "sorting"],
        description="Merge two sorted arrays into one sorted array.",
        input_format="Line 1: `n`. Line 2: `n` sorted integers.\nLine 3: `m`. Line 4: `m` sorted integers.",
        output_format="Print the `n + m` merged values.",
        constraints="- 1 ≤ n, m ≤ 10^5\n- -10^9 ≤ values ≤ 10^9",
        samples=["3\n1 3 5\n3\n2 4 6", "2\n1 1\n1\n1"],
        tests=["1\n5\n1\n-5", "3\n1 2 3\n2\n4 5", "2\n10 20\n3\n1 2 3"],
        gen=lambda r: arr(sorted(rand_arr(r, size(r), -1000, 1000))) + arr(sorted(rand_arr(r, size(r), -1000, 1000))),
        py=r'''
import sys
data = sys.stdin.read().split()
n = int(data[0]); a = list(map(int, data[1:1 + n]))
m = int(data[1 + n]); b = list(map(int, data[2 + n:2 + n + m]))
i = j = 0
out = []
while i < n and j < m:
    if a[i] <= b[j]:
        out.append(a[i]); i += 1
    else:
        out.append(b[j]); j += 1
out.extend(a[i:]); out.extend(b[j:])
print(" ".join(map(str, out)))
''',
        js=r'''
const t = require('fs').readFileSync(0, 'utf8').split(/\s+/).filter(Boolean).map(Number);
const n = t[0], a = t.slice(1, 1 + n), m = t[1 + n], b = t.slice(2 + n, 2 + n + m);
const out = [];
let i = 0, j = 0;
while (i < n && j < m) out.push(a[i] <= b[j] ? a[i++] : b[j++]);
while (i < n) out.push(a[i++]);
while (j < m) out.push(b[j++]);
console.log(out.join(' '));
''',
        explanation="Two pointers, one per array: repeatedly take the smaller front element. This is the merge step "
                    "of merge sort. **O(n + m)**.",
    ),
]
