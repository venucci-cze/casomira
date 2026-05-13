"""
UPDATER.EXE - Čistý oddělený proces pro update
================================================

ROLE:
1. Stáhni nový EXE z GitHub
2. Počkej až app se vypne (EXE není zamčený)
3. Atomic replace: app.exe → app.old / temp.exe → app.exe
4. Restart aplikace

VSTUPY: CLI parametry
VÝSTUPY: Exit code (0=OK, 1=FAIL)

DŮLEŽITÉ: ŽÁDNÝ TKINTER, ŽÁDNÝ GUI!
"""

import requests
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime
import argparse


# Konfigurace
GITHUB_REPO = "venucci-cze/casomira"
GITHUB_API = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
APP_NAME = "casomira.exe"
BACKUP_DIR = "backups"
VERSION_FILE = "version.txt"
MAX_RETRIES = 3
WAIT_FOR_QUIT = 10  # sekund


class CleanUpdater:
    """Čistý updater - jen download + replace + restart."""
    
    def __init__(self):
        self.current_version = self._load_version()
        self.latest_version = None
        self.download_url = None
    
    def _load_version(self):
        """Načte verzi z version.txt."""
        if os.path.exists(VERSION_FILE):
            try:
                with open(VERSION_FILE, 'r') as f:
                    return f.read().strip()
            except:
                return "0.0.0"
        return "0.0.0"
    
    def _save_version(self, version):
        """Uloží verzi."""
        try:
            with open(VERSION_FILE, 'w') as f:
                f.write(version)
            print(f"✅ Verze {version} uložena")
        except Exception as e:
            print(f"❌ Chyba zápisu verze: {e}")
    
    def get_latest_release(self):
        """Získá info o nejnovější verzi z GitHub."""
        try:
            print("🔍 Kontroluji GitHub releases...")
            response = requests.get(GITHUB_API, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            self.latest_version = data.get('tag_name', '0.0.0').lstrip('v')
            
            # Najdi casomira.exe v assets
            for asset in data.get('assets', []):
                if asset['name'] == APP_NAME:
                    self.download_url = asset['browser_download_url']
                    return True
            
            print("❌ casomira.exe nenalezen v release assets")
            return False
        
        except Exception as e:
            print(f"❌ Chyba GitHub API: {e}")
            return False
    
    def wait_for_app_exit(self, timeout=WAIT_FOR_QUIT):
        """Čeká až se aplikace vypne (EXE není zamčený)."""
        print(f"⏳ Čekám až se aplikace vypne ({timeout}s)...")
        
        for i in range(timeout):
            try:
                # Pokus se otevřít - pokud jde, není zamčený
                with open(APP_NAME, 'rb'):
                    pass
                print("✅ Aplikace vypnutá, pokračuji...")
                return True
            except (IOError, OSError):
                # Soubor je zamčený
                remaining = timeout - i - 1
                if remaining > 0:
                    print(f"   Čekám... ({remaining}s)")
                time.sleep(1)
        
        print("❌ Timeout - aplikace se nevypnula!")
        return False
    
    def download_file(self):
        """Stáhne nový EXE."""
        if not self.download_url:
            print("❌ Download URL není dostupná")
            return False
        
        temp_file = f"{APP_NAME}.tmp"
        
        for attempt in range(MAX_RETRIES):
            try:
                print(f"⬇️ Stahuju {APP_NAME} (pokus {attempt + 1}/{MAX_RETRIES})...")
                response = requests.get(
                    self.download_url,
                    stream=True,
                    timeout=30
                )
                response.raise_for_status()
                
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                
                with open(temp_file, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total_size:
                                percent = (downloaded / total_size) * 100
                                print(f"   {percent:.1f}%", end='\r')
                
                print(f"\n✅ Staženo: {temp_file}")
                return True
            
            except Exception as e:
                print(f"❌ Chyba stahování: {e}")
                if os.path.exists(temp_file):
                    try:
                        os.remove(temp_file)
                    except:
                        pass
                
                if attempt < MAX_RETRIES - 1:
                    print(f"🔄 Opakuji...")
                    time.sleep(2)
        
        return False
    
    def atomic_replace(self):
        """Atomicky nahradí EXE."""
        temp_file = f"{APP_NAME}.tmp"
        
        if not os.path.exists(temp_file):
            print("❌ Temp soubor neexistuje")
            return False
        
        try:
            print("🔄 Nahrazuji soubor...")
            
            # Vytvoř backup
            if os.path.exists(APP_NAME):
                if not os.path.exists(BACKUP_DIR):
                    os.makedirs(BACKUP_DIR)
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_file = os.path.join(BACKUP_DIR, f"{APP_NAME}.{timestamp}")
                
                shutil.move(APP_NAME, backup_file)
                print(f"💾 Záloha: {backup_file}")
            
            # Přejmenuj temp na finální (atomic)
            shutil.move(temp_file, APP_NAME)
            print(f"✅ Soubor nahrazen: {APP_NAME}")
            return True
        
        except Exception as e:
            print(f"❌ Chyba nahrazení: {e}")
            return False
    
    def restart_app(self):
        """Restartuje aplikaci."""
        try:
            print("🚀 Restart aplikace...")
            if sys.platform == 'win32':
                subprocess.Popen([APP_NAME])
            else:
                subprocess.Popen(['./' + APP_NAME])
            return True
        except Exception as e:
            print(f"❌ Chyba restartu: {e}")
            return False
    
    def run_update(self):
        """Hlavní update flow."""
        print("=" * 50)
        print("   CASOMIRA UPDATER")
        print("=" * 50)
        print(f"Aktuální verze: {self.current_version}\n")
        
        # 1. Kontrola nové verze
        if not self.get_latest_release():
            print("❌ Nelze kontaktovat GitHub")
            return False
        
        if self.latest_version == self.current_version:
            print("✅ Máš nejnovější verzi!")
            return True
        
        print(f"✅ Nová verze dostupná: {self.latest_version}")
        
        # 2. Čekat na vypnutí appky
        if not self.wait_for_app_exit():
            print("❌ Aplikace se nevypnula!")
            return False
        
        # 3. Stáhnout
        if not self.download_file():
            print("❌ Stahování selhalo!")
            return False
        
        # 4. Atomicky nahradit
        if not self.atomic_replace():
            print("❌ Nahrazení selhalo!")
            return False
        
        # 5. Uložit verzi
        self._save_version(self.latest_version)
        
        # 6. Restart
        time.sleep(1)
        if not self.restart_app():
            print("❌ Restart selhalo!")
            return False
        
        print("\n" + "=" * 50)
        print("✅ AKTUALIZACE HOTOVA!")
        print("=" * 50)
        return True


def check_for_updates():
    """
    Kontrola dostupné verze (pro casomira.py).
    Vrací dict s info nebo None.
    """
    try:
        updater = CleanUpdater()
        if updater.get_latest_release():
            if updater.latest_version != updater.current_version:
                return {
                    'available': True,
                    'current': updater.current_version,
                    'latest': updater.latest_version,
                    'download_url': updater.download_url
                }
    except:
        pass
    
    return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Casomira Updater")
    parser.add_argument('--check-only', action='store_true',
                       help='Jen zkontroluj, nesahuj na soubory')
    
    args = parser.parse_args()
    
    updater = CleanUpdater()
    
    if args.check_only:
        # Jen zkontroluj
        if updater.get_latest_release():
            print(f"Aktuální: {updater.current_version}")
            print(f"Dostupná: {updater.latest_version}")
            if updater.latest_version != updater.current_version:
                print("✅ Update je dostupný!")
                sys.exit(0)
        print("ℹ️ Máš nejnovější verzi")
        sys.exit(1)
    else:
        # Spusť update
        success = updater.run_update()
        sys.exit(0 if success else 1)