"""Course Directory — static catalogue of university programmes (no eligibility)."""
from __future__ import annotations

from app.course_directory.data import get_programme, list_fields, list_programmes

__all__ = ["list_programmes", "list_fields", "get_programme"]
