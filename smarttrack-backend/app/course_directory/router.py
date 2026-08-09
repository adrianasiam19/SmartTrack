"""Authenticated Course Directory API — browse university programmes (no cut-offs)."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.auth.dependencies import get_current_user
from app.course_directory import data as course_data
from app.users.models import User

router = APIRouter(prefix="/course-directory", tags=["Course Directory"])


@router.get("")
async def list_course_directory(
    field: str | None = Query(None, description="Exact field/category filter"),
    q: str | None = Query(None, description="Search name, brief, topics, careers"),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """List programme briefs for the Course Directory browse page."""
    _ = current_user
    programmes = course_data.list_programmes(field=field, q=q)
    return {
        "count": len(programmes),
        "fields": course_data.list_fields(),
        "programmes": programmes,
        "note": course_data.load_course_directory().get("note"),
    }


@router.get("/fields")
async def list_course_fields(
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    _ = current_user
    fields = course_data.list_fields()
    return {"fields": fields, "count": len(fields)}


@router.get("/{slug}")
async def get_course_programme(
    slug: str,
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    _ = current_user
    row = course_data.get_programme(slug)
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Programme not found in the Course Directory.",
        )
    return row
