"""Test setup: put src/ on the path and isolate the app DB to a temp file
so importing state.py never touches a real recall.db in the repo.
"""

import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

_fd, _db = tempfile.mkstemp(suffix=".db")
os.close(_fd)
os.environ.setdefault("RECALL_DB", _db)
