// Code execution + judging.
//
// Everything goes through runCode(language, code, input), so this local
// subprocess runner can later be swapped for Docker / Judge0 without touching
// the rest of the app.
//
// NOTE: a subprocess is NOT a real sandbox. It enforces a time limit, an
// output limit and (for Node) a heap limit, but user code can still touch the
// filesystem and network. Fine for running on your own machine; put this
// behind Docker/Judge0 before exposing it to the internet.

const { spawn } = require('child_process');
const fs = require('fs');
const os = require('os');
const path = require('path');

const PYTHON_CMD = process.env.PYTHON_CMD || (process.platform === 'win32' ? 'python' : 'python3');
const MAX_OUTPUT_BYTES = 1024 * 1024; // 1 MB
const DEFAULT_TIME_LIMIT_MS = 2000;
const CONCURRENCY = Math.max(1, Math.min(4, os.cpus().length));

const LANGUAGES = {
  python: {
    file: 'main.py',
    cmd: (file) => [PYTHON_CMD, ['-I', '-X', 'utf8', file]],
  },
  javascript: {
    file: 'main.js',
    cmd: (file) => [process.execPath, ['--max-old-space-size=256', '--stack-size=65500', file]],
  },
};

function runCode(language, code, input, { timeLimitMs = DEFAULT_TIME_LIMIT_MS } = {}) {
  const lang = LANGUAGES[language];
  if (!lang) return Promise.reject(new Error(`Unsupported language: ${language}`));

  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'codearena-'));
  const file = path.join(dir, lang.file);
  fs.writeFileSync(file, code);
  const [bin, args] = lang.cmd(file);

  return new Promise((resolve) => {
    const start = process.hrtime.bigint();
    const child = spawn(bin, args, {
      cwd: dir,
      env: { PATH: process.env.PATH, SYSTEMROOT: process.env.SYSTEMROOT, PYTHONIOENCODING: 'utf-8' },
      windowsHide: true,
    });

    let stdout = '';
    let stderr = '';
    let outBytes = 0;
    let timedOut = false;
    let outputExceeded = false;

    const timer = setTimeout(() => {
      timedOut = true;
      child.kill('SIGKILL');
    }, timeLimitMs);

    child.stdout.on('data', (chunk) => {
      outBytes += chunk.length;
      if (outBytes > MAX_OUTPUT_BYTES) {
        outputExceeded = true;
        child.kill('SIGKILL');
        return;
      }
      stdout += chunk;
    });
    child.stderr.on('data', (chunk) => {
      if (stderr.length < 64 * 1024) stderr += chunk;
    });
    child.stdin.on('error', () => {}); // program may exit before reading all input
    child.stdin.end(input);

    const finish = (exitCode, spawnError) => {
      clearTimeout(timer);
      const timeMs = Number(process.hrtime.bigint() - start) / 1e6;
      fs.rm(dir, { recursive: true, force: true }, () => {});
      resolve({
        stdout: stdout.replace(/\r\n/g, '\n'),
        stderr: spawnError ? String(spawnError.message) : stderr,
        exitCode,
        timedOut,
        outputExceeded,
        timeMs: Math.round(timeMs),
      });
    };
    child.on('error', (err) => finish(-1, err));
    child.on('close', (code) => finish(code));
  });
}

function normalize(output) {
  return output
    .replace(/\r\n/g, '\n')
    .split('\n')
    .map((line) => line.trimEnd())
    .join('\n')
    .trimEnd();
}

function isCompileError(language, stderr) {
  if (language === 'python') return /^(SyntaxError|IndentationError|TabError)\b/m.test(stderr);
  // Parse-time errors are thrown from Node's module compiler, runtime ones (e.g. JSON.parse) are not.
  return /^SyntaxError\b/m.test(stderr) && /wrapSafe|compileFunction|compileSourceTextModule/.test(stderr);
}

function cleanStderr(stderr) {
  return stderr
    .replace(/(?:[A-Za-z]:)?[^\s"'()]*codearena-[^\\/\s"'()]+[\\/]/g, '') // hide the temp directory path
    .split('\n')
    .filter((line) => !/^\s+at .*(node:internal|node:diagnostics_channel)/.test(line) && !/^Node\.js v\d/.test(line))
    .join('\n')
    .trim()
    .slice(0, 4000);
}

async function judgeOne(language, code, test, timeLimitMs) {
  const r = await runCode(language, code, test.input, { timeLimitMs });
  let verdict;
  if (r.timedOut) verdict = 'Time Limit Exceeded';
  else if (r.outputExceeded) verdict = 'Output Limit Exceeded';
  else if (r.exitCode !== 0) verdict = isCompileError(language, r.stderr) ? 'Compilation Error' : 'Runtime Error';
  else verdict = normalize(r.stdout) === normalize(test.output) ? 'Accepted' : 'Wrong Answer';
  return {
    verdict,
    passed: verdict === 'Accepted',
    input: test.input,
    expected: test.output,
    actual: r.stdout.slice(0, 10000),
    stderr: cleanStderr(r.stderr),
    timeMs: r.timeMs,
  };
}

/**
 * Run `code` against `tests`.
 * stopOnFail: stop scheduling new tests once one fails (used for Submit).
 * Returns { verdict, passedCount, totalCount, results, maxTimeMs }.
 */
async function judge(language, code, tests, { stopOnFail = false, timeLimitMs = DEFAULT_TIME_LIMIT_MS } = {}) {
  const results = new Array(tests.length);
  let next = 0;
  let failed = false;

  async function worker() {
    while (next < tests.length && !(stopOnFail && failed)) {
      const i = next++;
      results[i] = await judgeOne(language, code, tests[i], timeLimitMs);
      if (!results[i].passed) failed = true;
      // A compile error will fail every test identically — no point running more.
      if (results[i].verdict === 'Compilation Error') failed = true;
    }
  }
  await Promise.all(Array.from({ length: CONCURRENCY }, worker));

  const done = results.filter(Boolean);
  const firstFail = results.find((r) => r && !r.passed);
  const passedCount = done.filter((r) => r.passed).length;
  return {
    verdict: firstFail ? firstFail.verdict : 'Accepted',
    passedCount: firstFail && stopOnFail ? results.findIndex((r) => r && !r.passed) : passedCount,
    totalCount: tests.length,
    results,
    firstFailIndex: firstFail ? results.indexOf(firstFail) : -1,
    maxTimeMs: Math.max(0, ...done.map((r) => r.timeMs)),
  };
}

module.exports = { runCode, judge, normalize, cleanStderr, LANGUAGES };
