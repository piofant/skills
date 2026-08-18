---
name: report-styling
description: Оформление аналитических MD-отчётов (бенчмарки, ревью, исследования) в McKinsey-стиле — активные заголовки, matplotlib-чарты вместо таблиц где возможно, storytelling structure.
metadata: '{"nanobot": {"always": false}}'
---

# Report Styling

Скилл для написания **читаемых** аналитических отчётов: бенчмарков моделей, ревью архитектуры, A/B-тестов, прогона голден-сетов и т.п.

Главные принципы родились из работы над `workspace/docs/evals/2026-04-30-microbench/PHASE3-REPORT.md` — она получилась лучше предыдущих благодаря явным правилам ниже.

---

## Принцип 1 — McKinsey active headlines

**Заголовок должен сам по себе нести вывод.** Читатель пробежал по оглавлению — и уже знает основной message без чтения текста.

❌ Плохо (топик в заголовке):
- «Сравнение моделей»
- «Анализ результатов»
- «Что мы нашли»
- «Обзор латентности»

✅ Хорошо (вывод в заголовке):
- «Преемник за ту же цену даёт +9% качества и –36% латентности»
- «Все Yandex модели не вызывают tools на длинном промпте»
- «Только GPT-5 mini проходит все Trabun-фокусы — но она slow»
- «pathologization-traps — 6/6 fails, единственный системный provал»

**Тест:** прочитай ТОЛЬКО заголовки от h1 до последнего h2. Если по ним можно пересказать главные выводы — заголовки активные. Если нужно лезть в текст — это пассивные заголовки топика.

### Шаблон активных заголовков

- `<X> делает <Y> — <конкретная причина>`
- `<Метрика A> vs <Метрика B>: <победитель>`
- `Только <X> справляется с <Y> — но <минус>`
- `<N>% случаев <как-то> — это <уровень проблемы>`

---

## Принцип 2 — визуал > таблица где возможно

Таблица хороша для **точных значений**. Чарт хорош для **паттернов и сравнений**.

**Таблица уместна:**
- Цифры важно прочитать точно (price/1M, latency p50).
- 3-5 категорий, 3-5 столбцов — компактно.
- Список действий с дедлайнами.

**Чарт уместен:**
- Сравнение 5+ моделей / категорий по одной метрике.
- Распределения (histogram).
- Pareto frontier / quadrant plot.
- Heatmap по 2 осям.
- Timeline / progression.

**Никогда не делай чарт ради чарта.** Если 3 значения с подписями — это таблица, не bar plot.

### Какие чарты подходят под какие задачи

| Задача | Чарт | Пример |
|---|---|---|
| Сравнить N моделей по метрике | horizontal bar (отсортированный) | `01-quality-vs-cost.png` |
| Trade-off по 2 осям | scatter с подписями | `02-quality-vs-latency.png` |
| Распределение score | histogram с цветными зонами | `10-score-distribution.png` |
| Pass/fail по категориям | horizontal bar с цветной шкалой | `13-categories-passrate.png` |
| Состав сета | donut (только если ≤15 кусков) | `08-goldenset-composition.png` |
| Per-item × per-dim | heatmap | `04-trabun-heatmap.png` |
| Изменение метрики во времени | line с p50/p95 | `11-latency-timeline.png` |
| Pass/partial/fail по 3 категориям | grouped bars в subplots | `12-trabun-acceptance.png` |

---

## Принцип 3 — story arc

Хороший отчёт читается как история, не как энциклопедия. Стандартная структура:

1. **TL;DR (1-2 параграфа)** — главный вывод + базовые цифры.
2. **Setup** — что измеряли, какая методология, кратко.
3. **Headline finding 1** (active title) — главное наблюдение + чарт.
4. **Headline finding 2** — следующее по важности.
5. **Headline finding 3** — и т.д. до 5-6.
6. **Где локально косячит** — детали fails (можно таблицей).
7. **Что чинить** — priority backlog (severity / approach / effort).
8. **Финальный вывод** — go/no-go decision + actions.
9. **Артефакты** — ссылки на raw-data, charts, code.

Между findings давай связку: «после X логично спросить про Y» / «из этого следует, что…».

---

## Принцип 4 — каждый чарт должен иметь caption

Под чартом всегда:

```markdown
![Title](path/to/chart.png)

**Чтение:** что по X-оси, что по Y-оси, что значат цвета. 1-2 предложения.

**Что бросается в глаза:** 2-3 буллета с конкретикой.
```

Без caption'а читатель тратит 10-15 секунд на расшифровку. Caption убирает эту задержку.

---

## Принцип 5 — цветовая палитра

Используй **canonical palette** для consistency между чартами одного отчёта:

```python
PALETTE = {
    'win':       '#2ca02c',   # winner / pass / good
    'baseline':  '#1f77b4',   # current / control
    'warn':      '#ff7f0e',   # borderline / partial
    'fail':      '#d62728',   # fail / regression
    'muted':     '#7f7f7f',   # not interesting / N/A
    'highlight': '#ffd700',   # callout
}
```

**Rules:**
- Зелёный = победа/pass только. Не используй зелёный «просто потому что красиво».
- Красный = провал/регрессия. Не для контроля или нейтрального.
- Серый = N/A / не интересно.
- Оранжевый = borderline / partial. Yellow в RGB читается плохо на проекторе.

Для категориальных серий (10+ цветов) — `plt.cm.tab20`, не `tab10`.

---

## Принцип 6 — matplotlib hygiene

Вся matplotlib-конфигурация в начале скрипта:

```python
import matplotlib
matplotlib.use('Agg')  # no GUI dependency
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

plt.rcParams.update({
    'font.size': 11,
    'axes.titleweight': 'bold',
    'axes.titlesize': 14,
    'axes.spines.top': False,    # убрать верхнюю рамку
    'axes.spines.right': False,  # убрать правую рамку
    'figure.facecolor': 'white', # белый фон, не прозрачный
})
```

При сохранении:
```python
plt.tight_layout()
plt.savefig('chart.png', dpi=120, bbox_inches='tight')
plt.close()  # ВСЕГДА close, иначе memory leak в long-running scripts
```

`dpi=120` — компромисс между качеством и размером (чарт ~100KB). Для печати — 300.

---

## Принцип 7 — никогда не врать с осями

- **Y-axis для bar charts** — должен начинаться с 0, иначе разница преувеличивается.
- **Pass-rate** — всегда в 0–100% scale, не 60–100% «чтобы лучше видно».
- **Cost / latency** — log scale если разброс ≥ 1 порядок (например $0.10 vs $13.33).
- **Annotate exact values** — особенно когда bars близки. Не заставляй читателя гадать «4.46 или 4.62».

---

## Принцип 8 — annotate findings прямо на чарте

Если на чарте есть **ключевая точка** (победитель, outlier, anomaly) — стрелка + bbox с подписью прямо на графике.

```python
ax.annotate(
    'preview-Lite — лидер\nпо качеству + цене',
    xy=(0.10, 4.62),
    xytext=(0.30, 4.30),
    arrowprops=dict(arrowstyle='->', color='green', lw=2),
    fontsize=11, color='darkgreen', fontweight='bold',
    bbox=dict(boxstyle='round', facecolor='lightyellow', edgecolor='green'),
)
```

Не больше **1-2 annotations** на чарт — иначе шум.

---

## Принцип 9 — заголовки чартов — тоже active

Заголовок чарта — мини-McKinsey. Он повторяет (короче) активный заголовок секции в MD.

❌ «Quality vs Cost»
✅ «preview-Lite доминирует Парето-фронт за $0.10/1M»

---

## Quickstart — копируешь и адаптируешь

```python
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

PALETTE = {
    'win': '#2ca02c', 'baseline': '#1f77b4', 'warn': '#ff7f0e',
    'fail': '#d62728', 'muted': '#7f7f7f', 'highlight': '#ffd700',
}

plt.rcParams.update({
    'font.size': 11, 'axes.titleweight': 'bold', 'axes.titlesize': 14,
    'axes.spines.top': False, 'axes.spines.right': False,
    'figure.facecolor': 'white',
})

# YOUR DATA HERE
data = json.load(open('your-results.json'))

# YOUR CHART HERE — see templates/ for examples
fig, ax = plt.subplots(figsize=(13, 7))
# ... ax.bar(...) / ax.scatter(...) / etc.

# Always:
ax.set_title('<active headline that conveys the conclusion>', pad=15)
ax.set_xlabel('<axis label> (<unit>)', fontsize=12)
ax.set_ylabel('<axis label> (<unit>)', fontsize=12)
ax.legend(loc='lower right')

# Annotate key finding
ax.annotate('<key insight>',
    xy=(<x>, <y>), xytext=(<x_offset>, <y_offset>),
    arrowprops=dict(arrowstyle='->', color='green', lw=2),
    fontsize=11, fontweight='bold',
    bbox=dict(boxstyle='round', facecolor='lightyellow', edgecolor='green'))

plt.tight_layout()
plt.savefig('chart.png', dpi=120, bbox_inches='tight')
plt.close()
```

---

## MD-структура отчёта (template)

```markdown
# <Active title — main finding>

**Дата:** YYYY-MM-DD | **Что прогоняли:** <concise> | **Откуда данные:** <link>

---

## TL;DR — <one-line headline>

<1-2 параграфа: ключевые цифры + рекомендация + одна ссылка>

---

## <Active headline finding 1>

![Chart 1](charts/01-name.png)

**Чтение:** <1-2 предложения about chart axes/colours>

**Что бросается в глаза:**
- <buллет 1>
- <buллет 2>
- <buллет 3>

**Вывод:** <одно предложение что это значит для решения>

---

## <Active headline finding 2>

[same structure]

---

## Что чинить — priority backlog

| # | Issue | Severity | Approach | Effort |
|---|---|---|---|---|
| 1 | <X> | HIGH/MED/LOW | <как> | <время> |

---

## Финальный вывод

<3-5 ✅ buллетов и ⚠️ buллетов>
**Действия:** <numbered list>

---

## Артефакты

- [raw data](path)
- [implementation commit](url)
- charts/
```

---

## Принцип 10 — collapsible details (Notion-style)

Хороший отчёт — это **сначала картинка, потом цифры под катом**. Для деталей которые нужны не всем (полные таблицы, методология, edge-cases) — используй стандартный GitHub markdown `<details>/<summary>`:

```markdown
**Главное:** preview-Lite дешевле всех + лучшее mean.

![Cost chart](charts/cost.png)

<details>
<summary><strong>Подробная таблица — премии и Δ качества</strong></summary>

| Model | Cost | Mean | Premium |
|---|---|---|---|
| ... | ... | ... | ... |

</details>
```

Рендерится в GitHub автоматически: видно только summary-строку, кликом раскрывается контент. Тот же паттерн что в Notion-toggles. Работает в `*.md` файлах в любом GitHub-репо.

### Когда collapse'ить

- ✅ Полные таблицы из 10+ строк — после чарта.
- ✅ «Почему так» — гипотезы и обоснование вывода.
- ✅ Edge-case детали — для тех кому нужно.
- ✅ Бэк-стори / методологические нюансы — не на main path.

### Когда НЕ collapse'ить

- ❌ Главные цифры (TL;DR, headline-вывод). Они должны быть видны сразу.
- ❌ Action items / что чинить. Должно бить в глаза при беглом чтении.
- ❌ Чарты и их 1-строчные caption'ы. Картинка — это main flow.

### Шаблон summary-строки

`<strong>` для bold (без него выглядит бледно), 1 короткая фраза или вопрос:

- `<strong>Подробная таблица — премии и Δ качества</strong>`
- `<strong>Почему так — гипотеза про tuning</strong>`
- `<strong>Полный список 24 dim'ов с расшифровками</strong>`
- `<strong>Что было до этого фикса</strong>`

---

## Принцип 11 — slide-style чарты для headline-выводов

Для **главных** чартов (которые читатель должен заметить) — режим **«как слайд для презентации»**:

```python
setup_style(slide=True)  # из chart_helpers.py
```

Что это меняет:
- `font.size`: 11 → 14
- `axes.titlesize`: 14 → 18
- `lines.linewidth`: 1.5 → 2.5
- Жирные подписи на bars (`fontweight='bold'`).
- Бóльшие figsize: `(15, 8)` вместо `(13, 6)`.

Как тестировать: открой PNG на телефоне с расстояния руки. Видно заголовок? Видно цифры на bars? Если нет — шрифт мелкий.

### Где slide-style уместен

- Headline-чарты в начале отчёта.
- Чарты которые попадут в Notion-карточку или сообщение.
- Финальные «выбираем X потому что» визуалы.

### Где НЕ уместен

- Heatmap (24 dim × 16 моделей) — там нужен density, не размах.
- Detailed timeline (130 точек) — slide-style сделает их толстыми и слипшимися.
- Технические charts в appendix-collapse секции.

Compromise: можно делать **и slide, и compact версии** одного чарта. Slide — в main flow, compact — в `<details>` с raw данными.

---

## Анти-паттерны — что НЕ делай

❌ **«Wall of taблиц».** 5+ таблиц подряд = читатель теряется. Если есть бот для конвертации — лучше 1 чарт.
❌ **Pie charts с >7 кусками.** Eyes can't compare angles. Используй donut (≤15) или horizontal bar.
❌ **3D charts.** Никогда. 2D всегда читаемее.
❌ **Default matplotlib title fonts.** Без `axes.titleweight='bold'` и `titlesize=14` заголовок «теряется».
❌ **«Заговор всеми цветами».** Радужная палитра — только если категорий >7. Для 2-5 категорий — `[win, fail, baseline]` достаточно.
❌ **Чарт без axis labels.** Каждый ax.set_xlabel/ylabel обязателен.
❌ **Метрика без unit.** Не «Latency 1.4», а «Latency 1.4 sec».
❌ **«Мы нашли что …»** — слабая формулировка. Лучше прямо «X быстрее Y на 36%».
❌ **Скрытие fail-cases в подвале.** Если есть провал — он в первой трети, не в самом конце.

---

## Когда применять скилл

- Бенчмарки моделей (cost / quality / latency).
- Phase-отчёты по eval'у.
- A/B результаты.
- Code review summary (e.g. полное review большого PR).
- Architecture decision records (ADR) — но там скорее структура «context → options → decision → consequences», не sales pitch.
- Update reports («что сделали за неделю»).

**Не применять:**
- Технические how-to гайды (там лучше step-by-step без sales).
- API референсы.
- Onboarding-документы (там скорее tutorial flow).

---

## References

- Этот скилл сам родился из работы над PHASE1-REPORT и PHASE3-REPORT для микро-бенча 2026-04-30.
- Активные заголовки — McKinsey & Company, «Pyramid Principle» (Barbara Minto).
- Цветовая палитра — стандарт matplotlib `tab10` адаптированный для бренда.
- См. живые примеры в `workspace/docs/evals/2026-04-30-microbench/charts/01-13.png` и связанные `*-REPORT.md` файлы.
