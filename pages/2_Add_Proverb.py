"""
Bhashaverse - Root Page Forwarder
Delegates to Frontend/pages/2_Add_Proverb.py
"""

from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

target_file = BASE_DIR / "Frontend" / "pages" / "2_Add_Proverb.py"
with open(target_file, "r", encoding="utf-8") as f:
    code = compile(f.read(), str(target_file), "exec")
    exec(code, globals())
