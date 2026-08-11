# ☠️ ⚔️ ⚓ P1R4T3R3P0 ⚓ ⚔️ ☠️

> **El gestor CLI de descargas para Linux — Juegos 🎮, Películas 🎬 y Series 📺**

¡Bienvenido a bordo, marinero! 🌊 **P1R4T3R3P0** es un gestor interactivo para la terminal de Linux diseñado para buscar 🔍, descargar 📥, descomprimir 📦 e instalar 🚀 contenido multimedia de forma totalmente automática.

---

### ⚡ 📥 Instalación Rápida

Ejecutá cualquiera de estos dos comandos en tu terminal para abordar el barco ⛵:

<div align="left">
<pre style="background-color: #0d1117; color: #2ea043; padding: 18px; border-radius: 12px; border: 1px solid #30363d; font-family: 'Courier New', Courier, monospace;">
<span style="color: #8b949e;"># Opción 1: Con cURL (Recomendado)</span>
<span style="color: #00ff66;">curl -sSL https://raw.githubusercontent.com/Y0U4R34P1R4T3/P1R4T3R3P0/main/install.sh | sh</span>

<span style="color: #8b949e;"># Opción 2: Con Wget</span>
<span style="color: #00ff66;">wget -qO- https://raw.githubusercontent.com/Y0U4R34P1R4T3/P1R4T3R3P0/main/install.sh | sh</span>
</pre>
</div>

> ⚠️ **¡Atención Navegante!** El repositorio cambia constantemente. Acordate de ejecutar siempre `pirate update` antes de descargar algo para refrescar los mapas y asegurar que usás las últimas versiones disponibles.

---

### 🛠️ 💻 Uso y Comandos

Una vez instalado, ejecutá el comando `pirate` directamente en tu terminal:

| Comando | Estado | Descripción |
| :--- | :---: | :--- |
| `pirate update` | 🔄 | Actualiza el catálogo local y el script a la última versión |
| `pirate search <nombre>` | 🔍 | Busca juegos, películas o series por palabra clave |
| `pirate listall` | 📜 | Muestra el catálogo completo sin filtros |
| `pirate listgames` | 🎮 | Muestra únicamente el catálogo de juegos |
| `pirate listmovies` | 🎬 | Muestra únicamente la lista de películas |
| `pirate listseries` | 📺 | Muestra únicamente la lista de series |
| `pirate install <id>` | 📥 | Descarga, descomprime e instala un elemento |
| `pirate upgrade` | 🚀 | Actualiza tus juegos instalados a la versión más reciente |
| `pirate request "<nombre>"` | 📝 | Abre una solicitud en GitHub para pedir contenido |

---

### ✨ Características Principales

* 🚀 **Descargas Aceleradas:** Uso automático de `aria2c` (con multihilos) o `wget` como motor de respaldo.
* 🧲 **Soporte Multi-fuente:** Descargas directas, MediaFire, Buzzheavier, GoFile y Torrents / Magnets y mas fuentes.
* 🔔 **Sistema de Alerta Automatizado:** Notificaciones instantáneas push en caso de detectar enlaces o descargas caídas.
* 📂 **Estructura Organizada:** Todo se almacena automáticamente en tu carpeta personal (`~/PIRATE/Games` y `~/PIRATE/Movies`).

---

### 💬 Soporte, Sugerencias e Issues

¿Encontraste un enlace caído, un error en la terminal o querés solicitar que agreguemos un juego nuevo? 
Podés abrir un reporte en la sección de **[Issues](../../issues)** 🛠️.

<div align="center">
  <br>
  <b>☠️ ¡Gracias por usar Pirate CLI y surcar los mares con nosotros! ⚓ 🌊 ⛵</b>
</div>
