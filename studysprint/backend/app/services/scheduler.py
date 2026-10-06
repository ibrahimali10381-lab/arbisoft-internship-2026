"""Explainable spaced-practice rules: weakest and least-recently practiced topics come first."""

from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta

DEFAULT_HORIZON_DAYS = 7
MAX_HORIZON_DAYS = 21


@dataclass
class TopicState:
    id: int
    name: str
    mastery: float
    attempts: int
    last_practiced: date | None


def updated_mastery(old: float, attempts: int, score: int) -> float:
    """First attempt sets mastery; later attempts blend 60% history / 40% new score."""
    new = score / 5
    return round(new if attempts == 0 else 0.6 * old + 0.4 * new, 3)


def priority(topic: TopicState, today: date) -> float:
    if topic.attempts == 0:
        return 2.0
    days_since = (today - topic.last_practiced).days if topic.last_practiced else 7
    return (1 - topic.mastery) + 0.1 * min(days_since, 7)


def rank(topics: list[TopicState], today: date) -> list[TopicState]:
    return sorted(topics, key=lambda t: (-priority(t, today), t.mastery, t.id))


def build_plan(
    topics: list[TopicState],
    today: date,
    exam_date: date | None,
    per_day: int = 3,
) -> list[dict]:
    if not topics:
        return []
    if exam_date and exam_date > today:
        horizon = min((exam_date - today).days, MAX_HORIZON_DAYS)
    else:
        horizon = DEFAULT_HORIZON_DAYS
    sim = [TopicState(**vars(t)) for t in topics]
    days = []
    for offset in range(horizon):
        day = today + timedelta(days=offset)
        is_last = offset == horizon - 1 and exam_date is not None
        chosen = (
            sorted(sim, key=lambda t: (t.mastery, t.id))[:per_day]
            if is_last
            else rank(sim, day)[:per_day]
        )
        focus = (
            "review"
            if is_last
            else ("learn" if any(t.attempts == 0 for t in chosen) else "practice")
        )
        days.append(
            {
                "date": day,
                "focus": focus,
                "topics": [{"id": t.id, "name": t.name, "mastery": t.mastery} for t in chosen],
            }
        )
        for t in chosen:
            t.mastery = round(t.mastery + (1 - t.mastery) * 0.3, 3)
            t.attempts += 1
            t.last_practiced = day
    return days


def today_utc() -> date:
    return datetime.now(UTC).date()
