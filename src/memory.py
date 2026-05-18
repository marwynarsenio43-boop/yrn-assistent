"""
yrn.assistent — Gestão de histórico e memória
"""

import os
import json
from datetime import datetime
from typing import Optional

HISTORY_DIR  = os.path.join(os.path.expanduser("~"), ".yrn_assistent")
HISTORY_FILE = os.path.join(HISTORY_DIR, "history.json")


def _ensure_dir():
    os.makedirs(HISTORY_DIR, exist_ok=True)


def _load() -> list:
    _ensure_dir()
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def _save(data: list):
    _ensure_dir()
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def add_entry(command: str, result: dict):
    """Adiciona uma entrada ao histórico."""
    data = _load()
    entry = {
        "timestamp": datetime.now().isoformat(),
        "command": command,
        "intent": result.get("intent", ""),
        "success": result.get("success", False),
        "explanation": result.get("explanation", ""),
    }
    data.append(entry)
    # Manter apenas os últimos 500 registos
    if len(data) > 500:
        data = data[-500:]
    _save(data)


def get_history(n: int = 10) -> list:
    """Retorna os últimos n comandos."""
    data = _load()
    return data[-n:]


def clear_history():
    """Limpa todo o histórico."""
    _save([])


def get_stats() -> dict:
    """Retorna estatísticas de uso."""
    data = _load()
    total   = len(data)
    success = sum(1 for e in data if e.get("success"))
    rate    = round(success / total * 100, 1) if total else 0
    return {"total": total, "success": success, "success_rate": rate}
