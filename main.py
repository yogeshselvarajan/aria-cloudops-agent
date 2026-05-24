"""
CloudOps Triage Agent
Built for: AWS UG Madurai | Builders Skill Sprint — April 2026
"""

from __future__ import annotations

import json
import os
import sys
import urllib.request
import urllib.error

os.environ["BYPASS_TOOL_CONSENT"] = "true"

from aria import TriageAgent
from aria.config import DEFAULT_CONFIG
from aria.ui import Terminal


def check_ollama(host: str) -> bool:
    try:
        with urllib.request.urlopen(f"{host}/api/tags", timeout=3) as r:
            return r.status == 200
    except (urllib.error.URLError, OSError):
        return False


def check_model(host: str, model_id: str) -> bool:
    try:
        with urllib.request.urlopen(f"{host}/api/tags", timeout=3) as r:
            data = json.loads(r.read())
            names = [m.get("name", "") for m in data.get("models", [])]
            return any(model_id in name for name in names)
    except Exception:
        return False


def main() -> None:
    ui = Terminal()
    host = DEFAULT_CONFIG.host
    model = DEFAULT_CONFIG.model_id

    if not check_ollama(host):
        ui.error(
            "Ollama Not Running",
            f"Cannot reach {host}\n\n"
            "  1. Install : https://ollama.com/download\n"
            "  2. Start   : ollama serve\n"
            f"  3. Pull    : ollama pull {model}\n"
            "  4. Re-run  : python main.py",
        )
        sys.exit(1)

    if not check_model(host, model):
        ui.error(
            "Model Not Found",
            f"Ollama is running but '{model}' is not available to the server.\n\n"
            "This usually means Ollama was started before OLLAMA_MODELS was set.\n\n"
            "Fix — stop Ollama, then restart it like this:\n\n"
            "  Windows CMD:\n"
            "    set OLLAMA_MODELS=D:\\Ollama Models\n"
            "    ollama serve\n\n"
            "  PowerShell:\n"
            "    $env:OLLAMA_MODELS = 'D:\\Ollama Models'\n"
            "    ollama serve\n\n"
            f"Then verify:  ollama list   (should show {model})",
        )
        sys.exit(1)

    try:
        TriageAgent().run()
    except KeyboardInterrupt:
        print("\nExiting ARIA.")
        sys.exit(0)


if __name__ == "__main__":
    main()
