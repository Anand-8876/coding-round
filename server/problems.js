const fs = require('fs');
const path = require('path');

const DATA_DIR = path.join(__dirname, '..', 'problems', 'data');

function loadProblems() {
  if (!fs.existsSync(DATA_DIR)) return [];
  return fs
    .readdirSync(DATA_DIR)
    .filter((f) => f.endsWith('.json'))
    .map((f) => JSON.parse(fs.readFileSync(path.join(DATA_DIR, f), 'utf8')))
    .sort((a, b) => a.id - b.id);
}

const problems = loadProblems();
const byId = new Map(problems.map((p, index) => [p.id, { ...p, index }]));

module.exports = { problems, byId };
