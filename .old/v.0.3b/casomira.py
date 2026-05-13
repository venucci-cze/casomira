import customtkinter as ctk  # Pro moderní vzhled GUI
import tkinter as tk
from tkinter import ttk  # Pro lepší tabulku
import requests
import time
from datetime import datetime
import threading

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

SINGLE_ESP_IP = "192.168.4.1"  # IP adresa jediného ESP8266
URL = f"http://{SINGLE_ESP_IP}/data"

DATA_FILE = "timing_data.csv"
BACKUP_FILE = "timing_data_backup.csv"

# Global variables for GUI elements
time_label = None
team_a_label = None
team_b_label = None
tree = None
status_label = None
root = None
auto_measure_enabled = False
auto_measure_id = None
last_fetched_data = (None, None)  # Poslední načtená data
last_saved_data = (None, None)  # Poslední uložená data - pro detekci duplikátů





def save_data(team_a_time, team_b_time):
    """Ukládá časové údaje do CSV souboru. Ignoruje duplikujcí data a chybová data."""
    global last_saved_data
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(BACKUP_FILE, 'a') as f:
            f.write(f"{timestamp},{team_a_time},{team_b_time}\n") # Uložení do záložního souboru
            print(f"💾 Zápis dat do {BACKUP_FILE}.....")
    except IOError:
        print(f"❌ Chyba při zápisu do záložního souboru {BACKUP_FILE}.")
    
    # Kontrola chybových dat
    if team_a_time == "Chyba spojení" or team_b_time == "Chyba spojení" or team_a_time == "N/A" or team_b_time == "N/A":
        print("⚠️ Chybná data - ignorováno")
        return
    
    # Kontrola duplikujcích čísů
    if last_saved_data == (team_a_time, team_b_time):
        print("⚠️ Duplikujcí časy - ignorováno")
        return
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        with open(DATA_FILE, 'a') as f:
            f.write(f"{timestamp},{team_a_time},{team_b_time}\n") # Uložení do hlavního souboru
        last_saved_data = (team_a_time, team_b_time)  # Aktualizuj poslední uložená data
        print(f"💾 Data uložena do {DATA_FILE}")
    except IOError:
        print(f"❌ Chyba při zápisu do souboru {DATA_FILE}.")

def load_history():
    """Načte historii z CSV a zobrzí v tabulce. Aktualizuje poslední uložená data."""
    global tree, last_saved_data
    if tree is None:
        return
    # Vymazání starých dat
    for item in tree.get_children():
        tree.delete(item)
    try:
        with open(DATA_FILE, 'r') as f:
            lines = f.readlines()
            if lines:
                # Získej poslední záznam
                last_line = lines[-1].strip().split(',')
                if len(last_line) == 3:
                    last_saved_data = (last_line[1], last_line[2])  # timestamp, team_a, team_b
            # Vlož všechny záznamy
            f.seek(0)
            for line in f:
                parts = line.strip().split(',')
                if len(parts) == 3:
                    tree.insert('', 'end', values=parts)
    except FileNotFoundError:
        pass


def delete_last():
    """Odstraní poslední záznam z CSV a aktualizuje tabulku."""
    try:
        with open(DATA_FILE, 'r') as f:
            lines = f.readlines()
        if lines:
            lines = lines[:-1]  # Odstranit poslední řádek
            with open(DATA_FILE, 'w') as f:
                f.writelines(lines)
            print("Poslední záznam odstraněn.")
        else:
            print("Žádný záznam k odstranění.")
    except IOError:
        print(f"Chyba při práci se souborem {DATA_FILE}.")
    load_history()


def delete_all():
    """Odstraní všechny záznamy z CSV a vymaže tabulku."""
    try:
        with open(DATA_FILE, 'w') as f:
            pass  # Vymazat obsah
        print("Všechny záznamy --> odstraněny.")
    except IOError:
        print(f"Chyba při práci se souborem {DATA_FILE}.")
    else:
        print("Žádné další záznamy k odstranění.")
    load_history()


def fetch_timing_data_async():
    """Čte data z ESP8266 v separátním vlákně a pak aktualizuje GUI."""
    thread = threading.Thread(target=_fetch_in_thread, daemon=True)
    thread.start()


def _fetch_in_thread():
    """Vlákno, které čte data z ESP8266."""
    global last_fetched_data
    print("--- Požadavek na časy ---")
    print("⏳ Čekám na odpověď z ESP8266...")
    try:
        response = requests.get(URL, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        time_a = data.get('time_a', 'N/A')
        time_b = data.get('time_b', 'N/A')
        last_fetched_data = (time_a, time_b)
        print("✅ Data přijata úspěšně.")
    except requests.exceptions.RequestException as e:
        print(f"❌ Chyba spojení nebo data: {e}")
        last_fetched_data = ("Chyba spojení", "N/A")
    
    # Po načtení dat zavolej GUI aktualizaci (bezpečně z hlavního vlákna)
    root.after(0, _update_gui_from_thread)


def _update_gui_from_thread():
    """Aktualizuje GUI po přijetí dat ze vlákna."""
    global time_label, team_a_label, team_b_label, status_label
    time_a, time_b = last_fetched_data

    # Aktualizace konzole (Terminal)
    print("--------------------------------------")
    print(f"Aktuální Časy: Tým A={time_a}, Tým B={time_b}")
    print("--------------------------------------")

    # Aktualizace GUI
    if time_label:
        time_label.config(text=datetime.now().strftime("%H:%M:%S"))
    if team_a_label:
        team_a_label.config(text=str(time_a))
    if team_b_label:
        team_b_label.config(text=str(time_b))
    if status_label:
        status_label.config(text="Hotovo")

    # Uložení dat do souboru
    save_data(time_a, time_b)

    # Načtení historie do tabulky
    load_history()


def update_display():
    """Spustí asynchronní čtení dat z ESP8266."""
    global status_label
    if status_label:
        status_label.config(text="čtení")
    fetch_timing_data_async()


def schedule_measurement():
    """Naplánuje další měření za 10 sekund, pokud je auto measure zapnutý."""
    global auto_measure_id
    if auto_measure_enabled:
        curent_status_text = "Auto. měření --> ZAPNUTO"
        update_display()
        auto_measure_id = root.after(10000, schedule_measurement)  # Opakuje každých 10 sekund


def toggle_auto_measure():
    """Zapíná/vypíná automatické měření."""
    global auto_measure_enabled, auto_measure_id
    auto_measure_enabled = not auto_measure_enabled
    
    if auto_measure_enabled:
        # Když se zapíná, hned měř
        schedule_measurement()
        print("Auto. měření --> ZAPNUTO")
    else:
        # Když se vypíná, zrušit naplánované měření
        if auto_measure_id:
            root.after_cancel(auto_measure_id)
            auto_measure_id = None
        print("Auto. měření --> VYPNUTO")


def main_app():
    """Hlavní logika GUI."""
    global time_label, team_a_label, team_b_label, tree, status_label, root
    root = ctk.CTk()
    root.title("Časový Monitor ESP8266")
    root.geometry("900x520")

    # --- 1. Zobrazení Dat (Tabulka) ---
    frame_table = ctk.CTkFrame(root)
    frame_table.pack(side="left", padx=10, pady=10, fill="both", expand=True)

    title_table = ctk.CTkLabel(frame_table, text="Historie Časů", font=ctk.CTkFont(size=16, weight="bold"))
    title_table.pack(padx=5, pady=(5, 10), anchor="w")

    # Definice sloupců pro Treeview
    columns = ("Timestamp", "Tým A", "Tým B")
    tree = ttk.Treeview(frame_table, columns=columns, show='headings')

    # Nastavení šířek sloupců
    tree.column("Timestamp", width=220, anchor='w')
    tree.column("Tým A", width=180, anchor='w')
    tree.column("Tým B", width=180, anchor='w')

    # Přidání hlaviček
    tree.heading("Timestamp", text="Systémový čas")
    tree.heading("Tým A", text="Tým A")
    tree.heading("Tým B", text="Tým B")

    tree.pack(fill="both", expand=True, padx=5, pady=5)

    # --- 1b. Tlačítka pro správu dat ---
    frame_buttons = ctk.CTkFrame(root)
    frame_buttons.pack(side="right", padx=10, pady=10, fill="y")

    title_buttons = ctk.CTkLabel(frame_buttons, text="Správa Dat", font=ctk.CTkFont(size=16, weight="bold"))
    title_buttons.pack(padx=5, pady=(5, 10), anchor="w")

    delete_last_button = ctk.CTkButton(frame_buttons, text="Odstranit poslední", command=delete_last)
    delete_last_button.pack(pady=5, fill="x")

    delete_all_button = ctk.CTkButton(frame_buttons, text="Odstranit vše", command=delete_all)
    delete_all_button.pack(pady=5, fill="x")

    # --- 2. Zobrazení aktuálních hodnot (Labely) ---
    frame_status = ctk.CTkFrame(root)
    frame_status.pack(padx=10, pady=10, fill="x")

    title_status = ctk.CTkLabel(frame_status, text="Aktuální Hodnoty", font=ctk.CTkFont(size=16, weight="bold"))
    title_status.grid(row=0, column=0, columnspan=2, padx=5, pady=(5, 10), sticky='w')

    ctk.CTkLabel(frame_status, text="Systemový Čas:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
    time_label = ctk.CTkLabel(frame_status, text="--")
    time_label.grid(row=1, column=1, padx=5, pady=5, sticky='w')

    ctk.CTkLabel(frame_status, text="Tým A:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
    team_a_label = ctk.CTkLabel(frame_status, text="--")
    team_a_label.grid(row=2, column=1, padx=5, pady=5, sticky='w')

    ctk.CTkLabel(frame_status, text="Tým B:").grid(row=3, column=0, padx=5, pady=5, sticky='e')
    team_b_label = ctk.CTkLabel(frame_status, text="--")
    team_b_label.grid(row=3, column=1, padx=5, pady=5, sticky='w')

    ctk.CTkLabel(frame_status, text="IP adresa ESP8266:").grid(row=4, column=0, padx=5, pady=5, sticky='e')
    esp_ip_label = ctk.CTkLabel(frame_status, text=SINGLE_ESP_IP)
    esp_ip_label.grid(row=4, column=1, padx=5, pady=5, sticky='w')

    ctk.CTkLabel(frame_status, text="Stav:").grid(row=5, column=0, padx=5, pady=5, sticky='e')
    status_label = ctk.CTkLabel(frame_status, text="aktuální stav")
    status_label.grid(row=5, column=1, padx=5, pady=5, sticky='w')

    ctk.CTkLabel(frame_status, text="Auto. měření:").grid(row=6, column=0, padx=5, pady=5, sticky='e')
    auto_measure_check = ctk.CTkCheckBox(frame_status, text="Zapnout", command=toggle_auto_measure)
    auto_measure_check.grid(row=6, column=1, padx=5, pady=5, sticky='w')

    # --- 3. Tlačítko pro měření ---
    measure_button = ctk.CTkButton(root, text="📏 Měřit", command=update_display, font=ctk.CTkFont(size=14, weight="bold"))
    measure_button.pack(pady=15)

    # Inicializace – pouze načteme historii, bez automatického měření
    load_history()

    # Spuštění GUI
    root.mainloop()


if __name__ == "__main__":
    main_app()
