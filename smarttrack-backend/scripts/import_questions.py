import asyncio
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import json
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, delete
from app.assessment.models import Question
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)

engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def import_questions(file_path: str, clear_existing: bool = False):
    async with AsyncSessionLocal() as db:
        if clear_existing:
            print("Cleaning existing questions...")
            await db.execute(delete(Question))
            await db.commit()

        with open(file_path, "r") as f:
            questions_data = json.load(f)

        count = 0
        for q_data in questions_data:
            # Check for duplicates by text
            existing = await db.execute(select(Question).where(Question.question == q_data["question"]))
            if existing.scalar_one_or_none():
                continue

            q = Question(
                domain=q_data["domain"],
                question=q_data["question"],
                options=q_data["options"],
                correct_answer=q_data["correct_answer"],
                difficulty_a=q_data.get("difficulty_a", 1.0),
                difficulty_b=q_data.get("difficulty_b", 0.0),
                difficulty_c=q_data.get("difficulty_c", 0.25)
            )
            db.add(q)
            count += 1

        await db.commit()
        print(f"Successfully imported {count} new questions!")

if __name__ == "__main__":
    import sys
    path = "data/questions_expanded.json"
    clear = "--clear" in sys.argv
    asyncio.run(import_questions(path, clear))
