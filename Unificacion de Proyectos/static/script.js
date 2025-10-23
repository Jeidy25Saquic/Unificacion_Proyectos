// ============ UTILIDADES BÁSICAS ============

function insertAtCursor(contentEditable, text) {
  contentEditable.focus();
  const sel = window.getSelection();
  if (!sel || sel.rangeCount === 0) {
    contentEditable.textContent += text;
    return;
  }
  const range = sel.getRangeAt(0);
  range.deleteContents();
  const node = document.createTextNode(text);
  range.insertNode(node);
  range.setStartAfter(node);
  range.collapse(true);
  sel.removeAllRanges();
  sel.addRange(range);
}

// ============ DOM REFERENCIAS ============

const exprDisplay = document.getElementById('exprDisplay');
const statusEl = document.getElementById('status');
const resultEl = document.getElementById('result');
const stepsEl = document.getElementById('steps');
const btnSimplify = document.getElementById('btnSimplify');
const btnExport = document.getElementById('btnExport');
const btnClear = document.getElementById('btnClear');

// ============ EVENTOS DE BOTONES OPERADORES ============

document.querySelectorAll('.op').forEach(btn => {
  btn.addEventListener('click', () => {
    insertAtCursor(exprDisplay, btn.dataset.insert);
    exprDisplay.focus();
  });
});

btnClear.addEventListener('click', () => {
  exprDisplay.textContent = '';
  resultEl.textContent = '';
  stepsEl.innerHTML = '';
  status('Expresión limpia.');
});

// ============ TOKENIZACIÓN ============

function tokenize(input) {
  const tokens = [];
  let i = 0;
  const isLetter = c => /[A-Za-z]/.test(c);
  const isDigit = c => /[0-9]/.test(c);
  const isIdent = c => /[A-Za-z0-9_]/.test(c);

  while (i < input.length) {
    const c = input[i];
    if (c === ' ' || c === '\t' || c === '\n' || c === '\r') { i++; continue; }
    if (c === '(') { tokens.push({ type: 'LP', v: '(' }); i++; continue; }
    if (c === ')') { tokens.push({ type: 'RP', v: ')' }); i++; continue; }
    if (c === '&' || c === '*' || c === '·') { tokens.push({ type: 'AND', v: '&' }); i++; continue; }
    if (c === '|' || c === '+' || c.toLowerCase() === 'v') { tokens.push({ type: 'OR', v: '|' }); i++; continue; }
    if (c === '~' || c === '!') { tokens.push({ type: 'NOT', v: '~' }); i++; continue; }
    if (c === '0' || c === '1') { tokens.push({ type: 'CONST', v: c === '1' }); i++; continue; }
    if (isLetter(c)) {
      let j = i + 1;
      while (j < input.length && isIdent(input[j])) j++;
      tokens.push({ type: 'VAR', v: input.slice(i, j) });
      i = j;
      continue;
    }
    throw new Error('Carácter no válido: ' + c);
  }
  tokens.push({ type: 'EOF' });
  return tokens;
}

// ============ CONSTRUCTORES DE NODOS ============

function ConstNode(v) { return { type: 'CONST', value: !!v }; }
function VarNode(name) { return { type: 'VAR', name }; }
function NotNode(child) { return { type: 'NOT', child }; }
function AndNode(children) { return { type: 'AND', children }; }
function OrNode(children) { return { type: 'OR', children }; }

// ============ PARSING ============

function parse(input) {
  const tokens = Array.isArray(input) ? input : tokenize(input);
  let pos = 0;
  const peek = () => tokens[pos];
  const eat = (typ) => {
    const t = tokens[pos];
    if (t.type !== typ) throw new Error('Token inesperado: ' + t.type + ' se esperaba ' + typ);
    pos++;
    return t;
  };

  function parseExpr() { return parseOr(); }
  function parseOr() {
    let node = parseAnd();
    while (peek().type === 'OR') {
      eat('OR');
      const right = parseAnd();
      node = OrNode(flattenOr(node, right));
    }
    return node;
  }
  function parseAnd() {
    let node = parseUnary();
    while (peek().type === 'AND') {
      eat('AND');
      const right = parseUnary();
      node = AndNode(flattenAnd(node, right));
    }
    return node;
  }
  function parseUnary() {
    if (peek().type === 'NOT') { eat('NOT'); return NotNode(parseUnary()); }
    return parsePrimary();
  }
  function parsePrimary() {
    const t = peek();
    if (t.type === 'VAR') { eat('VAR'); return VarNode(t.v); }
    if (t.type === 'CONST') { eat('CONST'); return ConstNode(t.v); }
    if (t.type === 'LP') { eat('LP'); const e = parseExpr(); eat('RP'); return e; }
    throw new Error('Token inesperado: ' + t.type);
  }

  const ast = parseExpr();
  if (peek().type !== 'EOF') throw new Error('Entrada no consumida completamente');
  return ast;
}

// ============ CONVERSIÓN A STRING ============

function toString(node) {
  function precedence(n) {
    if (!n) return 0;
    switch (n.type) {
      case 'OR': return 1;
      case 'AND': return 3;
      case 'NOT': return 4;
      case 'VAR': case 'CONST': return 5;
    }
  }

  switch (node.type) {
    case 'VAR': return node.name;
    case 'CONST': return node.value ? '1' : '0';
    case 'NOT':
      if (node.child.type === 'VAR' || node.child.type === 'CONST' || node.child.type === 'NOT')
        return '~' + toString(node.child);
      return '~(' + toString(node.child) + ')';
    case 'AND':
      return node.children.map(c =>
        precedence(c) < precedence({ type: 'AND' }) ? '(' + toString(c) + ')' : toString(c)
      ).join(' & ');
    case 'OR':
      return node.children.map(c =>
        precedence(c) < precedence({ type: 'OR' }) ? '(' + toString(c) + ')' : toString(c)
      ).join(' | ');
  }
}

// ============ HELPERS ============

function flattenAnd(a, b) {
  const out = [];
  if (a.type === 'AND') out.push(...a.children); else out.push(a);
  if (b.type === 'AND') out.push(...b.children); else out.push(b);
  return out;
}

function flattenOr(a, b) {
  const out = [];
  if (a.type === 'OR') out.push(...a.children); else out.push(a);
  if (b.type === 'OR') out.push(...b.children); else out.push(b);
  return out;
}

function clone(node) {
  switch (node.type) {
    case 'CONST': return ConstNode(node.value);
    case 'VAR': return VarNode(node.name);
    case 'NOT': return NotNode(clone(node.child));
    case 'AND': return AndNode(node.children.map(clone));
    case 'OR': return OrNode(node.children.map(clone));
  }
}

function canonicalStr(n) {
  switch (n.type) {
    case 'AND':
      return 'AND(' + n.children.map(canonicalStr).sort().join(',') + ')';
    case 'OR':
      return 'OR(' + n.children.map(canonicalStr).sort().join(',') + ')';
    case 'NOT': return 'NOT(' + canonicalStr(n.child) + ')';
    case 'VAR': return 'VAR(' + n.name + ')';
    case 'CONST': return 'CONST(' + (n.value ? 1 : 0) + ')';
  }
}

// ============ SIMPLIFICACIÓN ============

function simplificar(ast) {
  const steps = [];

  function pushPaso(before, after, rule) {
    const sBefore = toString(before);
    const sAfter = toString(after);
    if (sBefore !== sAfter) {
      steps.push({ rule, before: sBefore, after: sAfter });
    }
    return after;
  }

  function uniqueByCanonical(arr) {
    const seen = new Set();
    const out = [];
    for (const x of arr) {
      const k = canonicalStr(x);
      if (!seen.has(k)) { seen.add(k); out.push(x); }
    }
    return out;
  }

  function containsNegation(list, node) {
    const s = toString(node);
    for (const x of list) {
      if (x.type === 'NOT' && toString(x.child) === s) return true;
      if (node.type === 'NOT' && toString(node.child) === toString(x)) return true;
    }
    return false;
  }

  function normalize(n) {
    switch (n.type) {
      case 'CONST': return n;
      case 'VAR': return n;
      case 'NOT': return NotNode(normalize(n.child));
      case 'AND': {
        let ch = n.children.map(normalize).flatMap(c => c.type === 'AND' ? c.children : [c]);
        ch = ch.filter(c => !(c.type === 'CONST' && c.value === true));
        if (ch.length === 0) return ConstNode(true);
        if (ch.some(c => c.type === 'CONST' && c.value === false)) return ConstNode(false);
        ch = uniqueByCanonical(ch).sort((a, b) => toString(a).localeCompare(toString(b)));
        return AndNode(ch);
      }
      case 'OR': {
        let ch = n.children.map(normalize).flatMap(c => c.type === 'OR' ? c.children : [c]);
        ch = ch.filter(c => !(c.type === 'CONST' && c.value === false));
        if (ch.length === 0) return ConstNode(false);
        if (ch.some(c => c.type === 'CONST' && c.value === true)) return ConstNode(true);
        ch = uniqueByCanonical(ch).sort((a, b) => toString(a).localeCompare(toString(b)));
        return OrNode(ch);
      }
    }
  }

  function step(node) {
    switch (node.type) {
      case 'CONST': return node;
      case 'VAR': return node;
      case 'NOT': {
        const c = step(node.child);
        if (c.type === 'NOT') return pushPaso(node, c.child, 'Doble negación');
        if (c.type === 'AND') {
          const mapped = c.children.map(x => NotNode(x));
          const res = OrNode(mapped);
          return pushPaso(node, res, 'De Morgan');
        }
        if (c.type === 'OR') {
          const mapped = c.children.map(x => NotNode(x));
          const res = AndNode(mapped);
          return pushPaso(node, res, 'De Morgan');
        }
        if (c.type === 'CONST') {
          const res = ConstNode(!c.value);
          return pushPaso(node, res, 'Complemento constante');
        }
        return NotNode(c);
      }
      case 'AND': {
        const children = node.children.map(step);
        const before = AndNode(children);
        if (children.some(c => c.type === 'CONST' && c.value === true)) {
          const filtered = children.filter(c => !(c.type === 'CONST' && c.value === true));
          const res = filtered.length === 0 ? ConstNode(true) : (filtered.length === 1 ? filtered[0] : AndNode(filtered));
          return pushPaso(before, res, 'Identidad AND');
        }
        if (children.some(c => c.type === 'CONST' && c.value === false)) {
          return pushPaso(before, ConstNode(false), 'Anulación AND');
        }
        let uniq = uniqueByCanonical(children);
        if (uniq.length !== children.length) return pushPaso(before, AndNode(uniq), 'Idempotencia AND');
        for (const c of uniq) {
          if (containsNegation(uniq, c)) return pushPaso(before, ConstNode(false), 'Complemento AND');
        }
        for (let i = 0; i < uniq.length; i++) {
          for (let j = 0; j < uniq.length; j++) {
            if (i === j) continue;
            const a = uniq[i], b = uniq[j];
            if (b.type === 'OR' && b.children.some(ch => toString(ch) === toString(a))) {
              return pushPaso(before, a, 'Absorción AND');
            }
          }
        }
        return before;
      }
      case 'OR': {
        const children = node.children.map(step);
        const before = OrNode(children);
        if (children.some(c => c.type === 'CONST' && c.value === false)) {
          const filtered = children.filter(c => !(c.type === 'CONST' && c.value === false));
          const res = filtered.length === 0 ? ConstNode(false) : (filtered.length === 1 ? filtered[0] : OrNode(filtered));
          return pushPaso(before, res, 'Identidad OR');
        }
        if (children.some(c => c.type === 'CONST' && c.value === true)) {
          return pushPaso(before, ConstNode(true), 'Anulación OR');
        }
        let uniq = uniqueByCanonical(children);
        if (uniq.length !== children.length) return pushPaso(before, OrNode(uniq), 'Idempotencia OR');
        for (const c of uniq) {
          if (containsNegation(uniq, c)) return pushPaso(before, ConstNode(true), 'Complemento OR');
        }
        for (let i = 0; i < uniq.length; i++) {
          for (let j = 0; j < uniq.length; j++) {
            if (i === j) continue;
            const a = uniq[i], b = uniq[j];
            if (b.type === 'AND' && b.children.some(ch => toString(ch) === toString(a))) {
              return pushPaso(before, a, 'Absorción OR');
            }
          }
        }
        return before;
      }
    }
  }

  let current = normalize(ast);
  while (true) {
    const beforeS = toString(current);
    const afterNode = normalize(step(current));
    const afterS = toString(afterNode);
    if (afterS === beforeS) break;
    current = afterNode;
  }
  return { node: current, steps };
}

// ============ RENDERIZADO DE PASOS ============

function renderSteps(steps) {
  stepsEl.innerHTML = '';
  if (!steps.length) {
    const li = document.createElement('li');
    li.textContent = 'No se aplicó ninguna ley (ya está simplificada o no hubo transformación).';
    stepsEl.appendChild(li);
    return;
  }
  for (const s of steps) {
    const li = document.createElement('li');
    li.textContent = s.rule + ' : ' + s.before + ' => ' + s.after;
    stepsEl.appendChild(li);
  }
}

// ============ GESTIÓN DE RESULTADOS ============

let lastResult = null;

btnSimplify.addEventListener('click', () => {
  const raw = exprDisplay.textContent.trim();
  if (!raw) {
    status('No hay expresión para simplificar.');
    alert('La expresión está vacía.');
    return;
  }
  try {
    const normalized = raw.replace(/·/g, '&').replace(/\s+/g, ' ').trim();
    const ast = parse(normalized);
    const out = simplificar(ast);
    const text = toString(out.node);
    resultEl.textContent = text;
    renderSteps(out.steps);
    status('Simplificación completa. ' + out.steps.length + ' paso(s).');
    lastResult = { original: raw, normalized, simplified: text, steps: out.steps };
  } catch (err) {
    console.error(err);
    resultEl.textContent = '';
    stepsEl.innerHTML = '';
    status('Error de sintaxis. Revisa la expresión.');
    alert('Error: ' + err.message);
  }
});

btnExport.addEventListener('click', () => {
  const payload = lastResult || {
    original: exprDisplay.textContent.trim() || null,
    normalized: null,
    simplified: null,
    steps: []
  };
  const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'simplificacion_con_pasos.json';
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(a.href), 0);
});

// ============ INICIALIZACIÓN ============

exprDisplay.textContent = '(A & B) | (A & ~B)';
status('Listo');

function status(msg) {
  statusEl.textContent = msg;
}