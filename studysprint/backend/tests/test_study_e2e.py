"""End-to-end HTTP flow: upload -> questions -> session -> grade -> mastery -> plan -> ask."""


def test_happy_path_study_loop(client, auth, course_with_pdf):
    course_id = course_with_pdf
    topics = client.get(f"/api/courses/{course_id}/topics", headers=auth).json()
    deadlocks = next(t for t in topics if t["name"] == "Deadlocks")

    generated = client.post(
        f"/api/topics/{deadlocks['id']}/questions", json={"count": 3}, headers=auth
    )
    assert generated.status_code == 200
    questions = generated.json()
    assert len(questions) >= 2
    assert all(q["source_page"] == 4 for q in questions)

    session = client.get(f"/api/courses/{course_id}/session?size=4", headers=auth).json()
    assert len(session["questions"]) == 4
    assert len({q["topic_id"] for q in session["questions"]}) == 4
    assert "reference_answer" not in session["questions"][0]

    target = questions[0]
    good = client.post(
        f"/api/questions/{target['id']}/attempts",
        json={"answer": target["reference_answer"]},
        headers=auth,
    ).json()
    assert good["score"] == 5
    assert good["missing_points"] == []
    assert good["topic_mastery"] == 1.0

    weak = client.post(
        f"/api/questions/{target['id']}/attempts", json={"answer": "no idea"}, headers=auth
    ).json()
    assert weak["score"] <= 1
    assert weak["missing_points"]
    assert weak["topic_mastery"] < 1.0

    plan = client.get(f"/api/courses/{course_id}/plan", headers=auth).json()
    assert plan["days"]
    first_day_ids = {t["id"] for t in plan["days"][0]["topics"]}
    assert deadlocks["id"] not in first_day_ids
    assert plan["days"][-1]["focus"] == "review"

    answer = client.post(
        f"/api/courses/{course_id}/ask", json={"question": "What causes thrashing?"}, headers=auth
    ).json()
    assert "page faults" in answer["answer"]
    assert answer["citations"][0]["page"] == 3

    cached = client.post(
        f"/api/courses/{course_id}/ask", json={"question": "What causes thrashing?"}, headers=auth
    ).json()
    assert cached["cached"] is True


def test_attempt_validation(client, auth, course_with_pdf):
    session = client.get(f"/api/courses/{course_with_pdf}/session?size=1", headers=auth).json()
    qid = session["questions"][0]["id"]
    assert (
        client.post(f"/api/questions/{qid}/attempts", json={"answer": ""}, headers=auth).status_code
        == 422
    )
    assert (
        client.post("/api/questions/9999/attempts", json={"answer": "x"}, headers=auth).status_code
        == 404
    )


def test_ask_without_material(client, auth):
    course_id = client.post("/api/courses", json={"title": "Empty"}, headers=auth).json()["id"]
    resp = client.post(
        f"/api/courses/{course_id}/ask", json={"question": "What is RAM?"}, headers=auth
    )
    assert resp.status_code == 200
    assert resp.json()["citations"] == []


def test_agent_prepare_quiz_plan_and_ask(client, auth, course_with_pdf):
    prepare = client.post(
        "/api/agent/run",
        json={"course_id": course_with_pdf, "goal": "Get me ready for the exam"},
        headers=auth,
    ).json()
    assert prepare["intent"] == "prepare"
    assert [s["worker"] for s in prepare["steps"]] == [
        "curriculum_worker",
        "quiz_worker",
        "planner_worker",
    ]
    assert prepare["output"]["questions_created"] >= 4
    assert prepare["output"]["plan"]

    quiz = client.post(
        "/api/agent/run", json={"course_id": course_with_pdf, "goal": "quiz me"}, headers=auth
    ).json()
    assert quiz["intent"] == "quiz"
    assert len(quiz["output"]["session"]) == 5

    plan = client.post(
        "/api/agent/run",
        json={"course_id": course_with_pdf, "goal": "make a study schedule"},
        headers=auth,
    ).json()
    assert plan["intent"] == "plan"

    ask = client.post(
        "/api/agent/run",
        json={"course_id": course_with_pdf, "goal": "What is a deadlock?"},
        headers=auth,
    ).json()
    assert ask["intent"] == "ask"
    assert ask["output"]["answer"]["citations"][0]["page"] == 4

    run_traces = client.get(f"/api/traces?run_id={prepare['run_id']}", headers=auth).json()
    kinds = {e["kind"] for e in run_traces}
    assert {"agent", "worker", "tool", "model"} <= kinds


def test_agent_without_material_stops(client, auth):
    course_id = client.post("/api/courses", json={"title": "Empty"}, headers=auth).json()["id"]
    run = client.post(
        "/api/agent/run", json={"course_id": course_id, "goal": "prepare"}, headers=auth
    ).json()
    assert len(run["steps"]) == 1
    assert run["output"]["message"] == "Upload course material first."


def test_compare_models(client, auth, course_with_pdf):
    models = client.get("/api/ai/models", headers=auth).json()
    available = [m["id"] for m in models if m["available"]]
    assert available == ["local-keyword", "local-semantic"]

    ask = client.post(
        "/api/ai/compare",
        json={"task": "ask", "course_id": course_with_pdf, "question": "What is paging?"},
        headers=auth,
    ).json()
    assert [r["model"] for r in ask["rows"]] == available
    assert all(r["ok"] for r in ask["rows"])

    question = client.get(f"/api/courses/{course_with_pdf}/session?size=1", headers=auth).json()[
        "questions"
    ][0]
    grade = client.post(
        "/api/ai/compare",
        json={
            "task": "grade",
            "course_id": course_with_pdf,
            "question_id": question["id"],
            "answer": "something about processes and memory",
            "models": ["local-keyword", "local-semantic", "openai"],
        },
        headers=auth,
    ).json()
    rows = {r["model"]: r for r in grade["rows"]}
    assert rows["local-keyword"]["ok"] and rows["local-semantic"]["ok"]
    assert rows["openai"]["ok"] is False


def test_compare_validation(client, auth, course_with_pdf):
    url = "/api/ai/compare"
    base = {"course_id": course_with_pdf}
    assert client.post(url, json={**base, "task": "ask"}, headers=auth).status_code == 422
    assert (
        client.post(
            url, json={**base, "task": "grade", "question_id": 999, "answer": "x"}, headers=auth
        ).status_code
        == 404
    )
    assert (
        client.post(
            url,
            json={**base, "task": "ask", "question": "hi there", "models": ["gpt-9"]},
            headers=auth,
        ).status_code
        == 422
    )


def test_tools_and_traces_endpoints(client, auth, course_with_pdf):
    tools = {t["name"] for t in client.get("/api/ai/tools", headers=auth).json()}
    assert {"ingest_document", "generate_questions", "grade_answer", "plan_sessions"} <= tools
    assert client.get("/api/traces", headers=auth).json()
    assert client.delete("/api/traces", headers=auth).status_code == 204
    assert client.get("/api/traces", headers=auth).json() == []
