# HTML fragment patterns

All classes below are already styled in `assets/template.html`. Write content as fragments in
`work/sections/NN-name.html` (one file per paper section, two-digit prefix for order) plus
`work/overview.html`, then run `scripts/assemble.py`.

Contents: 1 Section wrapper · 2 Paragraph row · 3 Lists, equations, run-in heads · 4 Figures · 5 Tables · 6 Overview

## 1. Section wrapper

```html
<section class="sec" id="method">            <!-- id must match a meta.json nav entry -->
  <div class="sec-title"><h2>3. Method</h2><span class="zh">方法</span></div>
  <div class="sub-title">3.1 Stage I: ... <span>阶段一：……</span></div>   <!-- optional subsection -->
  ...rows...
</section>
```

Typical nav ids: `abstract, intro, prelim/background, related, method, exp, discussion, concl, limits, overview`.
Use whatever the paper actually has; a subsection (e.g. Related Work inside §2) may get its own id on its `<section>`.

## 2. Paragraph row (the unit everything is built from)

```html
<div class="row">
  <div class="left">
    <div class="pid">¶ I3</div>                      <!-- stable id: section letter + index -->
    <p class="en">Significant progress ... exposing a fundamental <mark class="c">resolution trade-off</mark>.
      ... <mark class="g">While computationally scalable</mark>, this abstraction sacrifices ...
      Consequently, <mark class="t">joint modeling ... remains an unresolved challenge</mark>.</p>
    <div class="divider"></div>
    <p class="zh">……由此暴露出一个根本性的“<mark class="c">分辨率权衡</mark>”。……
      <mark class="g">这种抽象虽然计算上易于扩展</mark>，却……因此，<mark class="t">如何同时建模高频形态与长期纵向结构，至今仍未解决</mark>。</p>
  </div>
  <aside class="note c">                              <!-- note colour = the paragraph's dominant dimension -->
    <div class="fn"><span class="tag">批评既有方案</span><span class="tag light">研究空白（gap）</span></div>
    <dl>
      <dt>段落功能</dt><dd>……</dd>
      <dt>逻辑角色</dt><dd>完成“<b>问题 → 空白</b>”的推导……</dd>
      <dt>技巧 / 漏洞</dt><dd><span class="flag plus">技巧</span>……<br><span class="flag minus">漏洞</span>……</dd>
    </dl>
  </aside>
</div>
```

Highlight classes: `t` 核心论点 (yellow) · `c` 关键概念 (red) · `e` 实证证据 (blue) · `g` 让步/反驳 (green) · `m` 方法论 (purple).
Note classes: same letters. Flags: `flag plus`(技巧/强处) · `flag minus`(漏洞/遗漏/内部不一致) · `flag q`(存疑/注意/隐含假设).

## 3. Lists, equations, run-in heads

Paragraphs that contain lists use `<div class="en">` / `<div class="zh">` instead of `<p>`:

```html
<div class="en"><span class="lead">Contributions.</span> The main contributions are:
  <ol><li><b>Technically</b>, ...</li><li>...</li></ol></div>
```

Run-in paragraph headings (“Setup.”, “Baselines.”) → `<span class="lead">Setup.</span>`.

Math uses KaTeX (loaded by the template): inline `\( ... \)`, display blocks:

```html
<div class="eq">\[\mathcal{L}_i=-\frac{1}{|P(i)|}\sum_{j\in P(i)}\log\frac{\exp(q_i\cdot q_j/\gamma)}{\sum_a \exp(q_i\cdot q_a/\gamma)}\qquad(1)\]</div>
```

A paragraph broken by an equation stays one row: `<p class="en">…</p><div class="eq">…</div><p class="en">…</p>`,
then the divider and one Chinese block covering the whole paragraph.

## 4. Figures (original images, embedded at assembly)

Inside a paragraph row, append after the Chinese block (still inside `.left`):

```html
<figure class="fig after"><div class="orig-label">原图 · ORIGINAL FIGURE</div>
  <img src="{{FIG:fig3}}" alt="Figure 3" loading="lazy">
  <figcaption><b>Figure 3 | Original English caption.</b> 中文简述（可选）。</figcaption></figure>
```

- Narrow/portrait figures (single column, radar charts): `<img class="narrow" ...>` (max 520px).
- Several sub-figures side by side: wrap `<div>`s with img+figcaption in `<div class="fig-pair">`.
- A headline figure that deserves its own annotation (e.g. the teaser in the intro) gets its own row with
  `<div class="pid">图 1 · Figure 1</div>` and a note; the validator skips EN/ZH checks for such rows.
- Clicking any `.fig img` opens the built-in lightbox.

## 5. Tables

Re-type small result tables as HTML (searchable, crisp); crop as image only if they are huge or graphical.

```html
<figure class="fig"><div class="scroll-x"><table class="data">
  <thead><tr><th>Method</th><th style="text-align:right">AUROC↑</th></tr></thead>
  <tbody><tr><td>LSTM</td><td class="num">0.658</td></tr>
         <tr class="ours"><td>Ours</td><td class="num">0.719</td></tr></tbody>
</table></div><figcaption><b>Table 2 | ...</b></figcaption></figure>
```

`.best` bolds a winning cell; `.ours` tints the proposed method's row.

## 6. Overview (work/overview.html)

```html
<section class="overview" id="overview">
  <h2>论证结构总览</h2>
  <div class="sub">Argument Map · 问题 → 论点 → 证据 → 反驳 → 结论</div>
  <div class="chain">
    <div class="node n1"><h4>问题</h4><ul><li>… (I1, I2)</li></ul></div>
    <div class="node n2"><h4>论点</h4><ul><li>…</li></ul></div>
    <div class="node n3"><h4>证据</h4><ul><li>…</li></ul></div>
    <div class="node n4"><h4>反驳 / 让步</h4><ul><li>…</li></ul></div>
    <div class="node n5"><h4>结论</h4><ul><li>…</li></ul></div>
  </div>
  <div class="oneliner">
    <div class="k">作者核心主张 · 一句话版本</div>
    <p>English one-sentence version.</p>
    <p class="zhline">中文一句话版本。</p>
  </div>
  <div class="sw2">
    <div class="box strong"><h4>论证最强处：……</h4>……</div>
    <div class="box weak"><h4>论证最弱处：……</h4>……</div>
  </div>
  <details class="minor"><summary>其他值得在讨论课上追问的细节（点击展开）</summary>
    <ul><li><b>……：</b>……</li></ul></details>
</section>
```

Cite paragraph ids (I3, M6, E5 …) inside chain items so readers can jump back mentally.
