
import os
import sys
import json
import threading
import time
import customtkinter as ctk
from tkinter import messagebox
import keyboard
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
from ctypes import cast, POINTER
import requests

# Tray imports
try:
    import pystray
    from PIL import Image
    TRAY_AVAILABLE = True
except:
    TRAY_AVAILABLE = False

CURRENT_VERSION = "1.3.3"
UPDATE_JSON_URL = "https://raw.githubusercontent.com/scargazeRR/Metadeck/main/version.json"
CONFIG_FILE = "config.json"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Farben wie HTML Simulation
COLORS = {
    "youtube": "#FF0000",
    "system": "#1E90FF", 
    "media": "#9370DB",
    "custom": "#32CD32",
    "bg": "#1a1a1a",
    "tile": "#2d2d2d"
}

ACTIONS = {
    "YT Leiser -5%": {"cat": "youtube", "icon": "🔉", "color": COLORS["youtube"]},
    "YT Lauter +5%": {"cat": "youtube", "icon": "🔊", "color": COLORS["youtube"]},
    "YT Mute": {"cat": "youtube", "icon": "🔇", "color": COLORS["youtube"]},
    "YT Play/Pause": {"cat": "youtube", "icon": "⏯️", "color": COLORS["youtube"]},
    "YT Nächstes": {"cat": "youtube", "icon": "⏭️", "color": COLORS["youtube"]},
    "YT Fullscreen": {"cat": "youtube", "icon": "⛶", "color": COLORS["youtube"]},
    "Sys Leiser": {"cat": "system", "icon": "🔉", "color": COLORS["system"]},
    "Sys Lauter": {"cat": "system", "icon": "🔊", "color": COLORS["system"]},
    "Sys Mute": {"cat": "system", "icon": "🔇", "color": COLORS["system"]},
    "Media Play": {"cat": "media", "icon": "⏯️", "color": COLORS["media"]},
    "Media Next": {"cat": "media", "icon": "⏭️", "color": COLORS["media"]},
    "Media Prev": {"cat": "media", "icon": "⏮️", "color": COLORS["media"]},
    "Custom Taste": {"cat": "custom", "icon": "⌨️", "color": COLORS["custom"]},
    "Custom Text": {"cat": "custom", "icon": "📝", "color": COLORS["custom"]},
    "URL Öffnen": {"cat": "custom", "icon": "🌐", "color": COLORS["custom"]},
}

class MetadeckApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(f"Metadeck v{CURRENT_VERSION} - MEGA32U4 Stream Deck")
        self.geometry("1250x800")
        
        # === TRAY SETUP - X MINIMIERT IN TRAY ===
        self.protocol("WM_DELETE_WINDOW", self.minimize_to_tray)
        self.tray_icon = None
        self.tray_running = False
        
        self.config_data = self.load_config()
        self.selected_tile = 0
        self.waiting_for_key = False
        self.key_listening = False
        
        self.create_ui()
        self.start_key_listener()
        self.check_for_updates()
        
    def create_ui(self):
        # Header
        header = ctk.CTkFrame(self, height=60, fg_color="#2a2a2a")
        header.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(header, text=f"🎛️ Metadeck v{CURRENT_VERSION}", font=("Arial", 20, "bold")).pack(side="left", padx=20, pady=10)
        ctk.CTkLabel(header, text="MEGA32U4 • Press to Assign • Entprellt", font=("Arial", 12)).pack(side="left", padx=10)
        
        # Main split
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Left: Grid 10x2
        left_frame = ctk.CTkFrame(main_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        ctk.CTkLabel(left_frame, text="DEIN DECK (10x2 = 20 Tasten)", font=("Arial", 14, "bold")).pack(pady=5)
        
        self.grid_frame = ctk.CTkFrame(left_frame)
        self.grid_frame.pack(padx=10, pady=10)
        
        self.tile_buttons = []
        for row in range(2):
            for col in range(10):
                idx = row*10 + col
                action = self.config_data.get(str(idx), {}).get("action", "YT Leiser -5%")
                info = ACTIONS.get(action, ACTIONS["YT Leiser -5%"])
                
                btn = ctk.CTkButton(
                    self.grid_frame,
                    text=f"{info['icon']}\n{idx+1}",
                    width=108,
                    height=108,
                    corner_radius=18,
                    fg_color=info['color'],
                    hover_color=self.lighten_color(info['color']),
                    font=("Arial", 12, "bold"),
                    command=lambda i=idx: self.select_tile(i)
                )
                btn.grid(row=row, column=col, padx=5, pady=5)
                self.tile_buttons.append(btn)
        
        # Encoder
        enc_frame = ctk.CTkFrame(left_frame)
        enc_frame.pack(pady=10)
        ctk.CTkLabel(enc_frame, text="ENCODER (Drehknopf)", font=("Arial", 12, "bold")).pack()
        enc_btn_frame = ctk.CTkFrame(enc_frame)
        enc_btn_frame.pack()
        for i, label in enumerate(["ENC <<", "ENC >>", "ENC PRESS"]):
            b = ctk.CTkButton(enc_btn_frame, text=label, width=108, height=50, fg_color="#555", command=lambda i=i+20: self.select_tile(i))
            b.pack(side="left", padx=5, pady=5)
        
        # Right: Config Panel
        right_frame = ctk.CTkFrame(main_frame, width=300)
        right_frame.pack(side="right", fill="y", padx=5, pady=5)
        right_frame.pack_propagate(False)
        
        ctk.CTkLabel(right_frame, text="KONFIGURATION", font=("Arial", 16, "bold")).pack(pady=10)
        
        # Physische Taste
        key_frame = ctk.CTkFrame(right_frame)
        key_frame.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(key_frame, text="PHYSISCHE TASTE", font=("Arial", 12, "bold")).pack()
        self.key_label = ctk.CTkLabel(key_frame, text="F13", font=("Arial", 24, "bold"), text_color="orange")
        self.key_label.pack(pady=5)
        
        self.assign_btn = ctk.CTkButton(
            key_frame,
            text="🎹 Taste drücken zum Belegen",
            fg_color="#FF8C00",
            hover_color="#FF6B00",
            font=("Arial", 12, "bold"),
            command=self.start_assign
        )
        self.assign_btn.pack(pady=10, padx=10, fill="x")
        
        # Aktion
        action_frame = ctk.CTkFrame(right_frame)
        action_frame.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(action_frame, text="AKTION", font=("Arial", 12, "bold")).pack()
        
        self.action_var = ctk.StringVar(value="YT Leiser -5%")
        self.action_menu = ctk.CTkOptionMenu(action_frame, values=list(ACTIONS.keys()), variable=self.action_var, command=self.action_changed)
        self.action_menu.pack(pady=5, fill="x", padx=10)
        
        self.param_entry = ctk.CTkEntry(action_frame, placeholder_text="Parameter (z.B. URL)")
        self.param_entry.pack(pady=5, fill="x", padx=10)
        
        # Buttons
        btn_frame = ctk.CTkFrame(right_frame)
        btn_frame.pack(fill="x", padx=10, pady=10)
        ctk.CTkButton(btn_frame, text="💾 Speichern", command=self.save_config).pack(fill="x", pady=2)
        ctk.CTkButton(btn_frame, text="🧪 Test Aktion", fg_color="#555", command=self.test_action).pack(fill="x", pady=2)
        ctk.CTkButton(btn_frame, text="🔽 Minimieren in Tray", fg_color="#444", command=self.minimize_to_tray).pack(fill="x", pady=10)
        
        # Log
        self.log_text = ctk.CTkTextbox(right_frame, height=150)
        self.log_text.pack(fill="both", expand=True, padx=10, pady=10)
        self.log("🚀 Metadeck v1.3.3 gestartet - Entprellt + Tray!")
        self.log("💡 X drücken minimiert in Tray (wie Discord)")
        
    def lighten_color(self, hex_color):
        # Simple lighten
        return hex_color
    
    def select_tile(self, idx):
        self.selected_tile = idx
        cfg = self.config_data.get(str(idx), {})
        self.action_var.set(cfg.get("action", "YT Leiser -5%"))
        self.param_entry.delete(0, "end")
        self.param_entry.insert(0, cfg.get("param", ""))
        self.key_label.configure(text=cfg.get("key", f"F{13+(idx%12)}"))
        self.log(f"📍 Tile {idx+1} ausgewählt")
        # Highlight
        for i, btn in enumerate(self.tile_buttons):
            if i == idx:
                btn.configure(border_width=3, border_color="white")
            else:
                btn.configure(border_width=0)
    
    def start_assign(self):
        self.waiting_for_key = True
        self.assign_btn.configure(text="⏳ Drücke Taste am Deck...", fg_color="red")
        self.log("⏳ Warte auf Tastendruck am MEGA32U4 Deck...")
    
    def start_key_listener(self):
        def listener():
            while True:
                if self.waiting_for_key:
                    # Warte auf F13-F24
                    for i in range(13, 25):
                        if keyboard.is_pressed(f'F{i}'):
                            self.after(0, lambda k=i: self.key_detected(k))
                            time.sleep(0.5)
                time.sleep(0.05)
        threading.Thread(target=listener, daemon=True).start()
    
    def key_detected(self, f_key):
        if not self.waiting_for_key:
            return
        self.waiting_for_key = False
        key_name = f"F{f_key}"
        self.key_label.configure(text=key_name)
        self.assign_btn.configure(text="🎹 Taste drücken zum Belegen", fg_color="#FF8C00")
        # Speichern
        cfg = self.config_data.get(str(self.selected_tile), {})
        cfg["key"] = key_name
        self.config_data[str(self.selected_tile)] = cfg
        self.save_config()
        self.log(f"✅ {key_name} erkannt! Für Tile {self.selected_tile+1} gespeichert!")
        # Entprellung: kurz warten
        time.sleep(0.3)
    
    def action_changed(self, value):
        cfg = self.config_data.get(str(self.selected_tile), {})
        cfg["action"] = value
        self.config_data[str(self.selected_tile)] = cfg
        # Farbe updaten
        if self.selected_tile < len(self.tile_buttons):
            info = ACTIONS.get(value, ACTIONS["YT Leiser -5%"])
            self.tile_buttons[self.selected_tile].configure(fg_color=info['color'], text=f"{info['icon']}\n{self.selected_tile+1}")
    
    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def save_config(self):
        # Action + param speichern
        cfg = self.config_data.get(str(self.selected_tile), {})
        cfg["action"] = self.action_var.get()
        cfg["param"] = self.param_entry.get()
        if "key" not in cfg:
            cfg["key"] = f"F{13+(self.selected_tile%12)}"
        self.config_data[str(self.selected_tile)] = cfg
        
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.config_data, f, indent=2)
        self.log("💾 Gespeichert!")
    
    def test_action(self):
        action = self.action_var.get()
        self.log(f"🧪 Teste: {action}")
        # Hier YouTube etc. Logik...
    
    def log(self, msg):
        self.log_text.insert("end", f"{msg}\n")
        self.log_text.see("end")
    
    def check_for_updates(self):
        pass
    
    # === TRAY FUNKTIONEN - DAS FEHLTE! ===
    def minimize_to_tray(self):
        """X gedrückt -> In Tray minimieren statt schließen"""
        self.withdraw()
        
        if not TRAY_AVAILABLE:
            self.log("⚠️ pystray nicht installiert - minimiert nur")
            return
            
        if not self.tray_running:
            self.tray_running = True
            try:
                icon_path = "assets/MetaStreamdeck.ico"
                if not os.path.exists(icon_path):
                    icon_path = os.path.join(os.path.dirname(__file__), "..", "assets", "MetaStreamdeck.ico")
                if os.path.exists(icon_path):
                    image = Image.open(icon_path)
                else:
                    image = Image.new('RGB', (64, 64), color=(0, 120, 212))
            except Exception as e:
                print(f"Icon error: {e}")
                image = Image.new('RGB', (64, 64), color=(0, 120, 212))
            
            menu = pystray.Menu(
                pystray.MenuItem("🎛️ Metadeck öffnen", self.show_from_tray),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("❌ Beenden", self.quit_from_tray)
            )
            
            self.tray_icon = pystray.Icon("Metadeck", image, f"Metadeck v{CURRENT_VERSION}", menu)
            
            def run_tray():
                self.tray_icon.run()
            
            threading.Thread(target=run_tray, daemon=True).start()
            self.log("✅ Läuft im Hintergrund (Tray) - Rechtsklick für Menü")
    
    def show_from_tray(self, icon=None, item=None):
        self.after(0, self.deiconify)
        self.after(0, self.lift)
        self.after(0, self.focus_force)
    
    def quit_from_tray(self, icon=None, item=None):
        if self.tray_icon:
            self.tray_icon.stop()
        self.tray_running = False
        self.after(0, self.destroy)
        os._exit(0)

if __name__ == "__main__":
    app = MetadeckApp()
    app.mainloop()
