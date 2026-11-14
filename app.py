"""
Bhashaverse - Cultural Wisdom AI Platform
Root Entrypoint Delegate for Streamlit Cloud & Standard Runners
Forwards execution cleanly to Frontend/app.py
"""
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

target = BASE_DIR / "Frontend" / "app.py"
with open(target, "r", encoding="utf-8") as f:
    exec(compile(f.read(), str(target), "exec"), globals())

