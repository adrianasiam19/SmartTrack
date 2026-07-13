"""clear_content.py
Clears all lesson/question data arrays from frontend TypeScript files
while preserving types, interfaces, and utility functions.
"""

import re
import os

PROJECT = os.path.join(os.path.dirname(__file__), '..')


def clear_file(filepath, array_name, keep_lines_after=None):
    """Replace content of a named array with empty array []"""
    fullpath = os.path.join(PROJECT, filepath)
    with open(fullpath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the array declaration and replace its contents
    pattern = rf'({re.escape(array_name)}:\s*\w+\[\]\s*=\s*\[)(.*?)(\];)'
    
    def replace_callback(m):
        prefix = m.group(1)
        suffix = m.group(3)
        return prefix + '\n' + suffix

    new_content = re.sub(pattern, replace_callback, content, count=1, flags=re.DOTALL)

    with open(fullpath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"[OK] Cleared {array_name} in {filepath}")


def main():
    print("=" * 50)
    print("Clearing all content data from frontend files...")
    print("=" * 50)

    # 1. generalScienceContent.ts - empty GENERAL_SCIENCE_LESSONS
    clear_file(
        'app/lib/generalScienceContent.ts',
        'GENERAL_SCIENCE_LESSONS'
    )

    # 2. starterArenaData.ts - empty STARTER_ARENA_QUESTIONS
    clear_file(
        'app/lib/starterArenaData.ts',
        'STARTER_ARENA_QUESTIONS'
    )

    # 3. logicArenaData.ts - empty RAW (this feeds LOGIC_ARENA_QUESTIONS)
    clear_file(
        'app/lib/logicArenaData.ts',
        'RAW'
    )

    # 4. quantArenaData.ts - empty RAW
    clear_file(
        'app/lib/quantArenaData.ts',
        'RAW'
    )

    # 5. scientificArenaData.ts - empty RAW
    clear_file(
        'app/lib/scientificArenaData.ts',
        'RAW'
    )

    # 6. learningContent.ts - need special handling because ALL_LESSONS
    #    contains GENERAL_SCIENCE_LESSONS spread
    #    Let's replace the array contents between [ and ];
    print("\n--- learningContent.ts (special handling) ---")
    lc_path = os.path.join(PROJECT, 'app/lib/learningContent.ts')
    with open(lc_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find ALL_LESSONS array and replace everything between [ and ];
    pattern = r'(export const ALL_LESSONS: Lesson\[\] = \[)(.*?)(\];)'
    
    def replace_all_lessons(m):
        prefix = m.group(1)
        suffix = m.group(3)
        return prefix + '\n  // All lesson content has been cleared.\n  // Add new lessons here or import from content modules.\n' + suffix

    new_content = re.sub(pattern, replace_all_lessons, content, count=1, flags=re.DOTALL)
    
    with open(lc_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("[OK] Cleared ALL_LESSONS in app/lib/learningContent.ts")

    print("\n" + "=" * 50)
    print("[OK] All content cleared successfully!")
    print("=" * 50)


if __name__ == '__main__':
    main()
