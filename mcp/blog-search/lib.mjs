/**
 * Shared helpers для blog-search MCP: env, парсинг постов, эмбеддинги, cosine.
 * Без внешних зависимостей кроме встроенного fetch (Node 22+).
 */
import { readdir, readFile } from 'node:fs/promises';
import { existsSync, readFileSync } from 'node:fs';
import { join, dirname, basename } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createHash } from 'node:crypto';

export const HERE = dirname(fileURLToPath(import.meta.url));
export const ROOT = join(HERE, '..', '..');           // pioblog repo root
export const BLOG_DIR = join(ROOT, 'src/content/blog');
export const INDEX_PATH = join(HERE, 'index.json');
export const SITE = 'https://piofant.github.io';
export const EMBED_MODEL = 'openai/text-embedding-3-small'; // 1536 dims, OpenRouter
export const EMBED_ENDPOINT = 'https://openrouter.ai/api/v1/embeddings';

/** Грузит .env из директории сервера (KEY=VALUE построчно) в process.env. */
export function loadEnv() {
	const envPath = join(HERE, '.env');
	if (!existsSync(envPath)) return;
	for (const line of readFileSync(envPath, 'utf8').split('\n')) {
		const m = line.match(/^\s*([A-Z0-9_]+)\s*=\s*(.*)\s*$/i);
		if (!m) continue;
		const key = m[1];
		let val = m[2].trim().replace(/^["']|["']$/g, '');
		if (!process.env[key]) process.env[key] = val;
	}
}

/** OpenRouter API key из env (OR_LLM_API_KEY приоритетно, потом OPENROUTER_API_KEY). */
export function orKey() {
	return process.env.OR_LLM_API_KEY || process.env.OPENROUTER_API_KEY || '';
}

/** Лёгкий парсер frontmatter — без yaml-зависимости. Посты pioblog имеют
   стабильный формат: title в кавычках, tags как ['a','b'], pubDate, draft. */
export function parseFrontmatter(raw) {
	const m = raw.match(/^---\n([\s\S]*?)\n---\n?([\s\S]*)$/);
	if (!m) return { fm: {}, body: raw.trim() };
	const fmText = m[1];
	const body = m[2].trim();
	const fm = {};
	const title = fmText.match(/^title:\s*['"]?(.*?)['"]?\s*$/m);
	if (title) fm.title = title[1];
	const pub = fmText.match(/^pubDate:\s*['"]?(\d{4}-\d{2}-\d{2})/m);
	if (pub) fm.pubDate = pub[1];
	const upd = fmText.match(/^updatedDate:\s*['"]?(\d{4}-\d{2}-\d{2})/m);
	if (upd) fm.updatedDate = upd[1];
	const tg = fmText.match(/^tgMessageId:\s*'?(\d+)'?/m);
	if (tg) fm.tgMessageId = Number(tg[1]);
	const draft = fmText.match(/^draft:\s*(true|false)/m);
	fm.draft = draft ? draft[1] === 'true' : false;
	const tagsLine = fmText.match(/^tags:\s*\[([^\]]*)\]/m);
	fm.tags = tagsLine
		? tagsLine[1].split(',').map((s) => s.trim().replace(/^['"]|['"]$/g, '')).filter(Boolean)
		: [];
	return { fm, body };
}

/** URL поста на сайте. */
export function postUrl(slug) {
	return `${SITE}/blog/${slug}/`;
}

/** Контентный хэш (title+body) — для инкрементальной переиндексации. */
export function contentHash(title, body) {
	return createHash('sha1').update(title + '\n' + body).digest('hex').slice(0, 16);
}

/** Читает все НЕ-draft посты из BLOG_DIR. Возвращает [{slug,file,title,tags,
   pubDate,updatedDate,tgMessageId,body,hash,url}]. */
export async function loadPosts() {
	const files = (await readdir(BLOG_DIR)).filter((f) => f.endsWith('.md'));
	const posts = [];
	for (const file of files) {
		const raw = await readFile(join(BLOG_DIR, file), 'utf8');
		const { fm, body } = parseFrontmatter(raw);
		if (fm.draft) continue;
		const slug = basename(file, '.md');
		const title = fm.title || slug;
		posts.push({
			slug, file, title,
			tags: fm.tags || [],
			pubDate: fm.pubDate || '',
			updatedDate: fm.updatedDate || '',
			tgMessageId: fm.tgMessageId || null,
			body,
			hash: contentHash(title, body),
			url: postUrl(slug),
		});
	}
	return posts;
}

/** Читает body одного поста по slug свежим чтением (для get_post / full search). */
export async function readPostBody(slug) {
	const path = join(BLOG_DIR, `${slug}.md`);
	if (!existsSync(path)) return null;
	const raw = await readFile(path, 'utf8');
	return parseFrontmatter(raw);
}

/** Эмбеддит массив строк через OpenRouter. Батчами по 64. Возвращает массив
   векторов в том же порядке. text-embedding-3-small лимит 8191 токенов/строку
   → обрезаем вход до ~24k символов (с запасом). */
export async function embed(texts, key, { batchSize = 64 } = {}) {
	const out = [];
	for (let i = 0; i < texts.length; i += batchSize) {
		const batch = texts.slice(i, i + batchSize).map((t) => t.slice(0, 24000));
		const res = await fetch(EMBED_ENDPOINT, {
			method: 'POST',
			headers: { Authorization: `Bearer ${key}`, 'Content-Type': 'application/json' },
			body: JSON.stringify({ model: EMBED_MODEL, input: batch }),
		});
		if (!res.ok) {
			const text = await res.text().catch(() => '');
			throw new Error(`embeddings ${res.status}: ${text.slice(0, 300)}`);
		}
		const json = await res.json();
		// OpenRouter возвращает data[] в порядке input, с полем index — отсортируем.
		const sorted = [...json.data].sort((a, b) => (a.index ?? 0) - (b.index ?? 0));
		for (const d of sorted) out.push(d.embedding);
	}
	return out;
}

/** Cosine similarity двух векторов одинаковой длины. */
export function cosine(a, b) {
	let dot = 0, na = 0, nb = 0;
	for (let i = 0; i < a.length; i++) {
		dot += a[i] * b[i];
		na += a[i] * a[i];
		nb += b[i] * b[i];
	}
	if (na === 0 || nb === 0) return 0;
	return dot / (Math.sqrt(na) * Math.sqrt(nb));
}

/** Короткий excerpt из тела: убираем markdown-разметку, первые N символов. */
export function excerpt(body, n = 300) {
	const clean = body
		.replace(/!\[[^\]]*\]\([^)]*\)/g, '')        // images
		.replace(/\[([^\]]*)\]\([^)]*\)/g, '$1')       // links → text
		.replace(/[*_>#`~|]/g, '')                      // md symbols
		.replace(/\s+/g, ' ')
		.trim();
	return clean.length > n ? clean.slice(0, n).replace(/\s+\S*$/, '') + '…' : clean;
}
