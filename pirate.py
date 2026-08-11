#!/usr/bin/env python3
import sys
import time
import os
import json
import urllib.request
import urllib.parse
import subprocess
import webbrowser
import re
import shutil

# Configura las URLs del repositorio
SCRIPT_URL = "https://raw.githubusercontent.com/Y0U4R34P1R4T3/P1R4T3R3P0/main/pirate.py"
REPO_URL = "https://raw.githubusercontent.com/Y0U4R34P1R4T3/P1R4T3R3P0/main/juegos.json"
GITHUB_ISSUES_URL = "https://github.com/Y0U4R34P1R4T3/P1R4T3R3P0/issues/new?title="

# Si tus descargas usan una contraseña global por defecto, podés ponerla acá (ej: "1234"):
PASSWORD_COMPRIMIDO = "elenemigos.com"

# Canal de ntfy.sh para recibir notificaciones en tu celular
NTFY_CHANNEL = "LinuxRepoPirate"

# Carpetas de contenido visibles en tu carpeta personal (~/PIRATE)
PIRATE_DIR = os.path.expanduser("~/PIRATE")
GAMES_DIR = os.path.join(PIRATE_DIR, "Games")
MOVIES_DIR = os.path.join(PIRATE_DIR, "Movies")

# Archivos de datos locales y configuración
DATA_DIR = os.path.expanduser("~/.local/share/pirate")
LOCAL_CATALOG = os.path.join(DATA_DIR, "juegos.json")
INSTALLED_GAMES_FILE = os.path.join(DATA_DIR, "installed.json")
WELCOME_FLAG_FILE = os.path.join(DATA_DIR, ".welcome_done")

def instalar_aria2_si_falta():
    """Instala automáticamente aria2c si no se encuentra en el sistema."""
    if not shutil.which("aria2c"):
        print("[*] 'aria2' no está instalado. Instalándolo automáticamente para optimizar descargas...")
        try:
            if shutil.which("apt"):
                subprocess.run(["sudo", "apt", "update", "-y"], check=False)
                subprocess.run(["sudo", "apt", "install", "-y", "aria2"], check=False)
            elif shutil.which("pacman"):
                subprocess.run(["sudo", "pacman", "-S", "--noconfirm", "aria2"], check=False)
            elif shutil.which("dnf"):
                subprocess.run(["sudo", "dnf", "install", "-y", "aria2"], check=False)
        except Exception as e:
            print(f"[!] No se pudo instalar 'aria2' automáticamente: {e}")
            print("[!] Se usará 'wget' como motor de respaldo.")

def instalar_descompresores_si_falta():
    """Instala automáticamente unrar y p7zip si no se encuentran en el sistema."""
    falta_unrar = not shutil.which("unrar")
    falta_7z = not (shutil.which("7z") or shutil.which("7za"))

    if falta_unrar or falta_7z:
        print("[*] Instalando herramientas de descompresión (unrar / p7zip) para soporte RAR5/Encriptación...")
        try:
            if shutil.which("apt"):
                subprocess.run(["sudo", "apt", "update", "-y"], check=False)
                subprocess.run(["sudo", "apt", "install", "-y", "unrar", "p7zip-full"], check=False)
            elif shutil.which("pacman"):
                subprocess.run(["sudo", "pacman", "-S", "--noconfirm", "unrar", "p7zip"], check=False)
            elif shutil.which("dnf"):
                subprocess.run(["sudo", "dnf", "install", "-y", "unrar", "p7zip", "p7zip-plugins"], check=False)
        except Exception as e:
            print(f"[!] No se pudieron instalar los descompresores automáticamente: {e}")

def descomprimir_archivo(archive_path, game_dir, extension):
    """Intenta descomprimir usando unrar, 7z o bsdtar soportando encriptación y contraseñas."""
    instalar_descompresores_si_falta()

    if extension == ".rar":
        # Intento 1: unrar (Mejor soporte para contraseñas y RAR5)
        if shutil.which("unrar"):
            cmd = ["unrar", "x", "-o+"]
            if PASSWORD_COMPRIMIDO:
                cmd.append(f"-p{PASSWORD_COMPRIMIDO}")
            else:
                cmd.append("-p-")
            cmd.extend([archive_path, game_dir + "/"])
            res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if res.returncode == 0:
                return True

        # Intento 2: 7z / 7za
        bin_7z = shutil.which("7z") or shutil.which("7za")
        if bin_7z:
            cmd = [bin_7z, "x", f"-o{game_dir}", "-y"]
            if PASSWORD_COMPRIMIDO:
                cmd.append(f"-p{PASSWORD_COMPRIMIDO}")
            cmd.append(archive_path)
            res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if res.returncode == 0:
                return True

        # Intento 3: bsdtar como respaldo
        res = subprocess.run(["bsdtar", "-xf", archive_path, "-C", game_dir])
        return res.returncode == 0

    elif extension == ".zip":
        bin_7z = shutil.which("7z") or shutil.which("7za")
        if bin_7z:
            cmd = [bin_7z, "x", f"-o{game_dir}", "-y"]
            if PASSWORD_COMPRIMIDO:
                cmd.append(f"-p{PASSWORD_COMPRIMIDO}")
            cmd.append(archive_path)
            res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if res.returncode == 0:
                return True

        cmd = ["unzip", "-q", "-o"]
        if PASSWORD_COMPRIMIDO:
            cmd.extend(["-P", PASSWORD_COMPRIMIDO])
        cmd.extend([archive_path, "-d", game_dir])
        res = subprocess.run(cmd)
        return res.returncode == 0

    else:
        res = subprocess.run(["tar", "-xzf", archive_path, "-C", game_dir])
        return res.returncode == 0

def asegurar_carpetas():
    """Crea la estructura de carpetas y muestra el mensaje de bienvenida en la primera instalación."""
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(GAMES_DIR, exist_ok=True)
    os.makedirs(MOVIES_DIR, exist_ok=True)

    if not os.path.exists(WELCOME_FLAG_FILE):
        print("☠ Bienvenido al barco, marinero! He creado este repositorio para que puedas descargar juegos, películas y series! Puedes utilizar el comando 'pirate' para ver el listado de comandos! Suerte recorriendo estos mares, marinero...\n")
        with open(WELCOME_FLAG_FILE, 'w', encoding='utf-8') as f:
            f.write("1")

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

def notificar_error_instalacion(id_item, nombre_item, url_caida, tipo_enlace="Principal", motivo_error="Error desconocido"):
    """Envía una notificación push detallada al celular del owner vía ntfy.sh con la razón del error."""
    if not NTFY_CHANNEL:
        return

    try:
        titulo = f"⚠️ Fallo en reposición: {nombre_item}"
        mensaje = (
            f"📌 Elemento: {nombre_item} (ID: '{id_item}')\n"
            f"🔗 Enlace/Opción: {tipo_enlace}\n"
            f"🌐 URL: {url_caida}\n"
            f"❌ Motivo en terminal: {motivo_error}\n\n"
            f"💡 Sugerencia: Revisá los archivos en GitHub o el mirror seleccionado."
        )

        req = urllib.request.Request(
            f"https://ntfy.sh/{NTFY_CHANNEL}",
            data=mensaje.encode('utf-8'),
            headers={
                "Title": titulo.encode('utf-8').decode('latin-1'),
                "Priority": "high",
                "Tags": "warning,game,terminal_error",
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"
            }
        )
        urllib.request.urlopen(req, timeout=5)
        print("    [✓] Alerta de fallo enviada a tu celular vía ntfy.")
    except Exception as e:
        print(f"    [!] Ocurrió un inconveniente al enviar la alerta a ntfy: {e}")

def resolver_url_descarga(url):
    """Detecta enlaces de MediaFire y extrae la URL de descarga directa de forma robusta."""
    if "mediafire.com" in url:
        print("    [*] Procesando enlace de MediaFire...")
        try:
            req = urllib.request.Request(
                url, 
                headers={
                    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0',
                    'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8'
                }
            )
            html = urllib.request.urlopen(req, timeout=10).read().decode('utf-8', errors='ignore')
            
            # Intento 1: Buscar botón directo de descarga
            match = re.search(r'href="(https?://download[^"]+)"', html)
            if match:
                return match.group(1)
            
            # Intento 2: Atributo aria-label alternativo
            match_alt = re.search(r'aria-label="Download file"\s+href="([^"]+)"', html)
            if match_alt:
                return match_alt.group(1)

        except Exception as e:
            print(f"    [!] No se pudo resolver la URL de MediaFire: {e}")
    return url

def verificar_enlace_activo(url):
    """Verifica mediante una petición HEAD si el enlace responde antes de descargar."""
    if url.startswith("magnet:"):
        return True

    try:
        req = urllib.request.Request(
            url, 
            method='HEAD',
            headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0'}
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            return response.status in [200, 301, 302]
    except Exception:
        return False

def ejecutar_descarga(url_real, destino_archivo):
    """Descarga el archivo usando aria2c (instala si no está) o cae en wget."""
    instalar_aria2_si_falta()

    if shutil.which("aria2c"):
        print("    [*] Usando motor de descarga acelerado (aria2c)...")
        cmd = f"aria2c -x 8 -s 8 --summary-interval=1 -o '{os.path.basename(destino_archivo)}' -d '{os.path.dirname(destino_archivo)}' '{url_real}'"
        res = os.system(cmd)
        return res == 0
    else:
        print("    [*] Usando motor de descarga estándar (wget)...")
        res = os.system(f"wget -q --show-progress -O '{destino_archivo}' '{url_real}'")
        return res == 0

def manejar_torrent_cli(url_origen, directorio_destino, nombre_item):
    """Maneja la descarga de magnets o torrents en terminal instalando aria2c si hace falta."""
    instalar_aria2_si_falta()

    if shutil.which("aria2c"):
        print(f"[*] Iniciando cliente Torrent en terminal con aria2c para '{nombre_item}'...")
        cmd = f"aria2c --dir='{directorio_destino}' --seed-time=0 --summary-interval=1 '{url_origen}'"
        res = os.system(cmd)
        return res == 0
    else:
        print("[!] Intentando abrir en el cliente predeterminado del sistema...")
        try:
            subprocess.run(["xdg-open", url_origen])
            return True
        except Exception as e:
            print(f"[X] Error al abrir el torrent: {e}")
            return False

# --- COMANDOS ---

def listar_catalogo_generico(archivo_json, tipo_filtro=None, titulo_categoria="Contenido"):
    if not os.path.exists(archivo_json):
        print(f"[!] No se encontró el catálogo. Ejecutá 'pirate update' primero.")
        return

    try:
        with open(archivo_json, 'r', encoding='utf-8') as f:
            catalogo = json.load(f)
    except Exception as e:
        print(f"[X] Error al leer el catálogo de {titulo_categoria}: {e}")
        return

    print(f"\n=== CATÁLOGO DE {titulo_categoria.upper()} DISPONIBLES ===")
    if not catalogo:
        print(" No hay elementos en el catálogo.")
        return

    encontrados = 0
    for key, info in catalogo.items():
        tipo_item = info.get('tipo', 'juego').lower()
        
        if tipo_filtro is None or tipo_item == tipo_filtro.lower():
            nombre = info.get('nombre', key)
            version = info.get('version', '')
            version_str = f" (v{version})" if version else ""
            tag_tipo = f" [{tipo_item.capitalize()}]" if tipo_filtro is None else ""
            print(f" • [{key}]{tag_tipo} -> {nombre}{version_str}")
            encontrados += 1

    if encontrados == 0:
        print(f" No hay elementos en la categoría '{titulo_categoria}'.")
    print()

def list_juegos():
    listar_catalogo_generico(LOCAL_CATALOG, tipo_filtro="juego", titulo_categoria="Juegos")

def list_movies():
    listar_catalogo_generico(LOCAL_CATALOG, tipo_filtro="pelicula", titulo_categoria="Películas")

def list_series():
    listar_catalogo_generico(LOCAL_CATALOG, tipo_filtro="serie", titulo_categoria="Series")

def list_all():
    print("\n==========================================")
    print("         CATÁLOGO GENERAL DE PIRATE        ")
    print("==========================================")
    listar_catalogo_generico(LOCAL_CATALOG, tipo_filtro=None, titulo_categoria="Todo el Contenido")

def update_catalogo():
    asegurar_carpetas()
    print("☠ Surcando los mares del repositorio...")
    
    cache_buster = f"?t={int(time.time())}"

    try:
        req = urllib.request.urlopen(REPO_URL + cache_buster)
        data = req.read().decode('utf-8')
        json.loads(data)
        
        with open(LOCAL_CATALOG, 'w', encoding='utf-8') as f:
            f.write(data)
        print("☠ Se han actualizado los mapas del tesoro!")

        print("☠ Verificando que el barco esté en buen estado...")
        script_url = f"{SCRIPT_URL}{cache_buster}"
        req_script = urllib.request.urlopen(script_url)
        script_data = req_script.read().decode('utf-8')

        binary_path = os.path.expanduser("~/.local/bin/pirate")
        if os.path.exists(os.path.dirname(binary_path)):
            with open(binary_path, 'w', encoding='utf-8') as f:
                f.write(script_data)
            os.chmod(binary_path, 0o755)
            print("☠ ¡El barco está en su última versión, como nuevo!")

    except json.JSONDecodeError as e:
        print(f"[X] El juegos.json en GitHub tiene un error de formato y no se guardó: {e}")
    except Exception as e:
        print(f"[X] Error al actualizar: {e}")

def search_juegos(query=""):
    catalogo = cargar_catalogo_local()
    print(f"\n--- Resultados de búsqueda para '{query}' ---")
    encontrados = 0
    for key, info in catalogo.items():
        nombre = info.get('nombre', key)
        version = info.get('version', 'N/A')
        tipo = info.get('tipo', 'juego').capitalize()
        if query.lower() in key.lower() or query.lower() in nombre.lower():
            print(f" • [{tipo}] {key} -> {nombre} (v{version})")
            encontrados += 1
    
    if encontrados == 0:
        print("No se encontraron elementos que coincidan.")
    print()

def install_juego(id_juego):
    asegurar_carpetas()
    catalogo = cargar_catalogo_local()
    
    if id_juego not in catalogo:
        print(f"[!] El elemento '{id_juego}' no existe en el catálogo.")
        print("Probá buscando con: pirate search <nombre>")
        return

    info = catalogo[id_juego]
    nombre_item = info.get('nombre', id_juego)
    tipo_item = info.get('tipo', 'juego').lower()

    destino_base = MOVIES_DIR if tipo_item in ['pelicula', 'serie'] else GAMES_DIR
    game_dir = os.path.join(destino_base, id_juego)

    opciones = [("Principal", info['url'])]
    for idx, mirror_url in enumerate(info.get('mirrors', []), start=1):
        opciones.append((f"Mirror #{idx}", mirror_url))

    print(f"\n==========================================")
    print(f"   Instalación de: {nombre_item} (v{info.get('version', '1.0')})")
    print(f"==========================================")
    print("Seleccioná la fuente de descarga que preferís:\n")

    for idx, (etiqueta_fuente, url) in enumerate(opciones, start=1):
        tipo_host = "Directa"
        if "mediafire.com" in url:
            tipo_host = "MediaFire"
        elif "buzzheavier.com" in url:
            tipo_host = "Buzzheavier"
        elif "gofile.io" in url:
            tipo_host = "GoFile"
        elif "megadb.net" in url:
            tipo_host = "MegaDB"
        elif url.startswith("magnet:"):
            tipo_host = "Torrent (Magnet)"
        elif url.endswith(".torrent"):
            tipo_host = "Torrent (Archivo)"

        print(f"  [{idx}] {tipo_host} [{etiqueta_fuente}] -> {url[:60]}...")

    try:
        eleccion = int(input("\nIngresá el número de opción: ")) - 1
        if eleccion < 0 or eleccion >= len(opciones):
            print("[!] Opción no válida. Cancelando instalación.")
            return
    except ValueError:
        print("[!] Entrada no válida. Debe ser un número.")
        return

    etiqueta_elegida, url_elegida = opciones[eleccion]

    if url_elegida.startswith("magnet:") or url_elegida.endswith(".torrent"):
        os.makedirs(game_dir, exist_ok=True)
        exito = manejar_torrent_cli(url_elegida, game_dir, nombre_item)
        if not exito:
            notificar_error_instalacion(
                id_juego, nombre_item, url_elegida, etiqueta_elegida,
                motivo_error="Falló la descarga del torrent/magnet (sin semillas o interrupción)."
            )
        return

    url_real = resolver_url_descarga(url_elegida)

    if not verificar_enlace_activo(url_real):
        print(f"\n[X] El enlace seleccionado no responde o está caído.")
        notificar_error_instalacion(
            id_juego, nombre_item, url_elegida, etiqueta_elegida,
            motivo_error="Servidor caído / Error HTTP (404, 500 o Timeout)."
        )
        print("Probá ejecutando el comando de nuevo y seleccionando otro mirror.")
        return

    extension = ".tar.gz"
    if url_real.endswith(".rar"):
        extension = ".rar"
    elif url_real.endswith(".zip"):
        extension = ".zip"

    archive_path = os.path.join(destino_base, f"{id_juego}{extension}")

    print(f"\n[*] Descargando desde fuente {etiqueta_elegida}...")
    descarga_exitosa = ejecutar_descarga(url_real, archive_path)

    # Validar si el archivo es HTML o si es corrupto/vacío (<10KB)
    es_html = False
    if os.path.exists(archive_path):
        try:
            with open(archive_path, 'rb') as f:
                inicio = f.read(100)
                if b'<!doctype html>' in inicio.lower() or b'<html' in inicio.lower():
                    es_html = True
        except Exception:
            pass

    if not descarga_exitosa or not os.path.exists(archive_path) or os.path.getsize(archive_path) < 10240 or es_html:
        print(f"\n[X] Falló la descarga desde la opción seleccionada (Archivo bloqueado o corrupto por MediaFire/servidor).")
        motivo = "MediaFire devolvió una página HTML de captcha/bloqueo." if es_html else "Descarga incompleta o archivo corrupto (<10KB)."
        notificar_error_instalacion(
            id_juego, nombre_item, url_elegida, etiqueta_elegida,
            motivo_error=motivo
        )
        if os.path.exists(archive_path):
            os.remove(archive_path)
        return

    print(f"[*] Descomprimiendo archivos en {game_dir}...")
    os.makedirs(game_dir, exist_ok=True)

    descompresion_ok = descomprimir_archivo(archive_path, game_dir, extension)

    if os.path.exists(archive_path):
        os.remove(archive_path)

    if not descompresion_ok:
        print("\n[X] Ocurrió un error al descomprimir el archivo (Encriptación/Contraseña o formato RAR5 no soportado).")
        notificar_error_instalacion(
            id_juego, nombre_item, url_elegida, etiqueta_elegida,
            motivo_error=f"Error en extracción ({extension}) - Encriptación / Contraseña incorrecta o fallo en descompresor."
        )
        return

    ejecutable_relativo = info.get('ejecutable', '')
    if ejecutable_relativo:
        ejecutable_path = os.path.join(game_dir, ejecutable_relativo)
        if os.path.exists(ejecutable_path):
            os.chmod(ejecutable_path, 0o755)
        else:
            notificar_error_instalacion(
                id_juego, nombre_item, url_elegida, etiqueta_elegida,
                motivo_error=f"Falta ejecutable: No se halló '{ejecutable_relativo}' tras descompresión."
            )

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

    print(f"\n[✓] ¡{nombre_item} listo para disfrutar!")

def upgrade_juegos():
    if not os.path.exists(INSTALLED_GAMES_FILE):
        print("[*] No hay contenido instalado actualmente.")
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
        print("[✓] Todo tu contenido está en la última versión disponible.")

def request_juego(nombre_juego):
    print(f"[*] Abriendo navegador para solicitar: '{nombre_juego}'...")
    query_string = urllib.parse.quote(f"Request: {nombre_juego}")
    url = f"{GITHUB_ISSUES_URL}{query_string}"
    webbrowser.open(url)

# --- PANEL PRINCIPAL ---

def main():
    asegurar_carpetas()
    
    if len(sys.argv) < 2:
        print("Uso de Pirate CLI:")
        print("  pirate update               -> Actualiza el catálogo y el script")
        print("  pirate search <nombre>      -> Busca elementos en el catálogo")
        print("  pirate listgames            -> Muestra solo los juegos")
        print("  pirate listmovies           -> Muestra solo las películas")
        print("  pirate listseries           -> Muestra solo las series")
        print("  pirate listall              -> Muestra todo el catálogo completo")
        print("  pirate install <juego>      -> Descarga e instala un elemento")
        print("  pirate upgrade              -> Actualiza los juegos instalados")
        print("  pirate request \"<juego>\"   -> Solicita que agreguen contenido")
        print("\n Este repositorio agradece su uso del repositorio")
        sys.exit(1)

    cmd = sys.argv[1].lower()

    if cmd == "update":
        update_catalogo()
    elif cmd == "search":
        query = sys.argv[2] if len(sys.argv) >= 3 else ""
        search_juegos(query)
    elif cmd == "listgames":
        list_juegos()
    elif cmd == "listmovies":
        list_movies()
    elif cmd == "listseries":
        list_series()
    elif cmd == "listall":
        list_all()
    elif cmd == "install":
        if len(sys.argv) < 3:
            print("[!] Especificá qué elemento querés instalar. Ej: pirate install celeste")
        else:
            install_juego(sys.argv[2])
    elif cmd == "upgrade":
        upgrade_juegos()
    elif cmd == "request":
        if len(sys.argv) < 3:
            print('[!] Especificá el nombre entre comillas. Ej: pirate request "Hotline Miami"')
        else:
            request_juego(sys.argv[2])
    else:
        print("[!] Comando no reconocido. Usá 'pirate' sin parámetros para ver la ayuda.")

if __name__ == "__main__":
    main()
