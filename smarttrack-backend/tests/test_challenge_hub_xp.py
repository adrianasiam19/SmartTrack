"""Regression tests for Challenge Hub XP persistence before Level 3."""

from app.assessment.challenge_hub import (
    _challenge_sessions,
    complete_session,
    credit_pending_xp,
)


class _DummyUser:
    def __init__(self, user_id: str = "user-1", xp: int = 100):
        self.id = user_id
        self.xp = xp


class _DummyDBSession:
    def __init__(self, session_id: int = 1):
        self.id = session_id
        self.challenge_level = 1
        self.status = "level_complete"
        self.total_xp = 0
        self.correct_count = 0
        self.wrong_count = 0
        self.completed_at = None


class _FakeDB:
    def __init__(self, db_session: _DummyDBSession, user: _DummyUser):
        self._db_session = db_session
        self._user = user
        self.added = []
        self.commit_count = 0

    async def get(self, model, _id):
        name = getattr(model, "__name__", str(model))
        if "User" in name:
            return self._user
        return self._db_session

    def add(self, obj):
        self.added.append(obj)

    async def commit(self):
        self.commit_count += 1

    async def refresh(self, _obj):
        return None


def _seed_level_complete_session(
    session_id: str = "xp-session",
    user_id: str = "user-1",
    total_xp: int = 40,
    xp_credited: int = 0,
):
    _challenge_sessions[session_id] = {
        "session_id": session_id,
        "db_session_id": 1,
        "user_id": user_id,
        "shs_level": "SHS 2",
        "challenge_level": 1,
        "status": "level_complete",
        "current_subject_index": 0,
        "current_question_index": 0,
        "questions": {"Core Mathematics": []},
        "responses": {
            "Core Mathematics": [
                {
                    "question_index": 0,
                    "question_text": "q",
                    "question_type": "mcq",
                    "user_answer": "A",
                    "correct_answer": "A",
                    "is_correct": True,
                    "time_taken_seconds": 2,
                    "xp_earned": 5,
                }
            ]
        },
        "level_archives": [],
        "total_xp": total_xp,
        "xp_credited": xp_credited,
        "correct_count": 8,
        "wrong_count": 0,
        "started_at": "2026-01-01T00:00:00+00:00",
    }
    return session_id


async def test_credit_pending_xp_on_level_complete_persists_to_user():
    session_id = _seed_level_complete_session(total_xp=40, xp_credited=0)
    user = _DummyUser(xp=100)
    db = _FakeDB(_DummyDBSession(), user)

    result = await credit_pending_xp(db, user.id, session_id)

    assert result["xp_credited_delta"] == 40
    assert result["user_xp"] == 140
    assert user.xp == 140
    assert _challenge_sessions[session_id]["xp_credited"] == 40

    # Idempotent: second credit adds nothing
    again = await credit_pending_xp(db, user.id, session_id)
    assert again["xp_credited_delta"] == 0
    assert user.xp == 140

    _challenge_sessions.pop(session_id, None)


async def test_complete_after_level_credit_only_adds_remaining_xp():
    session_id = _seed_level_complete_session(total_xp=60, xp_credited=40)
    user = _DummyUser(xp=140)
    db = _FakeDB(_DummyDBSession(), user)

    summary = await complete_session(db, user.id, session_id)

    assert "error" not in summary
    assert summary["xp_credited_delta"] == 20
    assert summary["user_xp"] == 160
    assert user.xp == 160
    assert db._db_session.status == "completed"

    _challenge_sessions.pop(session_id, None)
