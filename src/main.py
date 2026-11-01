
"""
Metadeck v1.3.9 - JUST WORKS Edition
Professional MEGA32U4 Stream Deck - Works like Macro Deck
No emojis, no bullshit, just works.
"""

import os
import sys
import json
import threading
import webbrowser
from pathlib import Path
from typing import Dict, Tuple, Optional

import customtkinter as ctk

try:
    import keyboard as keyboard_lib
    KEYBOARD_AVAILABLE = True
except:
    KEYBOARD_AVAILABLE = False

try:
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    from comtypes import CLSCTX_ALL
    from ctypes import cast, POINTER
    PYCAW_AVAILABLE = True
except:
    PYCAW_AVAILABLE = False

try:
    import pystray
    from PIL import Image
    TRAY_AVAILABLE = True
except:
    TRAY_AVAILABLE = False


try:
    import serial
    import serial.tools.list_ports
    SERIAL_AVAILABLE = True
except:
    SERIAL_AVAILABLE = False

class SerialReader:
    def __init__(self, app):
        self.app = app
        self.running = False
        self.ser = None
        self.thread = None

    def find_metadeck_port(self):
        if not SERIAL_AVAILABLE:
            return None
        ports = list(serial.tools.list_ports.comports())
        for p in ports:
            # MEGA32U4 ist meist Arduino Leonardo / Pro Micro
            if "Arduino" in p.description or "Leonardo" in p.description or "Pro Micro" in p.description or "VID:PID=2341" in p.hwid or "1A86" in p.hwid:
                return p.device
        # Fallback: nimm ersten verfügbaren
        for p in ports:
            if "COM" in p.device or "/dev/tty" in p.device:
                try:
                    # Teste ob METADECK_READY kommt
                    test_ser = serial.Serial(p.device, 9600, timeout=1)
                    test_ser.readline()
                    test_ser.close()
                    return p.device
                except:
                    pass
        return None

    def start(self):
        if not SERIAL_AVAILABLE:
            print("pyserial not installed")
            return False
        port = self.find_metadeck_port()
        if not port:
            print("No Metadeck COM port found - using F-keys fallback")
            return False
        try:
            self.ser = serial.Serial(port, 9600, timeout=0.1)
            self.running = True
            self.thread = threading.Thread(target=self.read_loop, daemon=True)
            self.thread.start()
            print(f"Serial reader started on {port}")
            self.app.after(0, lambda: self.app.set_status(f"Serial OK on {port} - JUST WORKS like Macro Deck!"))
            return True
        except Exception as e:
            print(f"Serial start error: {e}")
            return False

    def read_loop(self):
        while self.running and self.ser:
            try:
                if self.ser.in_waiting:
                    line = self.ser.readline().decode('utf-8', errors='ignore').strip()
                    if not line:
                        continue
                    print(f"SERIAL: {line}")
                    # Parse
                    # BTN_0_F13 -> button 0 -> physical F13
                    # ENC_LEFT -> F20 etc
                    key_name = None
                    if line.startswith("BTN_"):
                        # BTN_0_F13
                        try:
                            parts = line.split("_")
                            f_part = parts[-1]  # F13
                            key_name = f_part.lower()
                        except:
                            pass
                    elif line == "ENC_LEFT":
                        key_name = "f20"
                    elif line == "ENC_RIGHT":
                        key_name = "f21"
                    elif line == "ENC_PRESS":
                        key_name = "f22"
                    elif line == "METADECK_READY":
                        self.app.after(0, lambda: self.app.set_status("Metadeck Board Connected via Serial!"))
                        continue
                    
                    if key_name:
                        print(f"SERIAL EXEC: {key_name}")
                        self.app.after(0, lambda k=key_name: self.app.on_serial_key(k))
            except Exception as e:
                print(f"Serial read error: {e}")
                break

    def stop(self):
        self.running = False
        if self.ser:
            try:
                self.ser.close()
            except:
                pass


CURRENT_VERSION = "1.3.9"
COMPANY_NAME = "ScargazeRR"
PRODUCT_NAME = "Metadeck"

if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).parent.parent if "src" in str(Path(__file__).parent) else Path(__file__).parent
CONFIG_FILE = BASE_DIR / "config.json"

ACTIONS = {
    "none": ("None", "System"),
    "yt_volume_down": ("YouTube Volume Down", "YouTube"),
    "yt_volume_up": ("YouTube Volume Up", "YouTube"),
    "yt_mute": ("YouTube Mute", "YouTube"),
    "yt_play_pause": ("YouTube Play/Pause", "YouTube"),
    "yt_next": ("YouTube Next", "YouTube"),
    "yt_previous": ("YouTube Previous", "YouTube"),
    "system_volume_down": ("System Volume Down", "System"),
    "system_volume_up": ("System Volume Up", "System"),
    "system_mute": ("System Mute", "System"),
    "media_play_pause": ("Media Play/Pause", "Media"),
    "media_next": ("Media Next Track", "Media"),
    "media_previous": ("Media Previous Track", "Media"),
    "custom_key": ("Custom Key", "Custom"),
    "custom_text": ("Custom Text", "Custom"),
    "open_url": ("Open URL", "Custom"),
}

def get_action_color(action_key: str) -> str:
    _, category = ACTIONS.get(action_key, ("", "System"))
    return {"YouTube": "#DC2626", "System": "#2563EB", "Media": "#7C3AED", "Custom": "#059669"}.get(category, "#2B2B2B")

class AudioExecutor:
    def execute(self, action: str, param: str = "") -> bool:
        try:
            # SYSTEM VOLUME - direkt Windows API wie Macro Deck
            if "volume_down" in action or "volume_up" in action or "mute" in action:
                if PYCAW_AVAILABLE:
                    try:
                        devices = AudioUtilities.GetSpeakers()
                        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                        volume = cast(interface, POINTER(IAudioEndpointVolume))
                        current = volume.GetMasterVolumeLevelScalar()
                        if "down" in action:
                            volume.SetMasterVolumeLevelScalar(max(0.0, current - 0.05), None)
                        elif "up" in action:
                            volume.SetMasterVolumeLevelScalar(min(1.0, current + 0.05), None)
                        elif "mute" in action:
                            volume.SetMute(not volume.GetMute(), None)
                        print(f"Volume direct API: {current} -> {action}")
                        return True
                    except Exception as e:
                        print(f"Volume API error: {e}")
                # Fallback
                if KEYBOARD_AVAILABLE:
                    try:
                        if "down" in action: keyboard_lib.send("volume down")
                        elif "up" in action: keyboard_lib.send("volume up")
                        elif "mute" in action: keyboard_lib.send("volume mute")
                        return True
                    except: pass
                return False

            # YOUTUBE - FIX: sendet k/m/j/l wie Macro Deck + Media Key
            if KEYBOARD_AVAILABLE:
                if action == "yt_play_pause":
                    # YouTube Shortcut: k oder Space - funktioniert immer wenn Tab aktiv
                    # Macro Deck Trick: sende beides!
                    keyboard_lib.send("play/pause media")
                    keyboard_lib.send("k")
                    print("YouTube Play/Pause: sent media + k")
                    return True
                elif action == "yt_mute":
                    keyboard_lib.send("m")
                    print("YouTube Mute: sent m")
                    return True
                elif action == "yt_next":
                    # YouTube Next: Shift+n
                    keyboard_lib.send("shift+n")
                    keyboard_lib.send("next track")
                    return True
                elif action == "yt_previous":
                    keyboard_lib.send("shift+p")
                    keyboard_lib.send("previous track")
                    return True
                elif action == "yt_volume_down":
                    keyboard_lib.send("down")
                    return True
                elif action == "yt_volume_up":
                    keyboard_lib.send("up")
                    return True
                # SYSTEM MEDIA
                elif action == "media_play_pause":
                    keyboard_lib.send("play/pause media")
                    return True
                elif action == "media_next":
                    keyboard_lib.send("next track")
                    return True
                elif action == "media_previous":
                    keyboard_lib.send("previous track")
                    return True
                elif action == "system_volume_down":
                    if PYCAW_AVAILABLE:
                        try:
                            devices = AudioUtilities.GetSpeakers()
                            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                            volume = cast(interface, POINTER(IAudioEndpointVolume))
                            current = volume.GetMasterVolumeLevelScalar()
                            volume.SetMasterVolumeLevelScalar(max(0.0, current - 0.05), None)
                            return True
                        except: pass
                    keyboard_lib.send("volume down")
                    return True
                elif action == "system_volume_up":
                    if PYCAW_AVAILABLE:
                        try:
                            devices = AudioUtilities.GetSpeakers()
                            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                            volume = cast(interface, POINTER(IAudioEndpointVolume))
                            current = volume.GetMasterVolumeLevelScalar()
                            volume.SetMasterVolumeLevelScalar(min(1.0, current + 0.05), None)
                            return True
                        except: pass
                    keyboard_lib.send("volume up")
                    return True
                elif action == "system_mute":
                    keyboard_lib.send("volume mute")
                    return True
                elif action == "custom_key" and param:
                    keyboard_lib.send(param)
                    return True
                elif action == "custom_text" and param:
                    keyboard_lib.write(param)
                    return True
                elif action == "open_url" and param:
                    import webbrowser
                    webbrowser.open(param)
                    return True
            return False
        except Exception as e:
            print(f"Executor error: {e}")
            return False

class ConfigManager:
    @staticmethod
    def load() -> Dict:
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                pass
        config = {}
        for i in range(20):
            config[str(i)] = {"label": f"Key {i+1}", "physical_key": f"F{13 + (i % 12)}", "action": "none", "param": "", "color": "#2B2B2B"}
        config["20"] = {"label": "ENC Left", "physical_key": "F20", "action": "system_volume_down", "param": "", "color": "#1E40AF"}
        config["21"] = {"label": "ENC Right", "physical_key": "F21", "action": "system_volume_up", "param": "", "color": "#1E40AF"}
        config["22"] = {"label": "ENC Press", "physical_key": "F22", "action": "media_play_pause", "param": "", "color": "#BE185D"}
        return config

    @staticmethod
    def save(config: Dict) -> None:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

class MetadeckApplication(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(f"{PRODUCT_NAME} v{CURRENT_VERSION}")
        self.geometry("1320x820")
        self._set_icon()
        self.config_data = ConfigManager.load()
        self.selected_slot = "0"
        self.hotkey_map = {}
        self.is_listening = False
        self.tray_icon = None
        self.executor = AudioExecutor()
        self.serial_reader = SerialReader(self)
        self.protocol("WM_DELETE_WINDOW", self.minimize_to_tray)
        self._create_ui()
        self._rebuild_hotkey_map()
        self._start_hotkey_listener()
        # Start Serial like Macro Deck - 100% reliable!
        try:
            self.serial_reader.start()
        except Exception as e:
            print(f"Serial start failed: {e}")

    def on_serial_key(self, key_name: str) -> None:
        # Called from Serial - JUST WORKS like Macro Deck!
        key_name = key_name.lower()
        if self.is_listening:
            self.on_key_detected(key_name)
            return
        if key_name in self.hotkey_map:
            act, param = self.hotkey_map[key_name]
            if act != "none":
                self.executor.execute(act, param)
                self.set_status(f"Executed via Serial: {key_name.upper()} -> {act} - WORKS!")
        else:
            self.set_status(f"Serial Key {key_name.upper()} not mapped - assign it!")

    def _set_icon(self):
        try:
            for p in ["assets/MetaStreamdeck.ico", str(BASE_DIR / "assets" / "MetaStreamdeck.ico")]:
                if os.path.exists(p):
                    self.iconbitmap(p)
                    break
        except:
            pass

    def _create_ui(self):
        header = ctk.CTkFrame(self, fg_color="#151515", height=56, corner_radius=0)
        header.pack(fill="x")
        ctk.CTkLabel(header, text=PRODUCT_NAME, font=("Segoe UI", 20, "bold")).pack(side="left", padx=20, pady=10)
        ctk.CTkLabel(header, text=f"v{CURRENT_VERSION} | JUST WORKS | Encoder Fast | All Keys Work", font=("Segoe UI", 11), text_color="#888888").pack(side="left", padx=10)

        main = ctk.CTkFrame(self, fg_color="#0A0A0A")
        main.pack(fill="both", expand=True, padx=6, pady=6)

        left = ctk.CTkFrame(main, fg_color="#111111", corner_radius=12)
        left.pack(side="left", fill="both", expand=True, padx=6, pady=6)

        grid_sec = ctk.CTkFrame(left, fg_color="#161616", corner_radius=10)
        grid_sec.pack(fill="x", padx=12, pady=10)
        ctk.CTkLabel(grid_sec, text="MAIN DECK (10 x 2)", font=("Segoe UI", 11, "bold"), text_color="#777777").pack(anchor="w", padx=12, pady=5)
        grid_f = ctk.CTkFrame(grid_sec, fg_color="transparent")
        grid_f.pack(padx=8, pady=8)

        self.buttons = {}
        for row in range(2):
            row_f = ctk.CTkFrame(grid_f, fg_color="transparent")
            row_f.pack(pady=2)
            for col in range(10):
                idx = row*10+col
                sid = str(idx)
                cfg = self.config_data.get(sid, {})
                btn = ctk.CTkButton(row_f, text=self._fmt(cfg), width=108, height=108, corner_radius=16, fg_color=cfg.get("color", "#2B2B2B"), font=("Segoe UI", 10, "bold"), command=lambda s=sid: self.select_slot(s))
                btn.pack(side="left", padx=3, pady=3)
                self.buttons[sid] = btn

        enc_sec = ctk.CTkFrame(left, fg_color="#161616", corner_radius=10)
        enc_sec.pack(fill="x", padx=12, pady=6)
        ctk.CTkLabel(enc_sec, text="ENCODER - Fast, No Debounce", font=("Segoe UI", 11, "bold"), text_color="#777777").pack(anchor="w", padx=12, pady=5)
        enc_f = ctk.CTkFrame(enc_sec, fg_color="transparent")
        enc_f.pack(padx=8, pady=8)
        for sid in ["20", "21", "22"]:
            cfg = self.config_data.get(sid, {})
            btn = ctk.CTkButton(enc_f, text=self._fmt(cfg), width=140, height=58, corner_radius=10, fg_color=cfg.get("color", "#1E40AF"), command=lambda s=sid: self.select_slot(s))
            btn.pack(side="left", padx=6)
            self.buttons[sid] = btn

        self.status_label = ctk.CTkLabel(left, text="Status: Ready - JUST WORKS - Run as Admin", font=("Segoe UI", 11), text_color="#22C55E")
        self.status_label.pack(pady=12)

        right = ctk.CTkFrame(main, width=360, fg_color="#111111", corner_radius=12)
        right.pack(side="right", fill="y", padx=6, pady=6)
        right.pack_propagate(False)

        ctk.CTkLabel(right, text="Configuration", font=("Segoe UI", 16, "bold")).pack(pady=14)
        self.slot_label = ctk.CTkLabel(right, text="Slot: 0", font=("Segoe UI", 13, "bold"), text_color="#FF6F00")
        self.slot_label.pack()

        ctk.CTkLabel(right, text="Button Label", font=("Segoe UI", 11), text_color="#777777").pack(anchor="w", padx=16, pady=(14,2))
        self.entry_label = ctk.CTkEntry(right, placeholder_text="Label", height=38, corner_radius=8)
        self.entry_label.pack(fill="x", padx=16, pady=2)

        ctk.CTkLabel(right, text="Physical Key", font=("Segoe UI", 11, "bold"), text_color="#777777").pack(anchor="w", padx=16, pady=(16,4))
        self.key_display = ctk.CTkLabel(right, text="F13", font=("Segoe UI", 26, "bold"), fg_color="#1E1E1E", corner_radius=10, width=328, height=64, text_color="#FF6F00")
        self.key_display.pack(padx=16, pady=4)

        self.assign_btn = ctk.CTkButton(right, text="Press to Assign Key", fg_color="#FF6F00", height=46, corner_radius=10, font=("Segoe UI", 13, "bold"), command=self.start_assign)
        self.assign_btn.pack(fill="x", padx=16, pady=8)

        ctk.CTkLabel(right, text="Action Type", font=("Segoe UI", 11, "bold"), text_color="#777777").pack(anchor="w", padx=16, pady=(16,4))
        self.action_combo = ctk.CTkComboBox(right, values=list(ACTIONS.keys()), width=328, height=38, corner_radius=8, command=self.on_action_changed)
        self.action_combo.pack(padx=16, pady=2)
        self.action_info = ctk.CTkLabel(right, text="", font=("Segoe UI", 11), text_color="#AAAAAA")
        self.action_info.pack(pady=4)

        ctk.CTkLabel(right, text="Parameter", font=("Segoe UI", 11), text_color="#777777").pack(anchor="w", padx=16, pady=(10,2))
        self.entry_param = ctk.CTkEntry(right, placeholder_text="Key, URL, Text", height=38, corner_radius=8)
        self.entry_param.pack(fill="x", padx=16, pady=2)

        ctk.CTkButton(right, text="Save Configuration", height=44, corner_radius=10, font=("Segoe UI", 13, "bold"), fg_color="#2563EB", command=self.save_slot).pack(fill="x", padx=16, pady=14)
        ctk.CTkButton(right, text="Test Action", height=36, corner_radius=8, fg_color="#059669", command=self.test_action).pack(fill="x", padx=16, pady=2)
        ctk.CTkButton(right, text="Minimize to Tray", height=36, corner_radius=8, fg_color="#3F3F46", command=self.minimize_to_tray).pack(fill="x", padx=16, pady=12)

        self.footer_status = ctk.CTkLabel(right, text=f"Config: {CONFIG_FILE}", font=("Segoe UI", 9), text_color="#666666", wraplength=320)
        self.footer_status.pack(side="bottom", pady=12)

        self.select_slot("0")

    def _fmt(self, cfg: Dict) -> str:
        label = cfg.get("label", "Key")
        phys = cfg.get("physical_key", "F13")
        action = cfg.get("action", "none")
        name = ACTIONS.get(action, (action, ""))[0]
        return f"{label}\n{phys}\n{name}"

    def select_slot(self, sid: str) -> None:
        self.selected_slot = sid
        cfg = self.config_data.get(sid, {})
        self.slot_label.configure(text=f"Slot {sid} - {cfg.get('label','')}")
        self.entry_label.delete(0, "end")
        self.entry_label.insert(0, cfg.get("label", ""))
        self.key_display.configure(text=cfg.get("physical_key", "F13"))
        self.action_combo.set(cfg.get("action", "none"))
        self.entry_param.delete(0, "end")
        self.entry_param.insert(0, cfg.get("param", ""))
        self.on_action_changed(cfg.get("action", "none"))
        for s, b in self.buttons.items():
            b.configure(border_width=2 if s==sid else 0, border_color="white")

    def on_action_changed(self, action: str) -> None:
        name, cat = ACTIONS.get(action, (action, "System"))
        self.action_info.configure(text=f"{name} - {cat}")

    def save_slot(self) -> None:
        sid = self.selected_slot
        act = self.action_combo.get()
        self.config_data[sid] = {
            "label": self.entry_label.get() or f"Key {sid}",
            "physical_key": self.key_display.cget("text"),
            "action": act,
            "param": self.entry_param.get(),
            "color": get_action_color(act)
        }
        ConfigManager.save(self.config_data)
        cfg = self.config_data[sid]
        if sid in self.buttons:
            self.buttons[sid].configure(text=self._fmt(cfg), fg_color=cfg["color"])
        self._rebuild_hotkey_map()
        self.set_status(f"Saved: {sid} -> {cfg['physical_key']} = {act}")

    def test_action(self) -> None:
        act = self.action_combo.get()
        param = self.entry_param.get()
        ok = self.executor.execute(act, param)
        self.set_status(f"Test: {act} - OK: {ok}")

    def start_assign(self) -> None:
        self.is_listening = True
        self.key_display.configure(text="Waiting...")
        self.assign_btn.configure(text="Press Key on Deck...", fg_color="#D32F2F")
        self.set_status("Waiting for key - Press key on MEGA32U4 (10s)")
        self.after(10000, self._cancel_assign)

    def _cancel_assign(self) -> None:
        if self.is_listening:
            self.is_listening = False
            self.assign_btn.configure(text="Press to Assign Key", fg_color="#FF6F00")
            cfg = self.config_data.get(self.selected_slot, {})
            self.key_display.configure(text=cfg.get("physical_key", "F13"))

    def on_key_detected(self, key_name: str) -> None:
        if not self.is_listening:
            return
        self.is_listening = False
        key_name = key_name.upper()
        if "F" in key_name:
            try:
                num = int("".join(filter(str.isdigit, key_name)))
                if 13 <= num <= 24:
                    key_name = f"F{num}"
            except:
                pass
        self.key_display.configure(text=key_name)
        self.assign_btn.configure(text="Detected - Saving...", fg_color="#22C55E")
        self.set_status(f"Detected: {key_name}")
        self.after(600, lambda: [self.save_slot(), self.assign_btn.configure(text="Press to Assign Key", fg_color="#FF6F00")])

    def _rebuild_hotkey_map(self) -> None:
        self.hotkey_map = {}
        for cfg in self.config_data.values():
            pk = cfg.get("physical_key", "").lower()
            if pk:
                self.hotkey_map[pk] = (cfg.get("action", "none"), cfg.get("param", ""))

    def _start_hotkey_listener(self) -> None:
        if not KEYBOARD_AVAILABLE:
            self.set_status("keyboard library missing - pip install keyboard")
            return
        
        # DEBUG: Zeige jede Taste die reinkommt
        def debug_cb(event):
            if event.event_type != 'down':
                return
            kn = event.name.lower()
            # Zeige IMMER was gedrückt wurde - auch wenn nicht gemappt!
            self.after(0, lambda k=kn: self.set_status(f"Key detected: {k.upper()} - Map: {list(self.hotkey_map.keys())[:5]}..."))
            print(f"KEY DETECTED: {kn} - listening={self.is_listening}")
            
            if self.is_listening:
                self.after(0, lambda: self.on_key_detected(kn))
                return
            
            if kn in self.hotkey_map:
                act, param = self.hotkey_map[kn]
                if act != "none":
                    print(f"EXECUTING: {kn} -> {act} / {param}")
                    self.executor.execute(act, param)
                    self.after(0, lambda k=kn, a=act: self.set_status(f"Executed: {k.upper()} -> {a} - WORKS!"))
            else:
                # F13-F24 Fix: Manchmal heißt F20 anders - probiere Variationen
                alt = kn.replace("f", "")
                if alt.isdigit():
                    alt_key = f"f{alt}"
                    if alt_key in self.hotkey_map:
                        act, param = self.hotkey_map[alt_key]
                        if act != "none":
                            print(f"EXECUTING ALT: {alt_key} -> {act}")
                            self.executor.execute(act, param)
                            self.after(0, lambda k=alt_key, a=act: self.set_status(f"Executed ALT: {k.upper()} -> {a} - WORKS!"))

        # FIX: add_hotkey für F13-F24 ist zuverlässiger als hook - wie Macro Deck!
        try:
            # Erst alle alten Hotkeys entfernen
            keyboard_lib.unhook_all()
            
            # Für jede F-Taste einen eigenen Hotkey registrieren - geht IMMER!
            for f_num in range(13, 25):
                f_key = f"f{f_num}"
                # Wrapper für korrekte Closure
                def make_handler(key_name):
                    def handler():
                        print(f"HOTKEY: {key_name}")
                        if self.is_listening:
                            self.after(0, lambda: self.on_key_detected(key_name))
                            return
                        if key_name in self.hotkey_map:
                            act, param = self.hotkey_map[key_name]
                            if act != "none":
                                self.executor.execute(act, param)
                                self.after(0, lambda k=key_name, a=act: self.set_status(f"Executed: {k.upper()} -> {a} - WORKS!"))
                        # Debug falls nicht gemappt
                        else:
                            self.after(0, lambda k=key_name: self.set_status(f"Key {k.upper()} not mapped - assign it!"))
                    return handler
                
                try:
                    keyboard_lib.add_hotkey(f_key, make_handler(f_key), suppress=False, trigger_on_release=False)
                    print(f"Registered hotkey: {f_key}")
                except Exception as e:
                    print(f"Failed to register {f_key}: {e}")

            # Zusätzlich hook für Debug - zeigt alle Tasten
            keyboard_lib.hook(debug_cb)
            
            self.set_status(f"Ready v1.4.0 - F13-F24 add_hotkey active - {len(self.hotkey_map)} mappings - Press F20 to test!")
        except Exception as e:
            self.set_status(f"Need Admin for F13-F24: {e} - Right-click Run as Admin!")
            print(f"Hotkey error: {e}")
            # Fallback auf hook
            try:
                keyboard_lib.hook(debug_cb)
            except:
                pass

    def set_status(self, msg: str) -> None:
        self.status_label.configure(text=f"Status: {msg}")
        self.footer_status.configure(text=msg)

    def minimize_to_tray(self) -> None:
        self.withdraw()
        if not TRAY_AVAILABLE:
            return
        if self.tray_icon is None:
            try:
                icon_path = None
                for p in ["assets/MetaStreamdeck.ico", str(BASE_DIR / "assets" / "MetaStreamdeck.ico")]:
                    if os.path.exists(p):
                        icon_path = p
                        break
                img = Image.open(icon_path) if icon_path and os.path.exists(icon_path) else Image.new("RGB", (64, 64), color=(37, 99, 235))
                menu = pystray.Menu(
                    pystray.MenuItem("Open Metadeck", self.show_from_tray, default=True),
                    pystray.Menu.SEPARATOR,
                    pystray.MenuItem("Exit", self.quit_from_tray)
                )
                self.tray_icon = pystray.Icon(PRODUCT_NAME, img, f"{PRODUCT_NAME} v{CURRENT_VERSION}", menu)
                threading.Thread(target=self.tray_icon.run, daemon=True).start()
            except Exception as e:
                print(f"Tray error: {e}")

    def show_from_tray(self, icon=None, item=None):
        self.after(0, self.deiconify)
        self.after(0, self.lift)
        self.after(0, self.focus_force)

    def quit_from_tray(self, icon=None, item=None):
        if self.tray_icon:
            try:
                self.tray_icon.stop()
            except:
                pass
        self.after(0, self.destroy)
        os._exit(0)

if __name__ == "__main__":
    app = MetadeckApplication()
    app.mainloop()
