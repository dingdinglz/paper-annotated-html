#!/usr/bin/env python3
"""Structural check of an assembled annotated-paper HTML.

Usage: python3 validate.py paper_annotated.html

Reports per paragraph row: missing English / Chinese / annotation parts, rows whose English or
Chinese block has no highlight, Chinese blocks with far fewer highlights than the English, notes
missing one of the three required fields, nav anchors without targets, leftover {{placeholders}}.
Exit code 1 if any hard problem was found.
"""
import re, sys
from html.parser import HTMLParser

src = open(sys.argv[1], encoding="utf-8").read()
problems, warnings = [], []

rows = re.split(r'<div class="row">', src)[1:]
for i, r in enumerate(rows, 1):
    pid = re.search(r'<div class="pid">(.*?)</div>', r)
    pid = pid.group(1) if pid else f"row#{i}"
    is_fig = "图" in pid or "表" in pid or "Figure" in pid or "Table" in pid
    en = re.search(r'class="en"(.*?)(?=class="divider"|class="zh"|</div>\s*<aside)', r, re.S)
    zh = re.search(r'class="zh"(.*?)(?=</p>|</div>\s*(?:<figure|</div>|<div class="divider"))', r, re.S)
    note = re.search(r'<aside class="note[^"]*">(.*?)</aside>', r, re.S)
    if not note:
        problems.append(f"{pid}: no annotation card")
    else:
        for field in ("段落功能", "逻辑角色", "技巧"):
            if field not in note.group(1):
                problems.append(f"{pid}: annotation lacks '{field}'")
    if is_fig:
        continue
    if not en:
        problems.append(f"{pid}: no English block"); continue
    if not zh:
        problems.append(f"{pid}: no Chinese block"); continue
    ne, nz = en.group(1).count("<mark"), zh.group(1).count("<mark")
    if ne == 0:
        warnings.append(f"{pid}: English has no highlights")
    if nz == 0:
        problems.append(f"{pid}: Chinese has no highlights (should mirror English)")
    elif ne and nz < ne * 0.5:
        warnings.append(f"{pid}: Chinese highlights ({nz}) much fewer than English ({ne})")

ids = set(re.findall(r'id="([^"]+)"', src))
for href in re.findall(r'<nav class="secnav".*?</nav>', src, re.S)[:1]:
    for anchor in re.findall(r'href="#([^"]+)"', href):
        if anchor not in ids:
            problems.append(f"nav link #{anchor} has no target")

left = set(re.findall(r"\{\{[^}]+\}\}", src))
if left:
    problems.append(f"unfilled placeholders: {sorted(left)}")
if 'class="overview"' not in src:
    problems.append("no argument overview section")

class P(HTMLParser):
    def __init__(s): super().__init__(); s.stack = []; s.bad = []
    def handle_starttag(s, t, a):
        if t not in ("br", "img", "meta", "link", "hr", "input", "source"): s.stack.append(t)
    def handle_endtag(s, t):
        if t in ("br", "img"): return
        if t in s.stack:
            while s.stack and s.stack[-1] != t: s.bad.append(s.stack.pop())
            s.stack.pop()
        else: s.bad.append("/" + t)
pp = P(); pp.feed(src)
if pp.bad:
    warnings.append(f"possibly unbalanced tags (first few): {pp.bad[:8]}")

print(f"rows: {len(rows)}   marks EN+ZH: {src.count('<mark')}   images: {src.count('data:image')}")
for w in warnings: print("WARN ", w)
for p in problems: print("ERROR", p)
print("OK" if not problems else f"{len(problems)} problem(s)")
sys.exit(1 if problems else 0)
