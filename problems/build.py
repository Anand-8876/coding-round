"""
Build + verify the problem set.

Problems are authored in problems/defs/*.py. Each module exposes PROBLEMS, a
list of dicts:

    dict(
        slug="two-sum", title="Two Sum", difficulty="easy", topics=[...],
        description="...markdown...", input_format="...", output_format="...",
        constraints="...",
        samples=["<input 1>", "<input 2>"],       # shown to the user
        tests=["<input>", ...],                    # hand-written edge cases (hidden)
        gen=lambda rnd: "<input>",                 # optional random-test generator
        gen_count=6,                               # how many random tests
        py=r'''...''', js=r'''...''',             # reference solutions
        explanation="...markdown...",
        starter_py=None, starter_js=None,          # optional, else generic
        time_limit_ms=2000,
    )

For every test input this script runs BOTH reference solutions, requires their
outputs to match, and writes problems/data/NNN-slug.json with expected outputs.

    python problems/build.py                 # build all
    python problems/build.py --verify-only   # re-run both solutions against the built JSON
    python problems/build.py --only 12       # build a single problem id
"""
import argparse
import glob
import importlib.util
import json
import os
import random
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.abspath(__file__))
DEFS = os.path.join(ROOT, "defs")
OUT = os.path.join(ROOT, "data")
NODE = shutil.which("node") or "node"
PY = sys.executable

GENERIC_PY = '''import sys


def main():
    data = sys.stdin.read()
    lines = data.splitlines()   # input line by line
    tokens = data.split()       # or: all whitespace-separated values
    # Parse the input described in "Input Format", solve, then print() the answer.


main()
'''

GENERIC_JS = r'''const data = require('fs').readFileSync(0, 'utf8');
const lines = data.split(/\r?\n/);              // input line by line
const tokens = data.split(/\s+/).filter(Boolean); // or: all whitespace-separated values
// Parse the input described in "Input Format", solve, then console.log() the answer.

'''


def norm(s):
    return "\n".join(line.rstrip() for line in s.replace("\r\n", "\n").split("\n")).rstrip()


def run(lang, path, inp, timeout):
    cmd = [PY, "-I", path] if lang == "py" else [NODE, "--stack-size=65500", path]
    r = subprocess.run(cmd, input=inp.encode(), capture_output=True, timeout=timeout)
    if r.returncode != 0:
        raise RuntimeError(f"{lang} solution crashed:\n{r.stderr.decode()[-1500:]}")
    return r.stdout.decode()


def load_defs():
    items = []
    sys.path.insert(0, DEFS)
    for f in sorted(glob.glob(os.path.join(DEFS, "*.py"))):
        if os.path.basename(f).startswith("_"):
            continue
        spec = importlib.util.spec_from_file_location(os.path.basename(f)[:-3], f)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        items.extend(mod.PROBLEMS)
    return items


def check_solutions(pid, slug, py_code, js_code, inputs, timeout):
    """Run both solutions on every input; return list of expected outputs."""
    tmp = tempfile.mkdtemp(prefix="ca-build-")
    try:
        pyf, jsf = os.path.join(tmp, "s.py"), os.path.join(tmp, "s.js")
        open(pyf, "w", encoding="utf-8").write(py_code)
        open(jsf, "w", encoding="utf-8").write(js_code)

        def one(inp):
            a = run("py", pyf, inp, timeout)
            b = run("js", jsf, inp, timeout)
            return a, b

        with ThreadPoolExecutor(max_workers=8) as ex:
            outs = list(ex.map(one, inputs))
        expected = []
        for i, (a, b) in enumerate(outs):
            if norm(a) != norm(b):
                raise RuntimeError(
                    f"#{pid} {slug}: python/javascript disagree on test {i + 1}\n"
                    f"input:\n{inputs[i][:500]}\npython:\n{a[:500]}\njavascript:\n{b[:500]}"
                )
            if not norm(a):
                raise RuntimeError(f"#{pid} {slug}: empty output on test {i + 1}")
            expected.append(norm(a) + "\n")
        return expected
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def build(only=None):
    defs = load_defs()
    slugs = [d["slug"] for d in defs]
    dupes = {s for s in slugs if slugs.count(s) > 1}
    if dupes:
        sys.exit(f"duplicate slugs: {dupes}")

    os.makedirs(OUT, exist_ok=True)
    if only is None:
        for f in glob.glob(os.path.join(OUT, "*.json")):
            os.remove(f)

    failures = 0
    for pid, d in enumerate(defs, start=1):
        if only is not None and pid != only:
            continue
        rnd = random.Random(f"{d['slug']}-seed")
        hidden_inputs = list(d.get("tests", []))
        if d.get("gen"):
            hidden_inputs += [d["gen"](rnd) for _ in range(d.get("gen_count", 6))]
        hidden_inputs = [i if i.endswith("\n") else i + "\n" for i in hidden_inputs]
        samples = [i if i.endswith("\n") else i + "\n" for i in d["samples"]]
        tl = d.get("time_limit_ms", 2000)
        try:
            outs = check_solutions(pid, d["slug"], d["py"], d["js"], samples + hidden_inputs, timeout=10)
        except Exception as e:  # noqa: BLE001
            failures += 1
            print(f"FAIL {e}", file=sys.stderr)
            continue
        if len(samples) < 2 or len(hidden_inputs) < 8:
            print(f"WARN #{pid} {d['slug']}: {len(samples)} samples, {len(hidden_inputs)} hidden tests")

        problem = {
            "id": pid,
            "slug": d["slug"],
            "title": d["title"],
            "difficulty": d["difficulty"],
            "topics": d["topics"],
            "description": d["description"].strip(),
            "inputFormat": d["input_format"].strip(),
            "outputFormat": d["output_format"].strip(),
            "constraints": d["constraints"].strip(),
            "sampleTests": [{"input": i, "output": o} for i, o in zip(samples, outs)],
            "hiddenTests": [{"input": i, "output": o} for i, o in zip(hidden_inputs, outs[len(samples):])],
            "starterCode": {
                "python": d.get("starter_py") or GENERIC_PY,
                "javascript": d.get("starter_js") or GENERIC_JS,
            },
            "solution": {"python": d["py"].strip() + "\n", "javascript": d["js"].strip() + "\n"},
            "explanation": d["explanation"].strip(),
            "timeLimitMs": tl,
        }
        with open(os.path.join(OUT, f"{pid:03d}-{d['slug']}.json"), "w", encoding="utf-8") as f:
            json.dump(problem, f, indent=1, ensure_ascii=False)
        print(f"ok   #{pid:03d} [{d['difficulty']:6}] {d['title']}  ({len(samples)} samples, {len(hidden_inputs)} hidden)")

    counts = {}
    for d in defs:
        counts[d["difficulty"]] = counts.get(d["difficulty"], 0) + 1
    print(f"\n{len(defs)} problems: {counts}")
    if failures:
        sys.exit(f"{failures} problem(s) failed")


def verify():
    """Re-run both stored solutions against every stored test (what the judge will do)."""
    failures = 0
    files = sorted(glob.glob(os.path.join(OUT, "*.json")))
    for f in files:
        p = json.load(open(f, encoding="utf-8"))
        tests = p["sampleTests"] + p["hiddenTests"]
        try:
            outs = check_solutions(p["id"], p["slug"], p["solution"]["python"], p["solution"]["javascript"],
                                   [t["input"] for t in tests], timeout=p.get("timeLimitMs", 2000) / 1000 * 2)
            bad = [i for i, (t, o) in enumerate(zip(tests, outs)) if norm(t["output"]) != norm(o)]
            if bad:
                raise RuntimeError(f"#{p['id']} {p['slug']}: stored output mismatch on tests {bad}")
            print(f"ok   #{p['id']:03d} {p['title']}")
        except Exception as e:  # noqa: BLE001
            failures += 1
            print(f"FAIL {e}", file=sys.stderr)
    print(f"\nverified {len(files) - failures}/{len(files)} problems")
    if failures:
        sys.exit(1)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify-only", action="store_true")
    ap.add_argument("--only", type=int)
    a = ap.parse_args()
    verify() if a.verify_only else build(a.only)
