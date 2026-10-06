import json

import httpx
import pytest

from app.ai.outputs import AnswerOutput, GradeOutput, TopicsOutput, grade_guard, pages_guard
from app.ai.providers import LocalProvider, OpenAICompatibleProvider, ProviderError
from app.ai.router import AIUnavailableError, ModelRouter


class FakeProvider:
    kind = "llm"
    available = True

    def __init__(self, id: str, responses: list) -> None:
        self.id = id
        self.label = id
        self.responses = list(responses)
        self.calls = 0

    def run(self, task, payload, schema):
        self.calls += 1
        item = self.responses.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


ANSWER_OK = json.dumps({"answer": "Paging maps pages to frames.", "citations": [3]})


def test_retries_once_after_invalid_json_then_succeeds():
    fake = FakeProvider("fake", ["not json", ANSWER_OK])
    router = ModelRouter([fake, LocalProvider("keyword")], ["fake"])
    result = router.run("answer_question", {"q": 1}, AnswerOutput)
    assert result.model == "fake"
    assert fake.calls == 2
    assert [a["ok"] for a in result.attempts] == [False, True]


def test_falls_back_when_provider_errors():
    fake = FakeProvider("fake", [ProviderError("boom")])
    router = ModelRouter([fake, LocalProvider("keyword")], ["fake"])
    payload = {"question": "what is paging", "passages": [{"page": 3, "text": "Paging is fun."}]}
    result = router.run("answer_question", payload, AnswerOutput)
    assert result.model == "local-keyword"


def test_guard_rejects_hallucinated_pages_and_falls_back():
    bad = json.dumps({"topics": [{"name": "Ghost topic", "summary": "", "source_page": 99}]})
    fake = FakeProvider("fake", [bad, bad])
    router = ModelRouter([fake, LocalProvider("keyword")], ["fake"])
    payload = {"pages": [{"page": 1, "text": "Caching\nA cache is a small fast memory store."}]}
    result = router.run("extract_topics", payload, TopicsOutput, pages_guard({1}))
    assert result.model == "local-keyword"
    assert result.output.topics[0].source_page == 1
    assert fake.calls == 2


def test_cache_hits_skip_provider():
    fake = FakeProvider("fake", [ANSWER_OK])
    router = ModelRouter([fake], ["fake"])
    first = router.run("answer_question", {"q": 1}, AnswerOutput)
    second = router.run("answer_question", {"q": 1}, AnswerOutput)
    assert not first.cached and second.cached
    assert fake.calls == 1


def test_cache_evicts_oldest():
    fake = FakeProvider("fake", [ANSWER_OK, ANSWER_OK, ANSWER_OK])
    router = ModelRouter([fake], ["fake"], cache_size=1)
    router.run("answer_question", {"q": 1}, AnswerOutput)
    router.run("answer_question", {"q": 2}, AnswerOutput)
    assert router.run("answer_question", {"q": 1}, AnswerOutput).cached is False


def test_all_models_failing_raises():
    fake = FakeProvider("fake", [ProviderError("down")])
    router = ModelRouter([fake], ["fake"])
    with pytest.raises(AIUnavailableError):
        router.run("answer_question", {}, AnswerOutput)


def test_preferred_model_goes_first_and_unavailable_are_skipped():
    offline = OpenAICompatibleProvider("openai", "OpenAI", "https://x", "m", api_key=None)
    router = ModelRouter([offline, LocalProvider("keyword"), LocalProvider("semantic")], ["openai"])
    assert router.chain("local-semantic") == ["local-semantic", "local-keyword"]
    assert router.available() == ["local-keyword", "local-semantic"]


def test_compare_reports_errors_per_model():
    good = FakeProvider("good", [ANSWER_OK])
    bad = FakeProvider("bad", [ProviderError("nope")])
    router = ModelRouter([good, bad], ["good"])
    rows = router.compare("answer_question", {}, AnswerOutput)
    assert rows[0]["ok"] and rows[0]["output"]["citations"] == [3]
    assert rows[1]["ok"] is False and "nope" in rows[1]["error"]


def test_grade_guard_rules():
    guard = grade_guard(["mutual exclusion"])
    with pytest.raises(ValueError):
        guard(GradeOutput(score=5, feedback="ok", missing_points=["x"]))
    with pytest.raises(ValueError):
        guard(GradeOutput(score=0, feedback="no", missing_points=[]))
    guard(GradeOutput(score=3, feedback="fine", missing_points=["x"]))


def test_openai_compatible_provider(monkeypatch):
    sent = {}

    def fake_post(url, json, headers, timeout):
        sent.update(url=url, body=json, headers=headers)
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": ANSWER_OK}}]},
            request=httpx.Request("POST", url),
        )

    monkeypatch.setattr(httpx, "post", fake_post)
    provider = OpenAICompatibleProvider("groq", "Groq", "https://api.test/v1/", "llama", "key")
    assert provider.available
    raw = provider.run("answer_question", {"question": "q"}, AnswerOutput)
    assert json.loads(raw)["citations"] == [3]
    assert sent["url"] == "https://api.test/v1/chat/completions"
    assert sent["headers"]["Authorization"] == "Bearer key"
    assert sent["body"]["response_format"] == {"type": "json_object"}


def test_openai_compatible_provider_errors(monkeypatch):
    def failing_post(url, **_):
        return httpx.Response(500, request=httpx.Request("POST", url))

    monkeypatch.setattr(httpx, "post", failing_post)
    provider = OpenAICompatibleProvider(
        "ollama", "Ollama", "http://local/v1", "m", requires_key=False
    )
    with pytest.raises(ProviderError):
        provider.run("answer_question", {}, AnswerOutput)
    with pytest.raises(ProviderError):
        OpenAICompatibleProvider("openai", "OpenAI", "https://x", "m").run(
            "answer_question", {}, AnswerOutput
        )
