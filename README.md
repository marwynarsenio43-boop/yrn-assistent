# ⚡ yrn.assistent

> **Controle o seu computador com linguagem natural — RPA + Inteligência Artificial**

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)](https://python.org)
[![Anthropic](https://img.shields.io/badge/Powered%20by-Groq%20%26%20Gemini-brightgreen)](https://console.groq.com)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)](https://github.com)

---

## 📖 O que é o yrn.assistent?

O **yrn.assistent** é um sistema desktop inteligente que combina **RPA (Robotic Process Automation)** com **Inteligência Artificial** para permitir que o utilizador execute tarefas no computador através de comandos em linguagem natural.

Basta escrever algo como:

```
abre a pasta Documentos e reproduz o filme Inception
```

E o sistema irá:
1. **Interpretar** a intenção usando IA (Claude da Anthropic)
2. **Decompor** em ações estruturadas (`open_folder` + `play_media`)
3. **Executar** automaticamente no sistema operativo via RPA

---

## ✨ Funcionalidades

| Funcionalidade | Descrição |
|---|---|
| 🧠 **Interpretação com IA** | Usa Gemini/Groq para entender comandos em português |
| 🤖 **Execução RPA** | Automatiza ações reais no sistema operativo |
| 💬 **Linguagem natural** | Sem sintaxe rígida — escreva como fala |
| 📁 **Gestão de ficheiros** | Abrir, criar, copiar, apagar pastas e ficheiros |
| 🎬 **Multimédia** | Reproduzir vídeos e áudio com o leitor padrão |
| 🖥️ **Abrir aplicações** | Chrome, VLC, Word, terminal, calculadora, e mais |
| 🔍 **Modo pré-visualização** | Ver o que seria feito antes de executar |
| 📊 **Histórico & Estatísticas** | Registo de todos os comandos executados |
| 🌐 **Interface Web** | UI elegante em HTML/JS sem dependências extras |
| ⌨️ **Interface CLI** | Terminal interativo com design visual rico |

---

## 🏗️ Arquitetura

```
yrn-assistent/
│
├── cli.py                    # Interface de linha de comandos (terminal)
├── requirements.txt          # Dependências Python
│
├── src/
│   ├── __init__.py
│   ├── ai_interpreter.py     # Módulo de IA — interpreta linguagem natural
│   ├── rpa_engine.py         # Motor RPA — executa ações no SO
│   ├── orchestrator.py       # Orquestrador — liga IA + RPA + memória
│   └── memory.py             # Gestão de histórico e aprendizagem
│
└── web_ui/
    └── index.html            # Interface web (abre no browser)
```

### Fluxo de execução

```
Utilizador escreve comando
        │
        ▼
┌─────────────────┐
│  ai_interpreter │  ← Groq LLaMA 3 / Gemini (GRATUITO)
│  Interpreta NLP │
└────────┬────────┘
         │  JSON estruturado
         ▼
┌─────────────────┐
│   orchestrator  │  ← Coordena tudo
│   Valida & Rota │
└────────┬────────┘
         │  Lista de ações
         ▼
┌─────────────────┐
│   rpa_engine    │  ← subprocess, os, shutil
│   Executa no SO │
└────────┬────────┘
         │  Resultados
         ▼
┌─────────────────┐
│    memory.py    │  ← JSON local
│   Regista tudo  │
└─────────────────┘
```

---

## 🚀 Instalação — 100% Gratuito

### Pré-requisitos

- Python 3.9 ou superior
- Chave gratuita do **Groq** ou **Google Gemini** (ver abaixo)

### ✅ Como obter uma chave de API GRATUITA

O yrn.assistent usa APIs **100% gratuitas**. Escolhe uma (ou ambas):

| Serviço | Tier Gratuito | Link |
|---|---|---|
| **Groq** ⭐ recomendado | 14.400 requests/dia grátis | [console.groq.com](https://console.groq.com) |
| **Google Gemini** | Tier gratuito generoso | [aistudio.google.com](https://aistudio.google.com) |

**Passos para o Groq (recomendado):**
1. Acede a [console.groq.com](https://console.groq.com)
2. Cria conta gratuita (podes usar o Google)
3. Vai a **API Keys** → **Create API Key**
4. Copia a chave (começa por `gsk_...`)

### Passos de instalação

```bash
# 1. Clonar o repositório
git clone https://github.com/SEU_USUARIO/yrn-assistent.git
cd yrn-assistent

# 2. Instalar dependência opcional
pip install -r requirements.txt

# 3. Definir a chave gratuita do Groq
# Linux / macOS:
export GROQ_API_KEY="gsk_..."

# Windows (CMD):
set GROQ_API_KEY=gsk_...

# Windows (PowerShell):
$env:GROQ_API_KEY="gsk_..."

# Alternativa com Google Gemini:
export GEMINI_API_KEY="AIza..."
```

> **Dica:** Para definir permanentemente, adiciona a linha ao teu `~/.bashrc` ou `~/.zshrc`.

---

## 💻 Como usar

### Interface CLI (Terminal)

```bash
python cli.py
```

```
  ✦  y r n . a s s i s t e n t  ✦

  RPA + Inteligência Artificial

yrn› abre a pasta Documentos
──────────────────────────────────────
  Confiança: 97%  Intenção: abrir pasta
  → Vou abrir a pasta Documentos no explorador de ficheiros.

  ✓ open_folder  folder=Documentos
     Pasta '/home/user/Documents' aberta com sucesso.

✓  Tarefa concluída com sucesso.
──────────────────────────────────────
```

**Comandos especiais do CLI:**

| Comando | Descrição |
|---|---|
| `ajuda` | Lista todos os comandos |
| `preview <cmd>` | Pré-visualiza sem executar |
| `histórico` | Últimos 10 comandos |
| `estatísticas` | Estatísticas de uso |
| `limpar` | Limpa o ecrã |
| `sair` | Encerra o assistente |

### Interface Web

```bash
# Abrir o ficheiro diretamente no browser:
# Linux/macOS:
open web_ui/index.html

# Windows:
start web_ui/index.html
```

> **Nota:** Para usar a interface web com a API real, edite `web_ui/index.html` e defina `window.ANTHROPIC_API_KEY = 'sk-ant-...'` no início do script.

### Uso programático (Python)

```python
from src.orchestrator import run_command, preview_command, stats

# Executar um comando
result = run_command("abre a pasta Documentos e reproduz o filme Inception")

print(result['explanation'])   # Descrição do que foi feito
print(result['success'])       # True / False
print(result['results'])       # Lista de resultados por ação

# Pré-visualizar sem executar
preview = preview_command("cria uma pasta chamada Projetos no Desktop")

# Ver estatísticas
s = stats()
print(f"Total de comandos: {s['total']}")
print(f"Taxa de sucesso: {s['success_rate']}%")
```

---

## 🎯 Exemplos de comandos

```
# Pastas
abre a pasta Documentos
abre o Desktop
lista o conteúdo de Downloads
cria uma pasta chamada Projetos no Desktop

# Ficheiros e multimédia
reproduz o filme Avatar na pasta Vídeos
abre o ficheiro relatorio.pdf em Documentos
reproduz a música favorita.mp3

# Aplicações
abre o Chrome
abre a calculadora
abre o bloco de notas e o Excel
inicia o VLC

# Operações compostas
abre a pasta Downloads e lista o seu conteúdo
cria uma pasta chamada Backup e abre-a
```

---

## 🔧 Ações RPA disponíveis

| Ação | Parâmetros | Descrição |
|---|---|---|
| `open_folder` | `folder` | Abre pasta no explorador |
| `open_file` | `file`, `folder?` | Abre ficheiro com app padrão |
| `play_media` | `file`, `folder?` | Reproduz vídeo ou áudio |
| `open_app` | `app` | Inicia uma aplicação |
| `list_folder` | `folder` | Lista conteúdo de uma pasta |
| `create_folder` | `name`, `location?` | Cria nova pasta |
| `delete_file` | `file`, `folder?` | Elimina ficheiro |
| `copy_file` | `file`, `destination`, `folder?` | Copia ficheiro |

---

## 🌍 Compatibilidade

| Sistema Operativo | Suporte |
|---|---|
| Windows 10/11 | ✅ Completo |
| Ubuntu / Debian | ✅ Completo |
| macOS (Monterey+) | ✅ Completo |
| Outras distros Linux | ✅ Parcial (xdg-open) |

---

## 📁 Histórico local

O histórico é guardado em `~/.yrn_assistent/history.json` e é usado para melhorar o contexto das interpretações futuras.

---

## 🤝 Contribuição

1. Fork o repositório
2. Crie um branch: `git checkout -b feature/nova-funcionalidade`
3. Commit: `git commit -m "feat: adiciona nova funcionalidade"`
4. Push: `git push origin feature/nova-funcionalidade`
5. Abra um Pull Request

---

## 📄 Licença

MIT License — veja [LICENSE](LICENSE) para detalhes.

---

## 👤 Autor

Desenvolvido por **Marwyn** — ISCIM, Sistemas de Informação

---

*yrn.assistent — Torne a interação homem-máquina mais natural, intuitiva e produtiva.*
