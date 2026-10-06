from types import SimpleNamespace

from app.routers import courses as courses_router
from tests.conftest import register


def test_course_crud(client, auth):
    created = client.post(
        "/api/courses", json={"title": "Databases", "exam_date": "2099-05-01"}, headers=auth
    )
    assert created.status_code == 201
    course_id = created.json()["id"]

    listed = client.get("/api/courses", headers=auth).json()
    assert [c["title"] for c in listed] == ["Databases"]

    updated = client.patch(f"/api/courses/{course_id}", json={"title": "DB Systems"}, headers=auth)
    assert updated.json()["title"] == "DB Systems"
    assert updated.json()["exam_date"] == "2099-05-01"

    assert client.delete(f"/api/courses/{course_id}", headers=auth).status_code == 204
    assert client.get(f"/api/courses/{course_id}", headers=auth).status_code == 404


def test_courses_are_private(client, auth, course_with_pdf):
    other = register(client, "mallory")
    assert client.get(f"/api/courses/{course_with_pdf}", headers=other).status_code == 404
    assert client.get("/api/courses", headers=other).json() == []
    topic_id = client.get(f"/api/courses/{course_with_pdf}/topics", headers=auth).json()[0]["id"]
    assert client.get(f"/api/topics/{topic_id}/questions", headers=other).status_code == 404


def test_pdf_upload_extracts_topics(client, auth, course_with_pdf):
    detail = client.get(f"/api/courses/{course_with_pdf}", headers=auth).json()
    assert detail["document_count"] == 1
    assert detail["documents"][0]["page_count"] == 4
    names = [t["name"] for t in detail["topics"]]
    assert names == [
        "Processes and Threads",
        "CPU Scheduling",
        "Virtual Memory and Paging",
        "Deadlocks",
    ]
    assert [t["source_page"] for t in detail["topics"]] == [1, 2, 3, 4]


def test_markdown_upload_splits_by_heading(client, auth):
    course_id = client.post("/api/courses", json={"title": "Networks"}, headers=auth).json()["id"]
    text = (
        "# TCP Handshake\nTCP is a connection-oriented protocol that uses a three-way handshake "
        "before data is sent.\n\n# DNS Resolution\nDNS is a system that translates domain names "
        "into IP addresses using a hierarchy of name servers.\n"
    )
    resp = client.post(
        f"/api/courses/{course_id}/documents",
        files={"file": ("net.md", text.encode(), "text/markdown")},
        headers=auth,
    )
    assert resp.status_code == 201
    assert resp.json()["topics_created"] == 2
    assert resp.json()["model"] == "local-keyword"


def test_upload_validation(client, auth):
    course_id = client.post("/api/courses", json={"title": "Bad files"}, headers=auth).json()["id"]
    url = f"/api/courses/{course_id}/documents"

    wrong_type = client.post(url, files={"file": ("a.docx", b"data", "x")}, headers=auth)
    assert wrong_type.status_code == 422
    assert "Unsupported" in wrong_type.json()["detail"]

    fake_pdf = client.post(url, files={"file": ("a.pdf", b"not a pdf", "x")}, headers=auth)
    assert fake_pdf.status_code == 422

    empty = client.post(url, files={"file": ("a.txt", b"", "text/plain")}, headers=auth)
    assert empty.status_code == 422

    binary = client.post(
        url, files={"file": ("a.txt", b"\xff\xfe\x00", "text/plain")}, headers=auth
    )
    assert binary.status_code == 422


def test_upload_size_limit(client, auth, monkeypatch):
    monkeypatch.setattr(courses_router, "settings", SimpleNamespace(max_upload_mb=0))
    course_id = client.post("/api/courses", json={"title": "Big"}, headers=auth).json()["id"]
    resp = client.post(
        f"/api/courses/{course_id}/documents",
        files={"file": ("a.txt", b"some text", "text/plain")},
        headers=auth,
    )
    assert resp.status_code == 413
