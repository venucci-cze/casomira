#!/usr/bin/env bash
set -euo pipefail

# Barvy
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[1;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Funkce
info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

ok() {
    echo -e "${GREEN}[ OK ]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERR ]${NC} $1"
}

clear

echo -e "${GREEN}"
echo "===================================="
echo "      Created by SVM 2026"
echo "===================================="
echo -e "${NC}"

info "Instaluji Python 3 a potřebné balíčky..."

sudo apt update
sudo apt install -y \
    python3 \
    python3-venv \
    python3-pip \
    python3-tk

ok "APT balíčky nainstalovány"

info "Instaluji Python knihovny..."

pip3 install customtkinter requests

ok "Python knihovny nainstalovány"

echo
echo -e "${GREEN}Hotovo!${NC}"
