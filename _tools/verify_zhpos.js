const fs = require('fs');
const vm = require('vm');

// ---- 1. 从真实 app.js 提取 block() 函数源码 ----
const app = fs.readFileSync('js/app.js', 'utf8');
const start = app.indexOf('function block(title, kind, arr) {');
let i = app.indexOf('{', start), depth = 0, end = -1;
for (; i < app.length; i++) {
  if (app[i] === '{') depth++;
  else if (app[i] === '}') { depth--; if (depth === 0) { end = i + 1; break; } }
}
const body = app.slice(start, end);
if (!body.includes('zh-pos')) { console.error('FAIL: 提取的 block 未含 zh-pos 改动'); process.exit(1); }

// ---- 2. stub 依赖 ----
function esc(t) {
  return String(t == null ? '' : t).replace(/&/g, '&amp;').replace(/</g, '&lt;')
    .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}
const AUDIO = 'audio/';
function curParte() { return { gid: 0 }; }
function curSec() { return { no: 1 }; }
function uid(g, s, k, i) { return 'u' + g + '_' + s + '_' + k + '_' + i; }

const fn = new Function('AUDIO', 'esc', 'uid', 'curParte', 'curSec', body + '\nreturn block;');
const block = fn(AUDIO, esc, uid, curParte, curSec);

// ---- 3. 加载真实 sec/0.js 数据 ----
const sb = { window: {} };
sb.window.BOOK_DATA = {};
vm.createContext(sb);
vm.runInContext(fs.readFileSync('data/sec/0.js', 'utf8'), sb);
const data = sb.window.BOOK_DATA[0];
const sec = data.secs.find(s => s.name === '数词（1）');
const html = block('数词（1）', 'w', sec.w);

// ---- 4. 断言 ----
const total = sec.w.length;
const withPos = (html.match(/zh-pos/g) || []).length;
console.log('数词（1）词条数:', total, '| 中文后词性标签数:', withPos);
// 取前 3 条中文渲染片段
const samples = sec.w.slice(0, 3).map(it => it[0] + ' (' + it[2] + ')');
console.log('样本:', samples.join('  '));
// 检查第一条中文后确有词性
const firstLine = html.split('class="row"')[1];
const ok = firstLine.includes('>一') && firstLine.includes('zh-pos') && firstLine.includes('m.');
console.log('首条 "一" 后含 zh-pos 词性:', ok);
// 词性缺失项（it[2] 为空但应标）
const missing = sec.w.filter(it => !it[2]).length;
console.log('无词性的词条:', missing);
console.log(ok && withPos === total - missing ? 'VERIFY PASS ✅' : 'VERIFY FAIL ❌');
