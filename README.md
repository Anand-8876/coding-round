# CodeArena

A CodeChef-style DSA practice site with **100 problems** (40 easy, 35 medium, 25 hard). Solve them in order in **Python or JavaScript**.

- You write code in the browser (Monaco editor) and submit it. The server runs it against sample and hidden tests.
- When you get **Accepted**, the next problem unlocks.
- When a submission fails, you can **reveal the reference solution** in your chosen language, along with an explanation of the approach. Viewing the solution also unlocks the next problem, but the problem is marked "solution viewed" and is worth half points if you solve it afterwards.
- User accounts (login/sign-up), progress, drafts, submission history and a leaderboard are stored in SQLite.

## Requirements

- **Node.js 22.13+** (uses the built-in `node:sqlite` module, so there are no native dependencies)
- **Python 3.8+** on your `PATH`, used to run Python submissions and to build the problem set

## Run it

```bash
npm install
npm start            # http://localhost:3000
```

Open the site, create an account, and start with problem 1.

`npm run dev` restarts the server on file changes.

### Configuration (environment variables)

| Variable     | Default                          | Purpose                                                |
|--------------|----------------------------------|--------------------------------------------------------|
| `PORT`       | `3000`                           | HTTP port                                              |
| `DATA_DIR`   | `./data`                         | Where the SQLite database and JWT secret are kept      |
| `JWT_SECRET` | auto-generated in `DATA_DIR`     | Secret used to sign login tokens                       |
| `PYTHON_CMD` | `python` (Windows) / `python3`   | Python interpreter used to run submissions             |

## Project layout

```
server/
  index.js        Express app: auth, problems, run/submit, progress, leaderboard
  judge.js        Runs code in a subprocess with a time limit and compares output
  db.js           SQLite schema (users, progress, drafts, submissions)
  auth.js         JWT sign/verify, bcrypt password hashes
  problems.js     Loads problems/data/*.json
  judge.test.js   Judge tests (npm test)
public/           Frontend: plain HTML/CSS/JS, no build step
problems/
  defs/*.py       Problem definitions: statement, reference solutions, test generators
  build.py        Builds problems/data/*.json and cross-checks both solutions
  data/*.json     The built problems (committed, so no build is needed to run)
```

## The problem set

Each problem in `problems/defs/` defines:

- its statement
- hand-written edge-case inputs
- a random test generator (seeded, so builds are reproducible)
- a reference solution in **both** Python and JavaScript

`npm run build-problems` runs both solutions on every input and requires their outputs to match. It then writes `problems/data/NNN-slug.json` with the expected outputs. If the two languages ever disagree, the build fails, which catches bugs in either solution or in the tests.

```bash
npm run build-problems         # rebuild all problem JSON
python problems/build.py --only 42   # rebuild one problem
npm run verify-problems        # re-run both solutions against the stored tests
```

To add a problem, append a `dict(...)` to one of the `defs/*.py` files. Problems are numbered in file order, then list order. Rebuild, then restart the server.

Topics covered:
- arrays, strings, hashing
- two pointers, sliding window, prefix sums
- stacks and monotonic stacks, queues and deques, linked lists
- binary search (including binary search on the answer)
- sorting, intervals, heaps
- trees and BSTs, tries, union-find, Fenwick trees
- graphs: BFS/DFS, topological sort, Dijkstra, MST, bridges, SCCs
- greedy, backtracking, and many kinds of dynamic programming (1-D, 2-D, knapsack, LIS/LCS, interval DP)

## Judging rules

- Programs read **stdin** and write **stdout**.
- Trailing whitespace on each line and trailing blank lines are ignored.
- The time limit is 2 s per test (3 s for a few heavy DP problems).
- Verdicts:
  - `Accepted`
  - `Wrong Answer`
  - `Time Limit Exceeded`
  - `Runtime Error`
  - `Compilation Error`
  - `Output Limit Exceeded`
- **Run** executes only the sample tests, or your own custom input.
- **Submit** runs every test and stops at the first failure.
- For a failed hidden test, the user sees its input and their own output, but never the expected output.
- Reference solutions are served only after at least one failed submission (or after solving the problem). The server enforces this.

## ⚠️ Security note

`judge.js` runs submitted code as a normal subprocess, with a time limit, an output limit and (for Node) a heap limit. **This is not a sandbox.** Submitted code can read files and use the network with the server's permissions.

That is fine when you run it locally for yourself or for trusted users. Before exposing the site publicly, replace the body of `runCode()` with a proper isolated runner, such as Docker with `--network none` and memory/CPU/pids limits, or a service like Judge0. Nothing else in the app needs to change.
