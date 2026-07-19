"""
seed_psychometric_cards.py
───────────────────────────
Inserts the psychometric question bank into the psychometric_cards table.
Reads from data/psychometric_cards.json and seeds the database.

Usage:
    cd smarttrack-backend
    python scripts/seed_psychometric_cards.py
"""
import asyncio
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if sys.platform == "win32":
    import asyncio as _asyncio
    _asyncio.set_event_loop_policy(_asyncio.WindowsSelectorEventLoopPolicy())

from app.config import settings
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "psychometric_cards.json"


def load_cards() -> list[dict]:
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


async def seed():
    cards = load_cards()
    print(f"Loaded {len(cards)} cards from data/psychometric_cards.json")
    
    engine = create_async_engine(settings.DATABASE_URL)
    
    async with engine.connect() as conn:
        # Check existing count
        result = await conn.execute(text("SELECT COUNT(*) FROM psychometric_cards"))
        existing = result.scalar()
        print(f"Existing cards in DB: {existing}")
        
        if existing > 0:
            print("Clearing existing cards...")
            await conn.execute(text("DELETE FROM psychometric_cards"))
            print("Cleared.")
        
        # Insert using raw SQL (avoids ORM circular import issues)
        for card_data in cards:
            await conn.execute(
                text("""
                    INSERT INTO psychometric_cards (card_id, question, options, created_at)
                    VALUES (:card_id, :question, :options_json, :created_at)
                """),
                {
                    "card_id": card_data["id"],
                    "question": card_data["question"],
                    "options_json": json.dumps(card_data["options"]),
                    "created_at": datetime.now(timezone.utc),
                }
            )
        
        await conn.commit()
        print(f"Inserted {len(cards)} cards.")
        
        # Verify
        result = await conn.execute(text("SELECT COUNT(*) FROM psychometric_cards"))
        final_count = result.scalar()
        print(f"Verified: {final_count} cards in database.")
        
        # Check duplicates
        result = await conn.execute(text("""
            SELECT card_id, COUNT(*) as cnt 
            FROM psychometric_cards 
            GROUP BY card_id 
            HAVING COUNT(*) > 1
        """))
        dups = result.fetchall()
        if dups:
            print(f"WARNING: {len(dups)} duplicate card_ids:")
            for d in dups:
                print(f"  {d[0]}: {d[1]}")
        else:
            print("No duplicates found.")
        
        # Show first 3 cards as sample
        result = await conn.execute(
            text("SELECT card_id, question FROM psychometric_cards ORDER BY card_id LIMIT 3")
        )
        print("\nSample cards:")
        for row in result:
            print(f"  [{row[0]}] {row[1][:60]}...")
    
    await engine.dispose()
    print("\nSeeding complete!")


if __name__ == "__main__":
    asyncio.run(seed())
