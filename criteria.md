# Acceptance criteria — The Unofficial Guide

Five criteria that say what "working" means for this system, written in unit 1
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"Retrieval works"* is an opinion. *"For at
least 4 of my 5 test questions, the top results include a chunk containing the
answer"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter or looser one. A reason that says something about your corpus or your
pipeline earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## 1. Retrieved chunks contain the answer

For at least 4 of my 5 test questions, the retrieved chunks include one that
contains the answer.

**Why this target:**
Q5 (mobile coverage in Corry Vale) is built to be hard on purpose. The correct
sentence is in one section of `guide_accessibility.md`, while nine word-for-word
identical `## Practical notes` chunks across the town guides say coverage is
"good in the centre" and can crowd the top-5. Q4's direct answer is in a
cross-cutting guide (`guide_eating.md`) rather than the town's own. I expect
one of those two to miss. Expecting both to hit would be pretending the corpus
is cleaner than it is.

---

## 2. Every answer names a source

Every answer the system produces names at least one source document.

**Why this target:**
`generate.py::build_prompt` labels every chunk `[from filename]`, and the
`GROUNDING_INSTRUCTION` tells the model to name the file it used. The gate
refuses before any answer can be produced without chunks, so there is never an
answer with nothing to cite. The only failure path left is the model ignoring
an explicit instruction on a ~1,000-token prompt. If that happens even once in
five, the prompt needs fixing, not the target — so it has to be all five.

---

## 3. The relevance gate stops out-of-corpus questions

When I ask a question my documents clearly don't cover, the relevance gate
stops it and the system returns "I don't have enough information about that" —
in at least 4 of 5 tries.

<!-- The five questions are the ones in `OUT_OF_SCOPE` at the bottom of
     `questions.py`, and `run_eval.py` puts them through the gate and writes
     what happened into your run log. Swap them for your own if you'd rather —
     just keep five of them, or the "4 of 5" above has nothing to be 4 of. -->

**Why this target:**
I have one data point so far: the Milestone 1 question ("how do I get to
Kestrelford?") scored 0.445 against the 0.6 cutoff. I have not measured the
out-of-scope group yet — that is Milestone 4. I'm keeping 4 of 5 rather than
5 of 5 because one `OUT_OF_SCOPE` question, ibuprofen dosage for a headache,
overlaps the corpus's own "minor injuries unit" and "hospital" wording, which
appears in nine boilerplate chunks, so it may land closer than the other four.
If Milestone 4 shows a clean gap, this target was too loose and I'll say so in
unit 2.

---

## 4. Chunks respect section boundaries

All 5 chunks printed by `python app.py chunks -n 5` start at a heading (`#` or
`##`) or the start of a paragraph, and end at the end of a sentence — no
sentence or word cut at either edge. Additionally, no chunk in the index is
shorter than 150 characters.

**Why this target:**
Every one of the 84 `##` sections in `city_guides` is between 158 and 691
characters (measured in Milestone 1), so a section always fits in one chunk at
any sensible size. The starter's fixed 800-character windows currently produce
a chunk ending in `## Eat and drin` and a 24-character tail fragment — that is
exactly the failure this criterion catches. 5 of 5 rather than 4 of 5 because
there is no hard case to excuse: a single cut sentence means the chunker
ignored the structure. The 150-character floor is the observable for "no
leftover fragments"; the shortest real section is 158.

---

## 5. The named source is the right one

For 5 of 5 test questions, at least one file the answer names actually
contains the `expects` phrase for that question.

**Why this target:**
Criterion 2 only checks that *a* file is named. In this corpus a plausible
wrong citation is easy: nine town guides contain identical boilerplate, and
that boilerplate contradicts `guide_accessibility.md` on where the hospital is
and whether Corry Vale has coverage — so the model can cite a real file that
does not hold the fact. 5 of 5 because a wrong citation is worse than none: a
reader who opens the named file and finds nothing stops trusting the system.
Checkable without judgement — grep the named file for the `expects` phrase.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 2 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 1. Retrieved chunks contain the answer

         For at least 4 of my 5 test questions, the retrieved chunks include
         one that contains the answer.

         **Why this target:** ...

         > **Revised in unit 2:** For at least 4 of 5 questions, the top three
         > results contain the answer.
         >
         > **Why revised:** I couldn't judge "the chunks include one that
         > contains the answer" the same way twice — I scored two questions
         > differently on Monday than on Wednesday. The new version is
         > something I can actually check.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said 4 of 5 but got 2 of 5, so 2 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.

     The whole reason the originals stay visible is so someone can see what you
     said before you knew the answer.
     ───────────────────────────────────────────────────────────────────────── -->
