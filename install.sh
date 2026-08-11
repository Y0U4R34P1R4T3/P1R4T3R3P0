#!/bin/sh
set -e

echo "☠ Instalando Pirate CLI..."

# Crear carpeta de binarios locales
mkdir -p "$HOME/.local/bin"

# Descargar pirate.py
if command -v curl >/dev/null 2>&1; then
    curl -sSL "https://raw.githubusercontent.com/Y0U4R34P1R4T3/P1R4T3R3P0/main/pirate.py" -o "$HOME/.local/bin/pirate"
elif command -v wget >/dev/null 2>&1; then
    wget -qO "$HOME/.local/bin/pirate" "https://raw.githubusercontent.com/Y0U4R34P1R4T3/P1R4T3R3P0/main/pirate.py"
else
    echo "[X] Error: Se necesita curl o wget para instalar Pirate CLI."
    exit 1
fi

# Permisos de ejecución
chmod +x "$HOME/.local/bin/pirate"

# Agregar a PATH en .bashrc si no está agregado
if ! echo "$PATH" | grep -q "$HOME/.local/bin"; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
    if [ -f "$HOME/.zshrc" ]; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.zshrc"
    fi
fi

# Exportar para la sesión actual y ejecutar primera actualización
export PATH="$HOME/.local/bin:$PATH"
"$HOME/.local/bin/pirate" update

echo "☠ ¡Pirate CLI se instaló correctamente! Reiniciá la terminal o ejecutá 'source ~/.bashrc' si el comando 'pirate' no responde."
