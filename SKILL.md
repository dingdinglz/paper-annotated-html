---
name: paper-annotated-html
description: Turn an academic paper (PDF) into a single-file, two-column annotated HTML for close reading — left column English original with five-colour argument highlighting (thesis / key concepts / evidence / concessions / methodology) plus a fluent Chinese translation under every paragraph (highlighted the same way), right column per-paragraph Chinese annotations (function, logical role, rhetorical moves and weaknesses), original figures embedded, and an argument-map overview at the end. Use this whenever the user wants to 精读/批注/导读 a paper, make a 双栏批注 or 中英对照 HTML of a paper, analyse a paper's 论证结构/逻辑层次 for a course, seminar, journal club or reading group, or shares a paper PDF and asks for an annotated, bilingual or argument-focused version — even if they don't say "HTML" or "skill".
---

# Paper → bilingual annotated HTML

Produce one self-contained `.html` file that lets a reader (typically a student preparing for a course
discussion) follow a paper's argument paragraph by paragraph: what each paragraph says (English + Chinese),
what it does in the argument, and where the argument is strong or weak.

The user's request may restate the spec (colours, fonts, layout). Follow their wording where it differs;
otherwise the defaults below are what earlier users settled on after iteration.

## Defaults the output should meet

- **Layout**: dark-navy top bar (title, course info, colour legend that toggles each highlight layer, a
  hide-translation button), sticky section nav, then rows of *left = EN + ZH* / *right = annotation card*,
  single column on mobile, argument overview at the bottom. All of this is in `assets/template.html`.
- **English**: original text, kept complete (don't summarize paragraphs away), highlighted in five colours.
- **Chinese**: 意译, reads like Chinese academic prose, in a beige block with a thin left rule under each
  English paragraph, separated by a 1px divider — **and highlighted with the same five colours**.
  (An early version left the Chinese plain; the user asked for highlights there too.)
- **Fonts**: English body Source Serif 4; Chinese translation and UI in a *sans* face (IBM Plex Sans for
  Latin + Noto Sans SC). Thin serif CJK (宋体 / Noto Serif SC) was reported as "太细、读着难受" — keep
  translations in sans with dark ink (#26292e), 16px, line-height ~1.9. The template already does this.
- **Original figures**: crop the paper's figures from the PDF and embed them (base64) next to the paragraph
  that discusses them; keep the output a single file. Small tables can be re-typed as HTML.
- **Course info**: if not given, leave the editable placeholder `［课程名称 · 学期］` and tell the user.

## Workflow

Paths: `SKILL_DIR` = this skill's directory. Work in a scratch folder (`WORK`), write the final file next to
the PDF unless the user names another place.

### 1. Extract

```bash
python3 SKILL_DIR/scripts/pdf_tools.py info  paper.pdf
python3 SKILL_DIR/scripts/pdf_tools.py text  paper.pdf WORK/paper.txt
```

Needs poppler-utils. If `pdftotext` is missing, install it (`sudo apt-get install -y poppler-utils` /
`brew install poppler`) — the Read tool's PDF mode also depends on it. Read the full text, main body first,
then skim appendices for implementation details, extra results and limitations that annotations can cite.

### 2. Plan the paragraph units

Decide the scope: by default the abstract, all main-body sections, the conclusion, and the
limitations/discussion appendix; skip references and long appendix tables (mention in the footer what was
covered). Split into rows at the paper's own paragraph boundaries; a very long paragraph may be split, a run
of short setup sentences may be merged. Give each row an id (A1, I1…, P1…, M1…, E1…, C1, L1) — annotations
and the overview refer to them.

Before writing, sketch the argument chain (problem → thesis → evidence → rebuttal → conclusion) in a few
lines. Every annotation's 逻辑角色 hangs off this sketch, so doing it first keeps the cards coherent.

### 3. Figures

```bash
python3 SKILL_DIR/scripts/pdf_tools.py captions paper.pdf --bbox-cache WORK/bbox.html
python3 SKILL_DIR/scripts/pdf_tools.py crop paper.pdf <page> <x0> <y0> <x1> <y1> WORK/figs/fig3.png
```

`captions` prints each figure caption with a suggested crop box (PDF points). Crop at 200 dpi and **look at
every PNG** before using it: the heuristic often includes the running header rule, a trailing line of body
text, or cuts a figure title. Adjust the box and re-crop. Figures wrapped beside text need a column-limited
box. Use `preview` for a low-res page render when you need to eyeball the layout. Name files `figN.png`.
Leave the caption text out of the crop; it goes into `<figcaption>`.

### 4. Write the content fragments

Read `references/annotation-guide.md` (highlight criteria, translation style, card fields, critical-reading
checklist) and `references/fragments.md` (exact HTML for rows, equations, figures, tables, overview).

Write one fragment per paper section into `WORK/sections/NN-name.html` and the overview into
`WORK/overview.html`, plus `WORK/meta.json`:

```json
{"short_title": "WavesFM", "paper_title": "Full paper title",
 "course": "［课程名称 · 学期］", "paper_meta": "arXiv:xxxx.xxxxx（Org, Year）",
 "footer": "批注基于 … 正文与附录 A 整理。译文为意译；原图截取自 PDF（点击可放大）。",
 "nav": [["abstract","摘要"],["intro","1 引言"],["method","3 方法"],["exp","4 实验"],["concl","5 结论"],["overview","论证结构总览"]]}
```

Splitting by section keeps each write manageable for long papers and lets you fix one section without
touching the rest. Write the English, Chinese and card for a row together — the highlights in both languages
and the card's claims should refer to the same spans.

### 5. Assemble, validate, look

```bash
python3 SKILL_DIR/scripts/assemble.py --template SKILL_DIR/assets/template.html --meta WORK/meta.json \
  --sections WORK/sections --overview WORK/overview.html --figs WORK/figs --out <name>_annotated.html
python3 SKILL_DIR/scripts/validate.py <name>_annotated.html
bash SKILL_DIR/scripts/screenshot.sh <name>_annotated.html WORK/shots    # optional visual QA
```

Fix every `ERROR` from the validator (missing Chinese highlights, missing card fields, dead nav links,
unfilled placeholders); judge the `WARN`s. If a headless Chromium is available, view `desktop.png` and
`mobile.png` to confirm highlights, figures and the mobile single-column layout render. If the browser
can't run, say so rather than implying the page was checked.

### 6. Report

Tell the user the file path and size, what was covered (sections / appendices / which figures), anything
left as a placeholder, and the 2–3 most important critical findings from the annotations (these are what
they'll want to discuss). Mention that fonts and KaTeX load from CDNs, so offline viewing falls back to
system fonts and raw LaTeX.

## Adjusting on request

Typical follow-ups and where to change them:
- Fonts / sizes / colours → the `:root` variables and `.en` / `.zh` / `mark.*` rules at the top of the
  template (or in the generated file for a one-off). For a heavier translation, try `font-weight:500` or 17px.
- More/fewer highlights or different emphasis → edit the fragments and re-assemble.
- A different target language → keep the structure; the translation block and cards switch language, and
  the font stack needs a suitable sans face for that script.
