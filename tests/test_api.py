import json
import os
import sys
from fastapi.testclient import TestClient

# Ensure repository root is on sys.path so `backend` package imports work during tests
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from backend.main import app


client = TestClient(app)


def test_plan_with_manual_topics():
    data = {
        "topics_text": "Topic A\nTopic B\nTopic C",
        "exam_date": "2025-12-01",
        "exam_type": "regular_test",
        "hours_per_day": 1.0,
        "plan_length": 7,
        "course_type": "Calculus",
    }
    resp = client.post("/plan", data=data)
    assert resp.status_code == 200
    j = resp.json()
    assert "plan" in j
    assert j["exam_type"] == "regular_test"


def test_plan_with_syllabus_text():
    syllabus = (
        "Chapter 1: Intro\nBasics of course.\n\nChapter 2: Advanced\nHard topics."
    )
    data = {
        "syllabus_text": syllabus,
        "exam_date": "2025-12-15",
        "exam_type": "final",
        "hours_per_day": 2.0,
        "plan_length": 14,
        "course_type": "Chemistry",
    }
    resp = client.post("/plan", data=data)
    assert resp.status_code == 200
    j = resp.json()
    assert j["plan_length"] == 14
    assert isinstance(j["plan"], list)


def test_large_topic_splitting():
    # Create a very large single topic that must be split across days
    long_text = "BigTopic " + ("x" * 5000)
    data = {
        "topics_text": long_text,
        "exam_date": "2025-12-01",
        "exam_type": "final",
        "hours_per_day": 1.0,
        "plan_length": 3,
        "course_type": "Test",
    }
    resp = client.post("/plan", data=data)
    assert resp.status_code == 200
    j = resp.json()
    # Should have topic parts across multiple days
    parts = 0
    for d in j['plan']:
        parts += len(d['topics'])
    assert parts >= 2


def test_ocr_status_endpoint():
    resp = client.get('/ocr_status')
    assert resp.status_code == 200
    j = resp.json()
    assert 'pytesseract_installed' in j and 'easyocr_installed' in j
