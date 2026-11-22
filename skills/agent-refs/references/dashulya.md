# Дашуля — карта кода (Lancetnik/dashulya)

Снято с коммита: `44fa11e` (2026-11-09). Пути — от корня репо, основной код в `src/dashulya/`. Копия: `~/.cache/agent-refs/dashulya`.

## Что это
Telegram-ассистентка для групповых чатов и лички владельца: саркастичная персона «Бунтарка», поиск по сохранённой истории чата с кликабельными ссылками на исходные сообщения, сводки за период, веб-поиск, YouTube по субтитрам, картинки и стикеры, реакции.
- Стек: Python 3.14, aiogram 3, AG2 (`ag2[openai,mcp]`), Dishka DI, PostgreSQL + pgvector + ParadeDB (`pg_search`), `pglast`.
- Модели: только OpenAI. Ответ — `OPENAI_MODEL` (Responses API, reasoning=high), два классификатора, эмбеддинги `text-embedding-3-small` 512d, веб — Keenable MCP, расчёты — Code Interpreter.
- Запуск: `docker compose up` (postgres, migrate, agent), long polling. ~10,9k строк в `src/`, ~36,6k с тестами и эвалами. Лицензия MIT.

## Архитектура за 1 минуту
1. `main/runtime.py:16` — контейнер, память, `start_polling`; роутер — `bot/router.py:9`.
2. Middleware: `TrackGroupsMiddleware` → `CaptureMessagesMiddleware` пишет каждое сообщение в БД (`bot/middlewares/memory.py:21`, проверка `capture_enabled` :39) → `AccessMiddleware` (владелец, активность группы, бан-лист, аудитория; `bot/middlewares/access.py:163`).
3. Группа: `group_chat` (`bot/handlers/dialogue.py:49`) → `GroupAddressing.decide` (`ai/addressing.py:47`). Реплай на бота или @mention — отвечать сразу. Имя в тексте (regex `:15`) — bool-классификатор. Имени нет, но бот отвечал в последних 4 сообщениях — классификатор продолжения: молчать / текст / эмодзи-реакция.
4. Реакция ставится сразу без модели ответа (`dialogue.py:91`). Текст → `ReplyDelivery.reply` (`bot/replies.py:266`): typing, загрузка картинок, `Dialogue.reply`.
5. Контекст: `Dialogue._reply` (`ai/dialogue.py:512`). Группа — свежий `MemoryStream`: последние 20 сообщений + до 5 уровней родителей по реплаям (`select_context`, `:128`), прошлые обмены восстанавливаются по `trigger_message_id`. Личка — общий in-memory stream.
6. `agent.ask(...)` с `variables` (user_id, chat_id) и `dependencies` (`dialogue.py:586`); выход — схема `ReplyBatch`: до 3 сообщений, текст или стикер + `reply_to`.
7. `_validate_replies` (`dialogue.py:678`) оставляет `reply_to` только на ID из контекста.
8. `_deliver` (`replies.py:391`): Markdown → entities, чанки; `CaptureSentMessagesMiddleware` (`bot/middlewares/memory.py:72`) сохраняет ответ с `trigger_message_id`.
9. `IndexingWorker` (`memory/_indexing.py:15`) каждые 2 с строит эмбеддинги и BM25.

## Карта фич → где в коде
| Фича | Файлы | Как сделано |
|---|---|---|
| Агентный цикл | `ai/agents/factory.py:74`, `ai/dialogue.py:512` | AG2 `Agent.ask` со структурированным выходом, таймаут 300 с, починка «висящих» tool-call (`dialogue.py:565`) |
| Промпт и контекст | `ai/agents/factory.py:83-94`, `ai/prompts.py`, `ai/message_format.py:241` | Системный промпт из XML-блоков (persona, trust, workflow, memory). Каждое сообщение — JSON-метаданные в `<external_input>` |
| Персона, юмор | `ai/prompts.py:3-156` | Архетип Rebel, юмор по образцу Jimmy Carr / Jefferies / Louis C.K.; блоки отпора, реакции на бред, отказа от механической работы, few-shot, женский род, запрет длинного тире |
| Запись памяти | `bot/middlewares/memory.py:33,39,101`, `memory/store.py:63` | LLM не решает: пишется всё после `/start` владельца (`capture_enabled`), правки и свои ответы. Факты не извлекаются (README: не реализовано) |
| Чтение памяти | `ai/tools/memory.py:16`, `ai/tools/history.py:244`, `ai/tools/sources.py:36`, `memory/indexed_search.py:246` | Только по инициативе агента: `search_memory` (BM25 + векторы, RRF, диверсификация), `chat_history` (SQL от модели), `read_sources` (оригиналы с ответами) |
| Схема хранения | `database/migrations/0001_canonical_storage.sql:14`, `0005_paradedb.sql`, `0007_incremental_search.sql` | `messages(collection, message_id, …, revision, indexed_revision)`, кэш `embeddings vector(512)`, снапшоты ParadeDB на чат; миграции с контрольными суммами (`database/migrate.py`) |
| Компакция, саммари | `ai/prompts.py:497-514`, `ai/dialogue.py:128`, `:392` | Саммаризации нет: в группе окно, в личке выкидываются старые картинки. Сводка за период — рецепт в промпте через `chat_history` |
| Ссылки на источники | `domain/memory.py:23`, `ai/prompts.py:294-297` | `message_url_template` (`t.me/<user>/{id}` или `t.me/c/<id>/{id}`); промпт требует ссылку у каждого утверждения |
| Инструменты | `main/providers/ai.py:102-111`, `ai/tools/*`, `ai/tools/web.py:178` | Явный список; новый = функция `@tool @inject` с подробным docstring и примерами вызова; веб через MCPToolkit |
| Проактивность | нет | Только реакция на входящие; ближе всего — самостоятельные реакции `set_reaction` |
| Поведение в группах | `ai/addressing.py:47-90`, `ai/prompts.py:311-465`, `bot/middlewares/access.py:245` | Двухступенчатое решение; «из нескольких действий выбирай наименее навязчивое»; `/stop` с отменой задач (`dialogue.py:98`), `/ban`, `/settings`, скрытые `/whisper` |
| Приватность | `ai/prompts.py:575-604`, `memory/sql_history.py:470`, `main/providers/ai.py:40` | Каждый ввод помечен источником (owner, external_user, bot, web, memory); группа видит только свой чат; SQL модели под ролью NOLOGIN над TEMP VIEW; whisper не сохраняется |
| Модели, фолбэк | `ai/agents/models.py:12` | Отдельные модели для ответа и решений; фолбэка нет, `max_retries=1` |
| Медиа | `bot/images.py`, `bot/media_frames.py`, `ai/tools/history.py:143` | Картинки, стикеры, первый кадр GIF нативно; бюджет 20 МБ, кэш в RAM, `retry_image` до 3 попыток. Голоса нет |
| Телеметрия | `ai/agents/tracing.py:201`, `observability.py:154` | JSON-лог каждого вызова модели (токены, `cache_hit`, `cached_input_percent`) и инструмента; секреты вырезаются; `addressing_reason` |
| Тесты, эвалы | `tests/local`, `tests/integration`, `evals/suites/{addressing,memory,bm25}` | pytest, hypothesis, mutmut; эвал адресации — 366 кейсов; эвал памяти — AG2 Evals с LLM-судьёй; датасеты приватные |
| Самоулучшение | нет | — |
| Деплой | `docker-compose.yaml`, `Dockerfile`, `main/config.py:49`, `.env.example` | Миграции до агента, healthcheck по файлу, исходники read-only |
| Ошибки, очереди | `memory/_indexing.py:47`, `ai/agents/tracing.py:38`, `bot/replies.py:339` | Очередь индексации в БД (`revision` vs `indexed_revision`); ошибка инструмента уходит модели текстом «это не пустой результат»; пользователю заглушка |

## Сильные практики
1. **Продолжение разговора: молчать / текст / реакция** — `ai/addressing.py:76-90`, `ai/prompts.py:374-465`. Главная беда групповых ботов — назойливость; на «спасибо» бот ставит 🙏 вместо абзаца. Перенос: низко.
2. **Контрастные пары few-shot для адресации** («Саша, перезапусти Дашулю» → false, «Дашуля, попроси Сашу…» → true) — `ai/prompts.py:356-370`. Перенос: низко.
3. **Метка источника на каждом вводе** — `ai/message_format.py:27-50`, `ai/prompts.py:575-604`. `owner` определяется только по числовому ID, текст внутри конверта — данные, не инструкции. Защита от prompt injection в группе. Перенос: низко.
4. **Песочница для SQL от модели** — `memory/sql_history.py:470-505`: разбор pglast → TEMP VIEW с `security_barrier` по чату и времени → `SET LOCAL ROLE`, read-only, таймаут 10 с. Гибкие подсчёты без выхода за свой чат. Перенос: средне.
5. **Персона как поведенческие правила, а не прилагательные** — `ai/prompts.py:23-109`, включая «без повторов в follow-up» и запрет подражать прошлым мягким ответам. Перенос: низко.
6. **Ссылка на сообщение у каждого утверждения** — `domain/memory.py:23`, `prompts.py:294`. Перенос: низко.
7. **Сводка за период через SQL** — `ai/prompts.py:497-514`: интервал от времени запроса, top-N веток по числу реплаев (`row_number()`), потом чтение веток. Честнее семантического поиска по «что было за неделю». Перенос: средне.
8. **Проверка выхода модели кодом** — `ai/dialogue.py:678`, `domain/messages.py:96-117`: `reply_to` только из контекста, ≤3 сообщений, текст и стикер взаимоисключающие. Перенос: низко.
9. **Лог решений и кэша промпта** — `ai/agents/tracing.py:237-312`, `ai/addressing.py` (`reason`): видно, почему бот промолчал и сколько входа ушло в кэш. Перенос: низко.
10. **Ошибка инструмента ≠ пустой результат** — `ai/agents/tracing.py:38-64`. Перенос: низко.

## Слабые места / что не брать
- Нет извлечённой долговременной памяти о людях и решениях — только поиск по сырым сообщениям.
- История лички только в RAM (`ai/dialogue.py:54`), пропадает при рестарте; сжатия нет.
- Нет фолбэка провайдера и повторного запроса при невалидной схеме — пользователю заглушка (`dialogue.py:697`, `replies.py:349`).
- Тяжёлая инфраструктура для чат-бота (ParadeDB со снапшотами на чат, роли Postgres, mutmut).
- Рендер Markdown заимствован под Apache-2.0, а файла лицензии в репо нет — при переносе оформлять самим.
- Эвалы не воспроизвести: датасеты приватные.

## Ключевые слова для grep
`CHARACTER_PROMPT`, `GROUP_THREAD_CONTINUATION_PROMPT`, `GROUP_ADDRESSING_PROMPT`, `INPUT_TRUST_PROMPT`, `MEMORY_TOOLS_PROMPT`, `_AGENT_NAME_PATTERN`, `ContinuationAction`, `AddressingDecision`, `select_context`, `trigger_message_id`, `external_input`, `message_url_template`, `search_memory`, `chat_history`, `read_sources`, `reciprocal_rank_fusion`, `CREATE TEMP VIEW messages`, `ReplyTrace`, `_validate_replies`, `capture_enabled`
