const path = require('path');
const express = require('express');
const bcrypt = require('bcryptjs');

const db = require('./db');
const { signToken, requireAuth } = require('./auth');
const { judge, runCode, cleanStderr, LANGUAGES } = require('./judge');
const { problems, byId } = require('./problems');

const PORT = Number(process.env.PORT) || 3000;
const app = express();
app.use(express.json({ limit: '200kb' }));
app.use(express.static(path.join(__dirname, '..', 'public')));

// ---------- helpers ----------

const stmt = {
  userById: db.prepare('SELECT id, username, email, preferred_lang, created_at FROM users WHERE id = ?'),
  userByLogin: db.prepare('SELECT * FROM users WHERE username = ? OR email = ?'),
  insertUser: db.prepare('INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)'),
  setLang: db.prepare('UPDATE users SET preferred_lang = ? WHERE id = ?'),
  progressAll: db.prepare('SELECT * FROM progress WHERE user_id = ?'),
  progressOne: db.prepare('SELECT * FROM progress WHERE user_id = ? AND problem_id = ?'),
  ensureProgress: db.prepare('INSERT OR IGNORE INTO progress (user_id, problem_id) VALUES (?, ?)'),
  recordAttempt: db.prepare(`
    UPDATE progress SET
      attempts = attempts + 1,
      failed_attempts = failed_attempts + (CASE WHEN ? THEN 0 ELSE 1 END),
      solved = MAX(solved, ?),
      solved_at = CASE WHEN ? AND solved = 0 THEN datetime('now') ELSE solved_at END
    WHERE user_id = ? AND problem_id = ?`),
  // Reading the solution after solving it yourself doesn't count against you.
  markViewed: db.prepare('UPDATE progress SET viewed_solution = 1 WHERE user_id = ? AND problem_id = ? AND solved = 0'),
  insertSubmission: db.prepare(`
    INSERT INTO submissions (user_id, problem_id, language, code, verdict, passed_count, total_count, runtime_ms)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)`),
  submissions: db.prepare(`
    SELECT id, problem_id, language, verdict, passed_count, total_count, runtime_ms, created_at
    FROM submissions WHERE user_id = ? ORDER BY id DESC LIMIT 50`),
  submissionsForProblem: db.prepare(`
    SELECT id, problem_id, language, code, verdict, passed_count, total_count, runtime_ms, created_at
    FROM submissions WHERE user_id = ? AND problem_id = ? ORDER BY id DESC LIMIT 20`),
  drafts: db.prepare('SELECT language, code FROM drafts WHERE user_id = ? AND problem_id = ?'),
  saveDraft: db.prepare(`
    INSERT INTO drafts (user_id, problem_id, language, code) VALUES (?, ?, ?, ?)
    ON CONFLICT (user_id, problem_id, language) DO UPDATE SET code = excluded.code, updated_at = datetime('now')`),
  leaderboard: db.prepare(`
    SELECT u.username,
           SUM(p.solved) AS solved,
           SUM(CASE WHEN p.solved = 1 AND p.viewed_solution = 0 THEN 1 ELSE 0 END) AS solved_clean,
           MAX(p.solved_at) AS last_solved_at
    FROM users u JOIN progress p ON p.user_id = u.id
    GROUP BY u.id HAVING solved > 0
    ORDER BY solved DESC, solved_clean DESC, last_solved_at ASC
    LIMIT 50`),
};

const POINTS = { easy: 10, medium: 20, hard: 40 };

/** Map of problemId -> { status, solved, viewedSolution, attempts, canViewSolution } for a user. */
function userStatuses(userId) {
  const rows = new Map(stmt.progressAll.all(userId).map((r) => [r.problem_id, r]));
  const out = new Map();
  let prevDone = true; // problem #1 is always unlocked
  for (const p of problems) {
    const r = rows.get(p.id);
    const solved = !!r?.solved;
    const viewed = !!r?.viewed_solution;
    let status;
    if (solved) status = 'solved';
    else if (viewed) status = 'viewed_solution';
    else if (!prevDone) status = 'locked';
    else if (r?.attempts) status = 'attempted';
    else status = 'unlocked';
    out.set(p.id, {
      status,
      solved,
      viewedSolution: viewed,
      attempts: r?.attempts || 0,
      canViewSolution: solved || viewed || (r?.failed_attempts || 0) > 0,
    });
    // Next problem unlocks once this one is solved OR its solution was viewed.
    prevDone = solved || viewed;
  }
  return out;
}

function nextProblemId(problemId) {
  const p = byId.get(problemId);
  return p && problems[p.index + 1] ? problems[p.index + 1].id : null;
}

function summary(userId) {
  const statuses = userStatuses(userId);
  const stats = { total: problems.length, solved: 0, viewed: 0, points: 0, byDifficulty: {} };
  for (const p of problems) {
    const d = (stats.byDifficulty[p.difficulty] ||= { total: 0, solved: 0 });
    d.total++;
    const s = statuses.get(p.id);
    if (s.solved) {
      stats.solved++;
      d.solved++;
      stats.points += s.viewedSolution ? POINTS[p.difficulty] / 2 : POINTS[p.difficulty];
    } else if (s.viewedSolution) stats.viewed++;
  }
  const current = problems.find((p) => ['unlocked', 'attempted'].includes(statuses.get(p.id).status));
  stats.currentProblemId = current ? current.id : null;
  return stats;
}

function publicUser(u) {
  return { id: u.id, username: u.username, email: u.email, preferredLang: u.preferred_lang, createdAt: u.created_at };
}

// A user can have only one judge job at a time; stops accidental request floods.
const busy = new Set();
function oneJobAtATime(req, res, next) {
  if (busy.has(req.userId)) return res.status(429).json({ error: 'Your previous run is still in progress' });
  busy.add(req.userId);
  res.on('close', () => busy.delete(req.userId));
  next();
}

const wrap = (fn) => (req, res, next) => Promise.resolve(fn(req, res, next)).catch(next);

function loadUser(req, res, next) {
  const user = stmt.userById.get(req.userId);
  if (!user) return res.status(401).json({ error: 'Account not found, please log in again' });
  req.user = user;
  next();
}
const authed = [requireAuth, loadUser];

function loadProblem(req, res, next) {
  const id = Number(req.params.id ?? req.body?.problemId);
  const problem = byId.get(id);
  if (!problem) return res.status(404).json({ error: 'Problem not found' });
  const status = userStatuses(req.userId).get(id);
  if (status.status === 'locked') return res.status(403).json({ error: 'Solve the previous problem to unlock this one' });
  req.problem = problem;
  req.problemStatus = status;
  next();
}

function checkLanguage(req, res, next) {
  const { language, code } = req.body || {};
  if (!LANGUAGES[language]) return res.status(400).json({ error: 'language must be "python" or "javascript"' });
  if (typeof code !== 'string' || !code.trim()) return res.status(400).json({ error: 'Code is empty' });
  if (code.length > 100_000) return res.status(400).json({ error: 'Code is too long' });
  next();
}

// ---------- auth ----------

app.post('/api/auth/register', (req, res) => {
  const { username, email, password } = req.body || {};
  if (!/^[A-Za-z0-9_]{3,20}$/.test(username || ''))
    return res.status(400).json({ error: 'Username must be 3-20 letters, numbers or underscores' });
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email || '')) return res.status(400).json({ error: 'Enter a valid email' });
  if (typeof password !== 'string' || password.length < 6)
    return res.status(400).json({ error: 'Password must be at least 6 characters' });

  const existing = stmt.userByLogin.get(username, email);
  if (existing) {
    const field = existing.username.toLowerCase() === username.toLowerCase() ? 'Username' : 'Email';
    return res.status(409).json({ error: `${field} is already taken` });
  }
  const hash = bcrypt.hashSync(password, 10);
  const { lastInsertRowid } = stmt.insertUser.run(username, email, hash);
  const user = stmt.userById.get(lastInsertRowid);
  res.status(201).json({ token: signToken(user), user: publicUser(user) });
});

app.post('/api/auth/login', (req, res) => {
  const { login, password } = req.body || {};
  const user = login ? stmt.userByLogin.get(login, login) : null;
  if (!user || !bcrypt.compareSync(password || '', user.password_hash))
    return res.status(401).json({ error: 'Wrong username/email or password' });
  res.json({ token: signToken(user), user: publicUser(user) });
});

app.get('/api/me', authed, (req, res) => {
  res.json({ user: publicUser(req.user), stats: summary(req.userId) });
});

app.patch('/api/me', authed, (req, res) => {
  const { preferredLang } = req.body || {};
  if (!LANGUAGES[preferredLang]) return res.status(400).json({ error: 'Unknown language' });
  stmt.setLang.run(preferredLang, req.userId);
  res.json({ user: publicUser(stmt.userById.get(req.userId)) });
});

// ---------- problems ----------

app.get('/api/problems', authed, (req, res) => {
  const statuses = userStatuses(req.userId);
  res.json({
    problems: problems.map((p) => ({
      id: p.id,
      slug: p.slug,
      title: p.title,
      difficulty: p.difficulty,
      topics: p.topics,
      ...statuses.get(p.id),
    })),
    stats: summary(req.userId),
  });
});

app.get('/api/problems/:id', authed, loadProblem, (req, res) => {
  const p = req.problem;
  const drafts = Object.fromEntries(stmt.drafts.all(req.userId, p.id).map((d) => [d.language, d.code]));
  res.json({
    id: p.id,
    number: p.index + 1,
    total: problems.length,
    slug: p.slug,
    title: p.title,
    difficulty: p.difficulty,
    topics: p.topics,
    description: p.description,
    inputFormat: p.inputFormat,
    outputFormat: p.outputFormat,
    constraints: p.constraints,
    sampleTests: p.sampleTests,
    hiddenTestCount: p.hiddenTests.length,
    starterCode: p.starterCode,
    drafts,
    timeLimitMs: p.timeLimitMs || 2000,
    nextProblemId: nextProblemId(p.id),
    prevProblemId: p.index > 0 ? problems[p.index - 1].id : null,
    ...req.problemStatus,
  });
});

app.put('/api/problems/:id/draft', authed, loadProblem, checkLanguage, (req, res) => {
  stmt.saveDraft.run(req.userId, req.problem.id, req.body.language, req.body.code);
  res.json({ ok: true });
});

app.post('/api/problems/:id/solution', authed, loadProblem, (req, res) => {
  const p = req.problem;
  if (!req.problemStatus.canViewSolution)
    return res.status(403).json({ error: 'Submit at least one attempt before viewing the solution' });
  stmt.ensureProgress.run(req.userId, p.id);
  stmt.markViewed.run(req.userId, p.id);
  res.json({
    solution: p.solution,
    explanation: p.explanation,
    nextProblemId: nextProblemId(p.id),
  });
});

app.get('/api/problems/:id/submissions', authed, loadProblem, (req, res) => {
  res.json({ submissions: stmt.submissionsForProblem.all(req.userId, req.problem.id) });
});

// ---------- judging ----------

app.post('/api/run', authed, loadProblem, checkLanguage, oneJobAtATime, wrap(async (req, res) => {
  const { language, code, customInput } = req.body;
  const p = req.problem;
  stmt.saveDraft.run(req.userId, p.id, language, code);
  const timeLimitMs = p.timeLimitMs || 2000;

  if (typeof customInput === 'string') {
    const r = await runCode(language, code, customInput, { timeLimitMs });
    return res.json({
      custom: true,
      stdout: r.stdout.slice(0, 10000),
      stderr: cleanStderr(r.stderr),
      timedOut: r.timedOut,
      exitCode: r.exitCode,
      timeMs: r.timeMs,
    });
  }

  const result = await judge(language, code, p.sampleTests, { timeLimitMs });
  res.json(result);
}));

app.post('/api/submit', authed, loadProblem, checkLanguage, oneJobAtATime, wrap(async (req, res) => {
  const { language, code } = req.body;
  const p = req.problem;
  stmt.saveDraft.run(req.userId, p.id, language, code);

  const tests = [...p.sampleTests, ...p.hiddenTests];
  const result = await judge(language, code, tests, { stopOnFail: true, timeLimitMs: p.timeLimitMs || 2000 });
  const accepted = result.verdict === 'Accepted';

  stmt.ensureProgress.run(req.userId, p.id);
  stmt.recordAttempt.run(accepted ? 1 : 0, accepted ? 1 : 0, accepted ? 1 : 0, req.userId, p.id);
  stmt.insertSubmission.run(
    req.userId, p.id, language, code, result.verdict, result.passedCount, result.totalCount, result.maxTimeMs,
  );

  // Only reveal details of the first failing test. Sample tests are public; for hidden
  // tests show the input (so the user can debug) but never the expected output.
  let failedTest = null;
  if (!accepted) {
    const i = result.firstFailIndex;
    const r = result.results[i];
    const isSample = i < p.sampleTests.length;
    failedTest = {
      number: i + 1,
      isSample,
      input: r.input.length > 2000 ? r.input.slice(0, 2000) + '\n…(truncated)' : r.input,
      expected: isSample ? r.expected : null,
      actual: r.actual.slice(0, 2000),
      stderr: r.stderr,
    };
  }

  const status = userStatuses(req.userId).get(p.id);
  res.json({
    verdict: result.verdict,
    passedCount: result.passedCount,
    totalCount: result.totalCount,
    runtimeMs: result.maxTimeMs,
    failedTest,
    nextProblemId: accepted ? nextProblemId(p.id) : null,
    canViewSolution: status.canViewSolution,
    stats: summary(req.userId),
  });
}));

app.get('/api/submissions', authed, (req, res) => {
  const rows = stmt.submissions.all(req.userId).map((s) => ({ ...s, title: byId.get(s.problem_id)?.title }));
  res.json({ submissions: rows });
});

app.get('/api/leaderboard', authed, (req, res) => {
  res.json({ leaderboard: stmt.leaderboard.all() });
});

app.use('/api', (req, res) => res.status(404).json({ error: 'Not found' }));
app.get('*', (req, res) => res.sendFile(path.join(__dirname, '..', 'public', 'index.html')));

app.use((err, req, res, next) => {
  console.error(err);
  res.status(500).json({ error: 'Internal server error' });
});

app.listen(PORT, () => {
  console.log(`CodeArena running at http://localhost:${PORT}  (${problems.length} problems loaded)`);
});
