"""
yrn.assistent — Interface de Linha de Comandos
"""

import os
import sys

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from orchestrator import run_command, preview_command, stats
from memory import get_history, clear_history


BANNER = r"""
  ╔══════════════════════════════════════╗
  ║                                      ║
  ║     ✦  y r n . a s s i s t e n t   ║
  ║                                      ║
  ║      RPA + Inteligência Artificial   ║
  ║                                      ║
  ╚══════════════════════════════════════╝
"""

AJUDA = """
  Comandos especiais:
  ─────────────────────────────────────────
  ajuda              → mostra esta ajuda
  preview <comando>  → pré-visualiza sem executar
  histórico          → últimos 10 comandos
  estatísticas       → estatísticas de uso
  limpar             → limpa o ecrã
  sair               → encerra o assistente
  ─────────────────────────────────────────
  Exemplos de comandos:
    abre a pasta Documentos
    abre o Chrome
    cria uma pasta chamada Projetos no Desktop
    lista o conteúdo de Downloads
"""


def limpar_ecra():
    os.system("cls" if os.name == "nt" else "clear")


def mostrar_resultado(result: dict):
    print("\n" + "─" * 50)
    confidence = result.get("confidence", 0)
    intent = result.get("intent", "desconhecida")
    explanation = result.get("explanation", "")

    print(f"  Confiança: {int(confidence * 100)}%  |  Intenção: {intent}")
    print(f"  → {explanation}\n")

    results = result.get("results", [])
    for r in results:
        action = r.get("action", "")
        success = r.get("success", False)
        message = r.get("message", "")
        icon = "✓" if success else "✗"
        print(f"  {icon} {action}")
        print(f"     {message}")

    overall = result.get("success", False)
    print()
    if overall:
        print("  ✓  Tarefa concluída com sucesso.")
    else:
        print("  ✗  Ocorreu um erro durante a execução.")
    print("─" * 50 + "\n")


def main():
    limpar_ecra()
    print(BANNER)

    # Verificar chave de API
    groq_key = os.environ.get("GROQ_API_KEY")
    gemini_key = os.environ.get("GEMINI_API_KEY")

    if not groq_key and not gemini_key:
        print("  ⚠  AVISO: Nenhuma chave de API configurada!")
        print("  Define GROQ_API_KEY ou GEMINI_API_KEY para usar a IA.\n")
        print("  Groq (gratuito): https://console.groq.com")
        print("  Gemini (gratuito): https://aistudio.google.com\n")
    else:
        provider = "Groq" if groq_key else "Gemini"
        print(f"  ✓  Conectado via {provider}\n")

    print('  Escreve "ajuda" para ver os comandos disponíveis.\n')

    while True:
        try:
            cmd = input("  yrn› ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\n  Até logo!\n")
            break

        if not cmd:
            continue

        # Comandos especiais
        if cmd.lower() in ("sair", "exit", "quit"):
            print("\n  Até logo!\n")
            break

        elif cmd.lower() == "ajuda":
            print(AJUDA)

        elif cmd.lower() == "limpar":
            limpar_ecra()
            print(BANNER)

        elif cmd.lower() == "histórico" or cmd.lower() == "historico":
            history = get_history(10)
            if not history:
                print("\n  Sem histórico ainda.\n")
            else:
                print("\n  Últimos comandos:")
                print("  " + "─" * 40)
                for i, entry in enumerate(history, 1):
                    c = entry.get("command", "")
                    s = "✓" if entry.get("success") else "✗"
                    print(f"  {i:2}. {s} {c}")
                print()

        elif cmd.lower() == "estatísticas" or cmd.lower() == "estatisticas":
            s = stats()
            print(f"\n  Total de comandos : {s.get('total', 0)}")
            print(f"  Bem sucedidos     : {s.get('success', 0)}")
            print(f"  Taxa de sucesso   : {s.get('success_rate', 0)}%\n")

        elif cmd.lower().startswith("preview "):
            comando = cmd[8:].strip()
            if not comando:
                print("\n  Uso: preview <comando>\n")
            else:
                print(f"\n  Pré-visualizando: {comando}")
                result = preview_command(comando)
                actions = result.get("actions", [])
                explanation = result.get("explanation", "")
                print(f"\n  → {explanation}")
                if actions:
                    print("\n  Ações que seriam executadas:")
                    for a in actions:
                        action = a.get("action", "")
                        params = a.get("parameters", {})
                        print(f"    • {action}: {params}")
                print()

        else:
            # Comando normal — executar
            print(f"\n  A processar: {cmd}")
            result = run_command(cmd)
            mostrar_resultado(result)


if __name__ == "__main__":
    main()
