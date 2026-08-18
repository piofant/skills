# blog-search MCP

Локальный MCP-сервер для семантического + тег-поиска по постам блога
(`src/content/blog/*.md`). Даёт Claude инструменты искать по смыслу,
фильтровать по тегам и читать полные тексты постов.

## Tools

| Tool | Что делает |
|---|---|
| `search_posts(query, limit?, tag?, full?)` | Семантический поиск: эмбеддит запрос → cosine-sim по индексу → топ-K постов. `tag` — фильтр. `full=true` → полный текст, иначе excerpt. |
| `list_by_tag(tag?, limit?)` | Посты с тегом (по дате). Без `tag` → список всех тегов. Без эмбеддингов. |
| `get_post(slug)` | Полный markdown поста по slug. |

## Setup

```bash
cd mcp/blog-search
npm install

# ключ OpenRouter (для эмбеддингов) — в .env (gitignored):
echo 'OR_LLM_API_KEY=sk-or-...' > .env

# построить индекс эмбеддингов (~7s, ~$0.004):
node build-index.mjs            # инкрементально (только изменённые посты)
node build-index.mjs --force    # пересчитать всё
```

`index.json` (~5 MB) и `.env` — gitignored, генерятся/хранятся локально.

## Подключить к Claude Code

```bash
claude mcp add blog-search -- node <путь-до-репо>/mcp/blog-search/server.mjs
```

Затем в Claude: «найди мои посты про X», «что я писал про автостоп»,
«дай полный текст поста про випассану».

## Как обновлять индекс

После новых постов (sync-telegram добавил .md) — перезапусти
`node build-index.mjs`. Инкрементально: эмбеддит только новые/изменённые,
переиспользует старые вектора по contentHash. Почти бесплатно.

## Архитектура

- `lib.mjs` — парсинг постов, эмбеддинги (OpenRouter `text-embedding-3-small`,
  1536 dims), cosine, excerpt.
- `build-index.mjs` — строит `index.json` `{slug, title, tags, url, hash, vector}`.
- `server.mjs` — stdio MCP, грузит индекс, на `search_posts` эмбеддит запрос
  и считает similarity локально. Тексты постов читаются из `.md` на лету
  (всегда свежие, индекс не хранит тела).

Draft-посты (`draft: true`) в индекс не попадают.
