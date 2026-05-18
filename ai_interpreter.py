"""
yrn.assistent — AI Interpreter
Converte linguagem natural em ações estruturadas.

Usa Groq (GRATUITO) como motor principal — llama-3.3-70b-versatile.
Fallback automático para Google Gemini (também GRATUITO).

Como obter as chaves (ambas gratuitas):
  Groq   → https://console.groq.com       (14.400 req/dia grátis)
  Gemini → https://aistudio.google.com    (tier gratuito generoso)
"""

import os
import json
import re
import urllib.request
import urllib.error
from typing import Optional

# ─── Prompt do sistema ────────────────────────────────────────────────────────

SYSTEM_PROMPT = """
Você é o módulo de interpretação do yrn.assistent, um assistente RPA inteligente.

O seu trabalho é converter comandos em linguagem natural (português ou inglês) em
ações estruturadas JSON que o sistema RPA irá executar no computador do utilizador.

## Ações disponíveis

| action        | Descrição                        | Parâmetros obrigatórios                   |
|---------------|----------------------------------|-------------------------------------------|
| open_folder   | Abre pasta no explorador         | folder: str                               |
| open_file     | Abre um ficheiro                 | file: str, folder?: str                   |
| play_media    | Reproduz vídeo/áudio             | file: str, folder?: str                   |
| open_app      | Abre uma aplicação               | app: str                                  |
| list_folder   | Lista conteúdo de uma pasta      | folder: str                               |
| create_folder | Cria uma nova pasta              | name: str, location?: str                 |
| delete_file   | Elimina um ficheiro              | file: str, folder?: str                   |
| copy_file     | Copia um ficheiro                | file: str, destination: str, folder?: str |

## Regras

1. Responda SEMPRE em JSON puro, sem texto adicional, sem markdown, sem backticks.
2. O JSON deve ter exactamente este formato:
   {
     "intent": "descrição breve da intenção do utilizador",
     "confidence": 0.0 a 1.0,
     "actions": [
       { "action": "nome_da_ação", "parameters": { ... } },
       ...
     ],
     "explanation": "explicação breve em português do que vai ser feito"
   }
3. Uma instrução pode gerar múltiplas ações (ex: "abre a pasta e reproduz o vídeo" = 2 ações).
4. Se a instrução não puder ser mapeada para nenhuma ação, retorne:
   { "intent": "desconhecida", "confidence": 0, "actions": [], "explanation": "Não consigo executar esta tarefa." }
5. Seja inteligente com aliases: "Documentos" = "Documents", "Área de trabalho" = "Desktop", etc.
6. Para ficheiros multimédia (mp4, mkv, avi, mp3, wav), use sempre "play_media".
7. Nunca invente nomes de ficheiros — use exactamente o que o utilizador mencionou.

## Exemplos

Entrada: "abre a pasta Documentos e reproduz o filme Inception"
Saída:
{"intent":"abrir pasta e reproduzir vídeo","confidence":0.97,"actions":[{"action":"open_folder","parameters":{"folder":"Documentos"}},{"action":"play_media","parameters":{"file":"Inception","folder":"Documentos"}}],"explanation":"Vou abrir a pasta Documentos e reproduzir o filme Inception."}

Entrada: "cria uma pasta chamada Projetos no Desktop"
Saída:
{"intent":"criar pasta","confidence":0.99,"actions":[{"action":"create_folder","parameters":{"name":"Projetos","location":"Desktop"}}],"explanation":"Vou criar a pasta 'Projetos' no ambiente de trabalho."}
""".strip()


# ─── Utilitário HTTP (sem dependências externas) ──────────────────────────────

def _post_json(url: str, headers: dict, body: dict) -> dict:
    data = json.dumps(body).encode("utf-8")
    req  = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _clean_json(raw: str) -> str:
    """Remove backticks e espaços residuais de respostas de IA."""
    raw = raw.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    # Extrair apenas o bloco JSON se houver texto antes/depois
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    return match.group(0) if match else raw


# ─── Provider: Groq (principal — gratuito) ────────────────────────────────────

def _call_groq(messages: list, system: str, max_tokens: int = 1024) -> str:
    """
    Chama a API do Groq com LLaMA 3.3 70B.
    Chave gratuita em: https://console.groq.com
    """
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise EnvironmentError("GROQ_API_KEY não definida.")

    body = {
        "model": "llama-3.3-70b-versatile",
        "max_tokens": max_tokens,
        "temperature": 0.1,
        "messages": [{"role": "system", "content": system}] + messages,
    }

    resp = _post_json(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        body=body,
    )
    return resp["choices"][0]["message"]["content"]


# ─── Provider: Google Gemini (fallback — gratuito) ────────────────────────────

def _call_gemini(messages: list, system: str, max_tokens: int = 1024) -> str:
    """
    Chama a API do Google Gemini 1.5 Flash.
    Chave gratuita em: https://aistudio.google.com
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError("GEMINI_API_KEY não definida.")

    # Converter mensagens para formato Gemini
    contents = []
    for m in messages:
        role = "user" if m["role"] == "user" else "model"
        contents.append({"role": role, "parts": [{"text": m["content"]}]})

    body = {
        "system_instruction": {"parts": [{"text": system}]},
        "contents": contents,
        "generationConfig": {
            "maxOutputTokens": max_tokens,
            "temperature": 0.1,
        },
    }

    url  = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    resp = _post_json(url, headers={"Content-Type": "application/json"}, body=body)
    return resp["candidates"][0]["content"]["parts"][0]["text"]


# ─── Router — tenta Groq, fallback Gemini ────────────────────────────────────

def _call_ai(messages: list, system: str, max_tokens: int = 1024) -> str:
    """
    Tenta Groq primeiro; se falhar (sem chave ou erro), tenta Gemini.
    Lança EnvironmentError se nenhum estiver configurado.
    """
    errors = []

    # 1. Groq
    if os.environ.get("GROQ_API_KEY"):
        try:
            return _call_groq(messages, system, max_tokens)
        except Exception as e:
            errors.append(f"Groq: {e}")

    # 2. Gemini
    if os.environ.get("GEMINI_API_KEY"):
        try:
            return _call_gemini(messages, system, max_tokens)
        except Exception as e:
            errors.append(f"Gemini: {e}")

    raise EnvironmentError(
        "Nenhuma chave de API configurada ou ambas falharam.\n"
        f"Detalhes: {'; '.join(errors)}\n\n"
        "Configure pelo menos uma das seguintes variáveis de ambiente:\n"
        "  GROQ_API_KEY   → https://console.groq.com       (gratuito)\n"
        "  GEMINI_API_KEY → https://aistudio.google.com    (gratuito)"
    )


# ─── Interface pública ────────────────────────────────────────────────────────

def interpret_command(command: str, history: Optional[list] = None) -> dict:
    """
    Interpreta um comando em linguagem natural e retorna ações estruturadas.

    Args:
        command: O comando do utilizador em linguagem natural.
        history: Histórico de mensagens anteriores para contexto (opcional).

    Returns:
        Dicionário com intent, confidence, actions e explanation.
    """
    messages = []
    if history:
        messages.extend(history[-6:])
    messages.append({"role": "user", "content": command})

    raw = ""
    try:
        raw    = _call_ai(messages, SYSTEM_PROMPT, max_tokens=1024)
        clean  = _clean_json(raw)
        return json.loads(clean)

    except json.JSONDecodeError as e:
        return {
            "intent": "erro_parse",
            "confidence": 0,
            "actions": [],
            "explanation": f"A IA respondeu em formato inválido: {e}",
            "raw_response": raw,
        }
    except EnvironmentError as e:
        return {
            "intent": "erro_config",
            "confidence": 0,
            "actions": [],
            "explanation": str(e),
        }
    except Exception as e:
        return {
            "intent": "erro",
            "confidence": 0,
            "actions": [],
            "explanation": f"Erro inesperado: {e}",
        }


def explain_command(command: str) -> str:
    result = interpret_command(command)
    return result.get("explanation", "Não foi possível interpretar o comando.")


def get_suggestions(partial: str) -> list:
    """Gera sugestões de autocomplete para um comando parcial."""
    system = (
        "Você é um assistente de autocomplete para comandos RPA em português. "
        "Dado um comando parcial, sugira 3 completamentos possíveis e úteis. "
        "Responda APENAS com um JSON array de strings, sem explicações, sem backticks."
    )
    try:
        raw   = _call_ai([{"role": "user", "content": f"Completar: '{partial}'"}], system, 256)
        clean = _clean_json(raw)
        return json.loads(clean)
    except Exception:
        return []
