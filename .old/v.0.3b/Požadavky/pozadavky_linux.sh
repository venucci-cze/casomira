#!/usr/bin/env bash
set -euo pipefail

echo "-- Created by SVM 2026 --"
echo "-- Instalace Python 3 --"

sudo apt install python3 python3-venv python3-pip -y

pip install tkinker
pip install customtkinter
pip install requests

echo "Hotovo!"
