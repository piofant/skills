#!/usr/bin/env node
/**
 * blog-search MCP — stdio-сервер семантического + тег-поиска по постам pioblog.
 *
 * Tools:
 *   search_posts(query, limit?, tag?, full?) — семантический поиск (эмбеддинг
 *       запроса → cosine-sim по index.json). full=true → отдаёт полный текст
 *       постов, иначе excerpt.
 *   list_by_tag(tag, limit?) — посты с тегом (без эмбеддингов).
 *   get_post(slug) — полный markdown конкретного поста.
 *
 * Требует: index.json (node build-index.mjs) + OR_LLM_API_KEY (для эмбеддинга
 * запроса в search_posts; list_by_tag/get_post работают без ключа).
 */
import { readFile } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { z } from 'zod';
import {
	loadEnv, orKey, embed, cosine, excerpt, readPostBody, postUrl,
	INDEX_PATH, EMBED_MODEL,
} from './lib.mjs';

loadEnv();

// ── Загрузка индекса (один раз при старте) ──────────────────────────────────
if (!existsSync(INDEX_PATH)) {
	console.error('💥 index.json не найден. Сначала: cd mcp/blog-search && node build-index.mjs');
	process.exit(1);
}
const INDEX = JSON.parse(await readFile(INDEX_PATH, 'utf8'));
const POSTS = INDEX.posts || [];
console.error(`[blog-search] загружено ${POSTS.length} постов из индекса (model=${INDEX.model})`);

// ── Хелперы ─────────────────────────────────────────────────────────────────
function uniqTags() {
	const s = new Set();
	for (const p of POSTS) for (const t of p.tags || []) s.add(t);
	return [...s].sort((a, b) => a.localeCompare(b, 'ru'));
}

/** Возвращает полный body поста (свежее чтение .md). null если файла нет. */
async function bodyOf(slug) {
	const parsed = await readPostBody(slug);
	return parsed ? parsed.body : null;
}

// ── MCP server ───────────────────────────────────────────────────────────────
const server = new McpServer({ name: 'blog-search', version: '1.0.0' });

server.registerTool(
	'search_posts',
	{
		title: 'Семантический поиск по постам',
		description:
			'Семантический поиск по блогу Вовы (piofant.github.io): эмбеддит запрос и ' +
			'находит самые смысловые-близкие посты (не по точным словам, а по смыслу). ' +
			'Возвращает посты с заголовком, ссылкой, тегами, score и текстом. ' +
			'Опционально фильтрует по тегу. full=true отдаёт ПОЛНЫЙ текст постов, ' +
			'иначе короткий excerpt (экономит токены).',
		inputSchema: {
			query: z.string().describe('Поисковый запрос на естественном языке (рус/англ)'),
			limit: z.number().int().min(1).max(20).optional().describe('Сколько постов вернуть (по умолчанию 5)'),
			tag: z.string().optional().describe('Фильтр по тегу (точное совпадение, напр. "танцы")'),
			full: z.boolean().optional().describe('true → полный текст постов; false (по умолчанию) → excerpt'),
		},
		annotations: { readOnlyHint: true, openWorldHint: false },
	},
	async ({ query, limit = 5, tag, full = false }) => {
		const KEY = orKey();
		if (!KEY) {
			return { isError: true, content: [{ type: 'text', text: 'Нет OR_LLM_API_KEY — семантический поиск недоступен. Используй list_by_tag или get_post, либо добавь ключ в mcp/blog-search/.env' }] };
		}
		let pool = POSTS;
		if (tag) {
			pool = POSTS.filter((p) => (p.tags || []).some((t) => t.toLowerCase() === tag.toLowerCase()));
			if (!pool.length) {
				return { content: [{ type: 'text', text: `Нет постов с тегом "${tag}". Доступные теги: ${uniqTags().join(', ')}` }] };
			}
		}
		let qvec;
		try {
			[qvec] = await embed([query], KEY);
		} catch (e) {
			return { isError: true, content: [{ type: 'text', text: `Ошибка эмбеддинга запроса: ${e.message}` }] };
		}
		const scored = pool
			.map((p) => ({ p, score: cosine(qvec, p.vector) }))
			.sort((a, b) => b.score - a.score)
			.slice(0, limit);

		const results = [];
		for (const { p, score } of scored) {
			const body = await bodyOf(p.slug);
			results.push({
				slug: p.slug,
				title: p.title,
				url: p.url,
				tags: p.tags,
				pubDate: p.pubDate,
				score: Number(score.toFixed(4)),
				text: full ? (body ?? '') : excerpt(body ?? '', 300),
			});
		}
		const header = `🔍 «${query}»${tag ? ` · тег: ${tag}` : ''} — топ ${results.length}:`;
		const md = results.map((r, i) =>
			`### ${i + 1}. ${r.title}  _(score ${r.score})_\n` +
			`${r.url} · ${r.pubDate} · теги: ${r.tags.join(', ') || '—'}\n\n` +
			`${r.text}`
		).join('\n\n---\n\n');
		return {
			content: [{ type: 'text', text: `${header}\n\n${md}` }],
			structuredContent: { query, tag: tag ?? null, full, results },
		};
	},
);

server.registerTool(
	'list_by_tag',
	{
		title: 'Посты по тегу',
		description:
			'Возвращает посты с указанным тегом, отсортированные по дате (новые сверху). ' +
			'Не требует эмбеддингов/ключа. Если тег не передан — вернёт список всех тегов.',
		inputSchema: {
			tag: z.string().optional().describe('Тег (точное совпадение). Пусто → список всех тегов'),
			limit: z.number().int().min(1).max(100).optional().describe('Максимум постов (по умолчанию 30)'),
		},
		annotations: { readOnlyHint: true, openWorldHint: false },
	},
	async ({ tag, limit = 30 }) => {
		if (!tag) {
			const tags = uniqTags();
			return {
				content: [{ type: 'text', text: `Доступные теги (${tags.length}):\n${tags.join(', ')}` }],
				structuredContent: { tags },
			};
		}
		const matched = POSTS
			.filter((p) => (p.tags || []).some((t) => t.toLowerCase() === tag.toLowerCase()))
			.sort((a, b) => (b.pubDate || '').localeCompare(a.pubDate || ''))
			.slice(0, limit);
		if (!matched.length) {
			return { content: [{ type: 'text', text: `Нет постов с тегом "${tag}". Доступные: ${uniqTags().join(', ')}` }] };
		}
		const md = matched.map((p) => `- **${p.title}** — ${p.url} (${p.pubDate})`).join('\n');
		return {
			content: [{ type: 'text', text: `Посты с тегом «${tag}» (${matched.length}):\n\n${md}` }],
			structuredContent: { tag, count: matched.length, posts: matched.map((p) => ({ slug: p.slug, title: p.title, url: p.url, pubDate: p.pubDate, tags: p.tags })) },
		};
	},
);

server.registerTool(
	'get_post',
	{
		title: 'Полный текст поста',
		description: 'Возвращает полный markdown-текст поста по slug (как в URL /blog/{slug}/).',
		inputSchema: {
			slug: z.string().describe('slug поста, напр. "moi-put-k-kontaktnoi-improvizatsii-380"'),
		},
		annotations: { readOnlyHint: true, openWorldHint: false },
	},
	async ({ slug }) => {
		const parsed = await readPostBody(slug);
		if (!parsed) {
			return { isError: true, content: [{ type: 'text', text: `Пост "${slug}" не найден. Проверь slug через search_posts/list_by_tag.` }] };
		}
		const { fm, body } = parsed;
		const meta = `# ${fm.title || slug}\n${postUrl(slug)} · ${fm.pubDate || ''} · теги: ${(fm.tags || []).join(', ') || '—'}\n\n`;
		return {
			content: [{ type: 'text', text: meta + body }],
			structuredContent: { slug, title: fm.title || slug, url: postUrl(slug), tags: fm.tags || [], pubDate: fm.pubDate || '', body },
		};
	},
);

const transport = new StdioServerTransport();
await server.connect(transport);
console.error('[blog-search] MCP server готов (stdio)');
