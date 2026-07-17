from app.users.schemas import UserPublic, UserUpdate


def test_user_public_exposes_starter_arena_completed():
    fields = set(UserPublic.model_fields)
    assert "onboarding_completed" in fields
    assert "starter_arena_completed" in fields


def test_user_update_accepts_starter_arena_completed():
    body = UserUpdate(starter_arena_completed=True, onboarding_completed=True)
    assert body.starter_arena_completed is True
    assert body.onboarding_completed is True
