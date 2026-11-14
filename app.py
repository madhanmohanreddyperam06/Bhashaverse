"""
Bhashaverse - Cultural Wisdom AI Platform
Root Entrypoint Delegate: executes Frontend/app.py cleanly.
"""

from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

frontend_app_file = BASE_DIR / "Frontend" / "app.py"
with open(frontend_app_file, "r", encoding="utf-8") as f:
    code = compile(f.read(), str(frontend_app_file), "exec")
    exec(code, globals())
