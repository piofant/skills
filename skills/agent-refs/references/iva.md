# Ива — карта кода (smixs/iva-agent)

Снято с коммита: `c158cea` (2026-11-17). Пути — от корня репо. Копия: `~/.cache/agent-refs/iva`.

## Что это
Личный ассистент в Telegram на сервере владельца; память — Markdown-vault в отдельном git-репо (дневные логи → выжимки → карточки, CORE.md). Node ≥24 + TypeScript на харнессе `eve` (форк vercel/eve 0.51.1, вендор в `eve/`, ~200k строк — не путать со своим кодом) и Vercel AI SDK v7. Провайдеры: OpenCode Go, Ollama Cloud, OpenRouter, Codex (подписка ChatGPT, OAuth), Claude (через локальный Claude Code CLI), любой OpenAI-совместимый (`agent/lib/model-provider.ts:58`). Голос — Deepgram. Есть юзербот на Telethon (`services/telegram-userbot/`). Установка `install.sh`/`bootstrap.sh`, systemd user-юниты (`deploy/`), CLI `iva` (`bin/iva.mjs` → `scripts/cli/`). Своего кода ~100k строк (`agent/` ~36k, `scripts/` ~60k), тестов ~190k строк, 41 TLA+-спека в `specs/`. Лицензия MIT.

## Архитектура за 1 минуту
1. Bridge `scripts/poller/main.ts:312` — отдельный процесс, long-polling `getUpdates` (:406), offset хранится, на 409 — backoff и Alert.
2. `processTelegramUpdate` (:168) → `admitTelegramUpdate` (`scripts/poller/inbox.ts:208`): надёжный inbox; части сообщения склеиваются после 800 мс тишины (`scripts/lib/telegram-collect.ts:8`).
3. `drainReadyQueueHeads` (`scripts/poller/routing.ts:422`) — очередь на чат → POST в локальный eve `/eve/v1/telegram/accepted` (`agent/lib/telegram-acceptance.ts:26`) с секретом и квитанцией дедупликации.
4. `agent/channels/telegram.ts:706` → `runTelegramInbound` (`agent/lib/telegram-inbound.ts:554`): allowlist (:564), отвечать ли (`shouldDispatch` :225), транскрипция и картинки, запись реплики в `daily/` (`appendDaily`), санитайзер Gate (:515).
5. Харнесс `agent/agent.ts:47`: модель выбирается на каждом шаге (`step.started`); цикл инструментов — `eve/packages/eve/src/harness/tool-loop.ts`; промпт из `agent/instructions.md` + `agent/instructions/*` на `turn.started`.
6. `message.completed` (`agent/channels/telegram.ts:591`) → `sendThroughOutbox` (`agent/lib/outbox.ts:216`) — единственный путь наружу (редакция секретов, rich-HTML, кнопки). Хук `agent/hooks/transcript.ts` дописывает ответ в daily.
7. Ночью `scripts/memory/night.ts`: daily → карточки, выжимки, правки CORE. В 05:00 `scripts/memory/brain.ts`: граф, git push, проверка размера CORE.

## Карта фич → где в коде
| Фича | Файлы | Как сделано |
|---|---|---|
| Агентный цикл | `agent/agent.ts:47`, `eve/packages/eve/src/harness/tool-loop.ts`, `agent/lib/eve-auth.ts:23` | Цикл даёт eve; сессия — durable workflow с TTL 24 ч (`agent.ts:91`); фоновые ходы ограничены 40–80 шагами и 4 млн входных токенов |
| Промпт и контекст | `agent/instructions.md`, `agent/instructions/10-map.md`, `20-core.ts`, `25-persona.ts`, `30-owner-rules.ts`, `40-open-failures.ts`, `now.ts` | Слои с числовыми префиксами; CORE, правила владельца и открытые провалы перечитываются каждый ход; дата-время идёт user-сообщением, чтобы не ломать кэш промпта |
| Запись памяти | `agent/lib/telegram-inbound.ts:511`, `agent/hooks/transcript.ts`, `agent/lib/vault-daily.ts:48`, `scripts/memory/night.ts:970`, `agent/tools/write_card.ts:52-73`, `agent/lib/core-write.ts:60` | Днём — сырой двусторонний транскрипт. Ночью модель отдаёт JSON-предложения, файлы пишет код. В чате CORE правится только по явному «запомни», карточки — `write_card` (fact/truth/merge) |
| Чтение памяти | `agent/tools/memory_search.ts:436-485`, `:680`, `:386` | SQLite FTS5 с весами колонок (BM25), самописный русский стемминг (:233), BFS по графу ссылок (бонус 1.5/1.3/1.15), опционально эмбеддинги + RRF. Как ходить по памяти — `10-map.md` |
| Схема хранения | `vault-template/schema.json`, `vault-template/CORE.md`, `docs/memory.md`, `agent/lib/card-store.ts:252` | `daily/`, `summaries/{daily,weekly,monthly,yearly}`, `cards/{contacts,projects,decisions,ideas,notes}`; карточка = frontmatter + Compiled Truth + `## Log` + `## History` |
| Компакция | `agent/lib/compaction.ts`, `docs/adr/0028-*`, `scripts/memory/night-periods.ts` | Свёртка eve перед шагом: порог min(300k, 0.8 окна), последние ~20k токенов дословно. Иерархия выжимок памяти — `night-periods.ts` |
| Устаревание, конфликты | `agent/lib/card-store.ts:452-735`, `scripts/memory/instructions/night/card.md`, `day.md`, `memory_search.ts:676` | Вытесненная правда уходит в append-only History; CAS по hash — правка владельца побеждает (`truth_pending`); superseded/archived скрыты из поиска; конфликт — «оба с датами». «Forget» в коде не реализован |
| Инструменты, скиллы, плагины | `agent/tools/*.ts`, `agent/skills/*/SKILL.md`, `agent/skills/custom.ts`, `agent/lib/plugin-*.ts`, `scripts/lib/plugin-install.ts`, `docs/extending.md`, `docs/plugins.md` | Инструмент — файл с `defineTool`; скиллы читаются с диска каждый ход без рестарта; плагины в формате Agent Plugins, MCP через `services/mcp-proxy` |
| Проактивность | `agent/schedules/{proactive,reminders,memory-night,jobs-watchdog}.ts`, `scripts/proactive/tick.ts`, `precheck.ts`, `agent/lib/reminder-tick.ts`, `agent/tools/remind.ts`, `schedule.ts`, `goal.ts`, `agent/lib/proactive-config.ts` | Тик раз в 30 мин: источники (TG, почта, systemd) сначала проверяет код без модели, модель будится только при новом; тихие часы 23–8, отложка 15 мин при живом диалоге, ответ `QUIET`. Напоминания — секундный тик по `data/reminders.json` |
| Группы | `agent/lib/telegram-inbound.ts:198-253`, `:298-335` | Только реплай боту, `/x@bot` или точное @упоминание по границе ника; каналы и боты игнорируются; principalId включает chat id |
| Приватность | `agent/lib/telegram-allowlist.ts`, `telegram-inbound.ts:299`, `agent/skills/brief/SKILL.md:17` | Allowlist по user ID, fail-closed. Граница группа/личное есть только у `/digest` и brief |
| Модели | `agent/agent.ts:22`, `agent/lib/eve-auth.ts:68`, `agent/provider.ts:809`, `agent/lib/claude-auth-rotation.ts` | Отдельная HELPER_MODEL для фоновых задач; middleware: repeat-guard, повтор без lookaround-regex, дедлайн первого чанка 90 с. Фолбэка на другую модель нет |
| Медиа | `agent/transcribe.ts:63`, `agent/vision.ts:28`, `:310`, `agent/provider.ts:462-544`, `agent/tools/send_file.ts`, `read_file.ts` | Голос → Deepgram с keyterms → daily; картинки модели напрямую, если умеет (ADR-0012), иначе describeImage |
| Телеметрия | `agent/hooks/trace.ts`, `agent/lib/trace.ts`, `agent/hooks/usage.ts`, `agent/lib/usage.ts`, `scripts/cli/trace.ts` | Один хук на `*` → `data/trace/YYYY-MM-DD.jsonl` с редакцией секретов; usage по ходам; `iva trace` |
| Тесты, эвалы | `scripts/memory-search-eval.ts`, `scripts/fixtures/memory-eval.json`, `scripts/memory/night-*.test.ts`, `scripts/smoke/*`, `specs/*.tla`, `docs/testing.md` | Эвал памяти hit@3 по парам query→card на живом vault; property-тесты (fast-check); герметичные e2e с фейковыми Telegram и провайдером; TLA+-модели |
| Самоулучшение | `agent/skills/insight/SKILL.md:58-94`, `scripts/lib/turn-repeats.ts:223`, `agent/instructions/10-map.md` | Insight раз в день ищет повторные поправки владельца («я же просил») и повторяющиеся цепочки в trace, предлагает правило или черновик скилла кнопками, ставит только после «да» |
| Деплой | `install.sh`, `bootstrap.sh`, `scripts/setup/wizard.ts`, `scripts/cli/systemd.ts`, `deploy/`, `.env.example`, `docs/configuration.md` | Мастер настройки, systemd user-юниты с UMask 0077, `iva update` с откатом |
| Ошибки, очереди | `scripts/poller/queue.ts`, `agent/lib/run-status.ts` (+ `specs/ChatRecord.tla`), `agent/lib/error-humanizer.ts:143`, `scripts/recover-interrupted-turns.ts`, `agent/lib/repeat-guard.ts`, `night.ts:1285` | Состояние чата — машина с CAS под замком; оборванный ход — кнопка «Повторить»; turn policy queue/steer; ночь — 3 попытки в день |

## Сильные практики
1. **Ночь: модель предлагает, код пишет** — `scripts/memory/night.ts:970`, промпты `scripts/memory/instructions/night/*.md`. Четыре шага (день → карточка → связи → CORE), каждый вызов модели даёт один JSON, записи, CAS и коммиты делает код. Идемпотентно и переживает рестарт. Перенос: средне.
2. **Факт только с дословной цитатой владельца** — `scripts/memory/instructions/night/day.md:11`: `src` и `quote` обязательны, факт без цитаты отбрасывается, ответы самой Ивы источником не считаются. Дёшево режет галлюцинации и самоподкрепление памяти. Перенос: низко.
3. **Compiled Truth + append-only History** — `agent/lib/card-store.ts:452`, `agent/tools/write_card.ts:52`. Текущая правда отдельно от истории, правка владельца выигрывает. Перенос: средне.
4. **CORE с жёстким лимитом** — `agent/instructions/20-core.ts`, `agent/lib/core-cap.ts:3`, `core-clamp.ts`: 3600 знаков, перечитывается каждый ход, ночь меняет не больше четверти строк. Перенос: низко.
5. **Retrieval без внешних зависимостей** — `agent/tools/memory_search.ts:436-485`: `node:sqlite` FTS5 + граф ссылок + RRF; в промпте — «выжимки раньше сырого». Перенос: низко.
6. **Проактивность «сначала код, потом модель»** — `scripts/proactive/tick.ts`, `precheck.ts`: тихие часы, отложка при живом диалоге, `QUIET`, дневной лимит токенов. Дёшево и не спамит. Перенос: средне.
7. **Строгий триггер ответа в группе** — `agent/lib/telegram-inbound.ts:216`; чужой голос в группе не отправляется в Deepgram (:241). Перенос: низко.
8. **Правила владельца — живой файл** — `agent/instructions/30-owner-rules.ts`: `rules.md` перечитывается каждый ход, лимит 4000 знаков, длинное выносится в скилл. Перенос: низко.
9. **Bridge отдельно от агента + надёжная очередь** — `scripts/poller/main.ts:312`, `inbox.ts`: приём живёт, даже когда агент завис; дедупликация по квитанции. Перенос: средне.
10. **Единый trace-хук** — `agent/hooks/trace.ts`: jsonl по дням с редакцией секретов; на нём же поиск повторов для Insight. Перенос: низко.

## Слабые места / что не брать
- Огромная сложность: ~100k строк своего кода, 190k тестов, CHANGELOG 341 КБ, собственная копия eve. Брать идеи, не код.
- Безопасность принята как риск: Gate fail-open, `bash` наследует все ключи из env (`docs/adr/0005-lethal-trifecta-deterministic-separation.md`).
- Слабая граница группа/личное: CORE подаётся в любой ход (`20-core.ts`), групповые реплики пишутся в тот же личный `daily/`.
- Нет фолбэка модели: сбой провайдера роняет ночь (`docs/memory.md`).
- «Forget» и HITL-подтверждение инструментов не реализованы (`docs/tech-debt.md` §1); `repeat-guard.ts` — временная заплатка; стемминг самописный, опечатки не находятся.

## Ключевые слова для grep
`runTelegramInbound`, `shouldDispatch`, `mentionsBot`, `allowedTelegramUsers`, `appendDaily`, `sendThroughOutbox`, `coreMarkdown`, `CORE_CAP`, `OWNER_RULES_CAP`, `searchMemory`, `bm25(d,`, `rrfFuse`, `processDay`, `truth_pending`, `## History`, `runProactiveTick`, `isQuietHour`, `LIVE_DIALOG_MINUTES`, `usesHelperModel`, `compactionThreshold`, `TURN_MAX_STEPS`, `QUIET`
