# The Unofficial Guide

**tlee817** — corpus: `city_guides`

> **This file is your submission.** Fill it in as you go — most sections get
> written during the milestone that produces them, not at the end.
>
> How the starter works, and every command you'll need, is in `RUNNING.md`.
> Leave that file alone.
>
> **Paste everything as text.** No screenshots, no video. A typed table gets
> full credit; a picture of the same table gets none.
>
> Delete these instruction blocks as you replace them. The `<!-- -->` comments
> are notes to you and don't show up when the page renders — you can leave them
> or remove them.

---

# Unit 1

## What This Does

<!-- Three or four sentences. Which corpus you picked, and the kinds of
     questions your system answers. Write it for someone who has never seen
     this repo.

     Milestone 5. -->

## Chunking Strategy

**Chunk size:** one paragraph, prefixed with the document's `# title` and the
paragraph's `## heading`. Measured across the index: 157–509 characters,
average 281. `CHUNK_SIZE = 800` in `config.py` is a ceiling that is never
reached; `CHUNK_MIN = 150` is a floor — a paragraph that would come out shorter
is merged into its neighbour in the same section (that happens four times, all
one-sentence asides in `guide_seasons.md` and `guide_eating.md`).
**Overlap:** 0.

**What I saw in Milestone 1.** All fourteen guides are markdown with the same
shape: a `# title`, an intro paragraph, then `##` sections of one or two
paragraphs. I measured every section: 84 of them, all between 158 and 691
characters. The nine town guides use the *same seven headings* in the same
order, and `## Practical notes` is word-for-word identical in all nine. The
starter's fixed 800-character windows cut straight through this — `app.py
chunks` showed a chunk ending in `## Eat and drin` and another that was 24
characters long.

**What I planned, and why I changed my mind.** My first plan was one `##`
section per chunk — the structure is obvious and every section fits. Before
writing it, I compared six strategies in memory using the same embedding model
and cosine distance the pipeline uses, on my five test questions and the five
out-of-scope ones. Section-per-chunk retrieved *worse* than the starter: the
answer stayed in the top 5 for only 4 of 5 questions, two of them at rank 5.
Two things caused that. Nine towns sharing the same headings means nine
near-identical "Eat and drink" chunks, so a topic question gets a wall of the
wrong towns. And Q5's answer ("genuinely absent in parts of Corry Vale") shares
a section with an unrelated hospital paragraph, which diluted it from 0.25 to
0.53. Splitting on paragraphs instead fixed the second problem outright. The
title prefix exists because "## Getting there" followed by bus times could be
any of nine towns; `# Kestrelford` on the front puts the town name in the
chunk.

**Why no overlap.** Overlap repairs cuts mid-thought. This chunker never cuts
mid-thought — every chunk starts at a heading or paragraph and ends at a
sentence end — so there is nothing to repair, and overlapping unrelated
paragraphs would only add noise.

**What it cost.** Retrieval-only comparison (`app.py retrieve`, no model call),
starter chunker kept as index variant `fallback`:

| Question | Before: best distance / rank of answer | After: best distance / rank of answer |
|---|---|---|
| Q1 Kestrelford market day | 0.394 / 1 | 0.251 / 1 |
| Q2 Givens Mill tearoom closed | 0.440 / 1 | 0.382 / 2 |
| Q3 Pellew Sands free car park | 0.402 / 1 | 0.414 / **not in top 5** |
| Q4 kitchens after 9pm | 0.431 / 4 | 0.450 / 5 |
| Q5 Corry Vale coverage | 0.265 / 1 | 0.250 / 1 |

The starter got 5 of 5 by accident of where its 800-character boundaries fell;
it fails criterion 4 by construction. The new chunker gets 4 of 5 by design.
Q3 is the loss: six other sections in the corpus talk about "car parks" and
"free" parking, and the Pellew Sands paragraph says "free *lot*". Smaller
chunks carry more topic and less document identity, and that question is where
it shows. **Going into unit 2, Q3 is my predicted criterion 1 miss — not Q5, as
I wrote in Milestone 2.**

## Sample Chunks

From `python app.py chunks -n 5` (111 chunks total, five spread across the
corpus). For each: could someone answer a question from only this?

**Chunk 1** — source: `guide_accessibility.md#0` — produced by: `chunker.py::split_documents`

```
# Getting around the region with limited mobility

An honest assessment rather than a promotional one. Some of these places are
difficult and it is better to know in advance.
```

The weakest of the five: an intro paragraph that says what the document *is*
rather than a fact about a place. It stands alone, but no test question would
land on it. It stays because dropping intros would lose the town descriptions
("a Victorian seaside resort", "a working fishing port") in the other guides.

**Chunk 2** — source: `guide_corry_vale.md#3` — produced by: `chunker.py::split_documents`

```
# Corry Vale

## Eat and drink

One pub in the largest village serves food seven days a week. A second, in the third village, opens Thursday to Sunday. There is a farm shop at the valley mouth that sells bread, cheese and little else, and it closes at 4pm. Bring supplies; this is not a place with options.
```

Yes. Which place, which topic, and four concrete facts. "When does the Corry
Vale farm shop close?" is answerable from this alone.

**Chunk 3** — source: `guide_givens_mill.md#3` — produced by: `chunker.py::split_documents`

```
# Givens Mill

## Eat and drink

A tearoom attached to the mill, open 10 to 4 daily except Tuesdays, which sells bread made from the flour ground twenty metres away and is the reason most people come. One pub, food served lunchtimes and Thursday to Saturday evenings.
```

Yes — this is the chunk that answers test question 2 ("Which day is the Givens
Mill tearoom closed?"). The answer is one clause inside one sentence, and the
chunk is small enough that it isn't buried.

**Chunk 4** — source: `guide_marchwood.md#1` — produced by: `chunker.py::split_documents`

```
# Marchwood

## Getting there

Every railway line in the region meets here, which is the city's defining feature. Trains to Brightwater run every 40 minutes until 11pm. The airport is 20 minutes out by a dedicated bus that runs every 15 minutes and costs more than the equivalent taxi shared between three people.
```

Yes. Without the `# Marchwood` line this would be an anonymous "Getting there"
— nine documents have one. The prefix is doing its job here.

**Chunk 5** — source: `guide_regional_transport.md#7` — produced by: `chunker.py::split_documents`

```
# Getting around the region

## Walking and cycling

Cycling is pleasant on the river path and the trackbed, and unpleasant on Mill
Road and the coast road, neither of which has a shoulder.
```

Yes, narrowly. One thought, complete. It is the second paragraph of its
section — the first, about walking routes, is its own chunk — and this is the
case for paragraph-level over section-level: "is the coast road good for
cycling?" matches this cleanly instead of a chunk that is mostly about
footpaths. The hard line-wrap after "Mill" is how the source file is written;
I left it rather than have the chunker rewrite text.

## Sample Answer

<!-- One complete question and answer, pasted as text, with the source line
     visible. Milestone 4. -->

**Question:**

**Answer:**

```
```

**My relevance cutoff:**

<!-- The number you set in config.py, and how you got there.

     You ran five questions your corpus covers and the five in OUT_OF_SCOPE
     that it clearly doesn't, and wrote down the best distance for each. What
     did those two groups look like? Where was the gap? Put the actual numbers
     here — the table below wants all ten rows.

     Milestone 4. -->

| Question | In corpus? | Best distance |
|---|---|---|
|  |  |  |

## How I Used AI

<!-- Two specific moments. For each: what you asked for, what came back, and
     what you changed about it.

     "I asked Claude to write the chunking function from my notes. It ignored
     the overlap, so I added that myself" is the level of detail we're after.
     "I used AI to help me code" is not.

     Milestone 5. -->

**1.**

**2.**

<!-- ── Stretch features ─────────────────────────────────────────────────────
     Doing one? Say so here BEFORE you start. A feature this README never
     claims earns nothing.
     ───────────────────────────────────────────────────────────────────────── -->

---

# Unit 2

<!-- These sections get ADDED to what's already above. Don't delete or rewrite
     unit 1 — the point is that someone can see what you said before you knew
     how it went. -->

## Run Log — Before

<!-- Your five criteria, three runs each. `python run_eval.py --label before`
     runs the questions, puts the OUT_OF_SCOPE ones through the gate, and
     writes it all into results/ for you. Targets come from criteria.md; the
     verdict column is your call.

     Criterion 3 is measured in one deterministic pass rather than three, so
     the same number goes in all three run columns. That's correct, not lazy.

     Milestone 1. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 |  |  |  |  |
| 2. Every answer names a source | 5 of 5 |  |  |  |  |
| 3. Gate stops out-of-corpus questions | 4 of 5 |  |  |  |  |
| 4. | | | | | |
| 5. | | | | | |

<!-- Underneath, paste the REAL output for each criterion from one of your
     runs — the actual text your system produced, not a description of it.
     Name the file and function that produced it. -->

## Verdicts

<!-- MET or MISSED for each of the five, against the target you wrote last
     unit — not a new one. Plus a sentence on how you decided. That sentence
     matters most where it was close.

     If your target said 4 of 5 and your runs came out 4, 3, 4, that's a MISS.
     The target has to hold, not show up occasionally.

     Milestone 2. -->

| # | Criterion | Verdict | How I decided |
|---|---|---|---|
| 1 |  |  |  |
| 2 |  |  |  |
| 3 |  |  |  |
| 4 |  |  |  |
| 5 |  |  |  |

## Diagnoses

<!-- For each miss: which stage caused it, and how. The stage alone isn't
     enough — you need the mechanism.

     Not a diagnosis: "Question 3 didn't work."
     A diagnosis:     "Question 3 asks about laundry costs. The answer is in
                       one sentence that got split across two chunks, so
                       neither chunk on its own contains it."

     The five stages: loading → chunking → embedding → retrieval → generation.

     Look for a pattern. If three misses all ask about numbers, that's one
     problem, not three.

     Missed nothing? Say so, then say honestly whether your targets were set
     low, and which one you'd tighten and to what.

     Milestone 3. -->

## The Improvement

**What I changed:**

**Why I picked it:**

<!-- Connect it to a specific diagnosis above in one sentence. If you can't,
     you picked a fix because it sounded impressive. -->

### Run Log — After

<!-- Same format, same five criteria, three runs each.
     `python run_eval.py --label after` -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 |  |  |  |  |
| 2. Every answer names a source | 5 of 5 |  |  |  |  |
| 3. Gate stops out-of-corpus questions | 4 of 5 |  |  |  |  |
| 4. | | | | | |
| 5. | | | | | |

**Did it help?**

<!-- Say plainly whether it did, and how you know. If it made things worse,
     say that — a change that backfired, honestly reported, earns full credit
     and is more interesting than one that worked. What matters is that you can
     tell.

     Milestone 4. -->

## What's Still Broken

<!-- For each criterion still missed after your fix: what you'd do about it,
     and why you stopped where you did.

     "I ran out of time" is fine if it's true. Pretending nothing is left is
     not.

     Milestone 5. -->

## What I'd Do Differently

<!-- Knowing what you know now — which of your five criteria would you write
     differently, and why?

     Milestone 5. -->
