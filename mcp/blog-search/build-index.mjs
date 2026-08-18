/**
 * build-index.mjs — строит/обновляет index.json с эмбеддингами постов.
 *
 * Инкрементально: re-embed только посты, у которых сменился contentHash
 * (title+body). Остальные вектора переиспользуются из старого index.json.
 * → почти бесплатно при ежедневных обновлениях.
 *
 * Запуск:
 *   node build-index.mjs           # инкрементально
 *   node build-index.mjs --force   # пересчитать все эмбеддинги
 *
 * ENV: OR_LLM_API_KEY (или OPENROUTER_API_KEY) — из .env или окружения.
 */
import { writeFile, readFile } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { loadEnv, orKey, loadPosts, embed, INDEX_PATH, EMBED_MODEL } from './lib.mjs';

loadEnv();
const KEY = orKey();
const FORCE = process.argv.includes('--force');

if (!KEY) {
	console.error('💥 Нет OR_LLM_API_KEY. Положи в mcp/blog-search/.env:\n   OR_LLM_API_KEY=sk-or-...');
	process.exit(1);
}

/** Загружает старый index.json → Map<slug, entry> для переиспользования векторов. */
async function loadPrev() {
	if (FORCE || !existsSync(INDEX_PATH)) return new Map();
	try {
		const json = JSON.parse(await readFile(INDEX_PATH, 'utf8'));
		return new Map((json.posts || []).map((p) => [p.slug, p]));
	} catch {
		return new Map();
	}
}

const posts = await loadPosts();
const prev = await loadPrev();
console.error(`📋 ${posts.length} постов (не-draft). Старый индекс: ${prev.size} записей.`);

// Что нужно переэмбеддить: новые ИЛИ изменившиеся (hash разъехался).
const toEmbed = [];
for (const p of posts) {
	const old = prev.get(p.slug);
	if (!old || old.hash !== p.hash || !Array.isArray(old.vector)) {
		toEmbed.push(p);
	}
}
console.error(`🔢 К переэмбеддингу: ${toEmbed.length}${FORCE ? ' (--force)' : ''}`);

const vectorBySlug = new Map();
// Переносим неизменившиеся вектора.
for (const p of posts) {
	const old = prev.get(p.slug);
	if (old && old.hash === p.hash && Array.isArray(old.vector) && !FORCE) {
		vectorBySlug.set(p.slug, old.vector);
	}
}

if (toEmbed.length) {
	// Эмбеддим title + body (обрезка до лимита делается в embed()).
	const inputs = toEmbed.map((p) => `${p.title}\n\n${p.body}`);
	const t0 = Date.now();
	const vectors = await embed(inputs, KEY);
	console.error(`✅ Получено ${vectors.length} векторов за ${((Date.now() - t0) / 1000).toFixed(1)}s`);
	toEmbed.forEach((p, i) => vectorBySlug.set(p.slug, vectors[i]));
}

// Собираем итоговый индекс (БЕЗ body — body читается из .md на лету в server).
const index = {
	model: EMBED_MODEL,
	dims: vectorBySlug.size ? (vectorBySlug.values().next().value?.length ?? 0) : 0,
	generated_at: new Date().toISOString(),
	posts: posts.map((p) => ({
		slug: p.slug,
		title: p.title,
		tags: p.tags,
		pubDate: p.pubDate,
		url: p.url,
		hash: p.hash,
		vector: vectorBySlug.get(p.slug) || null,
	})).filter((p) => Array.isArray(p.vector)),
};

await writeFile(INDEX_PATH, JSON.stringify(index));
console.error(`💾 Записал ${INDEX_PATH} — ${index.posts.length} постов, dims=${index.dims}`);
