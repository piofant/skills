// magistratura-interview-deck — 10-slide pitch deck for a Russian master's interview (3 min).
// Dark minimalist, active headlines, real project avatars, flow diagrams, stat cards.
//
// Run:  node template.js  →  deck.pptx
//   then:  soffice --headless --convert-to pdf deck.pptx
//          pdftoppm -png -r 80 deck.pdf pg     # and READ pg-*.png
//
// All content below is GENERIC placeholder — swap it for your own.
// Drop project avatars (PNG circles, ~500×500, transparent bg) into ./assets/
// See SKILL.md §4 for how to harvest avatars from existing PDFs.

const path = require("path");
const fs = require("fs");
const pptxgen = require("pptxgenjs");

const pptx = new pptxgen();
pptx.layout = "LAYOUT_WIDE"; // 13.333 x 7.5 in (16:9)

const F = "Arial", FB = "Arial", MONO = "Courier New";
const PAGE_W = 13.333, PAGE_H = 7.5, MX = 0.7;

const C = {
  bg: "000000", white: "FFFFFF", body: "D6D6D6", eyebrow: "9A9A9A", faint: "6E6E6E",
  card: "15161C", cardLine: "2C2E38", hl: "2B3450",
  purple: "9B87F5", blue: "1E73D6", amber: "D9920E", green: "3FA56B", red: "C44133", pink: "D98FBE",
  // brand colors for badge fallbacks
  yandex: "FFCC00", vkusvill: "5BAA50",
};

const ASSETS = path.join(__dirname, "assets");
// Optional real avatars. If file missing, badge() falls back to a letter circle.
const PHOTO     = path.join(ASSETS, "author_photo_circle.png");   // your photo (cover + final)
const PROJ_A    = path.join(ASSETS, "project_a_circle.png");      // main pet-project mascot
const PROJ_B    = path.join(ASSETS, "project_b_circle.png");      // secondary project
const PROJ_C    = path.join(ASSETS, "project_c_circle.png");      // tertiary
const PROJ_D    = path.join(ASSETS, "project_d_circle.png");      // fourth
const CERT      = path.join(ASSETS, "kmu_certificate.png");       // publication confirmation

// ---------- helpers ----------
let _page = 0;
function newSlide(eyebrow) {
  const s = pptx.addSlide();
  s.background = { color: C.bg };
  _page++;
  if (eyebrow) s.addText(eyebrow.toUpperCase(), { x: MX, y: 0.32, w: 10, h: 0.3, fontFace: FB, fontSize: 11, bold: true, charSpacing: 3, color: C.purple, margin: 0 });
  s.addText(String(_page), { x: PAGE_W - 1.0, y: 0.32, w: 0.6, h: 0.3, fontFace: F, fontSize: 11, color: C.faint, align: "right", margin: 0 });
  return s;
}
function headline(s, text, opts) {
  opts = opts || {};
  s.addText(text, { x: MX, y: opts.y || 0.85, w: PAGE_W - 2 * MX, h: opts.h || 1.4, fontFace: FB, fontSize: opts.size || 32, bold: true, color: C.white, margin: 0, valign: "top", lineSpacingMultiple: 1.04 });
}
function card(s, x, y, w, h, fill, line) {
  s.addShape(pptx.ShapeType.roundRect, { x, y, w, h, rectRadius: 0.08, fill: { color: fill || C.card }, line: { color: line || C.cardLine, width: 1 } });
}
function badge(s, x, y, size, letter, color, textColor) {
  // NOTE: pptxgenjs ships shapeName as "ellipse", NOT "oval".
  s.addShape(pptx.ShapeType.ellipse, { x, y, w: size, h: size, fill: { color: color }, line: { type: "none" } });
  s.addText(letter, { x, y, w: size, h: size, fontFace: FB, fontSize: size * 36, bold: true, color: textColor || C.white, align: "center", valign: "middle", margin: 0 });
}
function imgCircle(s, file, x, y, size) {
  // Image must already be circle-masked PNG with transparent bg.
  if (!fs.existsSync(file)) { console.warn("missing avatar:", file); return; }
  s.addImage({ path: file, x, y, w: size, h: size });
}
function bigNum(s, x, y, w, value, label, color, valueSize) {
  s.addText(value, { x, y, w, h: 1.4, fontFace: FB, fontSize: valueSize || 54, bold: true, color: color || C.purple, margin: 0, align: "center", valign: "middle" });
  s.addText(label, { x, y: y + 1.4, w, h: 0.5, fontFace: F, fontSize: 14, color: C.body, margin: 0, align: "center", valign: "top" });
}
function arrow(s, x1, y, x2, color) {
  // thin horizontal rect + arrowhead chevron (line shape with h=0 silently breaks)
  s.addShape(pptx.ShapeType.rect, {
    x: x1, y: y - 0.01, w: x2 - x1 - 0.12, h: 0.02,
    fill: { color: color || C.purple }, line: { type: "none" }
  });
  s.addText("›", {
    x: x2 - 0.18, y: y - 0.18, w: 0.2, h: 0.36,
    fontFace: FB, fontSize: 22, bold: true, color: color || C.purple, align: "center", valign: "middle", margin: 0
  });
}
function sourceLine(s, text) {
  s.addText(text, { x: MX, y: PAGE_H - 0.55, w: PAGE_W - 2 * MX, h: 0.3, fontFace: MONO, fontSize: 11, color: C.faint, align: "center", margin: 0 });
}

// ================ DEMO 10-SLIDE DECK (replace content) =================

// 1) COVER — "[Name] - планы в магистратуре [program] [faculty]"
{
  const s = pptx.addSlide(); s.background = { color: C.bg };
  s.addShape(pptx.ShapeType.ellipse, { x: 9.5, y: -1.5, w: 5.5, h: 5.5, fill: { color: C.purple, transparency: 75 }, line: { type: "none" } });
  s.addShape(pptx.ShapeType.ellipse, { x: 10.5, y: 4.5, w: 3.5, h: 3.5, fill: { color: C.blue, transparency: 80 }, line: { type: "none" } });

  s.addText("УНИВЕРСИТЕТ · ФАКУЛЬТЕТ · ПРОГРАММА · ДАТА", { x: 0.9, y: 1.5, w: 11, h: 0.4, fontFace: FB, fontSize: 14, bold: true, charSpacing: 3, color: C.purple, margin: 0 });
  s.addText("[Имя Фамилия] -\nпланы в магистратуре [программа] [факультет]", { x: 0.86, y: 2.2, w: 11.6, h: 2.6, fontFace: FB, fontSize: 46, bold: true, color: C.white, margin: 0, lineSpacingMultiple: 1.02 });

  if (fs.existsSync(PHOTO)) imgCircle(s, PHOTO, 0.86, 5.5, 1.1);
  s.addText("[Имя Фамилия]", { x: 2.2, y: 5.6, w: 8, h: 0.4, fontFace: FB, fontSize: 16, bold: true, color: C.white, margin: 0 });
  s.addText("[Текущая роль · место работы]", { x: 2.2, y: 6.0, w: 8, h: 0.35, fontFace: F, fontSize: 13, color: C.body, margin: 0 });
  s.addText("[Текущий бакалавриат · грант/особые отметки]", { x: 2.2, y: 6.35, w: 8, h: 0.35, fontFace: F, fontSize: 12, italic: true, color: C.eyebrow, margin: 0 });
}

// 2) КТО Я — 5 круглых аватарок проектов с полными описаниями (как в дек v4)
{
  const s = newSlide("О себе");
  headline(s, "Я делаю [тип продуктов] в [найме]\nи свои пет-проекты.");

  const projects = [
    { type: "image",  file: PROJ_A, color: C.purple, title: "Project A",   role: "Role A",      desc: "Описание проекта A\nв 2-3 строки\nс конкретикой" },
    { type: "image",  file: PROJ_B, color: C.amber,  title: "Project B",   role: "Role B",      desc: "Описание B\nв 2-3 строки\nс конкретикой" },
    { type: "image",  file: PROJ_C, color: C.green,  title: "Project C",   role: "Role C",      desc: "Описание C\nв 2-3 строки\nс конкретикой" },
    { type: "image",  file: PROJ_D, color: C.blue,   title: "Project D",   role: "Role D",      desc: "Описание D\nв 2-3 строки\nс конкретикой" },
    { type: "letter", letter: "★",  color: C.red,    title: "Grant/Award", role: "Где получил", desc: "За что получил,\nкакая привилегия,\nкогда" },
  ];

  const cardW = (PAGE_W - 2 * MX - 0.25 * 4) / 5;
  projects.forEach((p, i) => {
    const x = MX + i * (cardW + 0.25);
    const y = 2.4;
    card(s, x, y, cardW, 4.3, C.card, C.cardLine);
    const bsize = 1.1;
    const bx = x + (cardW - bsize) / 2;
    if (p.type === "image" && fs.existsSync(p.file)) {
      imgCircle(s, p.file, bx, y + 0.35, bsize);
    } else {
      badge(s, bx, y + 0.35, bsize, p.letter || p.title[0], p.color);
    }
    s.addText(p.title, { x: x + 0.15, y: y + 1.6, w: cardW - 0.3, h: 0.45, fontFace: FB, fontSize: 16, bold: true, color: C.white, align: "center", margin: 0 });
    s.addText(p.role,  { x: x + 0.15, y: y + 2.05, w: cardW - 0.3, h: 0.4, fontFace: F, fontSize: 11, italic: true, color: p.color, align: "center", margin: 0 });
    s.addText(p.desc,  { x: x + 0.15, y: y + 2.55, w: cardW - 0.3, h: 1.6, fontFace: F, fontSize: 11.5, color: C.body, align: "center", margin: 0, valign: "top", lineSpacingMultiple: 1.2 });
  });
}

// 3) УЧЁБА + НАУКА — ВКР слева, реальный сертификат публикации справа
{
  const s = newSlide("Часть 1 · Бэкграунд · учёба и наука");
  headline(s, "ВКР про [тему] + публикация в [конференция/журнал].");

  const w = (PAGE_W - 2 * MX - 0.4) / 2;
  // Левая — ВКР
  card(s, MX, 2.8, w, 3.8, C.card, C.cardLine);
  s.addShape(pptx.ShapeType.rect, { x: MX, y: 2.8, w: w, h: 0.1, fill: { color: C.purple, transparency: 50 } });
  badge(s, MX + 0.3, 3.1, 0.9, "ВКР", C.purple, C.white);
  s.addText("Название ВКР\nс контекстом темы", { x: MX + 1.35, y: 3.0, w: w - 1.55, h: 1.2, fontFace: FB, fontSize: 16, bold: true, color: C.white, margin: 0, valign: "top", lineSpacingMultiple: 1.15 });
  s.addText([
    { text: "Главный исследовательский вопрос", options: { bullet: { code: "2022" }, fontSize: 13, color: C.body, breakLine: true, paraSpaceAfter: 5 }},
    { text: "Что измеряется / какая метрика", options: { bullet: { code: "2022" }, fontSize: 13, color: C.body, breakLine: true, paraSpaceAfter: 5 }},
    { text: "Эмпирическая база / data source", options: { bullet: { code: "2022" }, fontSize: 13, color: C.body, breakLine: true, paraSpaceAfter: 5 }},
  ], { x: MX + 0.3, y: 4.55, w: w - 0.6, h: 1.5, fontFace: F, color: C.body, margin: 0, valign: "top", lineSpacingMultiple: 1.1 });
  s.addText("Научный руководитель: [Имя]", { x: MX + 0.3, y: 6.25, w: w - 0.6, h: 0.3, fontFace: F, fontSize: 12, italic: true, color: C.eyebrow, margin: 0 });

  // Правая — сертификат / публикация
  const x2 = MX + w + 0.4;
  card(s, x2, 2.8, w, 3.8, C.card, C.cardLine);
  s.addShape(pptx.ShapeType.rect, { x: x2, y: 2.8, w: w, h: 0.1, fill: { color: C.green, transparency: 50 } });
  if (fs.existsSync(CERT)) {
    const certW = w - 0.6, certH = certW / 1.5;
    s.addImage({ path: CERT, x: x2 + 0.3, y: 3.0, w: certW, h: certH });
    s.addText("В комиссии: [Имя] · опубликован в сборнике", { x: x2 + 0.3, y: 3.05 + certH + 0.15, w: w - 0.6, h: 0.4, fontFace: F, fontSize: 12, italic: true, color: C.eyebrow, align: "center", margin: 0 });
  } else {
    badge(s, x2 + 0.3, 3.1, 0.9, "PUB", C.green, C.white);
    s.addText("Название публикации,\nконференция, дата", { x: x2 + 1.35, y: 3.0, w: w - 1.55, h: 1.2, fontFace: FB, fontSize: 16, bold: true, color: C.white, margin: 0, valign: "top", lineSpacingMultiple: 1.15 });
    s.addText("[Положи скан сертификата как kmu_certificate.png в /assets и пересобери]", { x: x2 + 0.3, y: 5.5, w: w - 0.6, h: 0.6, fontFace: F, fontSize: 11, italic: true, color: C.faint, align: "center", margin: 0 });
  }
}

// 4) ПРОФЕССИОНАЛЬНЫЙ — горизонтальный timeline с результатами под каждой ролью
{
  const s = newSlide("Часть 1 · Бэкграунд · работа");
  headline(s, "[N] продакт-ролей в [компании].");

  const timeline = [
    { letter: "A", color: C.yandex,   tcolor: "000000", title: "Compny1",  role: "PM",            year: "2023", desc: "Конкретный результат с цифрой" },
    { letter: "B", color: C.vkusvill, tcolor: C.white,  title: "Company2", role: "PM B2C",        year: "2024", desc: "Конкретный результат с цифрой" },
    { letter: "C", color: C.yandex,   tcolor: "000000", title: "Company3", role: "AI Product",    year: "2025", desc: "Конкретный результат с цифрой" },
    { letter: "D", color: C.purple,   tcolor: C.white,  title: "Company4", role: "AI Product Mgr", year: "2026", desc: "Конкретный результат с цифрой" },
  ];

  const lineY = 4.2;
  const lineX1 = MX + 1.0, lineX2 = PAGE_W - MX - 1.0;
  s.addShape(pptx.ShapeType.rect, {
    x: lineX1, y: lineY - 0.01, w: lineX2 - lineX1, h: 0.02,
    fill: { color: C.cardLine }, line: { type: "none" }
  });

  const colW = (PAGE_W - 2 * MX) / 4;
  timeline.forEach((t, i) => {
    const cx = MX + colW * (i + 0.5);
    const bsize = 1.0;
    badge(s, cx - bsize/2, lineY - bsize/2, bsize, t.letter, t.color, t.tcolor);
    s.addText(t.year,  { x: cx - 0.7, y: lineY - bsize/2 - 0.55, w: 1.4, h: 0.4, fontFace: FB, fontSize: 14, bold: true, color: t.color, align: "center", margin: 0 });
    s.addText(t.title, { x: cx - 1.3, y: lineY + bsize/2 + 0.15, w: 2.6, h: 0.35, fontFace: FB, fontSize: 13.5, bold: true, color: C.white, align: "center", margin: 0 });
    s.addText(t.role,  { x: cx - 1.3, y: lineY + bsize/2 + 0.55, w: 2.6, h: 0.3, fontFace: F, fontSize: 10.5, italic: true, color: t.color, align: "center", margin: 0 });
    s.addText(t.desc,  { x: cx - 1.4, y: lineY + bsize/2 + 0.95, w: 2.8, h: 1.1, fontFace: F, fontSize: 11, color: C.body, align: "center", margin: 0, valign: "top", lineSpacingMultiple: 1.2 });
  });
}

// 5) PIVOT — найм vs пет-проекты, переход к плану
{
  const s = newSlide("Часть 2 · Итог бэкграунда");
  headline(s, "Опыт в найме и в своих проектах -\nдальше масштабирую пет-проекты в бизнес.");

  const w = (PAGE_W - 2 * MX - 0.4) / 2;

  // Левая — найм
  card(s, MX, 2.8, w, 3.2, C.card, C.cardLine);
  s.addShape(pptx.ShapeType.rect, { x: MX, y: 2.8, w: w, h: 0.08, fill: { color: C.blue, transparency: 55 } });
  s.addText("В НАЙМЕ", { x: MX + 0.3, y: 2.95, w: w - 0.6, h: 0.4, fontFace: FB, fontSize: 12, bold: true, charSpacing: 3, color: C.blue, margin: 0 });
  const nx = MX + 0.3, ny = 3.5;
  const nsw = (w - 0.6 - 0.2) / 2;
  bigNum(s, nx + 0 * (nsw + 0.2), ny, nsw, "[N]M+",     "пользователей в [продукт]",      C.purple, 44);
  bigNum(s, nx + 1 * (nsw + 0.2), ny, nsw, "[N] млн ₽", "OPEX/год в [компания]",          C.amber,  36);
  s.addText("+ другие достижения одной строкой", { x: MX + 0.3, y: 5.45, w: w - 0.6, h: 0.5, fontFace: F, fontSize: 12, italic: true, color: C.eyebrow, align: "center", margin: 0 });

  // Правая — пет-проекты
  const x2 = MX + w + 0.4;
  card(s, x2, 2.8, w, 3.2, C.card, C.cardLine);
  s.addShape(pptx.ShapeType.rect, { x: x2, y: 2.8, w: w, h: 0.08, fill: { color: C.purple, transparency: 55 } });
  s.addText("СВОИ ПЕТ-ПРОЕКТЫ", { x: x2 + 0.3, y: 2.95, w: w - 0.6, h: 0.4, fontFace: FB, fontSize: 12, bold: true, charSpacing: 3, color: C.purple, margin: 0 });
  const px = x2 + 0.3;
  const psw = (w - 0.6 - 0.2) / 2;
  bigNum(s, px + 0 * (psw + 0.2), ny, psw, "[N]+", "активных в [Проект A]", C.green, 44);
  bigNum(s, px + 1 * (psw + 0.2), ny, psw, "[N]+", "подписчиков в [Проект B]", C.amber, 44);
  s.addText("+ другие проекты и активности одной строкой", { x: x2 + 0.3, y: 5.45, w: w - 0.6, h: 0.5, fontFace: F, fontSize: 12, italic: true, color: C.eyebrow, align: "center", margin: 0 });

  // Bottom CTA
  s.addText("Хочу превратить свои проекты в полноценные бизнесы →", {
    x: MX, y: 6.3, w: PAGE_W - 2 * MX, h: 0.5, fontFace: FB, fontSize: 18, bold: true, color: C.white, align: "center", margin: 0
  });
}

// 6) PROJECT 1 — flow + stat cards
{
  const s = newSlide("Часть 2 · [Проект A]");
  headline(s, "[Активный заголовок-вывод про проект A с цифрой].");

  const flowY = 2.7, flowH = 1.4;
  const blocks = [
    { x: MX,            color: C.blue,   title: "Источники",     body: "Что на входе" },
    { x: MX + 3.4,      color: C.purple, title: "Ядро / AI",     body: "Что делает продукт" },
    { x: MX + 6.8,      color: C.amber,  title: "Результат",     body: "Куда уходит ценность" },
  ];
  blocks.forEach((b, i) => {
    card(s, b.x, flowY, 3.0, flowH, i === 1 ? "1A1230" : C.card, b.color);
    s.addShape(pptx.ShapeType.rect, { x: b.x, y: flowY, w: 3.0, h: 0.08, fill: { color: b.color, transparency: i === 1 ? 0 : 55 } });
    s.addText(b.title, { x: b.x + 0.2, y: flowY + 0.15, w: 2.6, h: 0.35, fontFace: FB, fontSize: 13, bold: true, color: b.color, margin: 0 });
    s.addText(b.body,  { x: b.x + 0.2, y: flowY + 0.55, w: 2.6, h: 0.8, fontFace: F, fontSize: 12, color: C.body, margin: 0, valign: "top", lineSpacingMultiple: 1.15 });
  });
  arrow(s, MX + 3.0 + 0.05, flowY + flowH/2, MX + 3.4 - 0.05, C.purple);
  arrow(s, MX + 6.4 + 0.05, flowY + flowH/2, MX + 6.8 - 0.05, C.amber);

  // optional side annotation card
  card(s, MX + 10.0, flowY, 1.93, flowH, C.card, C.cardLine);
  s.addText("◇", { x: MX + 10.0, y: flowY + 0.1, w: 1.93, h: 0.5, fontFace: F, fontSize: 28, color: C.eyebrow, align: "center", margin: 0 });
  s.addText("Стэйкхолдер", { x: MX + 10.0, y: flowY + 0.7, w: 1.93, h: 0.3, fontFace: FB, fontSize: 12, bold: true, color: C.eyebrow, align: "center", margin: 0 });
  s.addText("его роль / эффект", { x: MX + 10.0, y: flowY + 1.0, w: 1.93, h: 0.3, fontFace: F, fontSize: 10, italic: true, color: C.faint, align: "center", margin: 0 });

  const sx = MX, sy = 4.5;
  const sw = (PAGE_W - 2 * MX - 0.3 * 3) / 4;
  bigNum(s, sx + 0 * (sw + 0.3), sy, sw, "[N]+",  "audience",         C.purple, 44);
  bigNum(s, sx + 1 * (sw + 0.3), sy, sw, "×[N]",  "key uplift metric",C.green,  54);
  bigNum(s, sx + 2 * (sw + 0.3), sy, sw, "[N]",   "saved time/cost",  C.blue,   54);
  bigNum(s, sx + 3 * (sw + 0.3), sy, sw, "[N]+",  "market size proxy",C.amber,  50);

  sourceLine(s, "github.com/[handle]/[repo]  ·  станет магистерской ВКР");
}

// 7) PROJECT 2 — same shape, can embed avatar in the bot card
{
  const s = newSlide("Часть 2 · [Проект B]");
  headline(s, "[Проект B] - [одна фраза о статусе],\nуже [время] [статус прибыли/scale].");

  const flowY = 2.7, flowH = 1.4;
  // user
  const u = { x: MX, y: flowY, w: 3.0, h: flowH };
  card(s, u.x, u.y, u.w, u.h, C.card, C.cardLine);
  s.addShape(pptx.ShapeType.rect, { x: u.x, y: u.y, w: u.w, h: 0.08, fill: { color: C.blue, transparency: 55 } });
  s.addText("✦", { x: u.x, y: u.y + 0.2, w: u.w, h: 0.4, fontFace: F, fontSize: 22, color: C.blue, align: "center", margin: 0 });
  s.addText("Пользователь", { x: u.x + 0.2, y: u.y + 0.65, w: u.w - 0.4, h: 0.3, fontFace: FB, fontSize: 13, bold: true, color: C.white, align: "center", margin: 0 });
  s.addText("[N]+ активных", { x: u.x + 0.2, y: u.y + 1.0, w: u.w - 0.4, h: 0.3, fontFace: F, fontSize: 11.5, color: C.body, align: "center", margin: 0 });

  // bot/core with optional avatar
  const b = { x: MX + 3.4, y: flowY, w: 3.0, h: flowH };
  card(s, b.x, b.y, b.w, b.h, "1A1230", C.purple);
  s.addShape(pptx.ShapeType.rect, { x: b.x, y: b.y, w: b.w, h: 0.08, fill: { color: C.purple } });
  if (fs.existsSync(PROJ_C)) imgCircle(s, PROJ_C, b.x + 0.25, b.y + 0.2, 1.0);
  s.addText("[Проект] AI-ядро", { x: b.x + 1.35, y: b.y + 0.3, w: b.w - 1.5, h: 0.35, fontFace: FB, fontSize: 13, bold: true, color: C.purple, margin: 0 });
  s.addText("Что делает ядро\nв 2 строки", { x: b.x + 1.35, y: b.y + 0.65, w: b.w - 1.5, h: 0.7, fontFace: F, fontSize: 11, color: C.body, margin: 0, valign: "top", lineSpacingMultiple: 1.1 });

  // output
  const d = { x: MX + 6.8, y: flowY, w: 3.0, h: flowH };
  card(s, d.x, d.y, d.w, d.h, C.card, C.cardLine);
  s.addShape(pptx.ShapeType.rect, { x: d.x, y: d.y, w: d.w, h: 0.08, fill: { color: C.green, transparency: 55 } });
  s.addText("▤", { x: d.x, y: d.y + 0.2, w: d.w, h: 0.4, fontFace: F, fontSize: 22, color: C.green, align: "center", margin: 0 });
  s.addText("Артефакт / выход", { x: d.x + 0.2, y: d.y + 0.65, w: d.w - 0.4, h: 0.3, fontFace: FB, fontSize: 13, bold: true, color: C.white, align: "center", margin: 0 });
  s.addText("[N]+ единиц", { x: d.x + 0.2, y: d.y + 1.0, w: d.w - 0.4, h: 0.3, fontFace: F, fontSize: 11.5, color: C.body, align: "center", margin: 0 });

  arrow(s, MX + 3.0 + 0.05, flowY + flowH/2, MX + 3.4 - 0.05, C.purple);
  arrow(s, MX + 6.4 + 0.05, flowY + flowH/2, MX + 6.8 - 0.05, C.green);

  // tech badge on the right
  const r = { x: MX + 10.0, y: flowY, w: 1.93, h: flowH };
  card(s, r.x, r.y, r.w, r.h, C.card, C.cardLine);
  s.addText("py", { x: r.x, y: r.y + 0.2, w: r.w, h: 0.6, fontFace: FB, fontSize: 30, bold: true, color: C.amber, align: "center", margin: 0 });
  s.addText("Python\nс нуля", { x: r.x, y: r.y + 0.85, w: r.w, h: 0.5, fontFace: F, fontSize: 11, color: C.eyebrow, align: "center", margin: 0, lineSpacingMultiple: 1.1 });

  // stats
  const sx = MX, sy = 4.5;
  const sw = (PAGE_W - 2 * MX - 0.3 * 2) / 3;
  bigNum(s, sx + 0 * (sw + 0.3), sy, sw, "[N]+",   "active users",  C.purple, 50);
  bigNum(s, sx + 1 * (sw + 0.3), sy, sw, "[N]+",   "artifacts",     C.green,  44);
  bigNum(s, sx + 2 * (sw + 0.3), sy, sw, "[N] years", "since launch", C.blue,   54);

  sourceLine(s, "github.com/[handle]/[repo]  ·  Vision: [куда хочу довести]");
}

// 8) ПЛАН — два аватара проектов + 4-semester timeline
{
  const s = newSlide("Часть 3 · План в магистратуре");
  headline(s, "Масштабирую [Проект A] и [Проект B] в бизнес\nза 4 семестра магистратуры.");

  if (fs.existsSync(PROJ_A)) imgCircle(s, PROJ_A, MX + 0.3, 2.6, 0.9);
  s.addText("[Проект A] → [бизнес-модель]", { x: MX + 1.3, y: 2.65, w: 4.5, h: 0.4, fontFace: FB, fontSize: 14, bold: true, color: C.white, margin: 0 });
  s.addText("[одна фраза описания]", { x: MX + 1.3, y: 3.05, w: 4.5, h: 0.4, fontFace: F, fontSize: 11.5, italic: true, color: C.amber, margin: 0 });

  if (fs.existsSync(PROJ_C)) imgCircle(s, PROJ_C, MX + 7.0, 2.6, 0.9);
  s.addText("[Проект B] → [куда ведёт]", { x: MX + 8.0, y: 2.65, w: 4.5, h: 0.4, fontFace: FB, fontSize: 14, bold: true, color: C.white, margin: 0 });
  s.addText("[одна фраза описания]", { x: MX + 8.0, y: 3.05, w: 4.5, h: 0.4, fontFace: F, fontSize: 11.5, italic: true, color: C.purple, margin: 0 });

  const steps = [
    { n: "1", t: "Custdev",        c: C.purple },
    { n: "2", t: "Юнит-экономика", c: C.blue },
    { n: "3", t: "Пилоты",         c: C.green },
    { n: "4", t: "Раунд + ВКР",    c: C.amber },
  ];
  const colW = (PAGE_W - 2 * MX) / 4;
  const bsize = 1.3, bY = 4.7;
  steps.forEach((st, i) => {
    const cx = MX + colW * (i + 0.5);
    badge(s, cx - bsize/2, bY, bsize, st.n, st.c);
    s.addText(st.t, { x: cx - 1.5, y: bY + bsize + 0.3, w: 3.0, h: 0.5, fontFace: FB, fontSize: 18, bold: true, color: C.white, align: "center", margin: 0 });
    if (i < steps.length - 1) {
      arrow(s, cx + bsize/2 + 0.1, bY + bsize/2, MX + colW * (i + 1.5) - bsize/2 - 0.1, C.faint);
    }
  });
}

// 9) ПОЧЕМУ ИМЕННО ЭТА ПРОГРАММА — 3 cards 01/02/03
{
  const s = newSlide("Часть 3 · Мотивация");
  headline(s, "[Программа] закрывает три моих конкретных пробела.");

  const items = [
    { num: "01", title: "Курсы и научрук", desc: "Конкретные курсы / майноры / научрук с релевантным опытом.", c: C.purple },
    { num: "02", title: "Комьюнити",       desc: "Люди, которые уже довели свои проекты до выручки/нужного состояния.", c: C.blue },
    { num: "03", title: "Партнёрства",     desc: "Индустрия / стартап-комьюнити / выходы на первых клиентов.", c: C.green },
  ];
  const cw = (PAGE_W - 2 * MX - 0.3 * 2) / 3;
  items.forEach((it, i) => {
    const x = MX + i * (cw + 0.3), y = 2.7;
    card(s, x, y, cw, 3.9, C.card, C.cardLine);
    s.addShape(pptx.ShapeType.rect, { x: x, y: y, w: cw, h: 0.1, fill: { color: it.c, transparency: 55 } });
    s.addShape(pptx.ShapeType.ellipse, { x: x + (cw - 1.4) / 2, y: y + 0.4, w: 1.4, h: 1.4, fill: { color: it.c, transparency: 75 }, line: { color: it.c, width: 1 } });
    s.addText(it.num, { x: x + (cw - 1.4) / 2, y: y + 0.4, w: 1.4, h: 1.4, fontFace: FB, fontSize: 32, bold: true, color: C.white, align: "center", valign: "middle", margin: 0 });
    s.addText(it.title, { x: x + 0.3, y: y + 2.05, w: cw - 0.6, h: 0.5, fontFace: FB, fontSize: 17, bold: true, color: C.white, align: "center", margin: 0 });
    s.addText(it.desc,  { x: x + 0.3, y: y + 2.65, w: cw - 0.6, h: 1.15, fontFace: F, fontSize: 12.5, color: C.body, align: "center", margin: 0, valign: "top", lineSpacingMultiple: 1.2 });
  });
}

// 10) СПАСИБО — author photo + contacts
{
  const s = pptx.addSlide(); s.background = { color: C.bg };
  s.addShape(pptx.ShapeType.ellipse, { x: -1.5, y: 4.5, w: 4.0, h: 4.0, fill: { color: C.purple, transparency: 85 }, line: { type: "none" } });
  s.addShape(pptx.ShapeType.ellipse, { x: 11.0, y: -1.0, w: 3.5, h: 3.5, fill: { color: C.blue, transparency: 85 }, line: { type: "none" } });

  s.addText("Спасибо.", { x: 0.9, y: 2.4, w: 11.6, h: 1.4, fontFace: FB, fontSize: 88, bold: true, color: C.white, margin: 0, align: "center" });
  s.addText("Готов к вопросам.", { x: 0.9, y: 3.95, w: 11.6, h: 0.6, fontFace: F, fontSize: 26, italic: true, color: C.eyebrow, margin: 0, align: "center" });

  if (fs.existsSync(PHOTO)) imgCircle(s, PHOTO, 6.17, 5.0, 1.0);
  s.addText("@[handle]  ·  [email]", { x: 0.9, y: 6.15, w: 11.6, h: 0.4, fontFace: MONO, fontSize: 13, color: C.body, align: "center", margin: 0 });
}

pptx.writeFile({ fileName: path.join(__dirname, "deck.pptx") }).then((f) => console.log("WROTE", f));
