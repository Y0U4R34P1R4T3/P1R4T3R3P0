#!/bin/bash

echo "[*] Instalando P1R4T3 CLI..."

# 1. Instalar dependencias necesarias (wget y python)
if command -v pacman &> /dev/null; then
    sudo pacman -S --needed wget python -y
elif command -v apt &> /dev/null; then
    sudo apt update && sudo apt install -y wget python3
fi

# 2. Crear carpetas locales del usuario si no existen
mkdir -p ~/.local/bin
mkdir -p ~/.local/share/pirate/games

# 3. Descargar el ejecutable de pirate y darle permisos
wget -q -O ~/.local/bin/pirate https://raw.githubusercontent.com/Y0U4R34P1R4T3/P1R4T3R3P0/main/pirate.py
chmod +x ~/.local/bin/pirate

# 4. Asegurar que ~/.local/bin esté en el PATH
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
fi

echo "[V] ¡Instalación completada! Abrí una nueva terminal o ejecutá: source ~/.bashrc"
echo "[*] Probá con: pirate update"
