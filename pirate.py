#!/usr/bin/env python3
import sys
import time
import os
import json
import urllib.request
import urllib.parse
import subprocess
import webbrowser

# Configura las URLs del repositorio
SCRIPT_URL = "https://raw.githubusercontent.com/Y0U4R34P1R4T3/P1R4T3R3P0/main/pirate.py"
REPO_URL = "https://raw.githubusercontent.com/Y0U4R34P1R4T3/P1R4T3R3P0/main/juegos.json"
GITHUB_ISSUES_URL = "https://github.com/Y0U4R34P1R4T3/P1R4T3R3P0/issues/new?title="

# Carpetas de contenido visibles en tu carpeta personal (~/PIRATE)
PIRATE_DIR = os.path.expanduser("~/PIRATE")
GAMES_DIR = os.path.join(PIRATE_DIR, "Games")
MOVIES_DIR = os.path.join(PIRATE_DIR, "Movies")

# Archivos de datos locales y configuración
DATA_DIR = os.path.expanduser("~/.local/share/pirate")
LOCAL_CATALOG = os.path.join(DATA_DIR, "juegos.json")
INSTALLED_GAMES_FILE = os.path.join(DATA_DIR, "installed.json")

def asegurar_carpetas():
    """Crea la estructura de carpetas si no existen."""
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(GAMES_DIR, exist_ok=True)
    os.makedirs(MOVIES_DIR, exist_ok=True)

def cargar_catalogo_local():
    """Carga el JSON descargado localmente e informa errores detallados de sintaxis."""
    if not os.path.exists(LOCAL_CATALOG):
        print("[!] No hay un catálogo local. Ejecutando 'pirate update' primero...")
        update_catalogo()
    
    try:
        with open(LOCAL_CATALOG, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"[X] Error de sintaxis en el catálogo JSON (Línea {e.lineno}, Columna {e.colno}): {e.msg}")
        print("[!] Corrige el archivo en tu repositorio de GitHub y ejecuta 'pirate update'.")
        sys.exit(1)
    except Exception as e:
        print(f"[X] Error insospechado al leer el catálogo: {e}")
        sys.exit(1)

# --- COMANDOS ---

def listar_catalogo_generico(archivo_json, tipo_contenido):
    """Función genérica para listar cualquier categoría (Juegos, Películas, Series)."""
    if not os.path.exists(archivo_json):
        print(f"[!] No se encontró el catálogo de {tipo_contenido}. Ejecutá 'pirate update' primero.")
        return

    try:
        with open(archivo_json, 'r', encoding='utf-8') as f:
            catalogo = json.load(f)
    except Exception as e:
        print(f"[X] Error al leer el catálogo de {tipo_contenido}: {e}")
        return

    print(f"\n=== CATÁLOGO DE {tipo_contenido.upper()} DISPONIBLES ===")
    if not catalogo:
        print(" No hay elementos en el catálogo.")
        return

    for key, info in catalogo.items():
        nombre = info.get('nombre', key)
        version = info.get('version', '')
        version_str = f" (v{version})" if version else ""
        print(f" • [{key}] -> {nombre}{version_str}")
    print()

def list_juegos():
    """[pirate listgames] Muestra el catálogo completo de juegos."""
    listar_catalogo_generico(LOCAL_CATALOG, "Juegos")

def list_all():
    """[pirate listall] Muestra todo el catálogo disponible en el sistema."""
    print("\n==========================================")
    print("         CATÁLOGO GENERAL DE PIRATE        ")
    print("==========================================")
    
    listar_catalogo_generico(LOCAL_CATALOG, "Juegos")

def update_catalogo():
    """[pirate update] Descarga la última versión del catálogo y del propio script."""
    asegurar_carpetas()
    print("[*] Leyendo listas de juegos desde el repositorio...")
    
    cache_buster = f"?t={int(time.time())}"

    try:
        # 1. Actualizar catálogo de juegos
        req = urllib.request.urlopen(REPO_URL + cache_buster)
        data = req.read().decode('utf-8')
        
        # Validar que sea un JSON válido antes de guardarlo localmente
        json.loads(data)
        
        with open(LOCAL_CATALOG, 'w', encoding='utf-8') as f:
            f.write(data)
        print("[✓] Catálogo de juegos actualizado correctamente.")

        # 2. Auto-actualizar pirate.py
        print("[*] Verificando actualizaciones del script...")
        script_url = f"{SCRIPT_URL}{cache_buster}"
        req_script = urllib.request.urlopen(script_url)
        script_data = req_script.read().decode('utf-8')

        binary_path = os.path.expanduser("~/.local/bin/pirate")
        if os.path.exists(os.path.dirname(binary_path)):
            with open(binary_path, 'w', encoding='utf-8') as f:
                f.write(script_data)
            os.chmod(binary_path, 0o755)
            print("[✓] Script pirate.py actualizado a la última versión de GitHub.")

    except json.JSONDecodeError as e:
        print(f"[X] El juegos.json en GitHub tiene un error de formato y no se guardó: {e}")
    except Exception as e:
        print(f"[X] Error al actualizar: {e}")

def search_juegos(query=""):
    """[pirate search] Busca un juego en el catálogo local."""
    catalogo = cargar_catalogo_local()
    print(f"\n--- Resultados de búsqueda para '{query}' ---")
    encontrados = 0
    for key, info in catalogo.items():
        nombre = info.get('nombre', key)
        version = info.get('version', 'N/A')
        if query.lower() in key.lower() or query.lower() in nombre.lower():
            print(f" • {key} -> {nombre} (v{version})")
            encontrados += 1
    
    if encontrados == 0:
        print("No se encontraron juegos que coincidan.")
    print()

def install_juego(id_juego):
    """[pirate install] Descarga e instala un juego manejando múltiples formatos de compresión."""
    asegurar_carpetas()
    catalogo = cargar_catalogo_local()
    
    if id_juego not in catalogo:
        print(f"[!] El juego '{id_juego}' no existe en el catálogo.")
        print("Probá buscando con: pirate search <nombre>")
        return

    info = catalogo[id_juego]
    print(f"[*] Preparando la instalación de: {info.get('nombre', id_juego)} (v{info.get('version', '')})")

    fuentes = [info['url']] + info.get('mirrors', [])
    descarga_exitosa = False
    
    # Determinar extensión del archivo según la URL
    url_principal = info['url']
    extension = ".tar.gz"
    if url_principal.endswith(".rar"):
        extension = ".rar"
    elif url_principal.endswith(".zip"):
        extension = ".zip"

    archive_path = os.path.join(GAMES_DIR, f"{id_juego}{extension}")
    game_dir = os.path.join(GAMES_DIR, id_juego)

    for url in fuentes:
        print(f"[*] Descargando desde: {url}")
        res = os.system(f"wget -q --show-progress -O '{archive_path}' '{url}'")
        if res == 0:
            descarga_exitosa = True
            break
        print("[!] Enlace caído o no disponible, intentando con mirror de respaldo...")

    if not descarga_exitosa:
        print("[X] Error: No se pudo descargar el juego desde ninguna fuente.")
        return

    print(f"[*] Descomprimiendo archivos en {game_dir}...")
    os.makedirs(game_dir, exist_ok=True)

    # Extraer según el formato de compresión
    if extension == ".rar":
        # bsdtar viene por defecto en Arch Linux y soporta RAR/RAR5 perfectamente
        res_extraer = subprocess.run(["bsdtar", "-xf", archive_path, "-C", game_dir])
    elif extension == ".zip":
        res_extraer = subprocess.run(["unzip", "-q", archive_path, "-d", game_dir])
    else:
        res_extraer = subprocess.run(["tar", "-xzf", archive_path, "-C", game_dir])

    if res_extraer.returncode != 0:
        print("[X] Ocurrió un error al descomprimir el archivo del juego.")

    if os.path.exists(archive_path):
        os.remove(archive_path)

    # Asignar permisos al ejecutable
    ejecutable_relativo = info.get('ejecutable', '')
    if ejecutable_relativo:
        ejecutable_path = os.path.join(game_dir, ejecutable_relativo)
        if os.path.exists(ejecutable_path):
            os.chmod(ejecutable_path, 0o755)

    # Registrar instalación localmente
    instalados = {}
    if os.path.exists(INSTALLED_GAMES_FILE):
        try:
            with open(INSTALLED_GAMES_FILE, 'r') as f:
                instalados = json.load(f)
        except Exception:
            instalados = {}
            
    instalados[id_juego] = info.get('version', '1.0')
    with open(INSTALLED_GAMES_FILE, 'w') as f:
        json.dump(instalados, f, indent=2)

    print(f"\n[✓] ¡{info.get('nombre', id_juego)} listo para jugar!")

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
            v_remota = catalogo[id_juego].get('version', '')
            if v_remota and v_remota != v_local:
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
        print("  pirate update               -> Actualiza el catálogo y el script")
        print("  pirate search <nombre>      -> Busca elementos en el catálogo")
        print("  pirate listgames            -> Muestra solo los juegos")
        print("  pirate listall              -> Muestra todo el catálogo completo")
        print("  pirate install <juego>      -> Descarga e instala un juego")
        print("  pirate upgrade              -> Actualiza los juegos instalados")
        print("  pirate request \"<juego>\"   -> Solicita que agreguen un juego")
        sys.exit(1)

    cmd = sys.argv[1].lower()

    if cmd == "update":
        update_catalogo()
    elif cmd == "search":
        query = sys.argv[2] if len(sys.argv) >= 3 else ""
        search_juegos(query)
    elif cmd == "listgames":
        list_juegos()
    elif cmd == "listall":
        list_all()
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
