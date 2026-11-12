#!/usr/bin/env python3
"""Assemble the final single-file HTML from the template + content fragments, embedding figures.

Usage
  python3 assemble.py --template <skill>/assets/template.html \
      --meta meta.json --sections <dir with 01-*.html, 02-*.html ...> \
      --overview overview.html --figs <dir with PNGs> --out paper_annotated.html

meta.json keys: short_title, paper_title, course, paper_meta, footer,
                nav: [[anchor_id, label], ...]   (include ["overview", "论证结构总览"] last)

Section fragments are concatenated in filename order and replace {{SECTIONS}}.
Any  src="{{FIG:name}}"  becomes a base64 data URI of <figs>/name.png (or .jpg), so the output stays one file.
"""
import argparse, base64, glob, html, json, os, re, sys

p = argparse.ArgumentParser()
p.add_argument("--template", required=True)
p.add_argument("--meta", required=True)
p.add_argument("--sections", required=True)
p.add_argument("--overview", required=True)
p.add_argument("--figs", default=None)
p.add_argument("--out", required=True)
a = p.parse_args()

tpl = open(a.template, encoding="utf-8").read()
meta = json.load(open(a.meta, encoding="utf-8"))
frags = sorted(glob.glob(os.path.join(a.sections, "*.html")))
if not frags:
    sys.exit(f"no fragments in {a.sections}")
sections = "\n\n".join(open(f, encoding="utf-8").read() for f in frags)
overview = open(a.overview, encoding="utf-8").read()
nav = "\n".join(f'    <a href="#{i}">{html.escape(l)}</a>' for i, l in meta["nav"])

out = (tpl.replace("{{SHORT_TITLE}}", html.escape(meta["short_title"]))
          .replace("{{PAPER_TITLE}}", html.escape(meta["paper_title"]))
          .replace("{{COURSE}}", html.escape(meta.get("course", "［课程名称 · 学期］")))
          .replace("{{PAPER_META}}", html.escape(meta.get("paper_meta", "")))
          .replace("{{FOOTER}}", meta.get("footer", ""))
          .replace("{{SECNAV_LINKS}}", nav)
          .replace("{{SECTIONS}}", sections)
          .replace("{{OVERVIEW}}", overview))

missing = []
def embed(m):
    name = m.group(1)
    for ext, mime in ((".png", "image/png"), (".jpg", "image/jpeg"), (".jpeg", "image/jpeg")):
        path = os.path.join(a.figs or "", name + ext)
        if a.figs and os.path.exists(path):
            return 'src="data:%s;base64,%s"' % (mime, base64.b64encode(open(path, "rb").read()).decode())
    missing.append(name)
    return m.group(0)
out = re.sub(r'src="\{\{FIG:([\w.-]+)\}\}"', embed, out)

left = sorted(set(re.findall(r"\{\{[A-Z_:a-z0-9.-]+\}\}", out)))
open(a.out, "w", encoding="utf-8").write(out)
print(f"wrote {a.out} ({len(out) // 1024} KB) from {len(frags)} fragments")
if missing:
    print("MISSING FIGURES:", missing)
if left:
    print("UNFILLED PLACEHOLDERS:", left)
