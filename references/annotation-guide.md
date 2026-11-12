# Annotation guide: highlighting, translation, critique

Contents: 1 Five highlight dimensions · 2 Chinese translation · 3 Annotation cards · 4 Critical-reading checklist · 5 Overview

## 1. Five highlight dimensions

The point of highlighting is to let a reader skim one colour and see one layer of the argument.
Mark meaningful *clauses*, not single common words; typically 2–6 marks per paragraph. Too many marks
make the colours useless.

| class | 维度 | mark when the text… | examples |
|---|---|---|---|
| `t` 黄 | 核心论点 / thesis | states the paper's claim, a sub-claim it will defend, the gap it fills, or a conclusion drawn from evidence | “we propose X, which reconciles …”, “Together, these results demonstrate …”, “remains an unresolved challenge” |
| `c` 红 | 关键概念 / 术语 | introduces or names a concept the argument depends on (first or defining use) | “resolution trade-off”, “identity shortcut”, “circaseptan”, “M ≪ N” |
| `e` 蓝 | 实证证据 / 数据 | reports numbers, results, statistical tests, dataset scale, observed patterns in figures | “52 of 58 tasks (89.7%)”, “0.817→0.928”, “6.8M hours” |
| `g` 绿 | 让步 / 反驳处理 | concedes a point, anticipates an objection, rejects an alternative, limits a claim | “While computationally scalable, …”, “we caution against interpreting …”, “Conventional X is ill-suited …” |
| `m` 紫 | 方法论说明 | describes how something is done: design choices, objectives, protocols, splits, baselines, hyper-parameters | “positive pairs are segments from the same subject”, “linear probing on frozen embeddings”, “70/15/15 split” |

When a span fits two dimensions, choose the one that serves the argument-structure reading (a number used to
make a claim is `e`; a design choice defended against an alternative is `g` for the defence and `m` for the design).

**Chinese mirrors English.** Highlight the corresponding Chinese phrase with the same class, so the colour
layer works in either language. The Chinese span will not be a word-for-word match; mark the clause that
carries the same meaning. Aim for roughly the same count as the English paragraph.

## 2. Chinese translation

Goal: reads like a Chinese academic paper, not a gloss.

- 意译为主：重组语序，长句拆短，被动改主动（“it is shown that” → “研究表明”），英文的名词堆叠改成动词结构。
- Keep established terms consistent across the whole document; on first use give the English abbreviation in
  parentheses (光电容积脉搏波（PPG）). Keep model names, dataset names, metrics (AUROC), and math as-is.
- Keep citations `[9–16]` and equation numbers in place.
- Don't silently "fix" the paper. If the source is inconsistent (e.g. a number that contradicts its own
  definition), translate what it says and add a short 注 in parentheses, then raise it in the annotation.
- Formulas inside Chinese text may reuse the same `\( \)` KaTeX snippets.

## 3. Annotation cards (right column)

Every paragraph row gets one card with three fields. Keep each field to 1–3 sentences; the card sits beside
the paragraph and should be readable in one glance.

- **段落功能** — what the paragraph *does*: 引出问题 / 背景铺垫 / 界定难点 / 批评既有方案 / 提出论点 / 形式化 /
  方法细节 / 设计辩护 / 提供证据 / 机制解释 / 让步处理 / 预设反驳 / 总结 / 局限声明 … Put the short label in the
  dark `tag`, a finer label in the light `tag`.
- **逻辑角色** — where it sits in the argument chain: which earlier claim it supports, which later section
  answers it, which contribution it backs. Name paragraph ids / sections explicitly (“回应 M6 的恒等捷径”).
- **技巧 / 漏洞** — the most valuable field. Point out rhetorical moves that work (`flag plus` 技巧/强处) and
  weaknesses (`flag minus` 漏洞, `flag q` 存疑/注意). Be specific and checkable: quote the number, name the
  missing control, cite the contradicting paragraph. Not every paragraph has a flaw; don't invent one, but
  don't be a fan either — a course reader wants to know where to push in discussion.

Card colour = the paragraph's dominant dimension (thesis paragraphs yellow, evidence blue, etc.).

## 4. Critical-reading checklist

Run through this while reading; most real findings come from here.

- **Internal consistency of numbers**: splits that don't add up, totals vs. percentages, a value contradicting
  its own definition (patch sizes × bin width), main text vs. appendix figures.
- **Claim strength vs. evidence**: abstract/conclusion wording (“consistently”, “significantly”, “demonstrate …
  leads to”) against the actual win counts and margins; causal language from comparative evidence.
- **Concession contradicted elsewhere**: a caveat in §4.x that the conclusion or contributions ignore.
- **Baselines**: built in-house vs. the real prior systems (strawman risk); same data/capacity (good control).
  Which baseline is the *stronger* one, and how large is the gain over it specifically?
- **Statistics**: independence assumptions across correlated tasks; bootstrap only over test set; relative %
  vs. absolute points mixed; post-hoc selection of the most favourable examples.
- **Circularity**: a visualization or probe that could show the claimed property just because of an input
  the model was given (e.g. time-of-day positional encodings → periodic similarity).
- **Missing ablations**: the components the narrative leans on most but never removes.
- **Related work framing**: the closest prior method folded into a broad category and not compared.
- **Citations that don't fit** the sentence they support.
- **Labels and cohort**: self-reported labels, single-site or condition-specific cohorts, external validity.
- **Notation clashes**, train/inference mismatches, unstated handling of missing data.

Collect the minor ones in the overview's `details.minor` list.

## 5. Overview

- **逻辑骨架**: five nodes 问题 → 论点 → 证据 → 反驳/让步 → 结论, each 2–4 bullets with paragraph ids.
- **一句话版本**: the authors' core claim as one English sentence plus its Chinese rendering — what they argue,
  not your verdict.
- **最强处 vs 最弱处**: one each, a short paragraph with concrete evidence. Strongest is usually a
  well-controlled comparison or a prediction the paper made and confirmed; weakest is usually where the
  headline claim outruns the margin, a circular piece of evidence, or a contradiction between sections.
