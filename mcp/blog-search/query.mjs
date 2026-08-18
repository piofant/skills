/**
 * One-off CLI: воспроизводит search_posts MCP-тула напрямую (без MCP-сервера).
 * usage: node query.mjs "<запрос>" [limit] [tag]
 * Переиспользует lib.mjs (embed через OpenRouter + cosine) и index.json.
 */
import { readFile } from 'node:fs/promises';
import { loadEnv, orKey, embed, cosine, INDEX_PATH } from './lib.mjs';

loadEnv();
const key = orKey();
if (!key) { console.error('💥 нет OR_LLM_API_KEY в .env'); process.exit(1); }

const query = process.argv[2] || 'опыт через тело, телесные практики';
const limit = Number(process.argv[3] || 15);
const tag = process.argv[4] || null;

const INDEX = JSON.parse(await readFile(INDEX_PATH, 'utf8'));
let posts = INDEX.posts || [];
if (tag) posts = posts.filter((p) => (p.tags || []).some((t) => t.toLowerCase() === tag.toLowerCase()));

const [qvec] = await embed([query], key);
const scored = posts
  .map((p) => ({ p, score: cosine(qvec, p.vector) }))
  .sort((a, b) => b.score - a.score)
  .slice(0, limit);

console.log(`\n🔍 «${query}»${tag ? ` · тег:${tag}` : ''} — топ ${scored.length} из ${posts.length}\n`);
for (const { p, score } of scored) {
  const id = p.tgMessageId || (p.slug.match(/-(\d+)$/)?.[1] ?? '?');
  console.log(`[${String(id).padStart(3)}] ${score.toFixed(3)}  ${p.title}`);
  console.log(`        теги: ${(p.tags || []).join(', ') || '—'}`);
}
