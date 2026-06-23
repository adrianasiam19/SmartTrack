"""
import_communication.py
────────────────────────
Imports Communication Arena SHS 1 questions into the database
without clearing existing questions. Checks for duplicates by question text.
"""

import asyncio
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import json
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, func
from app.assessment.models import Question
from dotenv import load_dotenv

load_dotenv()

# ── Database URL ──────────────────────────────────────────────────────────────
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    if DATABASE_URL.startswith("postgresql://"):
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)

if not DATABASE_URL:
    print("[ERROR] DATABASE_URL not set in environment or .env file.")
    sys.exit(1)

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def import_communication_questions():
    """Read communication_shs1.json and insert questions into DB."""
    file_path = os.path.join(os.path.dirname(__file__), "..", "data", "communication_shs1.json")
    if not os.path.exists(file_path):
        print(f"[ERROR] File not found: {file_path}")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        questions_data = json.load(f)

    print(f"[INFO] Loaded {len(questions_data)} questions from communication_shs1.json")

    async with AsyncSessionLocal() as db:
        with db.no_autoflush:
            # Find the current max id in the DB
            result = await db.execute(select(func.max(Question.id)))
            max_id = result.scalar() or 0
            print(f"[INFO] Current max question ID in DB: {max_id}")

            # Fetch all existing question texts for duplicate checking
            existing_result = await db.execute(select(Question.question))
            existing_texts = {row[0] for row in existing_result.fetchall()}
            print(f"[INFO] Existing questions in DB: {len(existing_texts)}")

            count = 0
            skipped = 0
            next_id = max_id + 1

            for q_data in questions_data:
                question_text = q_data["question"]

                # Check for duplicates by question text
                if question_text in existing_texts:
                    skipped += 1
                    continue

                q = Question(
                    id=next_id,
                    domain=q_data.get("domain", "General"),
                    arena=q_data.get("arena"),
                    difficulty_tier=q_data.get("difficulty_tier"),
                    shs_levels=q_data.get("shs_levels"),
                    template_id=q_data.get("template_id"),
                    question=question_text,
                    options=q_data["options"],
                    correct_answer=q_data["correct_answer"],
                    explanation=q_data.get("explanation"),
                    difficulty_a=q_data.get("difficulty_a", 1.0),
                    difficulty_b=q_data.get("difficulty_b", 0.0),
                    difficulty_c=q_data.get("difficulty_c", 0.25),
                )
                db.add(q)
                existing_texts.add(question_text)  # prevent same-file duplicates
                count += 1
                next_id += 1

        # Commit all at once (outside no_autoflush block)
        await db.commit()
        print(f"[OK] Imported {count} new Communication Arena questions.")
        if skipped > 0:
            print(f"[SKIP] {skipped} questions already existed (duplicate check).")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(import_communication_questions())
