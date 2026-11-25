"""A plain HTTP server. The HTTP parsing is in shared/tiny_http.py: do read it.

    python 03-http/http_server.py
    python 03-http/http_server.py 9010      (use another port)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "shared"))
from lab import serve
from tiny_http import handle_http

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 9003
serve(PORT, handle_http)
