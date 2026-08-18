---
name: itmo-report
description: Создание отчётов и презентаций для ИТМО в LaTeX (XeLaTeX) и PPTX с правильным ГОСТ-оформлением, кириллицей и фирменным стилем ИТМО. Используй при любых задачах связанных с отчётами/презентациями для университета ИТМО.
---

# ИТМО: Отчёты (LaTeX) и Презентации (PPTX)

## 1. LaTeX отчёт (XeLaTeX + ГОСТ)

### Компиляция
Только XeLaTeX (не pdflatex!) для корректной работы с кириллицей:
```bash
xelatex -interaction=nonstopmode main.tex
```

### Преамбула-шаблон
```latex
\documentclass[14pt,a4paper]{extarticle}

% Шрифты и язык (XeLaTeX)
\usepackage{fontspec}
\setmainfont{Times New Roman}
\setsansfont{Helvetica}
\usepackage{polyglossia}
\setdefaultlanguage{russian}
\setotherlanguage{english}
% Фикс кириллицы в monospace
\newfontfamily\russianfonttt{Times New Roman}

% Поля по ГОСТу: лево 30, право 15, верх 20, низ 20
\usepackage[left=30mm,right=15mm,top=20mm,bottom=20mm]{geometry}

% Межстрочный интервал 1.5
\usepackage{setspace}
\onehalfspacing

% Абзацный отступ 1.25 см
\usepackage{indentfirst}
\setlength{\parindent}{1.25cm}

% Глобальная защита от переполнения строк
\tolerance=9000
\emergencystretch=3em
\hbadness=10000
\setlength{\overfullrule}{0pt}

% Изображения, таблицы
\usepackage{graphicx}
\usepackage{float}
\usepackage{array}
\usepackage{tabularx}
\usepackage{longtable}

% Типы колонок
\newcolumntype{L}[1]{>{\raggedright\arraybackslash}p{#1}}
\newcolumntype{C}[1]{>{\centering\arraybackslash}p{#1}}

% Подписи
\usepackage{caption}
\captionsetup[figure]{name=Рисунок,labelsep=endash}
\captionsetup[table]{name=Таблица,labelsep=endash}

% Нумерация страниц
\usepackage{fancyhdr}
\pagestyle{fancy}
\fancyhf{}
\fancyfoot[C]{\thepage}
\renewcommand{\headrulewidth}{0pt}

% Гиперссылки
\usepackage[hidelinks]{hyperref}
\usepackage{url}

% Диаграммы TikZ
\usepackage{tikz}
\usetikzlibrary{arrows.meta, positioning, shapes.geometric, fit, calc}
```

### Титульная страница
Используй `\begin{minipage}[t]{\dimexpr\textwidth-1.25cm\relax}` для полей с длинным текстом (Направление подготовки итд), чтобы текст корректно переносился:
```latex
\begin{flushleft}
\hspace{1.25cm}\begin{minipage}[t]{\dimexpr\textwidth-1.25cm\relax}
\textbf{Факультет:} ...
\textbf{Образовательная программа:} ...
\textbf{Направление подготовки (специальность):} ...
\end{minipage}
\end{flushleft}
```

### Частые проблемы и решения
| Проблема | Решение |
|----------|---------|
| Кириллица не отображается | Использовать XeLaTeX + fontspec + polyglossia |
| Monospace шрифт ломает кириллицу | `\newfontfamily\russianfonttt{Times New Roman}` |
| Текст вылезает за поля | `\tolerance=9000`, `\emergencystretch=3em` |
| Таблица не влезает | `\resizebox{\textwidth}{!}{...}` или уменьшить colW |
| URL вылезает за поля | `\nolinkurl{...}` вместо `\url{...}` |
| standalone.cls not found | Не используй standalone, делай диаграммы внутри документа |
| multirow/enumitem/tocloft not found | Не подключай -- используй стандартные средства |

### Стиль текста (humanize)
- Используй `--` (короткое тире), НЕ `---` (длинное тире EM-dash -- палево ИИ)
- Пиши простым языком, как студент
- Не злоупотребляй канцеляритом
- Без лишних эпитетов и водянистых формулировок

## 2. Презентация (PPTX в стиле ИТМО)

### Генерация через pptxgenjs (Node.js)
```bash
npm install -g pptxgenjs  # если ещё нет
node create_pptx.js
```

### Цветовая палитра ИТМО
```javascript
const ITMO_PURPLE = "4B0082";  // фиолетовый ИТМО
const ITMO_RED = "E52B2B";     // красный ИТМО
const DARK_BG = "1A1A2E";      // тёмный фон (титульный/финальный слайд)
const WHITE = "FFFFFF";
const LIGHT_GRAY = "F5F5F5";
const TEXT_DARK = "2D2D2D";
const TEXT_LIGHT = "CCCCCC";
```

### Структура слайдов
- **Титульный**: тёмный фон (DARK_BG), фиолетовый акцент справа, "ИТМО" крупно, команда в боксе
- **Контентные**: цветная шапка (красная/фиолетовая чередуются), лого "ИТМО" справа вверху, белые rounded-rect контентные области с тенью, номер слайда внизу справа
- **Финальный**: тёмный фон как титульный, "Спасибо за внимание!", таблица с итогами, ссылки

### Паттерн контентного слайда
```javascript
function makeContentSlide(title, color) {
  const slide = pres.addSlide();
  // Шапка
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 0.95, fill: { color }
  });
  // Заголовок в шапке
  slide.addText(title, {
    x: 0.4, y: 0.1, w: 7.5, h: 0.75,
    fontSize: 26, fontFace: "Georgia",
    color: "FFFFFF", bold: true, italic: true, margin: 0
  });
  // Лого ИТМО
  slide.addText("ИТМО", {
    x: 8.2, y: 0.15, w: 1.5, h: 0.5,
    fontSize: 28, fontFace: "Arial Black",
    color: "E52B2B", bold: true, align: "right", margin: 0
  });
  return slide;
}
```

### Диаграммы в презентации
Компилируй TikZ диаграммы из отчёта, извлекай как изображения:
```bash
# Компиляция отчёта
xelatex main.tex
# Извлечение страницы с диаграммой
pdftoppm -jpeg -r 300 -f PAGE -l PAGE main.pdf diagrams/name
# Обрезка до нужной области
sips -c HEIGHT WIDTH --cropOffset Y X input.jpg --out output.jpg
```
Затем вставляй в PPTX через `slide.addImage({ path: ..., sizing: { type: "contain", ... } })`.

### Конвертация PPTX в PDF для проверки
```bash
# Через LibreOffice
soffice --headless --convert-to pdf presentation.pptx
# Или через скрипт из skills
python3 scripts/office/soffice.py --headless --convert-to pdf presentation.pptx
# Превью слайдов
pdftoppm -jpeg -r 150 presentation.pdf slide
```

## 3. Чеклист перед сдачей

- [ ] Отчёт компилируется без ошибок (XeLaTeX)
- [ ] Титульный лист: все поля на месте, текст не вылезает
- [ ] Содержание корректное
- [ ] Таблицы не вылезают за поля
- [ ] URL не вылезают за поля (nolinkurl)
- [ ] Диаграммы читаемые
- [ ] Нет длинных тире (---, ем-дэш)
- [ ] Презентация: кириллица отображается
- [ ] Презентация: все 12 слайдов на месте
- [ ] Ссылки: GitHub репозиторий, Google Drive видео
- [ ] Нет AI-tells в тексте
