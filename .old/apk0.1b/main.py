from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.properties import StringProperty
import requests
from datetime import datetime
import threading
import os

# --- KONFIGURACE (OVĚŘTE TUTO ADRESU!) ---
SINGLE_ESP_IP = "192.168.4.1"  # IP adresa jediného ESP8266
URL = f"http://{SINGLE_ESP_IP}/data"

DATA_FILE = "timing_data.csv"
BACKUP_FILE = "timing_data_backup.csv"

# Zajistit, aby se soubory uložily do applikačního adresáře
if not os.path.exists(DATA_FILE):
    open(DATA_FILE, 'a').close()
if not os.path.exists(BACKUP_FILE):
    open(BACKUP_FILE, 'a').close()

# Global variables
app_instance = None
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
            f.write(f"{timestamp},{team_a_time},{team_b_time}\n")
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
            f.write(f"{timestamp},{team_a_time},{team_b_time}\n")
        last_saved_data = (team_a_time, team_b_time)
        print(f"💾 Data uložena do {DATA_FILE}")
    except IOError:
        print(f"❌ Chyba při zápisu do souboru {DATA_FILE}.")

def load_history():
    """Načte historii z CSV a aktualizuje seznam v Kivy aplikaci."""
    global app_instance, last_saved_data
    if app_instance is None:
        return
    
    # Vymazání starých dat
    app_instance.history_data = []
    
    try:
        with open(DATA_FILE, 'r') as f:
            lines = f.readlines()
            if lines:
                # Získej poslední záznam
                last_line = lines[-1].strip().split(',')
                if len(last_line) == 3:
                    last_saved_data = (last_line[1], last_line[2])
            # Vlož všechny záznamy
            for line in lines:
                parts = line.strip().split(',')
                if len(parts) == 3:
                    app_instance.history_data.append(parts)
        # Aktualizuj GUI
        if app_instance:
            app_instance.update_history_view()
    except FileNotFoundError:
        pass


def delete_last():
    """Odstraní poslední záznam z CSV a aktualizuje seznam."""
    try:
        with open(DATA_FILE, 'r') as f:
            lines = f.readlines()
        if lines:
            lines = lines[:-1]
            with open(DATA_FILE, 'w') as f:
                f.writelines(lines)
            print("✅ Poslední záznam odstraněn.")
        else:
            print("⚠️ Žádný záznam k odstranění.")
    except IOError:
        print(f"❌ Chyba při práci se souborem {DATA_FILE}.")
    load_history()


def delete_all():
    """Odstraní všechny záznamy z CSV a vymaže seznam."""
    try:
        with open(DATA_FILE, 'w') as f:
            pass
        print("✅ Všechny záznamy --> odstraněny.")
    except IOError:
        print(f"❌ Chyba při práci se souborem {DATA_FILE}.")
    load_history()


def fetch_timing_data_async():
    """Čte data z ESP8266 v separátním vlákně."""
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
    
    # Aktualizuj GUI z hlavního vlákna
    if app_instance:
        Clock.schedule_once(lambda dt: _update_gui_from_thread(), 0)


def _update_gui_from_thread():
    """Aktualizuje GUI po přijetí dat ze vlákna."""
    global app_instance
    if app_instance is None:
        return
    
    time_a, time_b = last_fetched_data

    # Aktualizace konzole
    print("--------------------------------------")
    print(f"Aktuální Časy: Tým A={time_a}, Tým B={time_b}")
    print("--------------------------------------")

    # Aktualizace GUI
    app_instance.time_label_text = datetime.now().strftime("%H:%M:%S")
    app_instance.team_a_text = str(time_a)
    app_instance.team_b_text = str(time_b)
    app_instance.status_text = "Hotovo"

    # Uložení dat do souboru
    save_data(time_a, time_b)

    # Načtení historie
    load_history()


def update_display():
    """Spustí asynchronní čtení dat z ESP8266."""
    if app_instance:
        app_instance.status_text = "čtení"
    fetch_timing_data_async()


def schedule_measurement():
    """Naplánuje další měření za 10 sekund."""
    global auto_measure_enabled, auto_measure_id
    if auto_measure_enabled:
        update_display()
        auto_measure_id = Clock.schedule_once(lambda dt: schedule_measurement(), 10)


def toggle_auto_measure():
    """Zapíná/vypíná automatické měření."""
    global auto_measure_enabled, auto_measure_id
    auto_measure_enabled = not auto_measure_enabled
    
    if auto_measure_enabled:
        schedule_measurement()
        print("✅ Auto. měření --> ZAPNUTO")
    else:
        if auto_measure_id:
            Clock.unschedule(auto_measure_id)
            auto_measure_id = None
        print("✅ Auto. měření --> VYPNUTO")


class TimingMonitorApp(App):
    """Kivy aplikace pro monitoring ESP8266."""
    
    time_label_text = StringProperty("--")
    team_a_text = StringProperty("--")
    team_b_text = StringProperty("--")
    status_text = StringProperty("aktuální stav")
    auto_measure_text = StringProperty("Zapnout automatické měření")
    history_data = []
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.history_grid = None
    
    def build(self):
        """Stavba UI."""
        global app_instance
        app_instance = self
        
        # Hlavní layout
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # --- Horní část: Aktuální hodnoty ---
        status_frame = BoxLayout(orientation='vertical', size_hint_y=0.35, padding=10, spacing=5)
        status_frame_label = Label(text="Aktuální Hodnoty", size_hint_y=0.1, bold=True)
        status_frame.add_widget(status_frame_label)
        
        # Systemový čas
        time_layout = BoxLayout(size_hint_y=0.15, spacing=10)
        time_layout.add_widget(Label(text="Systémový Čas:", size_hint_x=0.5))
        time_layout.add_widget(Label(text=self.time_label_text, size_hint_x=0.5))
        self.bind(time_label_text=lambda instance, value: time_layout.children[1].setter('text')(time_layout.children[1], value))
        status_frame.add_widget(time_layout)
        
        # Tým A
        team_a_layout = BoxLayout(size_hint_y=0.15, spacing=10)
        team_a_layout.add_widget(Label(text="Tým A:", size_hint_x=0.5))
        team_a_layout.add_widget(Label(text=self.team_a_text, size_hint_x=0.5))
        self.bind(team_a_text=lambda instance, value: team_a_layout.children[1].setter('text')(team_a_layout.children[1], value))
        status_frame.add_widget(team_a_layout)
        
        # Tým B
        team_b_layout = BoxLayout(size_hint_y=0.15, spacing=10)
        team_b_layout.add_widget(Label(text="Tým B:", size_hint_x=0.5))
        team_b_layout.add_widget(Label(text=self.team_b_text, size_hint_x=0.5))
        self.bind(team_b_text=lambda instance, value: team_b_layout.children[1].setter('text')(team_b_layout.children[1], value))
        status_frame.add_widget(team_b_layout)
        
        # IP adresa
        ip_layout = BoxLayout(size_hint_y=0.15, spacing=10)
        ip_layout.add_widget(Label(text="IP ESP8266:", size_hint_x=0.5))
        ip_layout.add_widget(Label(text=SINGLE_ESP_IP, size_hint_x=0.5))
        status_frame.add_widget(ip_layout)
        
        # Stav
        state_layout = BoxLayout(size_hint_y=0.15, spacing=10)
        state_layout.add_widget(Label(text="Stav:", size_hint_x=0.5))
        state_layout.add_widget(Label(text=self.status_text, size_hint_x=0.5))
        self.bind(status_text=lambda instance, value: state_layout.children[1].setter('text')(state_layout.children[1], value))
        status_frame.add_widget(state_layout)
        
        main_layout.add_widget(status_frame)
        
        # --- Tlačítko pro měření ---
        measure_button = Button(text="📏 Měřit", size_hint_y=0.1, bold=True, font_size='18sp')
        measure_button.bind(on_press=self.on_measure_button)
        main_layout.add_widget(measure_button)
        
        # --- Střední část: Historie ---
        history_label = Label(text="Historie Časů", size_hint_y=0.05, bold=True)
        main_layout.add_widget(history_label)
        
        # ScrollView pro tabulku
        scroll_view = ScrollView(size_hint_y=0.35)
        self.history_grid = GridLayout(cols=3, spacing=5, padding=5, size_hint_y=None)
        self.history_grid.bind(minimum_height=self.history_grid.setter('height'))
        
        # Hlavičky
        header_style = {'bold': True, 'color': (0.2, 0.6, 0.2, 1)}
        self.history_grid.add_widget(Label(text="Čas", size_hint_y=None, height=40, **header_style))
        self.history_grid.add_widget(Label(text="Tým A", size_hint_y=None, height=40, **header_style))
        self.history_grid.add_widget(Label(text="Tým B", size_hint_y=None, height=40, **header_style))
        
        scroll_view.add_widget(self.history_grid)
        main_layout.add_widget(scroll_view)
        
        # --- Dolní část: Tlačítka pro správu ---
        bottom_layout = BoxLayout(size_hint_y=0.15, spacing=5)
        
        delete_last_btn = Button(text="Odstranit poslední")
        delete_last_btn.bind(on_press=self.on_delete_last)
        bottom_layout.add_widget(delete_last_btn)
        
        delete_all_btn = Button(text="Odstranit vše")
        delete_all_btn.bind(on_press=self.on_delete_all)
        bottom_layout.add_widget(delete_all_btn)
        
        # Auto měření
        auto_checkbox = CheckBox(size_hint_x=0.2)
        auto_checkbox.bind(active=self.on_auto_measure_toggle)
        auto_layout = BoxLayout(size_hint_x=0.5, spacing=5)
        auto_layout.add_widget(Label(text="Auto měření:"))
        auto_layout.add_widget(auto_checkbox)
        bottom_layout.add_widget(auto_layout)
        
        main_layout.add_widget(bottom_layout)
        
        # Načti historii
        load_history()
        
        return main_layout
    
    def update_history_view(self):
        """Aktualizuje zobrazení historie."""
        if self.history_grid is None:
            return
        
        # Vymaž stare záznamy (s výjimkou hlaviček)
        children_to_remove = self.history_grid.children[:-3]  # Poslední 3 jsou hlavičky
        for child in children_to_remove:
            self.history_grid.remove_widget(child)
        
        # Přidej nové záznamy
        for record in reversed(self.history_data):
            for value in record:
                self.history_grid.add_widget(Label(text=value, size_hint_y=None, height=30))
    
    def on_measure_button(self, instance):
        """Callback pro tlačítko měření."""
        update_display()
    
    def on_delete_last(self, instance):
        """Callback pro odstranění posledního."""
        delete_last()
    
    def on_delete_all(self, instance):
        """Callback pro odstranění všeho."""
        delete_all()
    
    def on_auto_measure_toggle(self, instance, value):
        """Callback pro toggle automatického měření."""
        toggle_auto_measure()


def main_app():
    """Spuštění aplikace."""
    app = TimingMonitorApp()
    app.run()


if __name__ == "__main__":
    main_app()
