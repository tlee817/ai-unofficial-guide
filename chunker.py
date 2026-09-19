"""
Stage 2 of the pipeline: splitting documents into chunks.

`split_documents` splits each document one paragraph per chunk and prefixes
every chunk with the document's title and the `##` heading it sits under.
Written for `city_guides` (Milestone 3): fourteen markdown guides whose
authors already divided them into headed sections of one or two paragraphs,
each a complete thought. The chunker follows those boundaries instead of
counting characters.

`fallback_split` is the starter's original fixed-window chunker. It stays here
as the baseline for unit 2's before/after comparison — index it with
`--variant fallback` to keep both side by side.
"""

import re
from dataclasses import dataclass

import config
from ingest import Document


@dataclass
class Chunk:
    """One piece of one document."""

    text: str
    source: str        # which file it came from
    index: int         # which chunk within that file, starting at 0
    produced_by: str   # the function that made it — cite this in your README

    @property
    def label(self) -> str:
        return f"{self.source}#{self.index}"


def fallback_split(
    documents: list[Document],
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[Chunk]:
    """
    The starter's original chunker. Fixed-size character windows with overlap.

    Keep this function. Milestone 3's stop rule points back at it, and having
    something to compare your own strategy against is useful in unit 2.
    """
    chunk_size = chunk_size or config.CHUNK_SIZE
    overlap = overlap or config.CHUNK_OVERLAP

    if overlap >= chunk_size:
        raise ValueError("overlap has to be smaller than chunk_size")

    chunks: list[Chunk] = []
    for doc in documents:
        start = 0
        index = 0
        while start < len(doc.text):
            piece = doc.text[start : start + chunk_size].strip()
            if piece:
                chunks.append(
                    Chunk(
                        text=piece,
                        source=doc.source,
                        index=index,
                        produced_by="chunker.py::fallback_split",
                    )
                )
                index += 1
            start += chunk_size - overlap

    return chunks


def _title_and_sections(text: str) -> tuple[str, list[tuple[str | None, str]]]:
    """
    Pull the `# title` off the top and split the rest on `## ` headings.

    Returns the title (empty if the document has none) and a list of
    (heading, body) pairs in document order. Text before the first `##` — the
    intro paragraph in every town guide — comes back with heading None. A
    document with no headings at all yields one (None, whole_text) pair, so
    corpora that aren't markdown still chunk sensibly.
    """
    lines = text.split("\n")
    title = ""
    if lines and lines[0].startswith("# "):
        title, lines = lines[0].strip(), lines[1:]

    sections: list[tuple[str | None, str]] = []
    heading: str | None = None
    current: list[str] = []
    for line in lines:
        if line.startswith("## "):
            sections.append((heading, "\n".join(current).strip()))
            heading, current = line.strip(), []
        else:
            current.append(line)
    sections.append((heading, "\n".join(current).strip()))

    return title, [(h, body) for h, body in sections if body]


def _paragraphs(body: str) -> list[str]:
    """Split on blank lines. A single newline is a hard wrap here, not a break."""
    return [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]


def _sentences(paragraph: str) -> list[str]:
    return [s for s in re.split(r"(?<=[.!?])\s+", paragraph) if s]


def _pack(paragraphs: list[str], prefix: str) -> list[str]:
    """
    Turn one section's paragraphs into chunk texts, each carrying the prefix.

    Two guard rails, both measured against the finished chunk (prefix
    included), because that is what gets embedded and what criterion 4 counts:

      - Under CHUNK_MIN: merge the paragraph into the previous chunk of this
        section. If it is the first paragraph, the next one merges into it.
      - Over CHUNK_SIZE: split the paragraph on sentence ends and pack the
        sentences greedily up to the ceiling.

    On city_guides the ceiling never triggers and the floor catches four
    one-sentence asides, so the 150 in criterion 4 holds across the index.
    """
    joiner = "\n\n" if prefix else ""

    def finished(body: str) -> str:
        return f"{prefix}{joiner}{body}"

    merged: list[str] = []
    for para in paragraphs:
        too_short = len(finished(para)) < config.CHUNK_MIN
        prev_short = bool(merged) and len(finished(merged[-1])) < config.CHUNK_MIN
        if merged and (too_short or prev_short):
            merged[-1] = f"{merged[-1]}\n\n{para}"
        else:
            merged.append(para)

    chunks: list[str] = []
    for body in merged:
        if len(finished(body)) <= config.CHUNK_SIZE:
            chunks.append(finished(body))
            continue
        # Rare: a paragraph over the ceiling. Pack whole sentences up to it.
        room = config.CHUNK_SIZE - len(finished(""))
        piece: list[str] = []
        for sentence in _sentences(body):
            candidate = " ".join(piece + [sentence])
            if piece and len(candidate) > room:
                chunks.append(finished(" ".join(piece)))
                piece = [sentence]
            else:
                piece.append(sentence)
        if piece:
            chunks.append(finished(" ".join(piece)))
    return chunks


def split_documents(documents: list[Document]) -> list[Chunk]:
    """
    One paragraph per chunk, prefixed with the document title and `##` heading.

    Why a paragraph: in city_guides every paragraph is one complete thought,
    and the fact a question wants is almost always one sentence inside it.
    Section-sized chunks tested worse — two-paragraph sections diluted the
    sentence that mattered, and nine towns sharing the same seven headings made
    same-topic sections from different towns hard to tell apart.

    Why the prefix: "## Getting there" followed by bus times could be any of
    nine towns. "# Kestrelford" on the front puts the town name in every
    chunk, so a question that names the town can match on it.

    Why no overlap: overlap repairs cuts mid-thought, and this never cuts
    mid-thought. CHUNK_MIN and CHUNK_SIZE in config.py are the guard rails —
    see `_pack`.
    """
    chunks: list[Chunk] = []
    for doc in documents:
        title, sections = _title_and_sections(doc.text)
        index = 0
        for heading, body in sections:
            prefix = "\n\n".join(part for part in (title, heading) if part)
            for text in _pack(_paragraphs(body), prefix):
                chunks.append(
                    Chunk(
                        text=text,
                        source=doc.source,
                        index=index,
                        produced_by="chunker.py::split_documents",
                    )
                )
                index += 1
    return chunks


def describe(chunks: list[Chunk]) -> str:
    """A one-line summary, printed after indexing."""
    if not chunks:
        return "0 chunks"
    lengths = [len(c.text) for c in chunks]
    return (
        f"{len(chunks)} chunks, "
        f"{sum(lengths) // len(lengths)} characters on average "
        f"(shortest {min(lengths)}, longest {max(lengths)}), "
        f"produced by {chunks[0].produced_by}"
    )


if __name__ == "__main__":
    from ingest import load_documents

    chunks = split_documents(load_documents())
    print(describe(chunks))
