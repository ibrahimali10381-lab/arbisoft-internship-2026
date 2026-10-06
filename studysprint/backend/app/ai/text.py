import math
import re
from collections import Counter
from collections.abc import Iterable

STOPWORDS = frozenset(
    """a about above after again against all also am an and any are as at be because been
    before being below between both but by can could did do does doing down during each few
    for from further had has have having he her here hers him his how i if in into is it its
    itself just me more most my no nor not now of off on once only or other our ours out over
    own same she should so some such than that the their theirs them then there these they
    this those through to too under until up very was we were what when where which while who
    whom why will with would you your yours one two may might must used use uses using called
    each every many much often within without another example set inside always first next
    makes make gives give happens happen spends spend occurs occur keep keeps only""".split()
)

_TOKEN_RE = re.compile(r"[a-zA-Z][a-zA-Z\-]+")
_SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")


def stem(word: str) -> str:
    word = word.lower()
    if word.endswith("ss"):
        return word
    for suffix in ("ations", "ation", "ings", "ing", "ies", "es", "ed", "ly", "s"):
        if word.endswith(suffix) and len(word) - len(suffix) >= 4:
            return word[: -len(suffix)]
    return word


def tokenize(text: str) -> list[str]:
    return [stem(tok) for tok in _TOKEN_RE.findall(text) if tok.lower() not in STOPWORDS]


def sentences(text: str) -> list[str]:
    flat = re.sub(r"\s+", " ", text).strip()
    return [s.strip() for s in _SENTENCE_RE.split(flat) if s.strip()]


def idf(documents: Iterable[str]) -> dict[str, float]:
    docs = [set(tokenize(d)) for d in documents]
    total = len(docs) or 1
    counts: Counter[str] = Counter()
    for tokens in docs:
        counts.update(tokens)
    return {term: math.log((1 + total) / (1 + df)) + 1 for term, df in counts.items()}


def vector(text: str, weights: dict[str, float] | None = None) -> dict[str, float]:
    counts = Counter(tokenize(text))
    return {t: c * (weights.get(t, 1.0) if weights else 1.0) for t, c in counts.items()}


def cosine(a: dict[str, float], b: dict[str, float]) -> float:
    if not a or not b:
        return 0.0
    dot = sum(v * b.get(k, 0.0) for k, v in a.items())
    norm = math.sqrt(sum(v * v for v in a.values())) * math.sqrt(sum(v * v for v in b.values()))
    return dot / norm if norm else 0.0


def keywords(text: str, k: int = 5, weights: dict[str, float] | None = None) -> list[str]:
    """Top-k surface words, ranked by (tf * idf) of their stem."""
    surface: dict[str, str] = {}
    for tok in _TOKEN_RE.findall(text):
        if tok.lower() in STOPWORDS or len(tok) < 4:
            continue
        surface.setdefault(stem(tok), tok.lower())
    scores = vector(text, weights)
    ranked = sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))
    return [surface[t] for t, _ in ranked if t in surface][:k]


def contains_point(answer: str, point: str) -> bool:
    answer_stems = set(tokenize(answer))
    point_stems = tokenize(point)
    if not point_stems:
        return True
    hits = sum(1 for s in point_stems if s in answer_stems)
    return hits / len(point_stems) >= 0.5
