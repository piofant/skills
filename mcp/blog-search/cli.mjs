#!/usr/bin/env node
/**
 * cli.mjs — CLI для поиска по блогу. Работает БЕЗ node_modules: только
 * встроенные модули Node + fetch. Это осознанно: MCP-сервер зависит от
 * @modelcontextprotocol/sdk и падает, если node_modules снесли (так и
 * случилось 01.08.2026). CLI в такой ситуации продолжает работать.
 *
 * Субкоманды:
 *   check                     — свежий ли индекс (без запросов к API, ~100мс)
 *   sync                      — досбор индекса (инкрементально, только новое)
 *   search <запрос> [--tag T] [--limit N] [--full] [--min S]
 *   similar <slug> [--limit N]  — похожие на пост (вектор берётся из индекса,
 *                                 API не дёргается вообще)
 *   tags                      — все теги с количеством постов
 *   tag <имя> [--limit N] [--coherence]
 *                             — посты тега; --coherence считает разброс
 *                               внутри тега и показывает выбросы
 *   get <slug> [--meta]       — полный markdown поста
 *
 * Флаг --json у любой команды → машиночитаемый вывод (для скилла).
 */
import { readFile } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import {
	loadEnv, orKey, embed, cosine, excerpt,
	loadPosts, readPostBody, INDEX_PATH, HERE,
} from './lib.mjs';

loadEnv();

const argv = process.argv.slice(2);
const cmd = argv[0] || 'help';
const JSON_OUT = argv.includes('--json');

/** Достаёт значение флага: --limit 10 → 10. */
function flag(name, fallback = null) {
	const i = argv.indexOf(`--${name}`);
	return i !== -1 && argv[i + 1] && !argv[i + 1].startsWith('--') ? argv[i + 1] : fallback;
}
/** Позиционные аргументы (без субкоманды и без флагов с их значениями). */
function positional() {
	const out = [];
	for (let i = 1; i < argv.length; i++) {
		if (argv[i].startsWith('--')) {
			const takesValue = argv[i + 1] && !argv[i + 1].startsWith('--');
			const boolFlags = ['json', 'full', 'meta', 'coherence'];
			if (takesValue && !boolFlags.includes(argv[i].slice(2))) i++;
			continue;
		}
		out.push(argv[i]);
	}
	return out;
}

function die(msg, code = 1) {
	if (JSON_OUT) console.log(JSON.stringify({ ok: false, error: msg }));
	else console.error(`✗ ${msg}`);
	process.exit(code);
}

async function loadIndex() {
	if (!existsSync(INDEX_PATH)) die('индекса нет — запусти: node cli.mjs sync');
	const idx = JSON.parse(await readFile(INDEX_PATH, 'utf8'));
	return idx.posts || [];
}

/* === check: расходится ли индекс с постами ===
   Сравниваем по hash, не по количеству: пост мог быть отредактирован без
   изменения их числа. Дисковое чтение 181 файла ≈ 100мс, API не трогаем. */
async function checkFreshness() {
	const posts = await loadPosts();
	const indexed = existsSync(INDEX_PATH) ? (await loadIndex()) : [];
	const byslug = new Map(indexed.map((p) => [p.slug, p]));
	const added = [], changed = [];
	for (const p of posts) {
		const old = byslug.get(p.slug);
		if (!old) added.push(p.slug);
		else if (old.hash !== p.hash) changed.push(p.slug);
	}
	const removed = indexed.filter((p) => !posts.some((x) => x.slug === p.slug)).map((p) => p.slug);
	return { posts: posts.length, indexed: indexed.length, added, changed, removed,
	         stale: added.length + changed.length + removed.length > 0 };
}

/* === sync: досбор через build-index.mjs (он уже умеет инкрементально) === */
function runSync() {
	try {
		const out = execFileSync('node', ['build-index.mjs'], { cwd: HERE, encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] });
		return out.trim();
	} catch (e) {
		return `sync failed: ${(e.stderr || e.message || '').toString().slice(0, 400)}`;
	}
}

/** Гарантирует свежий индекс перед поиском. Возвращает строку-примечание. */
async function ensureFresh() {
	const st = await checkFreshness();
	if (!st.stale) return null;
	const n = st.added.length + st.changed.length + st.removed.length;
	runSync();
	return `индекс обновлён: +${st.added.length} новых, ~${st.changed.length} изменённых, -${st.removed.length} удалённых (${n} всего)`;
}

function fmtPost(p, score = null, { full = false } = {}) {
	const id = p.tgMessageId || (p.slug.match(/-(\d+)$/)?.[1] ?? '?');
	const s = score !== null ? `${score.toFixed(3)}  ` : '';
	let out = `[${String(id).padStart(3)}] ${s}${p.title}\n`;
	out += `      ${p.pubDate || '—'} · теги: ${(p.tags || []).join(', ') || '—'}\n`;
	out += `      ${p.url}\n`;
	if (full && p.excerpt) out += `      ${p.excerpt}\n`;
	return out;
}

// ─────────────────────────────────────────────────────────────────────
const pos = positional();

switch (cmd) {
	case 'check': {
		const st = await checkFreshness();
		if (JSON_OUT) { console.log(JSON.stringify(st, null, 2)); break; }
		if (!st.stale) console.log(`✓ индекс свежий — ${st.indexed} постов`);
		else {
			console.log(`⚠ индекс отстал: в блоге ${st.posts}, в индексе ${st.indexed}`);
			if (st.added.length) console.log(`  новых: ${st.added.length} — ${st.added.slice(0, 5).join(', ')}${st.added.length > 5 ? '…' : ''}`);
			if (st.changed.length) console.log(`  изменённых: ${st.changed.length} — ${st.changed.slice(0, 5).join(', ')}${st.changed.length > 5 ? '…' : ''}`);
			if (st.removed.length) console.log(`  удалённых: ${st.removed.length}`);
			console.log(`  чинится: node cli.mjs sync   (~2с)`);
		}
		break;
	}

	case 'sync': {
		const before = await checkFreshness();
		const out = runSync();
		if (JSON_OUT) console.log(JSON.stringify({ ok: !out.includes('failed'), before, log: out }, null, 2));
		else console.log(out || '✓ синхронизировано');
		break;
	}

	case 'search': {
		const query = pos[0];
		if (!query) die('нужен запрос: node cli.mjs search "текст"');
		const key = orKey();
		if (!key) die('нет OR_LLM_API_KEY в .env');

		const note = await ensureFresh();
		const limit = Number(flag('limit', 15));
		const tag = flag('tag');
		const minScore = Number(flag('min', 0));
		const full = argv.includes('--full');

		let posts = await loadIndex();
		const total = posts.length;
		if (tag) posts = posts.filter((p) => (p.tags || []).some((t) => t.toLowerCase() === tag.toLowerCase()));
		if (!posts.length) die(`нет постов${tag ? ` с тегом «${tag}»` : ''}`);

		const [qvec] = await embed([query], key);
		let scored = posts
			.map((p) => ({ p, score: cosine(qvec, p.vector) }))
			.sort((a, b) => b.score - a.score)
			.filter((x) => x.score >= minScore)
			.slice(0, limit);

		if (full) {
			for (const x of scored) {
				const r = await readPostBody(x.p.slug);
				x.p = { ...x.p, excerpt: r ? excerpt(r.body, 400) : '' };
			}
		}

		if (JSON_OUT) {
			console.log(JSON.stringify({
				ok: true, query, tag, note, total, found: scored.length,
				results: scored.map(({ p, score }) => ({
					slug: p.slug, title: p.title, score: Number(score.toFixed(4)),
					tags: p.tags, pubDate: p.pubDate, url: p.url,
					tgMessageId: p.tgMessageId, excerpt: p.excerpt,
				})),
			}, null, 2));
			break;
		}
		if (note) console.log(`ℹ ${note}`);
		console.log(`\n🔍 «${query}»${tag ? ` · тег:${tag}` : ''} — топ ${scored.length} из ${posts.length}\n`);
		for (const { p, score } of scored) process.stdout.write(fmtPost(p, score, { full }));
		break;
	}

	case 'similar': {
		const slug = pos[0];
		if (!slug) die('нужен slug: node cli.mjs similar <slug>');
		const note = await ensureFresh();
		const posts = await loadIndex();
		const target = posts.find((p) => p.slug === slug || p.slug.includes(slug));
		if (!target) die(`пост «${slug}» не найден в индексе`);
		const limit = Number(flag('limit', 10));

		/* Вектор берём из индекса — эмбеддинг не пересчитываем, API не трогаем. */
		const scored = posts
			.filter((p) => p.slug !== target.slug)
			.map((p) => ({ p, score: cosine(target.vector, p.vector) }))
			.sort((a, b) => b.score - a.score)
			.slice(0, limit);

		if (JSON_OUT) {
			console.log(JSON.stringify({
				ok: true, note,
				target: { slug: target.slug, title: target.title, tags: target.tags, url: target.url },
				results: scored.map(({ p, score }) => ({
					slug: p.slug, title: p.title, score: Number(score.toFixed(4)),
					tags: p.tags, pubDate: p.pubDate, url: p.url,
				})),
			}, null, 2));
			break;
		}
		if (note) console.log(`ℹ ${note}`);
		console.log(`\n🔗 похожие на «${target.title}»\n`);
		for (const { p, score } of scored) process.stdout.write(fmtPost(p, score));
		break;
	}

	case 'tags': {
		const posts = await loadIndex();
		const counts = new Map();
		for (const p of posts) for (const t of p.tags || []) counts.set(t, (counts.get(t) || 0) + 1);
		const sorted = [...counts.entries()].sort((a, b) => b[1] - a[1]);
		if (JSON_OUT) {
			console.log(JSON.stringify({ ok: true, total: sorted.length,
				tags: sorted.map(([tag, count]) => ({ tag, count })) }, null, 2));
			break;
		}
		console.log(`\n🏷  ${sorted.length} тегов на ${posts.length} постах\n`);
		for (const [tag, count] of sorted) console.log(`  ${String(count).padStart(3)}  ${tag}`);
		break;
	}

	case 'tag': {
		const name = pos[0];
		if (!name) die('нужен тег: node cli.mjs tag <имя>');
		const posts = await loadIndex();
		const inTag = posts.filter((p) => (p.tags || []).some((t) => t.toLowerCase() === name.toLowerCase()));
		if (!inTag.length) die(`тег «${name}» пуст или не существует`);
		const limit = Number(flag('limit', 50));
		const byDate = [...inTag].sort((a, b) => (b.pubDate || '').localeCompare(a.pubDate || '')).slice(0, limit);

		/* --coherence: насколько посты тега похожи между собой. Считаем центроид
		   векторов тега и cosine каждого поста к нему. Низкий скор = пост
		   тематически выпадает → кандидат на снятие тега. */
		let coherence = null;
		if (argv.includes('--coherence')) {
			const dims = inTag[0].vector.length;
			const centroid = new Array(dims).fill(0);
			for (const p of inTag) for (let i = 0; i < dims; i++) centroid[i] += p.vector[i] / inTag.length;
			const scored = inTag.map((p) => ({ p, score: cosine(centroid, p.vector) })).sort((a, b) => a.score - b.score);
			const avg = scored.reduce((s, x) => s + x.score, 0) / scored.length;
			coherence = { avg, outliers: scored.slice(0, 5) };
		}

		if (JSON_OUT) {
			console.log(JSON.stringify({
				ok: true, tag: name, count: inTag.length,
				coherence: coherence && { avg: Number(coherence.avg.toFixed(4)),
					outliers: coherence.outliers.map(({ p, score }) => ({ slug: p.slug, title: p.title, score: Number(score.toFixed(4)), tags: p.tags })) },
				posts: byDate.map((p) => ({ slug: p.slug, title: p.title, pubDate: p.pubDate, tags: p.tags, url: p.url })),
			}, null, 2));
			break;
		}
		console.log(`\n🏷  «${name}» — ${inTag.length} постов\n`);
		for (const p of byDate) process.stdout.write(fmtPost(p));
		if (coherence) {
			console.log(`\n📐 связность тега: ${coherence.avg.toFixed(3)} (1.0 = все посты об одном)`);
			console.log(`   дальше всех от темы тега:`);
			for (const { p, score } of coherence.outliers) console.log(`   ${score.toFixed(3)}  ${p.title}`);
		}
		break;
	}

	case 'get': {
		const slug = pos[0];
		if (!slug) die('нужен slug: node cli.mjs get <slug>');
		const r = await readPostBody(slug);
		if (!r) die(`пост «${slug}» не найден в src/content/blog/`);
		if (JSON_OUT) { console.log(JSON.stringify({ ok: true, slug, ...r.fm, body: r.body }, null, 2)); break; }
		if (argv.includes('--meta')) console.log(JSON.stringify(r.fm, null, 2) + '\n---\n');
		console.log(r.body);
		break;
	}

	default:
		console.log(`blog-search CLI — поиск по постам pioblog (без зависимостей)

  check                    свежий ли индекс (быстро, без API)
  sync                     досбор индекса (инкрементально)
  search <запрос>          семантический поиск
      --tag T --limit N --full --min 0.3
  similar <slug>           похожие посты (без обращения к API)
  tags                     все теги с количеством
  tag <имя> [--coherence]  посты тега; связность и выбросы
  get <slug> [--meta]      полный markdown поста

  --json                   машиночитаемый вывод (любая команда)`);
}
