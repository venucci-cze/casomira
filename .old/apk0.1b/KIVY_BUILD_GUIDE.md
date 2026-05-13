# Kivy Android Build Guide - Časomíra

## Změny z Tkinter na Kivy

Aplikace byla úspěšně konvertována z **Tkinter** (desktop) na **Kivy** (mobilní/desktop).

### Klíčové změny:

1. **Framework**: Tkinter → Kivy
   - `tkinter` → `kivy` importy
   - `tk.Tk()` → `kivy.app.App` třída
   - Tkinter widgets → Kivy widgets

2. **Layouts**: 
   - Tkinter `pack/grid` → Kivy `BoxLayout`, `GridLayout`
   - Reaktivní properties pomocí `StringProperty`

3. **GUI Threading**:
   - `root.after()` → `kivy.clock.Clock.schedule_once()`

4. **Tabulka/Seznam**:
   - Tkinter `Treeview` → Kivy `GridLayout` v `ScrollView`

5. **Soubory**:
   - CSV data se stále ukládají stejně
   - Data se čtou z ESP8266 pomocí `requests`

## Instalace a Build

### Předpoklady:

```bash
pip install buildozer cython
pip install kivy requests
```

### Build APK:

```bash
cd /path/to/casomira/apk0.1b
buildozer android debug
```

### Build Release APK:

```bash
buildozer android release
```

### Čištění a rebuild:

```bash
buildozer android clean
buildozer android debug
```

## Konfigurační soubory:

- **main.py** - Aktualizovaná Kivy aplikace
- **buildozer.spec** - Konfigurační soubor pro build
  - Obsahuje permissions pro INTERNET, čtení/zápis souborů
  - Nastaveno na Android build

## Spuštění na Android zařízení:

1. Dejte zařízení do Developer mode
2. Připojte USB kabel
3. Spusťte:

```bash
buildozer android debug deploy run
```

## Poznámky:

- Aplikace si ponechává CSV soubory (`timing_data.csv`, `timing_data_backup.csv`)
- Data se ukládají v aplikačním adresáři
- IP adresa ESP8266 je pevně nastavena na `192.168.4.1` (měňte v kódu dle potřeby)
- Auto-měření funguje stejně jako v původní verzi (10 sekund interval)

## Řešení problémů:

### "Kivy not found":
```bash
pip install kivy
```

### "Buildozer failed":
```bash
buildozer android clean
buildozer android debug
```

### Permission denied:
Ujistěte se, že máte práva k čtení/zápisu v projektovém adresáři.

---

**Aplikace je nyní připravena pro Android!** 🚀
