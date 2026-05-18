"""
yrn.assistent — Orquestrador
Liga a IA ao motor RPA e à memória.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from ai_interpreter import interpret_command
from rpa_engine import execute_action
from memory import add_entry, get_stats


def run_command(command: str, history: list = None) -> dict:
    """
    Interpreta e executa um comando em linguagem natural.
    Retorna um dicionário com os resultados.
    """
    # 1. Interpretar com IA
    interpretation = interpret_command(command, history)

    intent      = interpretation.get("intent", "desconhecida")
    confidence  = interpretation.get("confidence", 0)
    actions     = interpretation.get("actions", [])
    explanation = interpretation.get("explanation", "")

    # 2. Se sem ações, retornar
    if not actions:
        result = {
            "success": False,
            "intent": intent,
            "confidence": confidence,
            "explanation": explanation,
            "results": [],
        }
        add_entry(command, result)
        return result

    # 3. Executar cada ação
    results     = []
    all_success = True

    for action_def in actions:
        action     = action_def.get("action", "")
        parameters = action_def.get("parameters", {})
        r = execute_action(action, parameters)
        results.append(r)
        if not r.get("success"):
            all_success = False

    # 4. Montar resultado final
    result = {
        "success":     all_success,
        "intent":      intent,
        "confidence":  confidence,
        "explanation": explanation,
        "results":     results,
    }

    # 5. Guardar no histórico
    add_entry(command, result)

    return result


def preview_command(command: str, history: list = None) -> dict:
    """
    Interpreta um comando mas NÃO o executa.
    Retorna o que seria feito.
    """
    interpretation = interpret_command(command, history)
    return interpretation


def stats() -> dict:
    """Retorna estatísticas de uso."""
    return get_stats()
