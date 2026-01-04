#!/usr/bin/env python3
# aetos.py

import sys
import subprocess
import os
import json
from pathlib import Path

# 🔧 CONFIGURACIÓN POR DEFECTO
DEFAULT_INDEX_URL = "https://nexus.uclv.edu.cu/repository/pypi.org/"
CONFIG_DIR = Path.home() / ".aetos"
CONFIG_FILE = CONFIG_DIR / "config.json"


def get_config_dir() -> Path:
    """Obtiene el directorio de configuración y lo crea si no existe"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    return CONFIG_DIR


def load_config() -> dict:
    """Carga la configuración desde el archivo o retorna la config por defecto"""
    if not CONFIG_FILE.exists():
        return {"index_url": DEFAULT_INDEX_URL}

    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {"index_url": DEFAULT_INDEX_URL}


def save_config(config: dict) -> None:
    """Guarda la configuración en el archivo"""
    get_config_dir()
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)


def get_index_url() -> str:
    """Obtiene la URL del índice actual"""
    config = load_config()
    return config.get("index_url", DEFAULT_INDEX_URL)


def handle_config_command(args: list) -> None:
    """Maneja los comandos de configuración"""
    if not args or args[0] == "show":
        current_url = get_index_url()
        print(f"🦅 URL del índice actual: {current_url}")
        if current_url == DEFAULT_INDEX_URL:
            print("✅ Usando configuración por defecto")
        else:
            print(f"📝 Configuración personalizada guardada en: {CONFIG_FILE}")

    elif args[0] == "set":
        if len(args) < 2:
            print("❌ Uso: aetos config set <url>")
            print("Ej: aetos config set https://pypi.org/simple/")
            sys.exit(1)

        new_url = args[1]

        # Validar URL básica
        if not (new_url.startswith('http://') or new_url.startswith('https://')):
            print("❌ Error: La URL debe comenzar con http:// o https://")
            sys.exit(1)

        config = load_config()
        config["index_url"] = new_url
        save_config(config)
        print(f"✅ URL del índice actualizada a: {new_url}")
        print(f"📝 Configuración guardada en: {CONFIG_FILE}")

    elif args[0] == "reset":
        if CONFIG_FILE.exists():
            CONFIG_FILE.unlink()
            print(f"🗑️  Archivo de configuración eliminado: {CONFIG_FILE}")
        print(f"✅ Restablecida a la URL por defecto: {DEFAULT_INDEX_URL}")

    else:
        print(f"❌ Comando de configuración desconocido: {args[0]}")
        print("Uso: aetos config [show|set <url>|reset]")
        sys.exit(1)


def main():
    if len(sys.argv) < 2:
        print("❌ Uso: aetos <comando> [paquetes]")
        print("Ej: aetos install requests")
        print("\nComandos disponibles:")
        print("  aetos install <paquete>        Instalar un paquete")
        print("  aetos uninstall <paquete>      Desinstalar un paquete")
        print("  aetos list                     Listar paquetes instalados")
        print("  aetos show <paquete>           Mostrar información de un paquete")
        print("  aetos config show              Mostrar URL del índice actual")
        print("  aetos config set <url>         Cambiar URL del índice")
        print("  aetos config reset             Restablecer URL por defecto")
        sys.exit(1)

    # Comando de pip (ej: install, list, uninstall)
    command = sys.argv[1]

    # Manejar comandos de configuración
    if command == "config":
        handle_config_command(sys.argv[2:])
        return

    # Obtener URL del índice actual
    index_url = get_index_url()

    # Argumentos restantes
    args = sys.argv[2:]

    # Construir el comando de pip
    pip_cmd = [
        sys.executable, "-m", "pip", command,
        "--index-url", index_url,
        "--trusted-host", index_url.split("//")[-1].split("/")[0],  # Host sin https://
    ] + args

    print(f"🦅 Aetos: usando índice {index_url}")
    print(f"🚀 Ejecutando: {' '.join(pip_cmd)}")

    # Ejecutar el comando
    try:
        result = subprocess.run(pip_cmd, check=True)
        sys.exit(result.returncode)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al ejecutar pip: {e}")
        sys.exit(e.returncode)
    except FileNotFoundError:
        print("❌ No se encontró pip. Asegúrate de tener Python instalado correctamente.")
        sys.exit(1)


if __name__ == "__main__":
    main()