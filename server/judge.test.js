const test = require('node:test');
const assert = require('node:assert');
const { judge, normalize } = require('./judge');

const tests = [
  { input: '2 3\n', output: '5\n' },
  { input: '10 -4\n', output: '6\n' },
];

const programs = {
  python: {
    correct: 'a, b = map(int, input().split())\nprint(a + b)\n',
    wrong: 'a, b = map(int, input().split())\nprint(a - b)\n',
    tle: 'while True:\n    pass\n',
    crash: 'raise ValueError("boom")\n',
    syntax: 'def f(:\n    pass\n',
  },
  javascript: {
    correct: "const [a, b] = require('fs').readFileSync(0, 'utf8').trim().split(/\\s+/).map(Number);\nconsole.log(a + b);\n",
    wrong: "const [a, b] = require('fs').readFileSync(0, 'utf8').trim().split(/\\s+/).map(Number);\nconsole.log(a * b);\n",
    tle: 'for (;;) {}\n',
    crash: "throw new Error('boom');\n",
    syntax: 'function f( {\n',
  },
};

const expected = {
  correct: 'Accepted',
  wrong: 'Wrong Answer',
  tle: 'Time Limit Exceeded',
  crash: 'Runtime Error',
  syntax: 'Compilation Error',
};

for (const [language, progs] of Object.entries(programs)) {
  for (const [kind, code] of Object.entries(progs)) {
    test(`${language}: ${kind} -> ${expected[kind]}`, async () => {
      const r = await judge(language, code, tests, { stopOnFail: true, timeLimitMs: 1000 });
      assert.strictEqual(r.verdict, expected[kind], JSON.stringify(r.results[0]));
      if (kind === 'correct') assert.strictEqual(r.passedCount, 2);
    });
  }
}

test('normalize ignores trailing whitespace and CRLF', () => {
  assert.strictEqual(normalize('1 2  \r\n3\r\n\r\n'), normalize('1 2\n3'));
  assert.notStrictEqual(normalize('1 2'), normalize('1  2'));
});
