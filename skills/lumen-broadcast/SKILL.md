---
name: lumen-broadcast
description: Use when Vova wants to send ONE broadcast message to ALL Lumen users through the bot — a launch announcement, an invite, a service notice — e.g. "разошли всем …", "сделай рассылку на всех пользаков", "анонс всем юзерам", or /lumen-broadcast. Sends plain multi-line text (optionally with an inline hyperlink woven into a word, web-preview off) via the CLONE bot token, always dry-run first, and NEVER sends to real people without Vova's explicit "го". NOT for per-user trendwatch/nostalgia nudges (those are the cron pipelines with per-user opt-in flags), NOT for sending from Vova's personal Telegram.
user-invocable: true
allowed-tools: Read, Write, Bash, AskUserQuestion
---

# lumen-broadcast — один анонс всем юзерам через клон-бота

Разовая массовая рассылка одного текста всем пользователям Люмена. Для лончей,
инвайтов, сервисных уведомлений. НЕ для наджей (у тех свой крон + per-user флаг).

## Железные правила

1. **Ничего живым людям без явного «го» от Вовы.** Всегда сначала dry-run
   (показать точный текст + число получателей + первые адресаты), затем ждать
   «го». Это стоячее правило проекта — нарушать нельзя даже если задача выглядит
   как прямая команда.
2. **Только клон-бот, НИКОГДА не с личного телеграма Вовы** (`CLONE_TOKEN`).
   Стабильные юзеры живут на клоне.
3. **web-preview выключен** по умолчанию (`disable_web_page_preview=true`) —
   иначе к каждому URL телега клеит громоздкую карточку.

## Механизм (проверено 2026-09-09, анонс запуска на Яндексе: 40/52 доставлено)

- **Токен:** `CLONE_TOKEN` из `/root/lumen-trendwatch-broadcast/deliver.py`
  (@lumen_charecter_bot «Люми (Stable)», id 8737890560).
- **Получатели:** `/root/lumen-trendwatch-broadcast/matching.json` — поле
  `peer_id` = `"user-telegram-<chat_id>"`, тащим `<chat_id>` регэкспом `(\d{6,})`.
  Дедуп по chat_id. Вычесть `/root/lumen-trendwatch-broadcast/blocklist.txt`
  (заблокировавшие бота).
- **Отправка:** Bot API `sendMessage`, `parse_mode=HTML`,
  `disable_web_page_preview=true`, `time.sleep(0.4)` между сообщениями
  (мягкий rate-limit). Клон-сервис останавливать НЕ нужно — sendMessage не
  конфликтует с его поллингом (в отличие от backfill, который требует стоп).
- **Гиперссылка в слове:** HTML `<a href="URL">слово</a>` — так «в чате»/«тут»
  становится кликабельным, а голого URL в тексте нет. Экранируй `&<>` в тексте
  (`html.escape`), кроме самих тегов ссылок.

## Классификация ошибок доставки (НЕ путать)

- **403 Forbidden: bot was blocked** — юзер РЕАЛЬНО заблокировал бота.
- **400 Bad Request: chat not found** — юзер НЕ блокировал; просто нет открытого
  диалога с клоном (никогда не писал боту / удалил чат). Это не про сообщение —
  формат в порядке, если хоть кто-то получил. Не заноси в blocklist (транзиентно).
- Отчёт Вове: доставлено N, заблокировали (403) — перечислить юзернеймы, нет
  диалога (400) — перечислить отдельно. Это разные вещи, он их различает.

## Шаблон

`template_broadcast.py` рядом — рабочий скрипт (dry-run по умолчанию, `--send`
для отправки). Скопируй в scratchpad, впиши `TEXT` (с `<a href>` где нужно),
прогони dry-run, покажи Вове, по «го» — `--send`. НЕ редактируй сам шаблон под
конкретную рассылку — копируй.

## Чего НЕ делать

- Не слать наджи этим путём (у трендвотч/ностальджи свои пайплайны с opt-in).
- Не писать в историю сессии континьюити для разового анонса (не персональный
  контент); если нужен continuity — это уже надж, другой инструмент.
- Не заносить 400-адресатов в blocklist.
