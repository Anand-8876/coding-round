"""Helpers for writing test generators in problem definitions."""
import string


def arr(values):
    """Format an array as 'n' on one line and the values on the next."""
    return f"{len(values)}\n{' '.join(map(str, values))}\n"


def rand_arr(rnd, n, lo, hi):
    return [rnd.randint(lo, hi) for _ in range(n)]


LARGE_CAP = 10000  # keeps the generated JSON small; still enough to time out O(n^2) solutions in Python


def size(rnd, small=10, medium=1000, large=LARGE_CAP):
    """Pick a test size: mostly small/medium, occasionally large."""
    large = min(large, LARGE_CAP)
    medium = min(medium, large)
    x = rnd.random()
    if x < 0.4:
        return rnd.randint(1, small)
    if x < 0.85:
        return rnd.randint(small, medium)
    return rnd.randint(medium, large)


def rand_word(rnd, n, alphabet=string.ascii_lowercase):
    return "".join(rnd.choice(alphabet) for _ in range(n))


def grid(rows):
    return "\n".join("".join(r) if isinstance(r[0], str) else " ".join(map(str, r)) for r in rows)


# ---------- trees ----------
# Trees are given in level order: the root, then for every present node its left and right child,
# using -1 for a missing child (all real values are >= 0). Trailing -1s are dropped.

def random_tree(rnd, n, lo=0, hi=10**4, bst=False):
    """Return (root, children) where children[v] = [left, right] (None = missing); nodes are values."""
    if bst:
        vals = rnd.sample(range(lo, hi + 1), n)
        root = vals[0]
        ch = {root: [None, None]}
        for v in vals[1:]:
            cur = root
            while True:
                side = 0 if v < cur else 1
                if ch[cur][side] is None:
                    ch[cur][side] = v
                    ch[v] = [None, None]
                    break
                cur = ch[cur][side]
        return root, ch
    # generic tree: node ids 0..n-1 with random values, attached to random free slots;
    # a "chain" bias sometimes makes deep trees.
    vals = [rnd.randint(lo, hi) for _ in range(n)]
    ch = {0: [None, None]}
    free = [(0, 0), (0, 1)]
    for v in range(1, n):
        i = len(free) - 1 if rnd.random() < 0.3 else rnd.randrange(len(free))
        p, side = free[i]
        free[i] = free[-1]
        free.pop()
        ch[p][side] = v
        ch[v] = [None, None]
        free += [(v, 0), (v, 1)]
    return 0, {"vals": vals, "ch": ch}


def level_order(root, ch, value=lambda v: v):
    out = [str(value(root))]
    q = [root]
    for node in q:
        for c in ch[node]:
            if c is None:
                out.append("-1")
            else:
                out.append(str(value(c)))
                q.append(c)
    while out[-1] == "-1":
        out.pop()
    return f"{len(out)}\n{' '.join(out)}"


def tree_input(rnd, n, lo=0, hi=10**4, bst=False):
    if bst:
        root, ch = random_tree(rnd, n, lo, hi, bst=True)
        return level_order(root, ch)
    root, t = random_tree(rnd, n, lo, hi)
    return level_order(root, t["ch"], lambda v: t["vals"][v])


# ---------- graphs ----------

def edges_input(n, edges, header=None):
    head = header if header is not None else f"{n} {len(edges)}"
    return head + "\n" + "\n".join(" ".join(map(str, e)) for e in edges)
