const { JSDOM, ResourceLoader } = require('jsdom');
const http = require('http');
const fs = require('fs');
const path = require('path');

const ROOT = process.cwd();
const MIME = { '.html':'text/html', '.js':'application/javascript', '.css':'text/css', '.mp3':'audio/mpeg', '.json':'application/json' };

// 本地静态服务器（仅本测试用）
const server = http.createServer((req, res) => {
  let p = decodeURIComponent(req.url.split('?')[0]);
  if (p === '/') p = '/index.html';
  const fp = path.join(ROOT, p);
  if (!fp.startsWith(ROOT) || !fs.existsSync(fp)) { res.writeHead(404); res.end('nf'); return; }
  res.writeHead(200, { 'Content-Type': MIME[path.extname(fp)] || 'application/octet-stream' });
  fs.createReadStream(fp).pipe(res);
});

server.listen(0, '127.0.0.1', () => {
  const port = server.address().port;
  const base = 'http://127.0.0.1:' + port + '/';
  const errors = [];

  JSDOM.fromURL(base, {
    runScripts: 'dangerously',
    resources: 'usable',
    pretendToBeVisual: true
  }).then(dom => {
    const { window } = dom;
    window.addEventListener('error', e => errors.push('PAGEERROR: ' + (e.error ? e.error.stack : e.message)));
    window.console.error = (...a) => errors.push('console.error: ' + a.join(' '));

    setTimeout(() => {
      const doc = window.document;
      const content = doc.getElementById('content');
      const toc = doc.getElementById('toc');
      const hasData = !!(window.BOOK_DATA && window.BOOK_DATA[0]);
      const fc = doc.querySelector('.flashcard, .row, .sec-head, .word-row, h2, h3');
      console.log('=== jsdom 端到端测试结果（http origin）===');
      console.log('window.BOOK_DATA[0] 存在 :', hasData);
      console.log('#toc 渲染长度          :', toc ? toc.innerHTML.length : 'NO #toc');
      console.log('#toc 文本片段          :', toc ? toc.textContent.replace(/\s+/g,' ').slice(0,180) : '');
      console.log('#content 渲染长度      :', content ? content.innerHTML.length : 'NO #content');
      console.log('内容区首节点          :', fc ? (fc.className||fc.tagName) : '空（未渲染）');
      console.log('捕获错误数            :', errors.length);
      errors.slice(0, 10).forEach(e => console.log('  - ' + e.slice(0, 300)));
      console.log('=== 结束 ===');
      server.close();
      process.exit(0);
    }, 4500);
  }).catch(e => { console.error('JSDOM 启动失败:', e); server.close(); process.exit(1); });
});
