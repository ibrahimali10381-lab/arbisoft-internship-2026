from datetime import date, timedelta

import pytest

from app.ai.providers import LocalProvider, ProviderError
from app.ai.text import contains_point, keywords, stem
from app.services import scheduler
from app.services.ingest import IngestError, chunk_text, extract_pages

TODAY = date(2026, 10, 5)


def state(id, mastery, attempts=1, days_ago=1):
    return scheduler.TopicState(
        id=id,
        name=f"t{id}",
        mastery=mastery,
        attempts=attempts,
        last_practiced=TODAY - timedelta(days=days_ago) if attempts else None,
    )


def test_updated_mastery():
    assert scheduler.updated_mastery(0.0, 0, 4) == 0.8
    assert scheduler.updated_mastery(1.0, 3, 0) == 0.6


def test_rank_prefers_unseen_then_weak_then_stale():
    topics = [state(1, 0.9), state(2, 0.2), state(3, 0.0, attempts=0), state(4, 0.9, days_ago=7)]
    assert [t.id for t in scheduler.rank(topics, TODAY)] == [3, 2, 4, 1]


def test_plan_runs_until_exam_and_ends_with_review():
    topics = [state(i, i / 10) for i in range(1, 6)]
    plan = scheduler.build_plan(topics, TODAY, TODAY + timedelta(days=4), per_day=2)
    assert len(plan) == 4
    assert plan[-1]["focus"] == "review"
    assert [t["id"] for t in plan[0]["topics"]] == [1, 2]
    assert topics[0].mastery == 0.1


def test_plan_defaults_and_empty():
    assert scheduler.build_plan([], TODAY, None) == []
    plan = scheduler.build_plan([state(1, 0, attempts=0)], TODAY, TODAY - timedelta(days=1))
    assert len(plan) == scheduler.DEFAULT_HORIZON_DAYS
    assert plan[0]["focus"] == "learn"


def test_text_helpers():
    assert stem("processes") == stem("process") == "process"
    assert contains_point("The page table maps pages", "page table")
    assert not contains_point("nothing relevant", "page table")
    assert "deadlock" in keywords("Deadlock deadlock happens when processes wait", 2)


def test_text_ingest_variants():
    assert extract_pages(b"Page one text\fPage two text", "a.txt") == [
        (1, "Page one text"),
        (2, "Page two text"),
    ]
    long_text = ("word " * 700).encode()
    assert len(extract_pages(long_text, "a.txt")) == 2
    with pytest.raises(IngestError):
        extract_pages(b"   ", "a.md")


def test_chunk_text_respects_size():
    chunks = chunk_text("\n\n".join(["x" * 400] * 5), size=900)
    assert len(chunks) == 3


def test_local_grader_strategies_differ():
    payload = {
        "question": "What is a deadlock?",
        "reference_answer": "A deadlock is when processes wait for resources held by each other.",
        "key_points": ["processes", "resources", "held"],
        "source_page": 4,
        "answer": "processes wait for resources",
    }
    keyword = LocalProvider("keyword").run("grade_answer", payload, None)
    semantic = LocalProvider("semantic").run("grade_answer", payload, None)
    assert keyword["missing_points"] == ["held"]
    assert keyword["score"] == 3
    assert 0 <= semantic["score"] <= 5
    blank = LocalProvider("keyword").run("grade_answer", {**payload, "answer": "dunno"}, None)
    assert blank["score"] == 0 and blank["missing_points"]


def test_local_answer_not_found_and_unknown_task():
    provider = LocalProvider("semantic")
    out = provider.run(
        "answer_question",
        {"question": "quantum chromodynamics", "passages": [{"page": 1, "text": "Paging is ok."}]},
        None,
    )
    assert out["citations"] == []
    with pytest.raises(ProviderError):
        provider.run("write_poem", {}, None)


def test_local_topics_fallback_without_headings():
    out = LocalProvider("keyword").run(
        "extract_topics",
        {"pages": [{"page": 2, "text": "Hashing maps keys to buckets. Collisions need probing."}]},
        None,
    )
    assert out["topics"][0]["source_page"] == 2
