import http from 'node:http';
import { readFile } from 'node:fs/promises';
import path from 'node:path';

const PORT = Number(process.env.PORT || 4189);
const HOST = '0.0.0.0';
const SITE_DIR = path.resolve('site');
const BASE_PATH = '/causalis';
const routes = new Set(['/', '/theory/', '/audit/', '/model/', '/research/', '/method/', '/faq/', '/token/']);
const assets = new Map([
  ['/reference.css', ['reference.css', 'text/css; charset=utf-8']],
  ['/instruments.css', ['instruments.css', 'text/css; charset=utf-8']],
  ['/styles.css', ['styles.css', 'text/css; charset=utf-8']],
  ['/app.js', ['app.js', 'text/javascript; charset=utf-8']],
  ['/grain.png', ['grain.png', 'image/png']],
  ['/downloads/causalis-audit.zip', ['downloads/causalis-audit.zip', 'application/zip']],
  ['/downloads/causalis-audit/SKILL.md', ['downloads/causalis-audit/SKILL.md', 'text/markdown; charset=utf-8']],
  ['/downloads/causalis-audit/references/rules.md', ['downloads/causalis-audit/references/rules.md', 'text/markdown; charset=utf-8']],
  ['/downloads/causalis-audit/assets/mandate.schema.json', ['downloads/causalis-audit/assets/mandate.schema.json', 'application/schema+json; charset=utf-8']],
  ['/downloads/causalis-audit/mandate.template.json', ['downloads/causalis-audit/mandate.template.json', 'application/json; charset=utf-8']],
  ['/downloads/causalis-audit/examples/valid.mandate.json', ['downloads/causalis-audit/examples/valid.mandate.json', 'application/json; charset=utf-8']],
  ['/assets/causalis-transparent.png', ['assets/causalis-transparent.png', 'image/png']],
  ['/assets/causalis.png', ['assets/causalis.png', 'image/png']]
]);

const server = http.createServer(async (request, response) => {
  try {
    const url = new URL(request.url || '/', `http://${request.headers.host || `localhost:${PORT}`}`);
    const pathname = url.pathname === BASE_PATH ? '/' : url.pathname.startsWith(`${BASE_PATH}/`) ? url.pathname.slice(BASE_PATH.length) : url.pathname;
    if (request.method !== 'GET' && request.method !== 'HEAD') {
      response.writeHead(405, { allow: 'GET, HEAD' }); response.end(); return;
    }
    if (routes.has(pathname)) {
      const body = await readFile(path.join(SITE_DIR, 'index.html'));
      response.writeHead(200, { 'content-type': 'text/html; charset=utf-8', 'cache-control': 'no-cache' });
      response.end(request.method === 'HEAD' ? undefined : body); return;
    }
    const asset = assets.get(pathname);
    if (asset) {
      const body = await readFile(path.join(SITE_DIR, asset[0]));
      response.writeHead(200, { 'content-type': asset[1], 'cache-control': asset[1] === 'image/png' ? 'public, max-age=86400' : 'no-cache' });
      response.end(request.method === 'HEAD' ? undefined : body); return;
    }
    const fontMatch = pathname.match(/^\/assets\/fonts\/([a-z0-9-]+\.ttf)$/);
    if (fontMatch) {
      const body = await readFile(path.join(SITE_DIR, 'assets', 'fonts', fontMatch[1]));
      response.writeHead(200, { 'content-type': 'font/ttf', 'cache-control': 'public, max-age=604800' });
      response.end(request.method === 'HEAD' ? undefined : body); return;
    }
    const webFontMatch = pathname.match(/^\/assets\/fonts\/([a-z0-9-]+\.woff2)$/);
    if (webFontMatch) {
      const body = await readFile(path.join(SITE_DIR, 'assets', 'fonts', webFontMatch[1]));
      response.writeHead(200, { 'content-type': 'font/woff2', 'cache-control': 'public, max-age=604800' });
      response.end(request.method === 'HEAD' ? undefined : body); return;
    }
    response.writeHead(404, { 'content-type': 'text/plain; charset=utf-8' }); response.end('Not found');
  } catch (error) {
    response.writeHead(500, { 'content-type': 'text/plain; charset=utf-8' }); response.end(`CAUSALIS local service error\n${error.message}`);
  }
});

server.listen(PORT, HOST, () => console.log(`CAUSALIS local frontend: http://localhost:${PORT}${BASE_PATH}/`));
