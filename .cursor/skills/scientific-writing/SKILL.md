---
name: scientific-writing
description: >-
  Enforces Caio's Nature-grade scientific writing style and integrity contract.
  Apply whenever drafting, revising, editing, reviewing, or structuring academic
  prose — abstracts, introductions, related work, methods, results, discussion,
  limitations, conclusions, manuscripts, papers, theses, or paper-facing docs.
  Triggers on write the abstract, draft the introduction, revise this section,
  scientific writing, manuscript, paper prose, Nature style, or any request that
  produces or evaluates scholarly text. Use even when the user does not explicitly
  ask — always the right default for academic writing in this project. Style and
  structure only; never fabricate results, citations, or claims beyond the evidence.
---

# Scientific Writing — Caio

> A paper is an argument, not a report. Its job is to make one important thing understood and
> believed by a reader who is smart but not inside your head. Every sentence either advances that
> argument or is noise. The failure mode to fear is not "too simple" — it is "templated, hedged,
> and forgettable," the tell-tale texture of text a machine wrote and no one owned.

This skill governs how Caio's academic prose reads. It is a **style and integrity contract**, not a
content generator. The ideas, results, and interpretations come from Caio. This skill decides how
they are worded, structured, and defended on the page.

The target voice is **Nature-grade**: conceptually clear, technically precise, accessible to a
neighboring-field reader, and unafraid to state why the work matters. Dense enough to respect the
reader's intelligence, clear enough that they never re-read a sentence to parse it.

---

## The ten rules of the house style

### 1. Lead with the point, then support it
Every paragraph states its claim in the first sentence, then earns it. Never build up to the point
across five sentences of throat-clearing and reveal it at the end. Scientific readers skim first
sentences; make them load-bearing.

**Ask of every paragraph:** *If a reader read only the first sentence, would they get the point?*

### 2. Accessible does not mean dumbed down
The goal is a reader in an adjacent field understanding the argument without understanding every
technical detail. Achieve this by explaining the *why* and the *stakes* in plain language, while
keeping the *how* precise and technical. Never sacrifice a correct technical term for a vague one —
define it once, then use it. Clarity comes from structure and framing, not from vagueness.

### 3. Never hedge what you can state
Academic writing rots into mush when every claim is wrapped in "it could be argued that,"
"this may potentially suggest," "to some extent." State what the evidence shows, directly. Reserve
hedging for genuine uncertainty — and when you do hedge, hedge *precisely* ("agreement was high for
categorical fields but degraded for free-text fields") rather than *diffusely* ("results were
somewhat mixed"). A precise limitation is strong writing; a vague qualifier is weak writing.

### 4. Do not esquiva — confront the hard thing
The most important sentence in a paper is often the one admitting what the work does *not* show.
Never write around a limitation, bury it, or hope the reviewer misses it. Name it plainly, then
explain why the contribution still stands. A paper that confronts its weakness is more credible,
not less. (Example: agreement without a gold standard cannot distinguish "all correct" from "all
wrong in the same way" — state this as a headline limitation, do not tuck it into a subordinate
clause.)

### 5. Impact is a claim you make, not a mood you gesture at
The "why this matters" must be concrete and specific, tied to a real consequence — a decision that
becomes possible, a cost that drops, a process that scales. Never gesture vaguely at importance
("this is an important area with many applications"). If you cannot name the specific stake, you
have not yet found the impact — keep thinking, do not paper over it with grandeur.

### 6. Precision in numbers, restraint in adjectives
Let the numbers carry the weight. "Reduced weighted error by ~10%" is worth more than "dramatically
improved." Strip intensifiers — "very," "significantly" (unless statistical), "highly,"
"remarkably." If a result is impressive, the number shows it; the adjective only signals insecurity
about whether the number speaks.

### 7. Structure carries the argument
Sections, paragraph order, and figure placement are part of the writing. The reader should be able
to follow the logical spine — problem → why it's hard → what we did → what we found → what it means
— without getting lost. A well-placed figure that tells the story at a glance (the "money figure")
is worth a page of prose. Reference it early and return to it.

### 8. Cite to support, never to decorate
Every citation earns its place by backing a specific claim. Never pad a related-work section with
name-drops that don't connect to the argument. When citing Caio's own sources, represent what each
source actually argues — never invent a finding to fit a sentence. **If a citation is not on hand,
mark it `[CITATION NEEDED: <what it must support>]` and move on — never fabricate an author, year,
title, or result.**

### 9. Own every sentence
The test for AI-slop: could Caio defend this exact sentence in a viva? If a sentence is generic
enough that it could appear in any paper on any topic, it is filler — cut it or make it specific to
*this* work. Prose that says nothing falsifiable, nothing particular, nothing that could be wrong,
is the signature of text no human authored. Delete it.

### 10. In Methods, the *how* must be extractable, not buried
Methods sections are not read start to finish; they are mined. A reader wants a specific value (the
temperature, the retry count, the exact metric) and needs to find it in seconds, not excavate it
from a paragraph. So in any procedural or configuration-heavy section, the *how* is the content and
must be visually extractable, while the *why* shrinks to at most one clause per decision.

Concretely:
- **Put settings, parameters, model lists, and mode choices in tables**, one row per item, with a
  short "purpose"/"rationale" column carrying the justification. A parameter buried in prose is a
  parameter the reader will miss.
- **Formulas go in display math, defined symbol by symbol** — never describe a metric in words when
  an equation reproduces it exactly. If the reader cannot recompute the quantity from the section,
  the section has failed.
- **A worked example or a small diagram beats a paragraph of explanation** for anything with steps
  (how five labels become a coefficient, how a distance function scores two values). Show the
  mechanism; don't narrate around it.
- **Reserve prose for the one or two points a table cannot hold** — a caveat that qualifies a
  result, an asymmetry that carries into the Discussion. Give each its own bold lead-in so it is
  scannable too.
- The failure mode to avoid: the *how* (the extractable, reproducible content) drowning in an ocean
  of *why*. If a reader skims the section and cannot leave with the exact configuration, rewrite it
  as tables plus equations plus a few flagged notes.

This rule outranks rule 1's "prose-first" instinct *inside* Methods: front-load structure (tables,
equations), not sentences. Rules 3, 6, and 9 still apply to whatever prose remains.

---

## The AI-slop blocklist — phrases and patterns to never emit

These are the tells that make academic prose read as machine-generated. Avoid all of them.

| Banned pattern | Why it's bad | Do instead |
|---|---|---|
| "It is important to note that…" | Empty throat-clearing | State the thing directly |
| "This paper delves into…" / "delve" | Slop signature word | "We study…" / "We measure…" |
| "In today's rapidly evolving landscape…" | Contentless preamble | Open on the specific problem |
| "plays a crucial/vital/pivotal role" | Vague importance-gesturing | Name the specific role |
| "a wide range of" / "various" / "numerous" | Fake precision | Give the actual number or list |
| "leverage" (as verb), "utilize" | Corporate padding | "use" |
| "robust," "powerful," "cutting-edge," "state-of-the-art" (as filler) | Marketing adjectives | Show the property with evidence |
| "Furthermore, Moreover, Additionally" stacked | Mechanical connective tissue | Vary or cut; let logic connect |
| "it could be argued that" | Cowardly hedging | Argue it, or drop it |
| "significantly" (non-statistical) | False weight | Give the magnitude |
| Tricolon everywhere ("clear, concise, and compelling") | Rhythmic filler | One precise word |
| Restating the section title as sentence 1 | Zero information | Start with the actual claim |
| Concluding paragraph that summarizes with no new synthesis | Wasted real estate | End on implication or the open question |

---

## How to write each section (paper spine)

The default spine is Nature-style: short, front-loaded, methods deep but not first.

- **Abstract** — 150–200 words. Context → gap → what we did → key result (with a number) →
  implication. Write it last. No citations, no jargon that isn't unavoidable.
- **Introduction** — Funnel from why-the-problem-matters to the specific research question, ending
  in explicit contributions as a short list. The question must be *tractable* and stated as a
  question the paper actually answers.
- **Related Work** — Organized by idea, not by paper. Each cluster ends by locating *this* work
  relative to it. Descriptive, but every sentence connects to the argument.
- **Data / Methods** — Maximum precision, full reproducibility. This is where technical density is a
  virtue, not a vice. Describe decisions and their rationale, not just settings. A pipeline diagram
  earns its place here. Apply rule 10: the reader mines this section for exact values, so front-load
  tables and equations and let prose carry only what a table cannot — the *how* must be extractable
  in seconds, not buried in explanation.
- **Results** — Report, do not interpret. Numbers, tables, figures. Prose describes what the table
  shows and points to the pattern; saves the "why" for Discussion. Lead with the headline result.
- **Discussion** — The authorial core. Interpret, confront limitations head-on (rule 4), distinguish
  what is shown from what is suggested. This section is never delegated wholesale — it is where the
  thinking is visible.
- **Limitations & Future Work** — Honest and specific. The most important limitation gets its own
  paragraph, not a buried line.
- **Conclusion** — One paragraph. Recap the contribution and end on impact or the next open
  question. No new numbers.

---

## Integrity guardrails (non-negotiable)

This skill accelerates *writing*, never *claiming*. The ethical line:

- **Never fabricate** results, numbers, citations, author names, or findings. A missing citation is
  marked `[CITATION NEEDED: …]`, never invented.
- **Never overstate.** The prose may not claim more than the experiment showed. If results are
  preliminary, the writing says so — confidently, without apology (rule 3 governs *how*: precise,
  not hedged into mush).
- **Caio authors the ideas.** This skill words and structures them. Interpretation, experimental
  design, and conclusions are his. When drafting Discussion or Introduction framing, produce a
  proposal for him to own and edit — never a final claim he hasn't endorsed.
- **Disclose AI assistance.** Papers drafted with this skill should carry an acknowledgements line:
  *"LLM-based tools were used to assist with drafting and formatting; all experimental design,
  analysis, interpretation, and conclusions are the author's own."*

---

## Revision checklist

When drafting or revising any section, apply in order:

1. **Point-first** — Does every paragraph state its claim in sentence one?
2. **Slop scan** — Any phrase from the blocklist? Any sentence generic enough for any paper?
3. **Hedge audit** — Is any vague qualifier standing in for a precise statement?
4. **Confrontation** — Is the hardest limitation named plainly, or written around?
5. **Impact** — Is "why it matters" concrete and specific, or gestured at?
6. **Numbers over adjectives** — Are intensifiers doing work the data should do?
7. **Ownership** — Could Caio defend each sentence in a viva?
8. **Integrity** — Any claim exceeding the evidence? Any citation not backed by a real source?
9. **Extractability (Methods only)** — Can a skimming reader leave with the exact configuration in
   seconds? Are settings in tables, metrics in equations, and prose limited to flagged caveats — or
   is the *how* buried in an ocean of *why*?
