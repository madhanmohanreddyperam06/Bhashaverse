"""
Bhashaverse - Explore Proverbs Page Delegate
Forwards execution cleanly to Frontend/pages/1_Explore_Proverbs.py
"""
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

target = BASE_DIR / "Frontend" / "pages" / "1_Explore_Proverbs.py"
with open(target, "r", encoding="utf-8") as f:
    exec(compile(f.read(), str(target), "exec"), globals())
