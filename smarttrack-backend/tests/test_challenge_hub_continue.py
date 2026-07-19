"""Regression tests for Challenge Hub level continue / submit."""

from app.assessment.challenge_hub import (
    CORE_SUBJECTS,
    _challenge_sessions,
    continue_challenge_level,
    submit_answer,
)


class _DummyDBSession:
    def __init__(self, session_id: int = 1):
        self.id = session_id
        self.challenge_level = 1


class _FakeDB:
    def __init__(self, db_session: _DummyDBSession):
        self._db_session = db_session

    async def get(self, _model, _id):
        return self._db_session

    async def commit(self):
        return None

    async def refresh(self, _obj):
        return None


async def test_continue_level_allows_fresh_submits_on_level_two(monkeypatch):
    """
    After Level 1, continuing must clear current responses so Level 2 Q0
    is not rejected as a duplicate submit.
    """
    session_id = "test-session-l2"
    user_id = "user-1"
    db_session = _DummyDBSession()

    # Pretend Level 1 is finished for all subjects with answers at indices 0..5
    l1_questions = {
        subject: [
            {
                "id": f"{subject}-q{i}",
                "question": f"{subject} L1 Q{i}",
                "question_type": "mcq",
                "options": {"A": "1", "B": "2", "C": "3", "D": "4"},
                "correct_answer": "A",
                "explanation": "ok",
            }
            for i in range(6)
        ]
        for subject in CORE_SUBJECTS
    }
    l1_responses = {
        subject: [
            {
                "question_index": i,
                "question_text": f"{subject} L1 Q{i}",
                "question_type": "mcq",
                "user_answer": "A",
                "correct_answer": "A",
                "is_correct": True,
                "time_taken_seconds": 5,
                "xp_earned": 5,
            }
            for i in range(6)
        ]
        for subject in CORE_SUBJECTS
    }

    _challenge_sessions[session_id] = {
        "session_id": session_id,
        "db_session_id": db_session.id,
        "user_id": user_id,
        "shs_level": "SHS 1",
        "challenge_level": 1,
        "status": "level_complete",
        "current_subject_index": 0,
        "current_question_index": 0,
        "questions": l1_questions,
        "responses": l1_responses,
        "level_archives": [],
        "total_xp": 120,
        "correct_count": 24,
        "wrong_count": 0,
        "started_at": "2026-01-01T00:00:00+00:00",
    }

    async def fake_generate(subject, shs_level, level):
        return [
            {
                "id": f"{subject}-l2-{i}",
                "question": f"{subject} L2 Q{i}",
                "question_type": "mcq",
                "options": {"A": "1", "B": "2", "C": "3", "D": "4"},
                "correct_answer": "B",
                "explanation": "level 2",
            }
            for i in range(6)
        ]

    monkeypatch.setattr(
        "app.assessment.challenge_hub.generate_subject_questions",
        fake_generate,
    )

    result = await continue_challenge_level(
        db=_FakeDB(db_session),
        user_id=user_id,
        session_id=session_id,
    )

    session = _challenge_sessions[session_id]
    assert result["challenge_level"] == 2
    assert session["challenge_level"] == 2
    assert session["status"] == "in_progress"
    assert session["responses"] == {}
    assert len(session["level_archives"]) == 1
    assert session["level_archives"][0]["challenge_level"] == 1
    assert session["level_archives"][0]["responses"]["Core Mathematics"][0]["question_index"] == 0

    # First Level 2 answer for each subject must succeed (previously returned None).
    for subject in CORE_SUBJECTS:
        feedback = submit_answer(
            session_id=session_id,
            subject=subject,
            question_index=0,
            user_answer="B",
            time_taken_seconds=3,
        )
        assert feedback is not None, f"Level 2 submit failed for {subject}"
        assert feedback["is_correct"] is True
        assert feedback["xp_earned"] == 5

    # Clean up in-memory session
    _challenge_sessions.pop(session_id, None)
