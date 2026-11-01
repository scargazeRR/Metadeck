
import json, os, sys, time, threading, tempfile, subprocess
from pathlib import Path
import customtkinter as ctk
from pynput import keyboard as pynput_keyboard

try:
    from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume
    HAS_PYCAW = True
except: HAS_PYCAW = False
try:
    import keyboard as kb_lib
    HAS_KB_LIB = True
except: HAS_KB_LIB = False
try:
    import requests
    from packaging import version as pkg_version
    HAS_UPDATER = True
except: HAS_UPDATER = False

CURRENT_VERSION = "1.3.0"
UPDATE_JSON_URL = "https://raw.githubusercontent.com/scargazeRR/MetaStreamdeck/main/version.json"
CONFIG_FILE = Path(sys.executable).parent / "config.json" if getattr(sys, 'frozen', False) else Path(__file__).parent / "config.json"

ACTIONS = {
    "none": ("Keine Aktion", "⚪"),
    "yt_vol_down": ("YT Leiser", "🔉"),
    "yt_vol_up": ("YT Lauter", "🔊"),
    "yt_vol_mute": ("YT Mute", "🔇"),
    "yt_play_pause": ("YT Play/Pause", "⏯️"),
    "yt_next": ("YT Nächstes", "⏭️"),
    "yt_prev": ("YT Vorheriges", "⏮️"),
    "yt_fullscreen": ("YT Fullscreen", "⛶"),
    "sys_vol_down": ("Sys Leiser", "🔉"),
    "sys_vol_up": ("Sys Lauter", "🔊"),
    "sys_mute": ("Sys Mute", "🔇"),
    "media_play_pause": ("Media Play", "▶️"),
    "media_next": ("Media Next", "⏭️"),
    "media_prev": ("Media Prev", "⏮️"),
    "custom_key": ("Custom Taste", "⌨️"),
    "custom_text": ("Custom Text", "📝"),
    "open_url": ("URL Öffnen", "🌐"),
}

COLORS = {
    "none": "#2b2b2b",
    "yt": "#dc2626",
    "sys": "#2563eb",
    "media": "#7c3aed",
    "custom": "#059669",
    "encoder_ccw": "#1e40af",
    "encoder_cw": "#1e40af",
    "encoder_press": "#be185d",
}

def get_action_color(a):
    if a.startswith("yt_"): return COLORS["yt"]
    if a.startswith("sys_"): return COLORS["sys"]
    if a.startswith("media_"): return COLORS["media"]
    if a.startswith("custom") or a.startswith("open_"): return COLORS["custom"]
    return COLORS["none"]
def get_icon(a): return ACTIONS.get(a, ("","⚪"))[1]
def get_name(a): return ACTIONS.get(a, (a,""))[0]

KEYS = [f"F{i}" for i in range(13,25)]

class ActionExecutor:
    def __init__(self): self.ctrl = pynput_keyboard.Controller()
    def find_browser_sessions(self):
        if not HAS_PYCAW: return []
        sessions = AudioUtilities.GetAllSessions()
        browser_names = ["chrome.exe", "msedge.exe", "firefox.exe", "opera.exe", "brave.exe"]
        return [s for s in sessions if s.Process and any(b in s.Process.name().lower() for b in browser_names)]
    def change_browser_volume(self, delta_percent=0, mute_toggle=False):
        if not HAS_PYCAW: return
        for session in self.find_browser_sessions():
            vol = session._ctl.QueryInterface(ISimpleAudioVolume)
            curr = vol.GetMasterVolume()
            if mute_toggle: vol.SetMute(not vol.GetMute(), None)
            else: vol.SetMasterVolume(max(0.0, min(1.0, curr + delta_percent)), None)
            break
    def execute(self, action_id, param=""):
        try:
            if action_id == "yt_vol_down": self.change_browser_volume(delta_percent=-0.05)
            elif action_id == "yt_vol_up": self.change_browser_volume(delta_percent=0.05)
            elif action_id == "yt_vol_mute": self.change_browser_volume(mute_toggle=True)
            elif action_id in ("yt_play_pause", "media_play_pause"):
                if HAS_KB_LIB: kb_lib.send("play/pause media")
                else: self.ctrl.press(pynput_keyboard.Key.media_play_pause); self.ctrl.release(pynput_keyboard.Key.media_play_pause)
            elif action_id == "yt_next" and HAS_KB_LIB: kb_lib.send("shift+n")
            elif action_id == "yt_prev" and HAS_KB_LIB: kb_lib.send("shift+p")
            elif action_id == "yt_fullscreen" and HAS_KB_LIB: kb_lib.send("f")
            elif action_id == "sys_vol_down" and HAS_KB_LIB: kb_lib.send("volume down")
            elif action_id == "sys_vol_up" and HAS_KB_LIB: kb_lib.send("volume up")
            elif action_id == "sys_mute" and HAS_KB_LIB: kb_lib.send("volume mute")
            elif action_id == "media_next" and HAS_KB_LIB: kb_lib.send("next track")
            elif action_id == "media_prev" and HAS_KB_LIB: kb_lib.send("previous track")
            elif action_id == "custom_key" and param and HAS_KB_LIB: kb_lib.send(param)
            elif action_id == "custom_text" and param and HAS_KB_LIB: kb_lib.write(param)
            elif action_id == "open_url" and param:
                import webbrowser; webbrowser.open(param)
        except Exception as e: print(e)

executor = ActionExecutor()

def load_config():
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f: return json.load(f)
        except: pass
    config = {}
    for idx in range(20):
        phys = f"F{14+idx}" if idx < 10 else f"F{14+idx-10}"
        config[str(idx)] = {"phys_key": phys, "action": "none", "param": "", "label": f"Btn {idx+1}", "color": COLORS["none"]}
    config["encoder_ccw"] = {"phys_key": "F20", "action": "yt_vol_down", "param": "", "label": "ENC <<", "color": COLORS["encoder_ccw"]}
    config["encoder_cw"] = {"phys_key": "F21", "action": "yt_vol_up", "param": "", "label": "ENC >>", "color": COLORS["encoder_cw"]}
    config["encoder_press"] = {"phys_key": "F22", "action": "yt_play_pause", "param": "", "label": "ENC PRESS", "color": COLORS["encoder_press"]}
    return config

def save_config(cfg):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f: json.dump(cfg, f, indent=2, ensure_ascii=False)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class Updater:
    def __init__(self, app): self.app = app; self.info = None
    def check(self, silent=False):
        if not HAS_UPDATER: return
        def run():
            try:
                if not silent: self.app.set_status("Suche Updates...")
                r = requests.get(UPDATE_JSON_URL, timeout=5)
                if r.status_code != 200: return
                data = r.json()
                remote = data.get("version","0.0.0")
                self.info = data
                if pkg_version.parse(remote) > pkg_version.parse(CURRENT_VERSION):
                    self.app.after(0, lambda: self.app.show_update_dialog(data))
                else:
                    self.app.after(0, lambda: self.app.set_status(f"Bereit - v{CURRENT_VERSION} | MEGA32U4 Ready"))
            except: pass
        threading.Thread(target=run, daemon=True).start()
    def download_and_install(self, info):
        def run():
            try:
                url = info.get("url")
                r = requests.get(url, stream=True, timeout=30)
                tmp = tempfile.gettempdir()
                new_path = os.path.join(tmp, "MetaStreamdeck_new.exe")
                with open(new_path, 'wb') as f:
                    for chunk in r.iter_content(8192):
                        if chunk: f.write(chunk)
                current = sys.executable if getattr(sys, 'frozen', False) else __file__
                if not getattr(sys, 'frozen', False): return
                bat = os.path.join(tmp, "updater.bat")
                bat_c = f'@echo off\ntimeout /t 2 /nobreak >nul\nmove /Y "{new_path}" "{current}"\nstart "" "{current}"\ndel "%~f0"\n'
                open(bat,'w').write(bat_c)
                subprocess.Popen([bat], shell=True, creationflags=subprocess.DETACHED_PROCESS)
                self.app.after(0, lambda: self.app.destroy())
            except Exception as e: self.app.after(0, lambda: self.app.set_status(f"Fehler: {e}"))
        threading.Thread(target=run, daemon=True).start()

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(f"MetaStreamdeck v{CURRENT_VERSION} - Beautiful Edition")
        self.geometry("1440x880")
        try: self.iconbitmap("MetaStreamdeck.ico")
        except: pass
        self.config_data = load_config()
        self.selected_slot = "0"
        self.hotkey_map = {}
        self.updater = Updater(self)
        self.is_listening = False
        self.manual_visible = False
        self.create_ui()
        self.start_hotkey_listener()
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.after(2500, lambda: self.updater.check(silent=True))

    def create_ui(self):
        main_frame = ctk.CTkFrame(self, fg_color="#0a0a0a")
        main_frame.pack(fill="both", expand=True, padx=5, pady=5)
        left = ctk.CTkFrame(main_frame, fg_color="#111111", corner_radius=12)
        left.pack(side="left", fill="both", expand=True, padx=8, pady=8)
        header = ctk.CTkFrame(left, fg_color="#1a1a1a", corner_radius=10, height=60)
        header.pack(fill="x", padx=10, pady=10)
        header.pack_propagate(False)
        ctk.CTkLabel(header, text=f"🎛️ MetaStreamdeck v{CURRENT_VERSION}", font=("Segoe UI", 20, "bold")).pack(side="left", padx=15, pady=10)
        ctk.CTkLabel(header, text="MEGA32U4 • Beautiful Design • Press to Assign", font=("Segoe UI", 12), text_color="#888888").pack(side="left", padx=10)
        grid_bg = ctk.CTkFrame(left, fg_color="#151515", corner_radius=12)
        grid_bg.pack(padx=10, pady=10, fill="x")
        ctk.CTkLabel(grid_bg, text="10×2 GRID", font=("Segoe UI", 11, "bold"), text_color="#666666").pack(anchor="w", padx=12, pady=(8,2))
        grid_frame = ctk.CTkFrame(grid_bg, fg_color="transparent")
        grid_frame.pack(padx=8, pady=8)
        self.buttons = {}
        for row in range(2):
            row_frame = ctk.CTkFrame(grid_frame, fg_color="transparent")
            row_frame.pack(pady=3)
            for col in range(10):
                idx = row*10+col
                sid = str(idx)
                cfg = self.config_data.get(sid, {})
                action_id = cfg.get('action','none')
                icon = get_icon(action_id)
                color = cfg.get("color", get_action_color(action_id))
                btn = ctk.CTkButton(row_frame, text=f"{icon}\n{cfg.get('label','')}\n{cfg.get('phys_key','')}\n{get_name(action_id)[:12]}", width=108, height=108, fg_color=color, hover_color=color, corner_radius=16, font=("Segoe UI", 10, "bold"), text_color="white", border_width=0, command=lambda s=sid: self.select_slot(s))
                btn.pack(side="left", padx=4, pady=4)
                self.buttons[sid]=btn
        enc_bg = ctk.CTkFrame(left, fg_color="#151515", corner_radius=12)
        enc_bg.pack(padx=10, pady=8, fill="x")
        ctk.CTkLabel(enc_bg, text="ENCODER", font=("Segoe UI", 11, "bold"), text_color="#666666").pack(anchor="w", padx=12, pady=(8,2))
        enc_frame = ctk.CTkFrame(enc_bg, fg_color="transparent")
        enc_frame.pack(padx=10, pady=8, fill="x")
        for eid, icon in [("encoder_ccw","◀"),("encoder_cw","▶"),("encoder_press","●")]:
            cfg = self.config_data.get(eid,{})
            btn = ctk.CTkButton(enc_frame, text=f"{icon}\n{cfg.get('label')}\n{cfg.get('phys_key')}", width=130, height=70, fg_color=cfg.get("color", COLORS["encoder_ccw"]), corner_radius=16, font=("Segoe UI", 11, "bold"), command=lambda s=eid: self.select_slot(s))
            btn.pack(side="left", padx=6)
            self.buttons[eid]=btn
        log_frame = ctk.CTkFrame(left, fg_color="#151515", corner_radius=12)
        log_frame.pack(fill="x", padx=10, pady=8)
        self.log_label = ctk.CTkLabel(log_frame, text="Bereit - Drücke F14-F24 oder MEGA32U4 Tasten 🎹", font=("Segoe UI", 11), text_color="#cccccc")
        self.log_label.pack(padx=10, pady=5, anchor="w")
        self.vol_bar = ctk.CTkProgressBar(log_frame, width=600, height=10, corner_radius=5, progress_color="#dc2626")
        self.vol_bar.set(0.5)
        self.vol_bar.pack(pady=5, padx=10)
        self.yt_status = ctk.CTkLabel(log_frame, text="▶️ YouTube: Pausiert | Volume 50%", font=("Segoe UI", 11, "bold"))
        self.yt_status.pack(pady=2)
        right = ctk.CTkFrame(main_frame, width=380, fg_color="#111111", corner_radius=12)
        right.pack(side="right", fill="y", padx=8, pady=8)
        right.pack_propagate(False)
        right_header = ctk.CTkFrame(right, fg_color="#1a1a1a", corner_radius=10, height=50)
        right_header.pack(fill="x", padx=10, pady=10)
        right_header.pack_propagate(False)
        ctk.CTkLabel(right_header, text="Konfiguration", font=("Segoe UI", 16, "bold")).pack(pady=10)
        self.label_slot = ctk.CTkLabel(right, text="Slot: 0", font=("Segoe UI", 14, "bold"), text_color="#ff6f00")
        self.label_slot.pack(pady=5)
        self.entry_label = ctk.CTkEntry(right, placeholder_text="Button Label", height=36, corner_radius=10, font=("Segoe UI", 12))
        self.entry_label.pack(pady=6, padx=15, fill="x")
        ctk.CTkLabel(right, text="PHYSISCHE TASTE", font=("Segoe UI", 11, "bold"), text_color="#666666").pack(pady=(15,5))
        self.phys_key_display = ctk.CTkLabel(right, text="F14", font=("Segoe UI", 28, "bold"), fg_color="#1f1f1f", corner_radius=12, width=340, height=70, text_color="#ff6f00")
        self.phys_key_display.pack(pady=5, padx=15)
        self.btn_listen = ctk.CTkButton(right, text="🎹 Taste drücken zum Belegen", fg_color="#ff6f00", hover_color="#ff3d00", height=48, corner_radius=12, font=("Segoe UI", 14, "bold"), command=self.start_listen_mode)
        self.btn_listen.pack(pady=8, padx=15, fill="x")
        self.btn_manual = ctk.CTkButton(right, text="manuell wählen ▼", fg_color="transparent", text_color="#666666", height=24, font=("Segoe UI", 11), command=self.toggle_manual_select)
        self.btn_manual.pack()
        self.combo_phys = ctk.CTkComboBox(right, values=KEYS, width=340, height=36, corner_radius=10)
        ctk.CTkLabel(right, text="AKTION", font=("Segoe UI", 11, "bold"), text_color="#666666").pack(pady=(15,5))
        self.combo_action = ctk.CTkComboBox(right, values=list(ACTIONS.keys()), width=340, height=36, corner_radius=10, command=self.on_action_change)
        self.combo_action.pack(pady=6, padx=15)
        self.action_display = ctk.CTkLabel(right, text="", font=("Segoe UI", 12), wraplength=320, text_color="#cccccc")
        self.action_display.pack(pady=5)
        self.entry_param = ctk.CTkEntry(right, placeholder_text="Parameter", height=36, corner_radius=10)
        self.entry_param.pack(pady=6, padx=15, fill="x")
        self.color_entry = ctk.CTkEntry(right, placeholder_text="Farbe #RRGGBB", height=36, corner_radius=10)
        self.color_entry.pack(pady=6, padx=15, fill="x")
        ctk.CTkButton(right, text="💾 Speichern", height=44, corner_radius=12, font=("Segoe UI", 14, "bold"), fg_color="#2563eb", command=self.save_slot).pack(pady=12, padx=15, fill="x")
        ctk.CTkButton(right, text="🧪 Test Aktion", height=36, corner_radius=10, fg_color="#059669", command=self.test_action).pack(pady=2, padx=15, fill="x")
        self.progress = ctk.CTkProgressBar(right, width=340, height=6, corner_radius=3)
        self.progress.set(0)
        self.progress.pack(pady=8, padx=15)
        self.status = ctk.CTkLabel(right, text="🟢 Listener aktiv - MEGA32U4 Ready", text_color="#22c55e", font=("Segoe UI", 11), wraplength=340)
        self.status.pack(side="bottom", pady=15)
        self.select_slot("0")

    def toggle_manual_select(self):
        if self.manual_visible:
            self.combo_phys.pack_forget()
            self.btn_manual.configure(text="manuell wählen ▼")
            self.manual_visible=False
        else:
            self.combo_phys.pack(pady=6, padx=15)
            self.btn_manual.configure(text="manuell wählen ▲")
            self.manual_visible=True
    def start_listen_mode(self):
        self.is_listening=True
        self.phys_key_display.configure(text="...")
        self.btn_listen.configure(text="⏳ Drücke Taste am Deck...", fg_color="#d32f2f")
        self.set_status("🎹 Warte auf Tastendruck...")
        self.after(10000, self.cancel_listen_mode)
    def cancel_listen_mode(self):
        if self.is_listening:
            self.is_listening=False
            self.btn_listen.configure(text="🎹 Taste drücken zum Belegen", fg_color="#ff6f00")
            cfg=self.config_data.get(self.selected_slot,{})
            self.phys_key_display.configure(text=cfg.get("phys_key","F14"))
    def on_key_detected(self, key_name):
        if not self.is_listening: return
        self.is_listening=False
        key_name=key_name.lower()
        for i in range(13,25):
            if f"f{i}" in key_name: key_name=f"F{i}"; break
        self.phys_key_display.configure(text=key_name.upper())
        self.combo_phys.set(key_name)
        self.btn_listen.configure(text="✅ Erkannt! Speichere...", fg_color="#22c55e")
        self.set_status(f"✅ {key_name.upper()} erkannt!")
        self.after(700, lambda: [self.save_slot(), self.btn_listen.configure(text="🎹 Taste drücken zum Belegen", fg_color="#ff6f00")])
    def select_slot(self, sid):
        self.selected_slot=sid
        cfg=self.config_data.get(sid,{})
        self.label_slot.configure(text=f"Slot: {sid} - {cfg.get('label','')}")
        self.entry_label.delete(0,"end"); self.entry_label.insert(0,cfg.get("label",""))
        self.phys_key_display.configure(text=cfg.get("phys_key","F14"))
        self.combo_phys.set(cfg.get("phys_key","F14"))
        self.combo_action.set(cfg.get("action","none"))
        self.entry_param.delete(0,"end"); self.entry_param.insert(0,cfg.get("param",""))
        self.color_entry.delete(0,"end"); self.color_entry.insert(0,cfg.get("color",""))
        self.on_action_change(cfg.get("action","none"))
        for _sid,btn in self.buttons.items():
            if _sid==sid: btn.configure(border_width=3, border_color="white")
            else: btn.configure(border_width=0)
    def on_action_change(self, k): self.action_display.configure(text=f"{get_icon(k)} {get_name(k)}")
    def save_slot(self):
        sid=self.selected_slot
        color=self.color_entry.get() or get_action_color(self.combo_action.get())
        self.config_data[sid]={"label": self.entry_label.get() or f"Btn {sid}", "phys_key": self.combo_phys.get(), "action": self.combo_action.get(), "param": self.entry_param.get(), "color": color}
        save_config(self.config_data)
        cfg=self.config_data[sid]
        if sid in self.buttons:
            self.buttons[sid].configure(text=f"{get_icon(cfg.get('action','none'))}\n{cfg.get('label','')}\n{cfg.get('phys_key','')}\n{get_name(cfg.get('action','none'))[:12]}", fg_color=cfg.get("color", COLORS["none"]))
        self.rebuild_hotkeys()
        self.set_status(f"💾 Gespeichert: {sid}")
    def test_action(self):
        act=self.combo_action.get(); param=self.entry_param.get()
        executor.execute(act,param)
        self.log(f"🧪 TEST: {act}")
    def rebuild_hotkeys(self):
        self.hotkey_map={}
        for sid,cfg in self.config_data.items():
            pk=cfg.get("phys_key","").lower()
            self.hotkey_map[pk]=(cfg.get("action"),cfg.get("param"))
    def start_hotkey_listener(self):
        self.rebuild_hotkeys()
        if HAS_KB_LIB:
            def cb(event):
                kname=event.name.lower()
                if self.is_listening:
                    self.after(0, lambda: self.on_key_detected(kname))
                    return
                if kname in self.hotkey_map:
                    act,param=self.hotkey_map[kname]
                    if act and act!="none":
                        executor.execute(act,param)
                        self.after(0, lambda: self.log(f"✅ {kname.upper()} -> {act}"))
            try: kb_lib.hook(cb)
            except: pass
    def log(self, msg): self.log_label.configure(text=msg)
    def set_status(self, txt): self.status.configure(text=txt)
    def update_progress(self, pct): self.progress.set(pct/100)
    def show_update_dialog(self, info):
        dialog=ctk.CTkToplevel(self)
        dialog.title("Update verfügbar!"); dialog.geometry("480x350"); dialog.transient(self); dialog.grab_set()
        ctk.CTkLabel(dialog, text="🚀 Update verfügbar!", font=("Segoe UI", 20, "bold")).pack(pady=15)
        ctk.CTkLabel(dialog, text=f"Aktuell: v{CURRENT_VERSION} -> Neu: v{info.get('version')}", font=("Segoe UI", 14)).pack()
        ctk.CTkLabel(dialog, text=f"Changelog:\n{info.get('changelog','')}", wraplength=400, justify="left").pack(pady=10, padx=20)
        ctk.CTkButton(dialog, text=f"Jetzt updaten", fg_color="#22c55e", height=44, corner_radius=12, command=lambda: [dialog.destroy(), self.updater.download_and_install(info)]).pack(pady=10, padx=20, fill="x")
        ctk.CTkButton(dialog, text="Später", fg_color="#1a1a1a", command=dialog.destroy).pack(padx=20, fill="x")
    def on_close(self): save_config(self.config_data); self.destroy()

if __name__ == "__main__":
    app=App()
    app.mainloop()
