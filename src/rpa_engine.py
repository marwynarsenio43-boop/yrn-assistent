"""
yrn.assistent — Motor RPA
Executa ações no sistema operativo.
"""

import os
import sys
import shutil
import subprocess
import platform

try:
    import send2trash
    HAS_SEND2TRASH = True
except ImportError:
    HAS_SEND2TRASH = False


def _resolve_folder(folder: str) -> str:
    """Resolve nomes especiais de pastas para caminhos reais."""
    home = os.path.expanduser("~")
    mapping = {
        "documentos": os.path.join(home, "Documents"),
        "documents":  os.path.join(home, "Documents"),
        "desktop":    os.path.join(home, "Desktop"),
        "área de trabalho": os.path.join(home, "Desktop"),
        "ambiente de trabalho": os.path.join(home, "Desktop"),
        "downloads":  os.path.join(home, "Downloads"),
        "imagens":    os.path.join(home, "Pictures"),
        "pictures":   os.path.join(home, "Pictures"),
        "músicas":    os.path.join(home, "Music"),
        "music":      os.path.join(home, "Music"),
        "vídeos":     os.path.join(home, "Videos"),
        "videos":     os.path.join(home, "Videos"),
        "home":       home,
        "início":     home,
    }
    return mapping.get(folder.lower(), folder)


def _open_path(path: str):
    """Abre um caminho com a aplicação padrão do sistema."""
    if platform.system() == "Windows":
        os.startfile(path)
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])


def open_folder(folder: str, **_) -> dict:
    """Abre uma pasta no explorador de ficheiros."""
    path = _resolve_folder(folder)
    if not os.path.isabs(path):
        path = os.path.join(os.path.expanduser("~"), path)
    if not os.path.exists(path):
        return {"success": False, "message": f"Pasta não encontrada: {path}"}
    try:
        _open_path(path)
        return {"success": True, "message": f"Pasta '{path}' aberta com sucesso."}
    except Exception as e:
        return {"success": False, "message": str(e)}


def open_file(file: str, folder: str = "", **_) -> dict:
    """Abre um ficheiro com a aplicação padrão."""
    base = _resolve_folder(folder) if folder else os.path.expanduser("~")
    path = os.path.join(base, file) if folder else file
    if not os.path.exists(path):
        # Tentar encontrar em pastas comuns
        for d in ["Documents", "Desktop", "Downloads"]:
            candidate = os.path.join(os.path.expanduser("~"), d, file)
            if os.path.exists(candidate):
                path = candidate
                break
    if not os.path.exists(path):
        return {"success": False, "message": f"Ficheiro não encontrado: {file}"}
    try:
        _open_path(path)
        return {"success": True, "message": f"Ficheiro '{path}' aberto com sucesso."}
    except Exception as e:
        return {"success": False, "message": str(e)}


def play_media(file: str, folder: str = "", **_) -> dict:
    """Reproduz um ficheiro multimédia."""
    return open_file(file, folder)


def open_app(app: str, **_) -> dict:
    """Abre uma aplicação."""
    app_lower = app.lower()

    # Mapeamento de nomes comuns para executáveis
    app_map_win = {
        "chrome":       "chrome",
        "google chrome": "chrome",
        "firefox":      "firefox",
        "edge":         "msedge",
        "word":         "winword",
        "excel":        "excel",
        "powerpoint":   "powerpnt",
        "notepad":      "notepad",
        "bloco de notas": "notepad",
        "calculadora":  "calc",
        "calculator":   "calc",
        "terminal":     "cmd",
        "cmd":          "cmd",
        "vlc":          "vlc",
        "paint":        "mspaint",
        "explorador":   "explorer",
        "explorer":     "explorer",
    }

    app_map_linux = {
        "chrome":       "google-chrome",
        "google chrome": "google-chrome",
        "firefox":      "firefox",
        "calculadora":  "gnome-calculator",
        "calculator":   "gnome-calculator",
        "terminal":     "gnome-terminal",
        "vlc":          "vlc",
        "explorador":   "nautilus",
        "explorer":     "nautilus",
    }

    try:
        if platform.system() == "Windows":
            exe = app_map_win.get(app_lower, app)
            subprocess.Popen(exe, shell=True)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", "-a", app])
        else:
            exe = app_map_linux.get(app_lower, app)
            subprocess.Popen([exe])
        return {"success": True, "message": f"Aplicação '{app}' iniciada."}
    except Exception as e:
        return {"success": False, "message": f"Não foi possível abrir '{app}': {e}"}


def list_folder(folder: str, **_) -> dict:
    """Lista o conteúdo de uma pasta."""
    path = _resolve_folder(folder)
    if not os.path.isabs(path):
        path = os.path.join(os.path.expanduser("~"), path)
    if not os.path.exists(path):
        return {"success": False, "message": f"Pasta não encontrada: {path}"}
    try:
        items = os.listdir(path)
        dirs  = [i for i in items if os.path.isdir(os.path.join(path, i))]
        files = [i for i in items if os.path.isfile(os.path.join(path, i))]
        msg = f"Pasta '{path}': {len(dirs)} pastas, {len(files)} ficheiros.\n"
        if dirs:
            msg += "  Pastas: " + ", ".join(dirs[:10])
            if len(dirs) > 10:
                msg += f" ... (+{len(dirs)-10})"
            msg += "\n"
        if files:
            msg += "  Ficheiros: " + ", ".join(files[:10])
            if len(files) > 10:
                msg += f" ... (+{len(files)-10})"
        return {"success": True, "message": msg, "items": items}
    except Exception as e:
        return {"success": False, "message": str(e)}


def create_folder(name: str, location: str = "Desktop", **_) -> dict:
    """Cria uma nova pasta."""
    base = _resolve_folder(location) if location else os.path.expanduser("~")
    path = os.path.join(base, name)
    try:
        os.makedirs(path, exist_ok=True)
        return {"success": True, "message": f"Pasta '{path}' criada com sucesso."}
    except Exception as e:
        return {"success": False, "message": str(e)}


def delete_file(file: str, folder: str = "", **_) -> dict:
    """Elimina um ficheiro (move para o lixo se send2trash estiver disponível)."""
    base = _resolve_folder(folder) if folder else os.path.expanduser("~")
    path = os.path.join(base, file) if folder else file
    if not os.path.exists(path):
        return {"success": False, "message": f"Ficheiro não encontrado: {path}"}
    try:
        if HAS_SEND2TRASH:
            send2trash.send2trash(path)
            return {"success": True, "message": f"'{path}' movido para o lixo."}
        else:
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
            return {"success": True, "message": f"'{path}' eliminado permanentemente."}
    except Exception as e:
        return {"success": False, "message": str(e)}


def copy_file(file: str, destination: str, folder: str = "", **_) -> dict:
    """Copia um ficheiro para outro local."""
    base = _resolve_folder(folder) if folder else os.path.expanduser("~")
    src  = os.path.join(base, file) if folder else file
    dst  = _resolve_folder(destination)
    if not os.path.exists(src):
        return {"success": False, "message": f"Ficheiro não encontrado: {src}"}
    try:
        if os.path.isdir(dst):
            dst = os.path.join(dst, os.path.basename(src))
        shutil.copy2(src, dst)
        return {"success": True, "message": f"'{src}' copiado para '{dst}'."}
    except Exception as e:
        return {"success": False, "message": str(e)}


# Mapa de ações disponíveis
ACTION_MAP = {
    "open_folder":   open_folder,
    "open_file":     open_file,
    "play_media":    play_media,
    "open_app":      open_app,
    "list_folder":   list_folder,
    "create_folder": create_folder,
    "delete_file":   delete_file,
    "copy_file":     copy_file,
}


def execute_action(action: str, parameters: dict) -> dict:
    """Executa uma ação RPA com os parâmetros dados."""
    fn = ACTION_MAP.get(action)
    if not fn:
        return {"success": False, "message": f"Ação desconhecida: {action}"}
    result = fn(**parameters)
    result["action"] = action
    return result
