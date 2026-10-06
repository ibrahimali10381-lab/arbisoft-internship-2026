"""Model clients. LLM providers speak the OpenAI chat API; local models run offline."""

import json
import re
from typing import Any, Literal, Protocol

import httpx
from pydantic import BaseModel

from app.ai import text as T


class ProviderError(RuntimeError):
    pass


class Provider(Protocol):
    id: str
    label: str
    kind: Literal["llm", "local"]

    @property
    def available(self) -> bool: ...

    def run(self, task: str, payload: dict[str, Any], schema: type[BaseModel]) -> dict | str: ...


TASK_INSTRUCTIONS = {
    "extract_topics": (
        "Split the course material into distinct study topics (at most max_topics). "
        "source_page must be one of the page numbers given in the input."
    ),
    "generate_questions": (
        "Write `count` open-ended exam questions about the topic that can be answered from the "
        "passages alone. reference_answer paraphrases the passage; key_points are 2-4 short "
        "phrases a correct answer must mention; source_page is the passage page used."
    ),
    "grade_answer": (
        "Grade the student's answer using only reference_answer and key_points. score is 0-5. "
        "missing_points lists key points the answer does not cover. Accept paraphrases. "
        "feedback is 1-3 sentences addressed to the student."
    ),
    "answer_question": (
        "Answer the question using only the passages. citations are the page numbers used. "
        "If the passages do not contain the answer, say so and return no citations."
    ),
}


class OpenAICompatibleProvider:
    kind: Literal["llm"] = "llm"

    def __init__(
        self,
        id: str,
        label: str,
        base_url: str | None,
        model: str,
        api_key: str | None = None,
        requires_key: bool = True,
        timeout: float = 30.0,
    ) -> None:
        self.id = id
        self.label = f"{label} · {model}"
        self.base_url = (base_url or "").rstrip("/")
        self.model = model
        self.api_key = api_key
        self.requires_key = requires_key
        self.timeout = timeout

    @property
    def available(self) -> bool:
        return bool(self.base_url) and (bool(self.api_key) or not self.requires_key)

    def run(self, task: str, payload: dict[str, Any], schema: type[BaseModel]) -> str:
        if not self.available:
            raise ProviderError(f"{self.id} is not configured")
        system = (
            f"You are the StudySprint {task} model. {TASK_INSTRUCTIONS[task]} "
            "Reply with a single JSON object matching this JSON schema, no prose:\n"
            + json.dumps(schema.model_json_schema(), separators=(",", ":"))
        )
        body = {
            "model": self.model,
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": json.dumps(payload)},
            ],
        }
        headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        try:
            resp = httpx.post(
                f"{self.base_url}/chat/completions",
                json=body,
                headers=headers,
                timeout=self.timeout,
            )
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]
        except (httpx.HTTPError, KeyError, IndexError, ValueError) as exc:
            raise ProviderError(f"{self.id} request failed: {exc}") from exc


_DEF_RE = re.compile(
    r"^(?P<article>an?\s+|the\s+)?(?P<term>[a-z][\w\s\-()/]{2,60}?)\s+"
    r"(?P<verb>is|are|refers to|means)\s+(?P<rest>.+)$",
    re.IGNORECASE,
)


def _is_heading(line: str) -> bool:
    words = line.split()
    return 0 < len(words) <= 8 and not line.rstrip().endswith((".", "?", "!", ","))


def _body(text: str) -> str:
    return "\n".join(line for line in text.splitlines() if not _is_heading(line.strip()))


class LocalProvider:
    """Deterministic offline model so the app works (and tests run) without API keys.

    `strategy` selects how answers are matched: "keyword" checks key-point coverage,
    "semantic" uses TF-IDF cosine similarity against the reference answer.
    """

    kind: Literal["local"] = "local"
    available = True

    def __init__(self, strategy: Literal["keyword", "semantic"]) -> None:
        self.strategy = strategy
        self.id = f"local-{strategy}"
        self.label = f"Local · {strategy} matcher"

    def run(self, task: str, payload: dict[str, Any], schema: type[BaseModel]) -> dict:
        handler = getattr(self, f"_{task}", None)
        if handler is None:
            raise ProviderError(f"{self.id} cannot run {task}")
        return handler(payload)

    def _extract_topics(self, payload: dict[str, Any]) -> dict:
        corpus = [p["text"] for p in payload["pages"]]
        weights = T.idf(corpus)
        topics: list[dict] = []
        seen: set[str] = set()
        for page in payload["pages"]:
            lines = [ln.strip() for ln in page["text"].splitlines() if ln.strip()]
            if sum(len(ln) for ln in lines) < 40:
                continue
            if _is_heading(lines[0]) and len(lines[0]) >= 3:
                name = lines[0]
            else:
                name = " ".join(T.keywords(page["text"], 2, weights)).title() or "Overview"
            if name.lower() in seen:
                continue
            seen.add(name.lower())
            summary = " ".join(T.sentences(_body(page["text"]))[:2])[:600]
            topics.append({"name": name[:80], "summary": summary, "source_page": page["page"]})
        if not topics:
            whole = " ".join(corpus)
            name = " ".join(T.keywords(whole, 2)).title() or "Course overview"
            first_page = payload["pages"][0]["page"] if payload["pages"] else 1
            topics.append({"name": name, "summary": whole[:300], "source_page": first_page})
        return {"topics": topics[: payload.get("max_topics", 12)]}

    def _generate_questions(self, payload: dict[str, Any]) -> dict:
        topic = payload["topic"]
        passages = payload["passages"]
        candidates: list[tuple[float, str, int]] = []
        all_sentences = [s for p in passages for s in T.sentences(_body(p["text"]))]
        weights = T.idf(all_sentences or [topic])
        for p in passages:
            for sent in T.sentences(_body(p["text"])):
                n_words = len(sent.split())
                if not 6 <= n_words <= 45:
                    continue
                score = sum(T.vector(sent, weights).values()) / n_words
                if _DEF_RE.match(sent):
                    score += 2
                candidates.append((score, sent, p["page"]))
        candidates.sort(key=lambda c: -c[0])

        questions = []
        for _, sent, page in candidates[: payload.get("count", 3)]:
            match = _DEF_RE.match(sent)
            if match and len(match["term"].split()) <= 6:
                term = match["term"].strip()
                if not term[:2].isupper():
                    term = term[0].lower() + term[1:]
                term = ((match["article"] or "").lower() + term).strip()
                verb = match["verb"].lower()
                prompt = (
                    f"What {verb} {term}? Explain in your own words."
                    if verb in ("is", "are")
                    else f'What is meant by "{term}"?'
                )
                points = T.keywords(match["rest"], 4, weights)
            else:
                topic_stems = set(T.tokenize(topic))
                kws = [k for k in T.keywords(sent, 6, weights) if T.stem(k) not in topic_stems]
                blank = next((k for k in kws if len(k) >= 5), None)
                if blank:
                    cloze = re.sub(rf"\b{re.escape(blank)}\b", "_____", sent, count=1, flags=re.I)
                    prompt = f'Fill in the blank and explain why it matters: "{cloze}"'
                    points = [blank] + [k for k in kws if k != blank][:3]
                else:
                    prompt = f"Explain this idea about {topic} in your own words: {sent}"
                    points = T.keywords(sent, 4, weights)
            questions.append(
                {
                    "prompt": prompt,
                    "reference_answer": sent,
                    "key_points": points or T.keywords(sent, 3) or [topic],
                    "source_page": page,
                }
            )
        if not questions and passages:
            ref = passages[0]["text"][:400]
            questions.append(
                {
                    "prompt": f"Summarize what the material says about {topic}.",
                    "reference_answer": ref,
                    "key_points": T.keywords(ref, 3) or [topic],
                    "source_page": passages[0]["page"],
                }
            )
        return {"questions": questions}

    def _grade_answer(self, payload: dict[str, Any]) -> dict:
        answer = payload["answer"]
        key_points: list[str] = payload["key_points"]
        missing = [kp for kp in key_points if not T.contains_point(answer, kp)]
        if self.strategy == "keyword":
            covered = 1 - len(missing) / len(key_points) if key_points else 1.0
            score = round(5 * covered)
        else:
            sim = T.cosine(T.vector(answer), T.vector(payload["reference_answer"]))
            score = min(5, round(sim / 0.55 * 5))
        if len(answer.split()) < 3:
            score = min(score, 1)
        if score == 5 and missing:
            score = 4
        if score == 0 and not missing:
            missing = list(key_points)

        page = payload.get("source_page")
        where = f" (page {page})" if page else ""
        if score == 5:
            feedback = "Excellent — you covered every key point."
        elif not missing:
            feedback = f"You touched every key point; add more detail from the material{where}."
        elif score >= 3:
            feedback = f"Good answer. To make it complete, also mention: {', '.join(missing)}."
        elif score >= 1:
            feedback = f"Partially correct. Review the material{where}; you missed: "
            feedback += ", ".join(missing) + "."
        else:
            feedback = f"This doesn't match the material yet. Re-read{where} and try again."
        return {"score": score, "feedback": feedback, "missing_points": missing}

    def _answer_question(self, payload: dict[str, Any]) -> dict:
        question = payload["question"]
        scored: list[tuple[float, str, int]] = []
        all_sentences = [s for p in payload["passages"] for s in T.sentences(_body(p["text"]))]
        weights = T.idf(all_sentences or [question])
        q_vec = T.vector(question, weights if self.strategy == "semantic" else None)
        q_terms = set(q_vec)
        for p in payload["passages"]:
            for sent in T.sentences(_body(p["text"])):
                if self.strategy == "semantic":
                    score = T.cosine(q_vec, T.vector(sent, weights))
                else:
                    score = float(len(q_terms & set(T.tokenize(sent))))
                if score > 0:
                    scored.append((score, sent, p["page"]))
        scored.sort(key=lambda s: -s[0])
        top = scored[:3]
        if not top:
            return {"answer": "I couldn't find this in your uploaded material.", "citations": []}
        return {
            "answer": " ".join(s for _, s, _ in top),
            "citations": sorted({page for _, _, page in top}),
        }
