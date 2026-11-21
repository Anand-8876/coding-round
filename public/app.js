/* CodeArena frontend — hash-routed SPA, no build step. Visual design: "matrix terminal" Figma Make mockup. */
'use strict';

const MONACO_BASE = 'https://cdn.jsdelivr.net/npm/monaco-editor@0.52.2/min';
const LANGS = { python: 'Python 3', javascript: 'JavaScript (Node.js)' };
const DIFF_COLOR = { easy: '#00ff41', medium: '#fbbf24', hard: '#ff4444' };
const POINTS = { easy: 10, medium: 20, hard: 40 };

const $ = (sel, el = document) => el.querySelector(sel);
const $$ = (sel, el = document) => [...el.querySelectorAll(sel)];
const app = $('#app');

const state = {
  token: localStorage.getItem('ca_token'),
  user: null,
  stats: null,
  editor: null,
  cleanup: [], // run when leaving a view
};

// ---------------- utilities ----------------

function esc(s) {
  return String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}

function md(text) {
  if (window.marked) return window.marked.parse(text || '');
  return `<p>${esc(text).replace(/\n/g, '<br>')}</p>`;
}

function toast(msg, ms = 3000) {
  const el = $('#toast');
  el.textContent = msg;
  el.hidden = false;
  clearTimeout(toast.timer);
  toast.timer = setTimeout(() => (el.hidden = true), ms);
}

function timeAgo(sqlTime) {
  const d = new Date(sqlTime.replace(' ', 'T') + 'Z');
  const s = Math.floor((Date.now() - d) / 1000);
  if (s < 60) return 'just now';
  if (s < 3600) return `${Math.floor(s / 60)} min ago`;
  if (s < 86400) return `${Math.floor(s / 3600)} h ago`;
  if (s < 172800) return 'Yesterday';
  if (s < 604800) return `${Math.floor(s / 86400)} days ago`;
  return d.toLocaleDateString();
}

function debounce(fn, ms) {
  let t;
  const wrapped = (...args) => { clearTimeout(t); t = setTimeout(() => fn(...args), ms); };
  wrapped.flush = (...args) => { clearTimeout(t); fn(...args); };
  return wrapped;
}

function bar(value, max, color = '#00ff41') {
  const pct = max ? Math.round((value / max) * 100) : 0;
  return `<div class="bar"><span style="width:${pct}%;background:${color};box-shadow:0 0 6px ${color}66"></span></div>`;
}

const pill = (d) => `<span class="pill ${d}">${d}</span>`;
const tag = (t) => `<span class="tag">${esc(t)}</span>`;

async function api(path, { method = 'GET', body } = {}) {
  const res = await fetch(path, {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...(state.token ? { Authorization: `Bearer ${state.token}` } : {}),
    },
    body: body ? JSON.stringify(body) : undefined,
  });
  let data = {};
  try { data = await res.json(); } catch { /* empty body */ }
  if (res.status === 401 && state.token) {
    logout();
    throw new Error(data.error || 'Please log in again');
  }
  if (!res.ok) throw new Error(data.error || `Request failed (${res.status})`);
  return data;
}

// ---------------- decorative pieces ----------------

function logo(size = '') {
  return `<span class="logo ${size}"><span class="logo-box">&lt;/&gt;</span><span class="logo-text">CodeArena</span></span>`;
}

function robotSvg(size = 120) {
  return `
  <svg width="${size}" height="${size}" viewBox="0 0 120 120" fill="none" class="robot" aria-hidden="true">
    <circle cx="60" cy="60" r="55" fill="rgba(0,255,65,0.04)"/>
    <line x1="60" y1="8" x2="60" y2="20" stroke="#00ff41" stroke-width="2"/>
    <circle cx="60" cy="7" r="3" fill="#00ff41" class="pulse"/>
    <rect x="30" y="20" width="60" height="48" rx="8" fill="#0a0f0a" stroke="#00ff41" stroke-width="1.5"/>
    <rect x="40" y="30" width="14" height="10" rx="3" fill="#00ff41" class="pulse"/>
    <rect x="66" y="30" width="14" height="10" rx="3" fill="#00ff41" class="pulse"/>
    <rect x="38" y="48" width="44" height="12" rx="3" fill="#050a05" stroke="#1a3a1a"/>
    <text x="60" y="58" text-anchor="middle" font-family="JetBrains Mono, monospace" font-size="7" fill="#00ff41">&lt;/&gt;</text>
    <rect x="35" y="70" width="50" height="36" rx="6" fill="#0a0f0a" stroke="#00ff41" stroke-width="1.5"/>
    <rect x="42" y="76" width="16" height="10" rx="2" fill="#050a05" stroke="#1a3a1a"/>
    <rect x="62" y="76" width="16" height="10" rx="2" fill="#050a05" stroke="#1a3a1a"/>
    <rect x="42" y="90" width="36" height="4" rx="2" fill="#00ff41" opacity="0.3"/>
    <rect x="16" y="72" width="17" height="8" rx="4" fill="#0a0f0a" stroke="#00ff41" stroke-width="1.5"/>
    <rect x="87" y="72" width="17" height="8" rx="4" fill="#0a0f0a" stroke="#00ff41" stroke-width="1.5"/>
    <rect x="40" y="108" width="14" height="8" rx="4" fill="#0a0f0a" stroke="#00ff41" stroke-width="1.5"/>
    <rect x="66" y="108" width="14" height="8" rx="4" fill="#0a0f0a" stroke="#00ff41" stroke-width="1.5"/>
    <line x1="55" y1="85" x2="55" y2="95" stroke="#00ff41" stroke-width="0.5" opacity="0.5"/>
    <line x1="65" y1="85" x2="65" y2="95" stroke="#00ff41" stroke-width="0.5" opacity="0.5"/>
  </svg>`;
}

/** Falling "matrix" characters on a fixed canvas. Returns a stop function. */
function startMatrixRain() {
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) return () => {};
  const canvas = document.createElement('canvas');
  canvas.id = 'matrix-canvas';
  document.body.appendChild(canvas);
  const ctx = canvas.getContext('2d');
  const fontSize = 13;
  const chars = '01アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモ{}[]()<>=+-*/&|^~%$#@!';
  let drops = [];
  const resize = () => {
    canvas.width = innerWidth;
    canvas.height = innerHeight;
    drops = Array(Math.floor(canvas.width / fontSize)).fill(1);
  };
  resize();
  addEventListener('resize', resize);
  const timer = setInterval(() => {
    ctx.fillStyle = 'rgba(0,0,0,0.04)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.font = `${fontSize}px JetBrains Mono, monospace`;
    for (let i = 0; i < drops.length; i++) {
      ctx.fillStyle = i % 7 === 0 ? '#ffffff' : '#00ff41';
      ctx.globalAlpha = Math.random() * 0.5 + 0.3;
      ctx.fillText(chars[Math.floor(Math.random() * chars.length)], i * fontSize, drops[i] * fontSize);
      ctx.globalAlpha = 1;
      if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) drops[i] = 0;
      drops[i]++;
    }
  }, 50);
  return () => { clearInterval(timer); removeEventListener('resize', resize); canvas.remove(); };
}

// A tiny code hint shown on each problem card, picked from its topics.
const TOPIC_SNIPPETS = {
  'kadane': 'cur = max(x, cur+x)', 'sliding window': 'while s >= t: lo += 1', 'two pointers': 'i, j = 0, n-1',
  'prefix sums': 'pre[r] - pre[l-1]', 'binary search on answer': 'lo, hi = 1, max(a)', 'binary search': 'mid = (lo+hi)//2',
  'monotonic stack': 'while st and st[-1] < x', 'monotonic queue': 'dq.popleft()', 'stack': 'stack.pop()', 'deque': 'deque()',
  'heap': 'heappop(pq)', 'hashing': 'seen[x] = i', 'trie': 'node = node[bit]', 'union find': 'parent[ra] = rb',
  'fenwick tree': 'i += i & -i', 'topological sort': 'indeg[v] -= 1', 'shortest path': 'dist[v] = d + w', 'bfs': 'q.popleft()',
  'dfs': 'dfs(nx, ny)', 'tarjan': 'low[v] > tin[p]', 'kosaraju': 'order.append(v)', 'graphs': 'adj[u].append(v)',
  'interval dp': 'dp[l][r] = max(...)', 'dynamic programming': 'dp[i] = dp[i-1] + ...', 'backtracking': 'go(i + 1); cur.pop()',
  'bit manipulation': 'x & (x - 1)', 'sieve': 'is_p[i*i::i] = 0', 'bst': 'lo < node.val < hi', 'trees': 'node.left',
  'linked list': 'slow, fast = fast.next', 'intervals': 'merged[-1][1]', 'sorting': 'a.sort()', 'matrix': 'grid[i][j]',
  'recursion': 'return f(n-1)', 'strings': 's[::-1]', 'math': 'a % b', 'design': 'class Solution', 'greedy': 'best = max(best, …)',
  'arrays': 'a[i]', 'simulation': 'for i in range(n)', 'divide and conquer': 'mid = len(a)//2', 'segment tree': 'tree[2*i]',
  'cycle detection': 'done == n', 'memoization': '@lru_cache', 'quickselect': 'pivot = a[hi]',
};
function snippetFor(p) {
  for (const t of p.topics) if (TOPIC_SNIPPETS[t]) return TOPIC_SNIPPETS[t];
  return '...';
}

// ---------------- modal ----------------

function modal({ icon, title, body, actions }) {
  const wrap = $('#modal');
  $('#modal-body').innerHTML = `
    <div class="icon">${icon}</div>
    <h2>${title}</h2>
    <p>${body}</p>
    <div class="actions">${actions.map((a) => `<button class="btn ${a.style}" data-value="${a.value}">${a.label}</button>`).join('')}</div>`;
  wrap.hidden = false;
  return new Promise((resolve) => {
    const close = (value) => { wrap.hidden = true; wrap.onclick = null; document.removeEventListener('keydown', onKey); resolve(value); };
    const onKey = (e) => { if (e.key === 'Escape') close(null); };
    document.addEventListener('keydown', onKey);
    wrap.onclick = (e) => {
      if (e.target === wrap) return close(null);
      const btn = e.target.closest('[data-value]');
      if (btn) close(btn.dataset.value);
    };
    $('#modal-body .btn-primary, #modal-body .btn-danger')?.focus();
  });
}

// ---------------- session ----------------

function setSession(token, user) {
  state.token = token;
  state.user = user;
  localStorage.setItem('ca_token', token);
}

function logout() {
  state.token = null;
  state.user = null;
  state.stats = null;
  localStorage.removeItem('ca_token');
  location.hash = '#/login';
}

async function ensureUser() {
  if (state.user && state.stats) return;
  const data = await api('/api/me');
  state.user = data.user;
  state.stats = data.stats;
}

function updateTopbar(active) {
  $('#topbar').hidden = false;
  $('#username').textContent = state.user?.username || '';
  $('#points-badge').textContent = state.stats ? `⚡ ${state.stats.points} pts` : '';
  $$('#topbar nav a').forEach((a) => a.classList.toggle('active', a.dataset.nav === active));
}

// ---------------- cover ----------------

function renderCover() {
  $('#topbar').hidden = true;
  app.innerHTML = `
    <div class="fullscreen">
      <div class="grid-lines"></div>
      <div class="content cover">
        <div class="terminal fade-in">
          <div class="terminal-bar"><i style="background:#ff4444"></i><i style="background:#fbbf24"></i><i style="background:#00ff41"></i><span>codearena — bash</span></div>
          <div class="terminal-body"><p class="muted">$ welcome</p><p class="ok"><span id="typed"></span><span class="blink">▋</span></p></div>
        </div>
        ${robotSvg(160)}
        <div>
          ${logo('lg')}
          <p class="cover-tag">100 DSA problems · <span class="ok">solve</span> one to unlock the next</p>
        </div>
        <div class="cover-stats">
          <div><b>100</b><span>Problems</span></div>
          <div><b>2</b><span>Languages</span></div>
          <div><b>3</b><span>Difficulty tiers</span></div>
        </div>
        <a class="btn btn-primary large glow-pulse" href="#/login">Enter the Arena →</a>
      </div>
    </div>`;
  state.cleanup.push(startMatrixRain());
  const full = '> Initializing CodeArena...';
  let i = 0;
  const t = setInterval(() => {
    const el = $('#typed');
    if (!el || ++i > full.length) return clearInterval(t);
    el.textContent = full.slice(0, i);
  }, 60);
  state.cleanup.push(() => clearInterval(t));
}

// ---------------- auth ----------------

function renderAuth(mode = 'login') {
  $('#topbar').hidden = true;
  app.innerHTML = `
    <div class="fullscreen">
      <div class="deco-robot" style="right:64px;bottom:64px;opacity:.3">${robotSvg(200)}</div>
      <div class="deco-robot" style="left:48px;top:96px;opacity:.2">${robotSvg(120)}</div>
      <div class="content" style="width:100%;max-width:420px">
        <div class="card auth-card fade-in">
          <div class="auth-head">
            ${logo('lg')}
            <p>100 DSA problems from easy to hard.<br>Solve one to unlock the next.</p>
          </div>
          <div class="segmented">
            <button data-mode="login" class="${mode === 'login' ? 'active' : ''}">Log in</button>
            <button data-mode="register" class="${mode === 'register' ? 'active' : ''}">Sign up</button>
          </div>
          <form class="form" id="auth-form" novalidate>
            ${mode === 'register' ? `
              <div><label for="username">Username</label><input id="username" name="username" autocomplete="username" placeholder="your_handle"></div>
              <div><label for="email">Email</label><input id="email" name="email" type="email" autocomplete="email" placeholder="you@example.com"></div>
            ` : `
              <div><label for="login">Username or email</label><input id="login" name="login" autocomplete="username" placeholder="you@example.com"></div>
            `}
            <div><label for="password">Password</label>
              <input id="password" name="password" type="password" autocomplete="${mode === 'login' ? 'current-password' : 'new-password'}"
                placeholder="${mode === 'register' ? 'At least 6 characters' : '••••••••'}"></div>
            <div class="form-error" id="auth-error"></div>
            <button class="btn btn-primary block" style="padding:12px" type="submit">${mode === 'login' ? 'Log in →' : 'Create account →'}</button>
          </form>
        </div>
      </div>
    </div>`;
  state.cleanup.push(startMatrixRain());

  $$('.segmented button', app).forEach((b) => (b.onclick = () => (location.hash = `#/${b.dataset.mode}`)));
  $('input', app).focus();

  $('#auth-form').onsubmit = async (e) => {
    e.preventDefault();
    const form = Object.fromEntries(new FormData(e.target));
    if (Object.values(form).some((v) => !String(v).trim())) {
      $('#auth-error').textContent = '⚠ Please fill in all fields.';
      return;
    }
    const btn = $('button[type=submit]', e.target);
    const label = btn.textContent;
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span> Processing...';
    $('#auth-error').textContent = '';
    try {
      const data = await api(`/api/auth/${mode === 'login' ? 'login' : 'register'}`, { method: 'POST', body: form });
      setSession(data.token, data.user);
      location.hash = '#/problems';
    } catch (err) {
      $('#auth-error').textContent = `⚠ ${err.message}`;
      btn.disabled = false;
      btn.textContent = label;
    }
  };
}

// ---------------- problem list ----------------

function statusIcon(status) {
  switch (status) {
    case 'solved': return '<span class="ok" title="Solved" style="font-weight:700">✔</span>';
    case 'viewed_solution': return '<span title="Solution viewed">👁</span>';
    case 'attempted': return '<span class="status-dot" title="Attempted"></span>';
    case 'unlocked': return '<span style="color:var(--indigo)" title="Unlocked">○</span>';
    default: return '<span title="Locked">🔒</span>';
  }
}

function statusFooter(p) {
  switch (p.status) {
    case 'solved': return '<span class="ok">✔ solved</span>';
    case 'viewed_solution': return '<span class="warn">👁 viewed</span>';
    case 'attempted': return '<span class="warn">● attempted</span>';
    case 'unlocked': return '<span style="color:var(--indigo)">○ open</span>';
    default: return '<span style="color:var(--border-2)">🔒 locked</span>';
  }
}

async function renderProblems() {
  updateTopbar('problems');
  app.innerHTML = '<div class="center"><span class="spinner big"></span></div>';
  const { problems, stats } = await api('/api/problems');
  state.stats = stats;
  updateTopbar('problems');

  const d = stats.byDifficulty;
  const current = problems.find((p) => p.id === stats.currentProblemId);
  const filters = JSON.parse(sessionStorage.getItem('ca_filters') || '{}');
  const statCard = (label, value, total, color, sub = '') => `
    <div class="card stat fade-in" style="border-color:${color}22">
      <div class="label">${label}</div>
      <div class="value"><b style="color:${color};text-shadow:0 0 16px ${color}88">${value}</b><span>/ ${total}</span></div>
      ${bar(value, total, color)}
      ${sub ? `<div class="sub">${sub}</div>` : ''}
    </div>`;

  app.innerHTML = `
    <div class="page fade-in">
      <div class="stats">
        ${statCard('Overall Progress', stats.solved, stats.total, '#00ff41',
          `${stats.points} pts${stats.viewed ? ` · ${stats.viewed} solution${stats.viewed > 1 ? 's' : ''} viewed` : ''}`)}
        ${statCard('Easy', d.easy?.solved || 0, d.easy?.total || 0, DIFF_COLOR.easy)}
        ${statCard('Medium', d.medium?.solved || 0, d.medium?.total || 0, DIFF_COLOR.medium)}
        ${statCard('Hard', d.hard?.solved || 0, d.hard?.total || 0, DIFF_COLOR.hard)}
      </div>

      ${current ? `
        <div class="up-next">
          <div class="l"><span class="k">UP NEXT</span><span class="t">#${problems.indexOf(current) + 1} ${esc(current.title)}</span>${pill(current.difficulty)}</div>
          <a class="btn btn-primary" href="#/problem/${current.id}">${current.status === 'attempted' ? 'Continue' : 'Start'} →</a>
        </div>` : stats.solved + stats.viewed === stats.total ? `
        <div class="up-next"><div class="l"><span class="t">🏆 You've completed all ${stats.total} problems!</span></div></div>` : ''}

      <div class="filters">
        <div class="search"><span>⌕</span><input id="f-search" placeholder="Search problems or topics…" value="${esc(filters.q || '')}"></div>
        <select id="f-diff">
          <option value="">All</option><option value="easy">Easy</option><option value="medium">Medium</option><option value="hard">Hard</option>
        </select>
        <select id="f-status">
          <option value="">All</option><option value="solved">Solved</option><option value="todo">Not solved</option>
          <option value="viewed_solution">Solution viewed</option><option value="locked">Locked</option>
        </select>
        <span class="count" id="f-count"></span>
      </div>

      <div id="grid"></div>
    </div>`;

  $('#f-diff').value = filters.diff || '';
  $('#f-status').value = filters.status || '';

  const draw = () => {
    const q = $('#f-search').value.trim().toLowerCase();
    const diff = $('#f-diff').value;
    const st = $('#f-status').value;
    sessionStorage.setItem('ca_filters', JSON.stringify({ q, diff, status: st }));
    const rows = problems
      .map((p, i) => ({ ...p, num: i + 1 }))
      .filter((p) => !diff || p.difficulty === diff)
      .filter((p) => !st || (st === 'todo' ? p.status !== 'solved' : p.status === st))
      .filter((p) => !q || p.title.toLowerCase().includes(q) || p.topics.some((t) => t.includes(q)));
    $('#f-count').textContent = `${rows.length} problem${rows.length !== 1 ? 's' : ''}`;
    $('#grid').innerHTML = rows.length ? `<div class="problem-grid">${rows.map((p) => `
      <div class="pcard ${p.difficulty} ${p.status} ${p.status === 'locked' ? 'locked' : ''}" data-id="${p.id}" data-locked="${p.status === 'locked'}"
           tabindex="${p.status === 'locked' ? -1 : 0}" role="link" aria-label="${esc(p.title)}">
        <div class="snip">${esc(snippetFor(p))}</div>
        <div class="head"><span class="num">#${p.num} ${statusIcon(p.status)}</span>${pill(p.difficulty)}</div>
        <h3>${esc(p.title)}</h3>
        <div class="topics">${p.topics.slice(0, 3).map(tag).join('')}</div>
        <div class="foot"><span class="dim">${POINTS[p.difficulty]} pts${p.viewedSolution ? ' · ½ pts' : ''}</span>${statusFooter(p)}</div>
      </div>`).join('')}</div>`
      : '<div class="empty"><span class="sym">⟨/⟩</span><p>No problems match your filters.</p></div>';
  };
  draw();
  $('#f-search').oninput = draw;
  $('#f-diff').onchange = draw;
  $('#f-status').onchange = draw;
  const open = (card) => {
    if (!card) return;
    if (card.dataset.locked === 'true') return toast('🔒 Solve the previous problem to unlock this one');
    location.hash = `#/problem/${card.dataset.id}`;
  };
  $('#grid').onclick = (e) => open(e.target.closest('.pcard'));
  $('#grid').onkeydown = (e) => { if (e.key === 'Enter') open(e.target.closest('.pcard')); };
}

// ---------------- editor ----------------

let monacoPromise;
function loadMonaco() {
  if (monacoPromise) return monacoPromise;
  monacoPromise = new Promise((resolve) => {
    if (!window.require || !window.require.config) return resolve(null);
    window.MonacoEnvironment = {
      getWorkerUrl: () => `data:text/javascript;charset=utf-8,${encodeURIComponent(
        `self.MonacoEnvironment={baseUrl:'${MONACO_BASE}/'};importScripts('${MONACO_BASE}/vs/base/worker/workerMain.js');`)}`,
    };
    window.require.config({ paths: { vs: `${MONACO_BASE}/vs` } });
    const timer = setTimeout(() => resolve(null), 10000);
    window.require(['vs/editor/editor.main'], () => {
      clearTimeout(timer);
      window.monaco.editor.defineTheme('arena', {
        base: 'vs-dark',
        inherit: true,
        rules: [
          { token: 'keyword', foreground: 'ff79c6' },
          { token: 'string', foreground: 'f1fa8c' },
          { token: 'comment', foreground: '6272a4', fontStyle: 'italic' },
          { token: 'number', foreground: 'bd93f9' },
          { token: 'type', foreground: 'ffb86c' },
          { token: 'identifier', foreground: 'a0d0a0' },
          { token: 'delimiter', foreground: '8be9fd' },
        ],
        colors: {
          'editor.background': '#050a05',
          'editor.foreground': '#a0d0a0',
          'editorGutter.background': '#030803',
          'editorLineNumber.foreground': '#1f4a26',
          'editorLineNumber.activeForeground': '#00ff41',
          'editorCursor.foreground': '#00ff41',
          'editor.lineHighlightBackground': '#0a140a',
          'editor.lineHighlightBorder': '#00000000',
          'editor.selectionBackground': '#00ff4133',
          'editorIndentGuide.background1': '#0f180f',
          'editorWidget.background': '#0a0f0a',
          'editorWidget.border': '#1a3a1a',
          'scrollbarSlider.background': '#1a4a2066',
          'scrollbarSlider.hoverBackground': '#00ff4166',
        },
      });
      resolve(window.monaco);
    }, () => { clearTimeout(timer); resolve(null); });
  });
  return monacoPromise;
}

async function createEditor(container, { value, language, onChange, onRun, onSubmit }) {
  const monaco = await loadMonaco();
  if (!container.isConnected) return null;
  container.innerHTML = '';

  if (monaco) {
    const ed = monaco.editor.create(container, {
      value, language, theme: 'arena',
      automaticLayout: true, fontSize: 13, lineHeight: 22, minimap: { enabled: false },
      scrollBeyondLastLine: false, tabSize: 4, insertSpaces: true, padding: { top: 14 },
      fontFamily: '"JetBrains Mono", Consolas, monospace', cursorBlinking: 'smooth', renderLineHighlight: 'all',
    });
    ed.onDidChangeModelContent(() => onChange(ed.getValue()));
    ed.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, onRun);
    ed.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyMod.Shift | monaco.KeyCode.Enter, onSubmit);
    return {
      getValue: () => ed.getValue(),
      setValue: (v) => ed.setValue(v),
      setLanguage: (l) => monaco.editor.setModelLanguage(ed.getModel(), l),
      setTabSize: (n) => ed.getModel().updateOptions({ tabSize: n }),
      focus: () => ed.focus(),
      dispose: () => ed.dispose(),
    };
  }

  // Fallback when the Monaco CDN is unreachable: a plain textarea with Tab support.
  container.innerHTML = '<textarea class="fallback" spellcheck="false"></textarea>';
  const ta = $('textarea', container);
  ta.value = value;
  ta.oninput = () => onChange(ta.value);
  ta.onkeydown = (e) => {
    if (e.key === 'Tab') {
      e.preventDefault();
      ta.setRangeText('    ', ta.selectionStart, ta.selectionEnd, 'end');
      onChange(ta.value);
    } else if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault();
      e.shiftKey ? onSubmit() : onRun();
    }
  };
  return {
    getValue: () => ta.value,
    setValue: (v) => { ta.value = v; },
    setLanguage: () => {},
    setTabSize: () => {},
    focus: () => ta.focus(),
    dispose: () => {},
  };
}

// ---------------- problem workspace ----------------

function io(label, content, kind = '') {
  const cls = { 'EXPECTED OUTPUT': 'expected', 'YOUR OUTPUT': 'yours', ERROR: 'error' }[label] || '';
  return `<div class="io"><span class="io-label ${cls}">${label}</span><pre class="${kind}">${content === '' ? '<span class="dim">(no output)</span>' : esc(content)}</pre></div>`;
}

async function renderProblem(id) {
  updateTopbar('problems');
  app.innerHTML = '<div class="center"><span class="spinner big"></span></div>';
  let p;
  try {
    p = await api(`/api/problems/${id}`);
  } catch (err) {
    app.innerHTML = `<div class="page"><div class="empty"><span class="sym">🔒</span><p>${esc(err.message)}</p>
      <a class="btn btn-primary" href="#/problems">Back to problems</a></div></div>`;
    return;
  }

  const lang0 = localStorage.getItem('ca_lang') || state.user?.preferredLang || 'python';
  const view = {
    lang: LANGS[lang0] ? lang0 : 'python',
    codes: {
      python: p.drafts.python ?? p.starterCode.python,
      javascript: p.drafts.javascript ?? p.starterCode.javascript,
    },
    busy: false,
    solution: null,
    leftTab: 'description',
    consoleTab: 'sample',
    lastRun: null,
    selectedCase: 0,
    customInput: null,
  };

  // Code loaded from the Submissions page ("Load code →").
  const pending = JSON.parse(sessionStorage.getItem('ca_load') || 'null');
  sessionStorage.removeItem('ca_load');

  app.innerHTML = `
    <div class="workspace">
      <section class="pane left">
        <div class="tabs" id="left-tabs">
          <button data-tab="description" class="active">Description</button>
          <button data-tab="submissions">Submissions</button>
          <button data-tab="solution" id="solution-tab" ${p.canViewSolution ? '' : 'hidden'}>Solution</button>
        </div>
        <div class="scroll" id="left-body"></div>
      </section>
      <section class="pane right">
        <div class="toolbar">
          <div class="grp">
            <select id="lang">${Object.entries(LANGS).map(([k, v]) => `<option value="${k}">${v}</option>`).join('')}</select>
            <button class="btn btn-ghost small" id="reset-btn" title="Restore the starter code">↺ Reset</button>
          </div>
          <div class="grp">
            <button class="btn btn-secondary small" id="run-btn" title="Run sample tests (Ctrl+Enter)">▶ Run</button>
            <button class="btn btn-primary small" id="submit-btn" title="Submit against all tests (Ctrl+Shift+Enter)">↑ Submit</button>
          </div>
        </div>
        <div class="editor" id="editor"><div class="center"><span class="spinner big"></span></div></div>
        <div class="console">
          <div class="tabs" id="console-tabs">
            <div>
              <button class="tab active" data-tab="sample">Sample tests</button>
              <button class="tab" data-tab="result">Result</button>
              <button class="tab" data-tab="custom">Custom input</button>
            </div>
            <div class="hints"><span><kbd>Ctrl+Enter</kbd> run</span><span><kbd>Ctrl+⇧+Enter</kbd> submit</span></div>
          </div>
          <div class="console-body" id="console-body"></div>
        </div>
      </section>
    </div>`;

  $('#lang').value = view.lang;

  // ----- left pane -----
  function renderDescription() {
    const banner = p.solved
      ? `<div class="banner ok"><span>✔ You solved this problem${p.viewedSolution ? ' (after viewing the solution)' : ''}.</span>${p.nextProblemId ? `<a href="#/problem/${p.nextProblemId}">Next problem →</a>` : ''}</div>`
      : p.viewedSolution
        ? `<div class="banner warn"><span>👁 You viewed the solution. You can still solve it.</span>${p.nextProblemId ? `<a href="#/problem/${p.nextProblemId}">Next problem →</a>` : ''}</div>`
        : '';
    const canNext = p.nextProblemId && (p.solved || p.viewedSolution);
    return `
      ${banner}
      <div class="ptitle">
        <h1>${p.number}. ${esc(p.title)}</h1>
        <div class="navs">
          ${p.prevProblemId ? `<a class="btn btn-ghost small" href="#/problem/${p.prevProblemId}" title="Previous problem">‹</a>` : '<button class="btn btn-ghost small" disabled>‹</button>'}
          ${canNext ? `<a class="btn btn-ghost small" href="#/problem/${p.nextProblemId}" title="Next problem">›</a>` : '<button class="btn btn-ghost small" disabled title="Solve this problem to unlock the next">›</button>'}
        </div>
      </div>
      <div class="meta">${pill(p.difficulty)}${p.topics.map(tag).join('')}<span class="tl">Time limit: ${(p.timeLimitMs / 1000).toFixed(1)} s</span></div>
      <div class="statement">${md(p.description)}</div>
      <div><h3 class="section-h">Input Format</h3><div class="statement">${md(p.inputFormat)}</div></div>
      <div><h3 class="section-h">Output Format</h3><div class="statement">${md(p.outputFormat)}</div></div>
      <div><h3 class="section-h">Constraints</h3><div class="statement">${md(p.constraints)}</div></div>
      ${p.sampleTests.map((t, i) => `
        <div><h3 class="section-h">Example ${i + 1}</h3>
          <div class="io-grid">${io('INPUT', t.input)}${io('EXPECTED OUTPUT', t.output)}</div></div>`).join('')}
      <p class="foot-note">Your code reads from standard input and prints to standard output.
        Submissions are checked against ${p.sampleTests.length + p.hiddenTestCount} tests (${p.hiddenTestCount} hidden).</p>`;
  }

  async function renderSubmissionsTab(body) {
    body.innerHTML = '<div class="center"><span class="spinner big"></span></div>';
    const { submissions } = await api(`/api/problems/${p.id}/submissions`);
    if (!submissions.length) {
      body.innerHTML = '<div class="empty"><span class="sym">⟨/⟩</span><p>No submissions yet.</p></div>';
      return;
    }
    body.innerHTML = `
      <h2 class="section-h" style="color:var(--text);font-size:13px;text-transform:none;letter-spacing:0">Your submissions</h2>
      <table class="mini">
        <thead><tr><th>When</th><th>Verdict</th><th>Lang</th><th>Tests</th><th></th></tr></thead>
        <tbody>${submissions.map((s, i) => `
          <tr><td>${timeAgo(s.created_at)}</td>
            <td class="${s.verdict === 'Accepted' ? 'ok glow' : 'bad'}" style="font-weight:600">${esc(s.verdict)}</td>
            <td>${s.language === 'python' ? 'PY' : 'JS'}</td>
            <td>${s.passed_count}/${s.total_count}</td>
            <td><button class="btn btn-ghost small" data-load="${i}">Load</button></td></tr>`).join('')}
        </tbody>
      </table>`;
    body.onclick = (e) => {
      const b = e.target.closest('[data-load]');
      if (!b) return;
      const s = submissions[Number(b.dataset.load)];
      loadCode(s.language, s.code);
      toast('Loaded code into the editor');
    };
  }

  function renderSolutionTab(body) {
    const sol = view.solution;
    let shown = view.lang;
    const draw = () => {
      body.innerHTML = `
        <div class="banner warn">⚠ This is a reference solution. Try to understand it, then write it yourself — you can still submit!</div>
        <div><h3 class="section-h" style="color:var(--text);font-size:13px;text-transform:none;letter-spacing:0">Approach</h3>
          <div class="statement">${md(sol.explanation)}</div></div>
        <div class="solution-code">
          <div class="tabs">
            ${Object.entries(LANGS).map(([k, v]) => `<button data-sol="${k}" class="${k === shown ? 'active' : ''}">${v}</button>`).join('')}
            <span style="flex:1"></span>
            <button data-copy="1" style="text-transform:none">Copy to editor</button>
          </div>
          <pre>${esc(sol.solution[shown])}</pre>
        </div>
        ${sol.nextProblemId ? `<a class="btn btn-primary block" style="padding:10px" href="#/problem/${sol.nextProblemId}">Continue to next problem →</a>` : ''}`;
    };
    draw();
    body.onclick = (e) => {
      const t = e.target.closest('[data-sol]');
      if (t) { shown = t.dataset.sol; draw(); return; }
      if (e.target.closest('[data-copy]')) {
        loadCode(shown, sol.solution[shown]);
        toast('Solution copied into the editor');
      }
    };
  }

  async function showLeft(tab) {
    view.leftTab = tab;
    $$('#left-tabs button').forEach((b) => b.classList.toggle('active', b.dataset.tab === tab));
    const body = $('#left-body');
    body.onclick = null;
    body.scrollTop = 0;
    if (tab === 'description') body.innerHTML = renderDescription();
    else if (tab === 'submissions') await renderSubmissionsTab(body);
    else if (tab === 'solution') {
      if (!view.solution) {
        body.innerHTML = '<div class="center"><span class="spinner big"></span></div>';
        try {
          view.solution = await api(`/api/problems/${p.id}/solution`, { method: 'POST' });
          if (!p.solved) p.viewedSolution = true;
        } catch (err) {
          body.innerHTML = `<div class="empty"><p>${esc(err.message)}</p></div>`;
          return;
        }
      }
      renderSolutionTab(body);
    }
  }

  $('#left-tabs').onclick = async (e) => {
    const b = e.target.closest('button[data-tab]');
    if (!b) return;
    if (b.dataset.tab === 'solution' && !view.solution && !p.viewedSolution && !p.solved && !(await confirmSolution())) return;
    showLeft(b.dataset.tab);
  };

  function confirmSolution() {
    return modal({
      icon: '👁',
      title: 'Show the solution?',
      body: "This problem will be marked as 'solution viewed' and you'll earn only half the points if you solve it afterwards. The next problem will be unlocked.",
      actions: [
        { label: 'Keep trying', style: 'btn-secondary', value: 'no' },
        { label: 'Show solution', style: 'btn-primary', value: 'yes' },
      ],
    }).then((v) => v === 'yes');
  }

  // ----- console -----
  function showConsole(tab) {
    view.consoleTab = tab;
    $$('#console-tabs .tab').forEach((b) => b.classList.toggle('active', b.dataset.tab === tab));
    const body = $('#console-body');
    body.onclick = null;

    if (tab === 'sample') {
      const i = Math.min(view.selectedCase, p.sampleTests.length - 1);
      const t = p.sampleTests[i];
      body.innerHTML = `<div class="stack">
        <div class="chips">${p.sampleTests.map((_, k) => `<span class="chip ${k === i ? 'active' : ''}" data-case="${k}">Case ${k + 1}</span>`).join('')}</div>
        <div class="io-grid">${io('INPUT', t.input)}${io('EXPECTED OUTPUT', t.output)}</div>
      </div>`;
      body.onclick = (e) => {
        const b = e.target.closest('[data-case]');
        if (b) { view.selectedCase = Number(b.dataset.case); showConsole('sample'); }
      };
    } else if (tab === 'custom') {
      body.innerHTML = `<div class="stack custom">
        <textarea id="custom-input" placeholder="Enter custom input…">${esc(view.customInput ?? p.sampleTests[0].input)}</textarea>
        <div><button class="btn btn-secondary small" id="custom-run">▶ Run with this input</button></div>
        <div id="custom-out"></div>
      </div>`;
      $('#custom-input').oninput = (e) => (view.customInput = e.target.value);
      $('#custom-run').onclick = runCustom;
      $('#custom-run').disabled = view.busy;
    } else {
      renderResult();
    }
  }

  function renderResult() {
    const body = $('#console-body');
    const r = view.lastRun;
    if (!r) {
      body.innerHTML = '<div class="empty" style="padding:30px"><span class="sym">▶</span><p>Run or submit your code to see results here.</p></div>';
      return;
    }
    if (r.pending) {
      body.innerHTML = `<div class="running"><span class="spinner big"></span><p>${r.pending}</p></div>`;
      return;
    }
    if (r.error) {
      body.innerHTML = `<div class="stack"><div class="verdict bad">✘ Error</div>${io('ERROR', r.error, 'error')}</div>`;
      return;
    }

    if (r.kind === 'run') {
      const res = r.data.results;
      const ok = r.data.verdict === 'Accepted';
      const i = Math.min(view.selectedCase, res.length - 1);
      const c = res[i];
      body.innerHTML = `<div class="stack">
        <div class="verdict ${ok ? 'ok' : 'bad'}">${ok ? '✔ Sample tests passed' : '✘ ' + esc(r.data.verdict)}
          <span class="sub">· ${res.filter((x) => x.passed).length}/${res.length} · ${r.data.maxTimeMs} ms</span></div>
        <div class="chips">${res.map((x, k) => `<span class="chip ${x.passed ? 'pass' : 'fail'} ${k === i ? 'active' : ''}" data-case="${k}">${x.passed ? '✔' : '✘'} Case ${k + 1}</span>`).join('')}</div>
        <div class="io-grid three">${io('INPUT', c.input)}${io('EXPECTED OUTPUT', c.expected)}${io('YOUR OUTPUT', c.actual)}</div>
        ${c.stderr ? io('ERROR', c.stderr, 'error') : ''}
        ${ok ? '<div class="muted mono" style="font-size:12px">Looks good — hit <span class="ok">Submit</span> to run the hidden tests.</div>' : ''}
      </div>`;
      body.onclick = (e) => {
        const b = e.target.closest('[data-case]');
        if (b) { view.selectedCase = Number(b.dataset.case); renderResult(); }
      };
      return;
    }

    // submit
    const s = r.data;
    if (s.verdict === 'Accepted') {
      body.innerHTML = `<div class="accepted-box">
        <div class="emoji">🎉</div>
        <div class="verdict ok">✔ Accepted · ${s.passedCount}/${s.totalCount} tests passed · max ${s.runtimeMs} ms</div>
        ${s.nextProblemId ? `<a class="btn btn-primary" href="#/problem/${s.nextProblemId}">Next problem →</a>` : '<a class="btn btn-primary" href="#/problems">Back to problems</a>'}
      </div>`;
      return;
    }
    const f = s.failedTest;
    body.innerHTML = `<div class="stack">
      <div>
        <div class="verdict bad">✘ ${esc(s.verdict)} <span class="sub">· ${s.passedCount}/${s.totalCount} tests passed</span></div>
        <div class="muted mono" style="font-size:12px;margin-top:4px">Failed on test ${f.number} (${f.isSample ? 'sample' : 'hidden'}).</div>
      </div>
      <div class="io-grid ${f.isSample ? 'three' : ''}">${io('INPUT', f.input)}${f.isSample ? io('EXPECTED OUTPUT', f.expected) : ''}${io('YOUR OUTPUT', f.actual)}</div>
      ${f.stderr ? io('ERROR', f.stderr, 'error') : ''}
      ${f.isSample ? '' : '<div class="note">Expected output for hidden tests is not shown.</div>'}
      <div class="actions">
        <button class="btn btn-secondary" id="try-again">Try again</button>
        ${s.canViewSolution ? '<button class="btn btn-primary" id="show-solution">👁 Show solution</button>' : ''}
      </div>
    </div>`;
    $('#try-again').onclick = () => state.editor?.focus();
    const show = $('#show-solution');
    if (show) show.onclick = async () => {
      if (!p.viewedSolution && !p.solved && !(await confirmSolution())) return;
      $('#solution-tab').hidden = false;
      showLeft('solution');
    };
  }

  $('#console-tabs').onclick = (e) => {
    const b = e.target.closest('.tab');
    if (b) showConsole(b.dataset.tab);
  };

  // ----- actions -----
  const saveDraft = debounce((lang, code) => {
    api(`/api/problems/${p.id}/draft`, { method: 'PUT', body: { language: lang, code } }).catch(() => {});
  }, 1200);

  function switchLanguage(lang) {
    if (lang === view.lang) return;
    if (state.editor) view.codes[view.lang] = state.editor.getValue();
    saveDraft.flush(view.lang, view.codes[view.lang]);
    view.lang = lang;
    $('#lang').value = lang;
    localStorage.setItem('ca_lang', lang);
    api('/api/me', { method: 'PATCH', body: { preferredLang: lang } }).catch(() => {});
    if (state.editor) {
      state.editor.setLanguage(lang);
      state.editor.setTabSize(lang === 'python' ? 4 : 2);
      state.editor.setValue(view.codes[lang]);
    }
  }

  function loadCode(lang, code) {
    switchLanguage(lang);
    view.codes[lang] = code;
    state.editor?.setValue(code);
    saveDraft(lang, code);
  }

  $('#lang').onchange = (e) => switchLanguage(e.target.value);

  $('#reset-btn').onclick = async () => {
    const ok = await modal({
      icon: '↺',
      title: 'Reset code?',
      body: `Your current ${LANGS[view.lang]} code will be replaced with the starter template.`,
      actions: [
        { label: 'Cancel', style: 'btn-secondary', value: 'no' },
        { label: 'Reset', style: 'btn-danger', value: 'yes' },
      ],
    });
    if (ok === 'yes') loadCode(view.lang, p.starterCode[view.lang]);
  };

  function setBusy(b) {
    view.busy = b;
    $('#run-btn').disabled = b;
    $('#submit-btn').disabled = b;
    $('#submit-btn').innerHTML = b ? '<span class="spinner"></span> Submit' : '↑ Submit';
    const cr = $('#custom-run');
    if (cr) cr.disabled = b;
  }

  function currentCode() {
    const code = state.editor ? state.editor.getValue() : view.codes[view.lang];
    view.codes[view.lang] = code;
    return code;
  }

  async function run() {
    if (view.busy) return;
    setBusy(true);
    view.selectedCase = 0;
    view.lastRun = { pending: `Running ${p.sampleTests.length} sample tests…` };
    showConsole('result');
    try {
      const data = await api('/api/run', { method: 'POST', body: { problemId: p.id, language: view.lang, code: currentCode() } });
      view.lastRun = { kind: 'run', data };
    } catch (err) {
      view.lastRun = { error: err.message };
    }
    setBusy(false);
    if (view.consoleTab === 'result') renderResult();
  }

  async function runCustom() {
    if (view.busy) return;
    setBusy(true);
    const out = $('#custom-out');
    out.innerHTML = '<span class="spinner"></span>';
    try {
      const r = await api('/api/run', {
        method: 'POST',
        body: { problemId: p.id, language: view.lang, code: currentCode(), customInput: $('#custom-input').value },
      });
      out.innerHTML = `<div class="stack">
        <div class="io"><span class="io-label yours">YOUR OUTPUT ${r.timedOut ? '<span class="bad">· time limit exceeded</span>' : `<span class="muted">· ${r.timeMs} ms</span>`}</span>
          <pre>${esc(r.stdout) || '<span class="dim">(no output)</span>'}</pre></div>
        ${r.stderr ? io('ERROR', r.stderr, 'error') : ''}</div>`;
    } catch (err) {
      out.innerHTML = io('ERROR', err.message, 'error');
    }
    setBusy(false);
  }

  async function submit() {
    if (view.busy) return;
    setBusy(true);
    view.lastRun = { pending: `Judging against ${p.sampleTests.length + p.hiddenTestCount} tests…` };
    showConsole('result');
    try {
      const data = await api('/api/submit', { method: 'POST', body: { problemId: p.id, language: view.lang, code: currentCode() } });
      view.lastRun = { kind: 'submit', data };
      state.stats = data.stats;
      updateTopbar('problems');
      if (data.canViewSolution) $('#solution-tab').hidden = false;
      if (data.verdict === 'Accepted') {
        const firstSolve = !p.solved;
        p.solved = true;
        if (view.leftTab === 'description') showLeft('description');
        celebrate(data, firstSolve);
      }
    } catch (err) {
      view.lastRun = { error: err.message };
    }
    setBusy(false);
    if (view.consoleTab === 'result') renderResult();
  }

  async function celebrate(data, firstSolve) {
    const allDone = data.stats.solved + data.stats.viewed === data.stats.total;
    const choice = await modal({
      icon: '🎉',
      title: 'Accepted!',
      body: `All ${data.totalCount} tests passed (max ${data.runtimeMs} ms).` +
        (firstSolve ? ` You've solved ${data.stats.solved} of ${data.stats.total} problems.` : '') +
        (allDone ? '<br><strong class="ok">You have completed every problem. Amazing work!</strong>' : ''),
      actions: [
        { label: 'Stay here', style: 'btn-secondary', value: 'stay' },
        data.nextProblemId
          ? { label: 'Next problem →', style: 'btn-primary', value: 'next' }
          : { label: 'Back to problems', style: 'btn-primary', value: 'list' },
      ],
    });
    if (choice === 'next') location.hash = `#/problem/${data.nextProblemId}`;
    else if (choice === 'list') location.hash = '#/problems';
  }

  $('#run-btn').onclick = run;
  $('#submit-btn').onclick = submit;

  showLeft('description');
  showConsole('sample');

  const editor = await createEditor($('#editor'), {
    value: view.codes[view.lang],
    language: view.lang,
    onChange: (code) => { view.codes[view.lang] = code; saveDraft(view.lang, code); },
    onRun: run,
    onSubmit: submit,
  });
  if (!editor) return; // navigated away while the editor was loading
  editor.setTabSize(view.lang === 'python' ? 4 : 2);
  state.editor = editor;
  state.cleanup.push(() => {
    saveDraft.flush(view.lang, editor.getValue());
    editor.dispose();
    state.editor = null;
  });

  if (pending && pending.problemId === p.id) {
    const { submissions } = await api(`/api/problems/${p.id}/submissions`);
    const s = submissions.find((x) => x.id === pending.submissionId);
    if (s) { loadCode(s.language, s.code); toast('Loaded your submission into the editor'); }
  }
}

// ---------------- submissions ----------------

const VERDICT_ICON = { 'Accepted': '✔', 'Wrong Answer': '✘', 'Runtime Error': '✘', 'Time Limit Exceeded': '⏱', 'Compilation Error': '⚠', 'Output Limit Exceeded': '⚠' };

async function renderSubmissions() {
  updateTopbar('submissions');
  app.innerHTML = '<div class="center"><span class="spinner big"></span></div>';
  const { submissions } = await api('/api/submissions');
  app.innerHTML = `
    <div class="page narrow fade-in">
      <div class="page-head"><h1>Your recent submissions</h1><span>${submissions.length} submission${submissions.length !== 1 ? 's' : ''}</span></div>
      ${submissions.length ? `<div class="sub-grid">${submissions.map((s) => {
        const accepted = s.verdict === 'Accepted';
        const color = accepted ? '#00ff41' : '#ff4444';
        return `
        <div class="scard ${accepted ? 'accepted' : ''}">
          <div class="vb"><b>${VERDICT_ICON[s.verdict] || '·'} ${esc(s.verdict)}</b><span>${timeAgo(s.created_at)}</span></div>
          <div class="body">
            <a class="title" href="#/problem/${s.problem_id}">${esc(s.title || 'Problem ' + s.problem_id)}</a>
            <div class="tiles">
              <div><span>LANG</span><b>${s.language === 'python' ? 'Python 3' : 'JS (Node)'}</b></div>
              <div><span>TESTS</span><b style="color:${color}">${s.passed_count}/${s.total_count}</b></div>
              <div><span>TIME</span><b>${accepted && s.runtime_ms != null ? s.runtime_ms + ' ms' : '—'}</b></div>
            </div>
            ${bar(s.passed_count, s.total_count, color)}
          </div>
          <div class="foot"><button class="btn btn-ghost bordered block small" data-load="${s.id}" data-problem="${s.problem_id}">Load code →</button></div>
        </div>`;
      }).join('')}</div>`
      : '<div class="empty"><span class="sym">⟨/⟩</span><p>No submissions yet — <a href="#/problems">pick a problem</a>.</p></div>'}
    </div>`;
  app.onclick = (e) => {
    const b = e.target.closest('[data-load]');
    if (!b) return;
    sessionStorage.setItem('ca_load', JSON.stringify({ problemId: Number(b.dataset.problem), submissionId: Number(b.dataset.load) }));
    location.hash = `#/problem/${b.dataset.problem}`;
  };
  state.cleanup.push(() => (app.onclick = null));
}

// ---------------- leaderboard ----------------

async function renderLeaderboard() {
  updateTopbar('leaderboard');
  app.innerHTML = '<div class="center"><span class="spinner big"></span></div>';
  const { leaderboard } = await api('/api/leaderboard');
  const total = state.stats?.total || 100;
  const me = state.user?.username;
  const medals = ['🥇', '🥈', '🥉'];
  const initial = (u) => esc(u[0].toUpperCase());

  app.innerHTML = `
    <div class="page lb fade-in">
      <div class="page-head"><h1>Leaderboard</h1><span>${leaderboard.length} coder${leaderboard.length !== 1 ? 's' : ''}</span></div>
      ${leaderboard.length ? `
        <div class="podium">${leaderboard.slice(0, 3).map((u, i) => `
          <div class="pod r${i + 1} ${u.username === me ? 'you' : ''}">
            <span class="medal">${medals[i]}</span>
            <div class="avatar">${initial(u.username)}</div>
            <span class="name">${esc(u.username)}${u.username === me ? ' <small>(you)</small>' : ''}</span>
            <span class="solved">${u.solved}</span><small>solved</small>
            ${bar(u.solved, total)}
            <small class="dim">${u.solved_clean} no-hint</small>
          </div>`).join('')}
        </div>
        <div class="lb-rows">${leaderboard.slice(3).map((u, i) => {
          const you = u.username === me;
          return `
          <div class="lb-row ${you ? 'you' : ''}">
            <span class="rank">${i + 4}</span>
            <div class="avatar">${initial(u.username)}</div>
            <span class="name">${esc(u.username)}${you ? ' <small class="muted">(you)</small>' : ''}</span>
            <div class="prog">${bar(u.solved, total, you ? '#818cf8' : '#00ff41')}<b>${u.solved}</b></div>
            <div class="nh"><b>${u.solved_clean}</b><small>no hint</small></div>
          </div>`;
        }).join('')}</div>`
      : '<div class="empty"><span class="sym">🏆</span><p>Nobody has solved a problem yet. Be the first!</p></div>'}
    </div>`;
}

// ---------------- router ----------------

async function route() {
  while (state.cleanup.length) {
    try { state.cleanup.pop()(); } catch { /* ignore */ }
  }
  $('#modal').hidden = true;
  window.scrollTo(0, 0);
  const [, page, arg] = (location.hash || '#/').split('/');

  if (!state.token) {
    if (page === 'login' || page === 'register') renderAuth(page);
    else renderCover();
    return;
  }
  if (!page || page === 'login' || page === 'register') {
    location.hash = '#/problems';
    return;
  }

  try {
    await ensureUser();
    if (page === 'problem' && arg) await renderProblem(Number(arg));
    else if (page === 'submissions') await renderSubmissions();
    else if (page === 'leaderboard') await renderLeaderboard();
    else await renderProblems();
  } catch (err) {
    if (!state.token) return; // logout() already redirected
    app.innerHTML = `<div class="page"><div class="empty"><p>${esc(err.message)}</p>
      <button class="btn btn-primary" onclick="location.reload()">Retry</button></div></div>`;
  }
}

$('#logout-btn').onclick = logout;
window.addEventListener('hashchange', route);
window.addEventListener('beforeunload', () => state.cleanup.forEach((fn) => { try { fn(); } catch { /* ignore */ } }));
route();
