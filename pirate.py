#!/usr/bin/env python3
import sys
import os
import json
import urllib.request
import urllib.parse
import subprocess
import webbrowser

# Configura la URL directa a tu JSON en GitHub Pages
REPO_URL = "https://raw.githubusercontent.com/Y0U4R34P1R4T3/P1R4T3R3P0/main/juegos.json"
GITHUB_ISSUES_URL = f"https://github.com/Y0U4R34P1R4T3/P1R4T3R3P0/issues/new?title="

# Carpetas de datos locales
DATA_DIR = os.path.expanduser("~/.local/share/pirate")
INSTALL_DIR = os.path.join(DATA_DIR, "games")
LOCAL_CATALOG = os.path.join(DATA_DIR, "juegos.json")
INSTALLED_GAMES_FILE = os.path.join(DATA_DIR, "installed.json")

def asegurar_carpetas():
    os.makedirs(INSTALL_DIR, exist_ok=True)

def cargar_catalogo_local():
    """Carga el JSON descargado localmente."""
    if not os.path.exists(LOCAL_CATALOG):
        print("[!] No hay un catálogo local. Ejecutando 'pirate update' primero...")
        update_catalogo()
    
    try:
        with open(LOCAL_CATALOG, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        print("[X] Error al leer el catálogo local. Volvé a intentar con 'pirate update'.")
        sys.exit(1)

# --- COMANDOS ---

def update_catalogo():
    """[pirate update] Descarga la última versión del catálogo desde GitHub Pages."""
    asegurar_carpetas()
    print("[*] Leyendo listas de juegos desde el repositorio...")
    try:
        req = urllib.request.urlopen(REPO_URL)
        data = req.read().decode('utf-8')
        # Guardar en disco
        with open(LOCAL_CATALOG, 'w', encoding='utf-8') as f:
            f.write(data)
        print("[✓] Lista de juegos actualizada correctamente.")
    except Exception as e:
        print(f"[X] Error al conectar con el repositorio: {e}")

def search_juegos(query=""):
    """[pirate search] Busca un juego en el catálogo local."""
    catalogo = cargar_catalogo_local()
    print(f"\n--- Resultados de búsqueda para '{query}' ---")
    encontrados = 0
    for key, info in catalogo.items():
        if query.lower() in key.lower() or query.lower() in info['nombre'].lower():
            print(f" • {key} -> {info['nombre']} (v{info['version']})")
            encontrados += 1
    
    if encontrados == 0:
        print("No se encontraron juegos que coincidan.")
    print()

def install_juego(id_juego):
    """[pirate install] Descarga e instala un juego."""
    catalogo = cargar_catalogo_local()
    
    if id_juego not in catalogo:
        print(f"[!] El juego '{id_juego}' no existe en el catálogo.")
        print("Probá buscando con: pirate search <nombre>")
        return

    info = catalogo[id_juego]
    print(f"[*] Preparando la instalación de: {info['nombre']} (v{info['version']})")

    tar_path = os.path.join(INSTALL_DIR, f"{id_juego}.tar.gz")
    game_dir = os.path.join(INSTALL_DIR, id_juego)

    # Lista de fuentes (principal + mirrors)
    fuentes = [info['url']] + info.get('mirrors', [])
    descarga_exitosa = False

    for url in fuentes:
        print(f"[*] Descargando desde: {url}")
        res = os.system(f"wget -q --show-progress -O '{tar_path}' '{url}'")
        if res == 0:
            descarga_exitosa = True
            break
        print("[!] Enlace caído o no disponible, intentando con mirror de respaldo...")

    if not descarga_exitosa:
        print("[X] Error: No se pudo descargar el juego desde ninguna fuente.")
        return

    print(f"[*] Descomprimiendo archivos...")
    os.makedirs(game_dir, exist_ok=True)
    subprocess.run(["tar", "-xzf", tar_path, "-C", game_dir])

    if os.path.exists(tar_path):
        os.remove(tar_path)

    # Asignar permisos al ejecutable
    ejecutable_path = os.path.join(game_dir, info['ejecutable'])
    if os.path.exists(ejecutable_path):
        os.chmod(ejecutable_path, 0o755)

    # Registrar instalación localmente para el comando upgrade
    instalados = {}
    if os.path.exists(INSTALLED_GAMES_FILE):
        with open(INSTALLED_GAMES_FILE, 'r') as f:
            instalados = json.load(f)
    instalados[id_juego] = info['version']
    with open(INSTALLED_GAMES_FILE, 'w') as f:
        json.dump(instalados, f, indent=2)

    print(f"\n[✓] ¡{info['nombre']} listo para jugar!")

def upgrade_juegos():
    """[pirate upgrade] Revisa actualizaciones de juegos instalados."""
    if not os.path.exists(INSTALLED_GAMES_FILE):
        print("[*] No hay juegos instalados actualmente.")
        return

    with open(INSTALLED_GAMES_FILE, 'r') as f:
        instalados = json.load(f)

    catalogo = cargar_catalogo_local()
    actualizaciones = 0

    for id_juego, v_local in instalados.items():
        if id_juego in catalogo:
            v_remota = catalogo[id_juego]['version']
            if v_remota != v_local:
                print(f"[*] Nueva versión encontrada para {id_juego}: {v_local} -> {v_remota}")
                install_juego(id_juego)
                actualizaciones += 1

    if actualizaciones == 0:
        print("[✓] Todos tus juegos están en la última versión disponible.")

def request_juego(nombre_juego):
    """[pirate request] Abre la página de GitHub para pedir un juego."""
    print(f"[*] Abriendo navegador para solicitar: '{nombre_juego}'...")
    query_string = urllib.parse.quote(f"Request: {nombre_juego}")
    url = f"{GITHUB_ISSUES_URL}{query_string}"
    webbrowser.open(url)

# --- PANEL PRINCIPAL ---

def main():
    if len(sys.argv) < 2:
        print("Uso de Pirate CLI:")
        print("  pirate update               -> Actualiza el catálogo de juegos")
        print("  pirate search <nombre>      -> Busca juegos en el repositorio")
        print("  pirate install <juego>     -> Descarga e instala un juego")
        print("  pirate upgrade              -> Actualiza los juegos instalados")
        print("  pirate request \"<juego>\"   -> Solicita que agreguen un juego")
        sys.exit(1)

    cmd = sys.argv[1].lower()

    if cmd == "update":
        update_catalogo()
    elif cmd == "search":
        query = sys.argv[2] if len(sys.argv) >= 3 else ""
        search_juegos(query)
    elif cmd == "install":
        if len(sys.argv) < 3:
            print("[!] Especificá qué juego querés instalar. Ej: pirate install celeste")
        else:
            install_juego(sys.argv[2])
    elif cmd == "upgrade":
        upgrade_juegos()
    elif cmd == "request":
        if len(sys.argv) < 3:
            print('[!] Especificá el nombre del juego entre comillas. Ej: pirate request "Hotline Miami"')
        else:
            request_juego(sys.argv[2])
    else:
        print("[!] Comando no reconocido. Usá 'pirate' sin parámetros para ver la ayuda.")

if __name__ == "__main__":
    main()
