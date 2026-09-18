"""
Your test questions.

Milestone 2 asks you to write five questions your system should be able to
answer from your corpus, specific enough to have a right answer.

  ✗ "What are good dining halls?"          — no right answer
  ✓ "What do students say about wait times at Commons during lunch?"

Fill in `QUESTIONS` below. `expects` is a word or short phrase you'd expect a
correct answer to contain — you'll use it in unit 2 when you build a scorer,
and having written it now means you decided what "correct" meant before you saw
any results.

`OUT_OF_SCOPE` holds five questions your documents clearly don't cover. You
need these in Milestone 4 to find where your relevance cutoff belongs, and
again in unit 2, where `run_eval.py` runs them through the gate and writes what
happened into your run log — that's the evidence for criterion 3.

Swap them for your own if you like. Keep five of them either way: criterion 3
names a target of "4 of 5", and four of three is not a thing.
"""

QUESTIONS = [
    # Corpus: city_guides. Each `expects` is the corpus's own word for the
    # answer, so a correct reply should contain it verbatim.
    #
    # Q1-Q3 are single facts in a single sentence. Q4's direct answer is in a
    # cross-cutting guide rather than the town's own. Q5 is deliberately hard:
    # the true answer is one sentence in guide_accessibility.md, while nine
    # identical "Practical notes" boilerplate sections say the opposite.
    {
        "question": "Which day of the week is the Kestrelford market?",
        "expects": "Saturday",
    },
    {
        "question": "Which day is the Givens Mill tearoom closed?",
        "expects": "Tuesday",
    },
    {
        "question": "Where is the free car park in Pellew Sands?",
        "expects": "behind the station",
    },
    {
        "question": "Which town in the region has restaurant kitchens that serve after 9pm?",
        "expects": "Marchwood",
    },
    {
        "question": "Is there mobile phone coverage in Corry Vale?",
        "expects": "absent",
    },
]

# Questions from a different world entirely. Your gate should refuse all five.
#
# There are five of these because criterion 3 in criteria.md names a target of
# "at least 4 of 5" — you need five things to try before you can report 4 of 5.
# `run_eval.py` runs these through retrieval and the gate on every eval and
# records what happened, so criterion 3 has evidence in the run log alongside
# the others. They cost no model calls: a refusal never reaches the model.
OUT_OF_SCOPE = [
    "What is the capital of Mongolia?",
    "How do I change the oil in a diesel engine?",
    "Who won the 1994 World Cup?",
    "What is the recommended dosage of ibuprofen for a headache?",
    "How do I write a for loop in Rust?",
]


def answered() -> list[dict]:
    """The questions you've actually filled in."""
    return [q for q in QUESTIONS if q.get("question", "").strip()]
