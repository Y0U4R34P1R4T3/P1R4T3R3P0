#!/bin/bash

echo "[*] Instalando P1R4T3 CLI..."

# Detectar e instalar dependencias (wget y python)
if command -v pacman &> /dev/null; then
    sudo pacman -S --needed wget python -y
elif command -v apt &> /dev/null; then
    sudo apt update && sudo apt install -y wget python3
fi

# Crear carpetas locales
mkdir -p ~/.local/bin
mkdir -p ~/.local/share/pirate/games

# Descargar pirate.py desde tu GitHub a la carpeta de binarios del usuario
wget -q -O ~/.local/bin/pirate https://raw.githubusercontent.com/Y0U4R34P1R4T3/P1R4T3R3P0/main/pirate.py
chmod +x ~/.local/bin/pirate

# Agregar ~/.local/bin al PATH si no esta presente
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
fi

echo "[V] ¡Instalación completada!"
echo "[*] Reiniciá la terminal o ejecutá: source ~/.bashrc"
echo "[*] Luego probá con: pirate update"
