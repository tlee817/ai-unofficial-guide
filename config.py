"""
Settings for The Unofficial Guide.

Everything you're likely to change lives here, at the top, on purpose.
You'll edit THRESHOLD in Milestone 4 and the chunking numbers in Milestone 3.

Anything you set in your .env file wins over the defaults here.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).parent
load_dotenv(ROOT / ".env")


# ─── The corpus you're working with ──────────────────────────────────────────
# Change this to switch corpora, or pass --corpus on the command line.
# Options are the folder names inside corpora/. See corpora/README.md.

CORPUS = os.getenv("AI201_CORPUS", "city_guides")


# ─── Chunking (Milestone 3) ──────────────────────────────────────────────────
# city_guides is split one paragraph per chunk, each prefixed with the
# document's title and the paragraph's ## heading. The author already divided
# every guide into self-contained paragraphs of 70–500 characters, so the
# chunker follows those boundaries instead of counting characters. These three
# numbers are the guard rails around that, not the chunking itself.

CHUNK_SIZE = 800        # ceiling. A paragraph longer than this is split on
                        # sentence ends. Never reached on city_guides (max 509).
CHUNK_OVERLAP = 0       # overlap repairs cuts mid-thought; this chunker never
                        # cuts mid-thought, so there is nothing to repair.
CHUNK_MIN = 150         # floor, from criterion 4. A paragraph that would come
                        # out shorter (prefix included) is merged into its
                        # neighbour in the same section.


# ─── Retrieval (Milestone 4) ─────────────────────────────────────────────────

# Chunks average 281 characters, so eight of them is ~2,250 characters of
# context — less than the starter sent with five 650-character chunks. Measured
# rank of the answer for the five test questions at this setting: 1, 2, 8, 5, 1.
# At 5, Q3 (Pellew Sands car park) never reached the model.
TOP_K = 8               # how many chunks to pull back per question

# The relevance gate. If the best chunk is further away than this, the system
# refuses to answer instead of handing the model thin material.
#
# LOWER IS BETTER: 0.3 is a close match, 0.9 is unrelated.
#
# Measured on city_guides with the paragraph chunker (see README, "My
# relevance cutoff"): the five test questions scored 0.250–0.450; the five
# OUT_OF_SCOPE questions scored 0.803–0.975. 0.65 sits just above the middle
# of that gap, leaving headroom for real questions phrased more loosely than
# mine while refusing every different-world question by 0.15 or more.
#
# What the gate cannot do: same-world questions the corpus doesn't answer
# ("which hotel in Thornby Wells has a spa?") score 0.20–0.45 — like real
# questions — because distance measures topic, not answerability. Those are
# caught by the grounding instruction in generate.py, not by this number.
THRESHOLD = 0.65


# ─── Models ──────────────────────────────────────────────────────────────────
# Embeddings run on your own machine and cost no API quota.
# Only generation calls out to a service.

# This is the model Chroma bundles, and leaving it alone is the fast path: it
# downloads about 80 MB from Chroma's own CDN and needs nothing else installed.
#
# Setting it to any other name — unit 2's "try a second embedding model"
# stretch option — switches to loading that model from Hugging Face instead,
# which needs `pip install 'sentence-transformers>=3.4,<3.5'` first. store.py
# says so with a real error message rather than a stack trace if you forget.
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
MODEL = os.getenv("AI201_MODEL", "gemini-3.5-flash-lite")


# ─── Rate limiting and quota guards ──────────────────────────────────────────
# You should not need to touch these. They exist so that a runaway loop costs
# you a warning instead of your whole day's allowance.

REQUESTS_PER_MINUTE = 30       # outgoing calls the limiter will allow per minute
SESSION_REQUEST_BUDGET = 300   # stop and warn rather than draining the daily quota
MAX_RETRIES = 4                # on 429 / resource-exhausted, with backoff

CACHE_ENABLED = os.getenv("AI201_CACHE", "1") != "0"
CACHE_DIR = ROOT / ".cache"


# ─── Paths ───────────────────────────────────────────────────────────────────

CORPORA_DIR = ROOT / "corpora"
CHROMA_DIR = ROOT / "chroma_db"
RESULTS_DIR = ROOT / "results"


def corpus_path(name: str | None = None) -> Path:
    """Folder holding the documents for a corpus."""
    return CORPORA_DIR / (name or CORPUS) / "documents"


def collection_name(name: str | None = None, variant: str = "default") -> str:
    """
    Name of the vector-store collection for a corpus.

    `variant` lets you index the same corpus two different ways and query both
    without deleting anything — you'll want that in unit 2 when you compare
    chunking strategies.

    Chroma is fussy about collection names: 3 to 63 characters, starting and
    ending with a letter or digit, and nothing but letters, digits, underscores
    and hyphens in between. If you bring your own corpus and name the folder
    something Chroma won't accept, this cleans it up rather than failing.
    """
    import re

    raw = f"{name or CORPUS}__{variant}"
    cleaned = re.sub(r"[^A-Za-z0-9_-]", "-", raw)
    cleaned = cleaned.strip("_-")          # must start and end alphanumeric
    if not cleaned or not cleaned[0].isalnum():
        cleaned = f"c{cleaned}"
    if not cleaned[-1].isalnum():
        cleaned = f"{cleaned}0"
    return cleaned[:63].rstrip("_-") or "collection"
