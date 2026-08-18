// dark-deck-builder — starter skeleton for a flat-black, active-headline deck.
// Run:  node template.js  →  deck.pptx
//   then:  soffice --headless --convert-to pdf deck.pptx
//          pdftoppm -png -r 80 deck.pdf pg     # and LOOK at pg-*.png
//
// All content below is GENERIC placeholder — swap it for your own.
// Keep internal/NDA figures out of any file you commit publicly.

const path = require("path");
const fs = require("fs");
const pptxgen = require("pptxgenjs");

const pptx = new pptxgen();
pptx.layout = "LAYOUT_WIDE"; // 13.333 x 7.5 in (16:9)

const F = "Arial", FB = "Arial", MONO = "Courier New"; // swap to Inter if embedded
const PAGE_W = 13.333, PAGE_H = 7.5, MX = 0.7;

const C = {
  bg: "000000", white: "FFFFFF", body: "D6D6D6", eyebrow: "9A9A9A", faint: "6E6E6E",
  card: "15161C", cardLine: "2C2E38", hl: "2B3450",
  purple: "9B87F5", blue: "1E73D6", amber: "D9920E", green: "3FA56B", red: "C44133", pink: "D98FBE",
};

// ---------- helpers ----------
let _page = 0;
function newSlide(eyebrow, part) {
  const s = pptx.addSlide();
  s.background = { color: C.bg };
  _page++;
  if (eyebrow) s.addText(eyebrow.toUpperCase(), { x: MX, y: 0.32, w: 10, h: 0.3, fontFace: FB, fontSize: 11, bold: true, charSpacing: 3, color: C.purple, margin: 0 });
  s.addText(String(_page), { x: PAGE_W - 1.0, y: 0.32, w: 0.6, h: 0.3, fontFace: F, fontSize: 11, color: C.faint, align: "right", margin: 0 });
  return s;
}
function headline(s, text) {
  s.addText(text, { x: MX, y: 0.85, w: PAGE_W - 2 * MX, h: 1.1, fontFace: FB, fontSize: 28, bold: true, color: C.white, margin: 0, valign: "top", lineSpacingMultiple: 1.04 });
}
function subhead(s, text, y) {
  s.addText(text, { x: MX, y: y || 1.85, w: PAGE_W - 2 * MX, h: 0.6, fontFace: F, fontSize: 15, italic: true, color: C.eyebrow, margin: 0, valign: "top", lineSpacingMultiple: 1.05 });
}
function card(s, x, y, w, h, fill, line) {
  s.addShape(pptx.ShapeType.roundRect, { x, y, w, h, rectRadius: 0.08, fill: { color: fill || C.card }, line: { color: line || C.cardLine, width: 1 } });
}
function bullets(s, items, o) {
  o = o || {};
  const runs = items.map((it) => ({
    text: it.t,
    options: {
      bullet: it.sub ? { indent: 28, code: "2013" } : { indent: 16, code: "2022" },
      indentLevel: it.sub ? 1 : 0, paraSpaceAfter: (o.gap || 10),
      fontFace: it.b ? FB : F, bold: !!it.b, fontSize: it.fs || o.fontSize || 14,
      color: it.c || C.body, breakLine: true, lineSpacingMultiple: 1.05,
    },
  }));
  s.addText(runs, { x: o.x || MX, y: o.y || 2.0, w: o.w || (PAGE_W - 2 * MX), h: o.h || 4.0, margin: 0, valign: "top" });
}
function highlightBlock(s, runs, o) {
  card(s, MX, o.y, PAGE_W - 2 * MX, o.h, C.hl, C.hl);
  s.addText(runs.map((r) => ({ text: r.text, options: { ...r.options, fontFace: F, fontSize: o.fs || 16, color: r.options && r.options.color ? r.options.color : C.white } })),
    { x: MX + 0.3, y: o.y, w: PAGE_W - 2 * MX - 0.6, h: o.h, valign: "middle", margin: 0, lineSpacingMultiple: 1.12 });
}
function callout(s, title, body, o) {
  card(s, o.x, o.y, o.w, o.h, C.card, C.cardLine);
  s.addText(title, { x: o.x + 0.25, y: o.y + 0.18, w: o.w - 0.5, h: 0.4, fontFace: FB, fontSize: 15, bold: true, color: o.accent || C.purple, margin: 0 });
  s.addText(body, { x: o.x + 0.25, y: o.y + 0.62, w: o.w - 0.5, h: o.h - 0.8, fontFace: F, fontSize: 13, color: C.body, margin: 0, valign: "top", lineSpacingMultiple: 1.08 });
}
function stat(s, x, y, w, value, label, color) {
  s.addText(value, { x, y, w, h: 0.8, fontFace: FB, fontSize: 32, bold: true, color: color || C.purple, margin: 0, valign: "middle" });
  s.addText(label, { x, y: y + 0.8, w, h: 0.8, fontFace: F, fontSize: 12, color: C.body, margin: 0, valign: "top", lineSpacingMultiple: 1.05 });
}
function imgContain(s, file, box, ar) { // dark-bg scheme PNG, no frame
  const { x, y, w, h } = box; let dw = w, dh = w / ar;
  if (dh > h) { dh = h; dw = h * ar; }
  s.addImage({ path: path.join(__dirname, file), x: x + (w - dw) / 2, y: y + (h - dh) / 2, w: dw, h: dh });
}
function imageCard(s, file, box, ar) { // light figure on a small white card
  const { x, y, w, h, pad = 0.12 } = box; let dw = w - 2 * pad, dh = (w - 2 * pad) / ar;
  if (dh > h - 2 * pad) { dh = h - 2 * pad; dw = dh * ar; }
  const cw = dw + 2 * pad, ch = dh + 2 * pad, cx = x + (w - cw) / 2, cy = y + (h - ch) / 2;
  s.addShape(pptx.ShapeType.roundRect, { x: cx, y: cy, w: cw, h: ch, rectRadius: 0.04, fill: { color: C.white }, line: { type: "none" } });
  s.addImage({ path: path.join(__dirname, file), x: cx + pad, y: cy + pad, w: dw, h: dh });
}
function sourceLine(s, text) {
  s.addText(text, { x: MX, y: PAGE_H - 0.55, w: PAGE_W - 2 * MX, h: 0.3, fontFace: F, fontSize: 9.5, color: C.faint, margin: 0 });
}
// numbered sequential trace flow (steps top→bottom with ↓)
function traceFlow(s, steps, y0) {
  let y = y0 || 2.4; const w = PAGE_W - 2 * MX, rh = 0.74, gap = 0.18;
  steps.forEach((st, i) => {
    card(s, MX, y, w, rh, C.card, C.cardLine);
    s.addShape(pptx.ShapeType.roundRect, { x: MX + 0.24, y: y + 0.17, w: 0.4, h: 0.4, rectRadius: 0.09, fill: { color: st.c, transparency: 18 } });
    s.addText(st.n, { x: MX + 0.24, y: y + 0.17, w: 0.4, h: 0.4, fontFace: FB, fontSize: 16, bold: true, color: C.white, align: "center", valign: "middle", margin: 0 });
    s.addText(st.t, { x: MX + 0.85, y, w: 2.7, h: rh, fontFace: FB, fontSize: 14.5, bold: true, color: C.white, margin: 0, valign: "middle" });
    s.addText(st.d, { x: MX + 3.6, y, w: w - 3.85, h: rh, fontFace: F, fontSize: 13.5, color: st.dc || C.body, bold: !!st.db, margin: 0, valign: "middle", lineSpacingMultiple: 1.03 });
    if (i < steps.length - 1) s.addText("↓", { x: MX + 0.34, y: y + rh - 0.01, w: 0.2, h: gap + 0.05, fontFace: F, fontSize: 13, color: C.faint, align: "center", valign: "middle", margin: 0 });
    y += rh + gap;
  });
}

// ================= DEMO DECK (replace with your content) =================

// 1) Cover — eyebrow, two-line active title, subtitle, optional right image.
{
  const s = pptx.addSlide(); s.background = { color: C.bg };
  const img = path.join(__dirname, "cover.png"); // black-bg PNG melts into canvas
  if (fs.existsSync(img)) s.addImage({ path: img, x: 8.55, y: 1.15, w: 4.2, h: 5.2, sizing: { type: "contain", w: 4.2, h: 5.2 } });
  s.addText("PROJECT · DECK", { x: 0.9, y: 1.6, w: 8, h: 0.4, fontFace: FB, fontSize: 15, bold: true, charSpacing: 3, color: C.purple, margin: 0 });
  s.addText("How we measure what\nactually matters", { x: 0.86, y: 2.15, w: 7.6, h: 2.0, fontFace: FB, fontSize: 46, bold: true, color: C.white, margin: 0, lineSpacingMultiple: 1.0 });
  s.addText("A short, honest walkthrough — method and first steps", { x: 0.9, y: 4.45, w: 7.6, h: 0.6, fontFace: F, fontSize: 18, color: C.body, margin: 0 });
}

// 2) 3-card overview, with the "we're here" card highlighted.
{
  const s = newSlide("Part 1 · Landscape", 1);
  headline(s, "Three kinds of metric — today we focus on answer quality");
  const m = [
    { t: "Product", d: "retention, depth, volume", note: "move slowly, many causes", c: C.blue, hl: false },
    { t: "Answer quality", d: "how good a single reply is", note: "today — this one", c: C.purple, hl: true },
    { t: "Technical", d: "stability, latency, errors", note: "so it reaches the user at all", c: C.green, hl: false },
  ];
  let x = MX; const w = (PAGE_W - 2 * MX - 2 * 0.3) / 3;
  m.forEach((mm) => {
    card(s, x, 2.6, w, 3.05, mm.hl ? "171327" : C.card, mm.hl ? C.purple : C.cardLine);
    s.addShape(pptx.ShapeType.rect, { x, y: 2.6, w, h: 0.12, fill: { color: mm.c, transparency: mm.hl ? 0 : 60 } });
    s.addText(mm.t, { x: x + 0.25, y: 2.86, w: w - 0.5, h: 0.5, fontFace: FB, fontSize: 18, bold: true, color: C.white, margin: 0, valign: "top" });
    s.addText(mm.d, { x: x + 0.25, y: 3.5, w: w - 0.5, h: 1.3, fontFace: F, fontSize: 13.5, color: C.body, margin: 0, valign: "top", lineSpacingMultiple: 1.1 });
    s.addText(mm.note, { x: x + 0.25, y: 4.95, w: w - 0.5, h: 0.55, fontFace: F, fontSize: 12, italic: true, color: mm.hl ? C.purple : C.eyebrow, margin: 0, valign: "top" });
    x += w + 0.3;
  });
}

// 3) Sequential trace flow.
{
  const s = newSlide("Part 1 · How it works", 1);
  headline(s, "One item, checked end to end — step by step");
  traceFlow(s, [
    { n: "1", t: "Input", d: "the user's request enters the pipeline", c: C.blue },
    { n: "2", t: "Cheap filter", d: "deterministic checks, no model — catches obvious failures free", c: C.green },
    { n: "3", t: "Judge", d: "a separate model scores against the rubric", c: C.purple },
    { n: "4", t: "Verdict", d: "any critical miss → fail, even at a high average", c: C.red, dc: C.red, db: true },
  ], 2.45);
}

// 4) Transition divider.
{
  const s = newSlide("Part 2 · Next", 2);
  s.addText("We can measure it now.", { x: MX + 0.16, y: 2.55, w: PAGE_W - 2 * MX, h: 0.8, fontFace: FB, fontSize: 30, color: C.eyebrow, margin: 0 });
  s.addText("So how do we move it →", { x: MX + 0.16, y: 3.35, w: PAGE_W - 2 * MX, h: 0.9, fontFace: FB, fontSize: 46, bold: true, color: C.white, margin: 0 });
}

pptx.writeFile({ fileName: path.join(__dirname, "deck.pptx") }).then((f) => console.log("WROTE", f));
