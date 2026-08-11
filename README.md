# :skull: :crossed_swords: :anchor: P1R4T3R3P0 :anchor: :crossed_swords: :skull:

> **El gestor CLI de descargas para Linux — Juegos :video_game:, Películas :clapper: y Series :tv:**

¡Bienvenido a bordo, marinero! :ocean: **P1R4T3R3P0** es un gestor interactivo para la terminal de Linux diseñado para buscar :mag:, descargar :inbox_tray:, descomprimir :package: e instalar :rocket: contenido multimedia de forma totalmente automática.

---

### :zap: :inbox_tray: Instalación Rápida

Ejecutá cualquiera de estos dos comandos en tu terminal para abordar el barco :ship::

<div align="left">
<pre style="background-color: #0d1117; color: #2ea043; padding: 18px; border-radius: 12px; border: 1px solid #30363d; font-family: 'Courier New', Courier, monospace;">
<span style="color: #8b949e;"># :rocket: Opción 1: Con cURL (Recomendado)</span>
<span style="color: #00ff66;">curl -sSL https://raw.githubusercontent.com/Y0U4R34P1R4T3/P1R4T3R3P0/main/install.sh | sh</span>

<span style="color: #8b949e;"># :package: Opción 2: Con Wget</span>
<span style="color: #00ff66;">wget -qO- https://raw.githubusercontent.com/Y0U4R34P1R4T3/P1R4T3R3P0/main/install.sh | sh</span>
</pre>
</div>

> :warning: **¡Atención Navegante!** :map: El repositorio cambia constantemente. Acordate de ejecutar siempre `pirate update` :counterclockwise: antes de descargar algo para refrescar los mapas y asegurar que usás las últimas versiones disponibles.

---

### :tools: :computer: :scroll: Uso y Comandos

Una vez instalado, ejecutá el comando `pirate` :gear: directamente en tu terminal:

| Comando | Icono | Descripción |
| :--- | :---: | :--- |
| `pirate update` | :counterclockwise: | Actualiza el catálogo local y el script a la última versión :rocket: |
| `pirate search <nombre>` | :mag: | Busca juegos, películas o series por palabra clave :key: |
| `pirate listall` | :scroll: | Muestra el catálogo completo sin filtros :crown: |
| `pirate listgames` | :video_game: | Muestra únicamente el catálogo de juegos :dart: |
| `pirate listmovies` | :clapper: | Muestra únicamente la lista de películas :movie_camera: |
| `pirate listseries` | :tv: | Muestra únicamente la lista de series :film_strip: |
| `pirate install <id>` | :inbox_tray: | Descarga, descomprime e instala un elemento :zap: |
| `pirate upgrade` | :rocket: | Actualiza tus juegos instalados a la versión más reciente :gem: |
| `pirate request "<nombre>"` | :pencil: | Abre una solicitud en GitHub para pedir contenido :envelope: |

---

### :sparkles: :crossed_swords: :fire: Características Principales

* :rocket: **Descargas Aceleradas:** Uso automático de `aria2c` :zap: (con multihilos) o `wget` :package: como motor de respaldo.
* :magnet: **Soporte Multi-fuente:** Descargas directas, MediaFire :package:, Buzzheavier :zap:, GoFile :open_file_folder: y Torrents / Magnets :magnet:.
* :bell: **Sistema de Alerta Automatizado:** Notificaciones instantáneas push :iphone: en caso de detectar enlaces o descargas caídas.
* :file_folder: **Estructura Organizada:** Todo se almacena automáticamente en tu carpeta personal :house: (`~/PIRATE/Games` :video_game: y `~/PIRATE/Movies` :clapper:).

---

### :speech_balloon: :bug: Soporte, Sugerencias e Issues

¿Encontraste un enlace caído :x:, un error en la terminal :computer: o querés solicitar que agreguemos un juego nuevo :video_game:? 
Podés abrir un reporte en la sección de **[Issues](../../issues)** :tools:.

<div align="center">
  <br>
  <b>:skull: ¡Gracias por usar Pirate CLI y surcar los mares con nosotros! :anchor: :ocean: :ship:</b>
</div>
