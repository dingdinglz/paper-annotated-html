#!/usr/bin/env python3
"""PDF helpers for the paper-annotated-html skill (needs poppler-utils: pdftotext, pdftoppm, pdfinfo).

Subcommands
  info     <pdf>                         page count, page size, title
  text     <pdf> <out.txt>               plain text extraction (one file, pages separated by \f)
  captions <pdf> [--bbox-cache f.html]   list every "Figure N |" / "Table N |" caption with page,
                                         coordinates (pt) and a SUGGESTED crop box for the figure above it
  crop     <pdf> <page> <x0> <y0> <x1> <y1> <out.png> [--dpi 200]
                                         crop a region given in PDF points (72 pt = 1 inch, origin top-left)
  preview  <pdf> <page> <out.png> [--dpi 40]
                                         low-res page render for eyeballing layout

The suggested crop box is a heuristic (body-text line above the figure -> top edge, caption -> bottom edge).
Always look at the cropped PNG before using it; headers, stray body text or cut-off titles are common.
"""
import os, re, subprocess, sys, tempfile


def need(tool):
    from shutil import which
    if not which(tool):
        sys.exit(f"[pdf_tools] '{tool}' not found. Install poppler-utils "
                 f"(e.g. `sudo apt-get install -y poppler-utils` or `brew install poppler`).")


def info(pdf):
    need("pdfinfo")
    out = subprocess.run(["pdfinfo", pdf], capture_output=True, text=True).stdout
    for line in out.splitlines():
        if line.split(":")[0] in ("Title", "Pages", "Page size"):
            print(line)


def text(pdf, out):
    need("pdftotext")
    subprocess.run(["pdftotext", pdf, out], check=True)
    words = len(open(out, encoding="utf-8", errors="ignore").read().split())
    print(f"wrote {out} ({words} words)")


WORD_RE = re.compile(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">([^<]*)</word>')


def load_pages(pdf, cache=None):
    need("pdftotext")
    if cache and os.path.exists(cache):
        html = open(cache, encoding="utf-8").read()
    else:
        path = cache or tempfile.mktemp(suffix=".html")
        subprocess.run(["pdftotext", "-bbox", pdf, path], check=True)
        html = open(path, encoding="utf-8").read()
    pages = []
    for chunk in html.split("<page ")[1:]:
        m = re.match(r'width="([\d.]+)" height="([\d.]+)"', chunk)
        w, h = (float(m.group(1)), float(m.group(2))) if m else (595.0, 842.0)
        words = [(float(a), float(b), float(c), float(d), t) for a, b, c, d, t in WORD_RE.findall(chunk)]
        pages.append((w, h, words))
    return pages


def lines_of(words):
    """Group words into lines by yMin (within 2pt); keep word boxes to measure spacing."""
    lines = []
    for w in sorted(words, key=lambda w: (round(w[1]), w[0])):
        if lines and abs(lines[-1]["y0"] - w[1]) < 2:
            lines[-1]["boxes"].append(w)
        else:
            lines.append({"y0": w[1], "boxes": [w]})
    for L in lines:
        b = sorted(L["boxes"], key=lambda w: w[0])
        L["x0"] = b[0][0]; L["x1"] = max(w[2] for w in b); L["y1"] = max(w[3] for w in b)
        L["words"] = [w[4] for w in b]
        L["gaps"] = [b[i + 1][0] - b[i][2] for i in range(len(b) - 1)]
    return lines


def is_body_line(L, cx0, cx1):
    """Running text spanning the column with tight word spacing (figure tick labels have big gaps)."""
    if len(L["words"]) < 6:
        return False
    if not (L["x0"] <= cx0 + 12 and L["x1"] >= cx1 - 12):
        return False
    h = L["y1"] - L["y0"]
    return 6 <= h <= 15 and max(L["gaps"] or [0]) < 14


def is_para_tail(L, prev, cx0):
    """Short last line of a paragraph: starts at the column edge right below a full body line."""
    return (prev is not None and prev.get("_body") and 8 < L["y0"] - prev["y0"] < 18
            and abs(L["x0"] - prev["x0"]) < 3 and max(L["gaps"] or [0]) < 14)


def captions(pdf, cache=None):
    pages = load_pages(pdf, cache)
    found = 0
    for pno, (pw, ph, words) in enumerate(pages, 1):
        lines = lines_of(words)
        if not lines:
            continue
        text_x0 = min(l["x0"] for l in lines); text_x1 = max(l["x1"] for l in lines)
        full = text_x1 - text_x0
        for i, w in enumerate(words):
            if w[4] in ("Figure", "Table", "Fig.") and i + 2 < len(words) and words[i + 2][4] in ("|", ":", "."):
                label = f"{w[4]} {words[i + 1][4]}"
                cap_y = w[1]
                cap_line = next((l for l in lines if abs(l["y0"] - cap_y) < 2), None)
                cap_text = " ".join(cap_line["words"])[:90] if cap_line else ""
                # caption may sit in a side column (wrapped figure): restrict horizontally
                col_x0 = w[0] - 6
                side = col_x0 > text_x0 + 0.3 * full
                x0 = col_x0 if side else text_x0 - 4
                x1 = text_x1 + 4
                # top edge: nearest running-text line above the caption that spans this column
                # never include the running header: start below the first line if it sits in the top margin
                top = (lines[0]["y1"] + 6) if lines[0]["y0"] < 60 else 40.0
                # another caption above on the same page (stacked figures) is also a boundary
                for l in lines:
                    if l["y1"] < cap_y - 1 and l["words"][0] in ("Figure", "Table") and len(l["words"]) > 1:
                        top = max(top, l["y1"] + 4)
                # nearest running-text line (or paragraph tail) above the caption within this column
                prev = None
                for l in lines:
                    l["_body"] = is_body_line(l, x0 + 4, x1 - 4)
                    if l["y1"] < cap_y - 1 and (l["_body"] or is_para_tail(l, prev, x0 + 4)):
                        top = max(top, l["y1"] + 4)
                    prev = l
                kind = "table (caption ABOVE content: crop BELOW the caption instead)" if w[4] == "Table" else "figure"
                print(f"p{pno:<3} {label:<10} caption@({w[0]:.0f},{cap_y:.0f})  {kind}")
                print(f"      caption: {cap_text}")
                if w[4] != "Table":
                    print(f"      suggested crop: {pno} {x0:.0f} {top:.0f} {x1:.0f} {cap_y - 3:.0f}")
                found += 1
    if not found:
        print("no 'Figure N |' style captions found; fall back to `preview` and pick boxes by eye")


def crop(pdf, page, x0, y0, x1, y1, out, dpi=200):
    need("pdftoppm")
    r = dpi / 72.0
    x, y, w, h = int(x0 * r), int(y0 * r), int((x1 - x0) * r), int((y1 - y0) * r)
    stem = out[:-4] if out.endswith(".png") else out
    subprocess.run(["pdftoppm", "-r", str(dpi), "-f", str(page), "-l", str(page), "-x", str(x), "-y", str(y),
                    "-W", str(w), "-H", str(h), "-png", "-singlefile", pdf, stem], check=True)
    print(f"wrote {stem}.png ({os.path.getsize(stem + '.png') // 1024} KB)")


def preview(pdf, page, out, dpi=40):
    need("pdftoppm")
    stem = out[:-4] if out.endswith(".png") else out
    subprocess.run(["pdftoppm", "-r", str(dpi), "-f", str(page), "-l", str(page), "-png", "-singlefile", pdf, stem],
                   check=True)
    print(f"wrote {stem}.png")


def opt(args, name, default):
    if name in args:
        i = args.index(name); v = args[i + 1]; del args[i:i + 2]; return v
    return default


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    cmd = a.pop(0)
    if cmd == "info":
        info(a[0])
    elif cmd == "text":
        text(a[0], a[1])
    elif cmd == "captions":
        cache = opt(a, "--bbox-cache", None); captions(a[0], cache)
    elif cmd == "crop":
        dpi = int(opt(a, "--dpi", 200))
        crop(a[0], int(a[1]), float(a[2]), float(a[3]), float(a[4]), float(a[5]), a[6], dpi)
    elif cmd == "preview":
        dpi = int(opt(a, "--dpi", 40)); preview(a[0], int(a[1]), a[2], dpi)
    else:
        sys.exit(__doc__)
