"""End-to-end smoke test: POST /analyze -> verify image_url, traits, label."""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def run():
    assert client.get("/health").json()["status"] == "ok"

    payload = {
        "answers": [
            {"question_id": "q_hobby", "answer_id": "stargazing"},
            {"question_id": "q_energy", "answer_id": "low"},
            {"question_id": "q_setting", "answer_id": "outdoors"},
        ]
    }

    r = client.post("/analyze?include_prompt=true", json=payload)
    assert r.status_code == 200, r.text
    body = r.json()

    print("label  ->", body["label"])
    print("traits ->", body["traits"])
    print("style  ->", body["style"])
    print("prompt ->")
    print(body["prompt"])
    print("image  ->", body["image_url"])

    assert body["label"]["name"]
    assert set(body["traits"]["scores"]) == {
        "energy", "warmth", "openness", "intensity", "nature_affinity"
    }

    # image is actually fetchable and is a real PNG
    name = body["image_url"].rsplit("/", 1)[-1]
    img = client.get(f"/files/{name}")
    assert img.status_code == 200 and img.content[:8] == b"\x89PNG\r\n\x1a\n"
    print("image bytes ->", len(img.content), "PNG OK")

    # determinism: same answers -> same traits/style/prompt
    r2 = client.post("/analyze?include_prompt=true", json=payload)
    b2 = r2.json()
    assert b2["traits"] == body["traits"]
    assert b2["style"] == body["style"]
    assert b2["prompt"] == body["prompt"]
    print("determinism -> identical traits/style/prompt OK")

    # a different answer set produces a different label/style
    payload2 = {
        "answers": [
            {"question_id": "q_hobby", "answer_id": "music"},
            {"question_id": "q_energy", "answer_id": "high"},
            {"question_id": "q_setting", "answer_id": "city"},
        ]
    }
    b3 = client.post("/analyze", json=payload2).json()
    print("alt label ->", b3["label"]["name"], "| alt style ->", b3["style"])
    assert b3["label"] != body["label"] or b3["style"] != body["style"]

    print("\nALL CHECKS PASSED")


if __name__ == "__main__":
    run()
