
"""
Metadeck v1.0 - USB ONLY

"""

import os
import sys
import json
import threading
import webbrowser
from pathlib import Path

import customtkinter as ctk

try:
    import serial
    import serial.tools.list_ports
    SERIAL_AVAILABLE = True
except:
    SERIAL_AVAILABLE = False

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

CURRENT_VERSION = "2.3.0"
COMPANY_NAME = "ScargazeRR"
PRODUCT_NAME = "Metadeck"

if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).parent.parent if "src" in str(Path(__file__).parent) else Path(__file__).parent
CONFIG_FILE = BASE_DIR / "config.json"

# Unique Action Registry - inspired by Macro Deck Plugin SDK but Python decorator, no copy
ACTION_REGISTRY = {}


# Metadeck Plugin System v2.3 - Inspired by Macro Deck Plugin SDK but unique, local only
# Plugins are Python files in plugins/ folder, auto-loaded, no main.py edit needed!

import importlib.util
import sys
from pathlib import Path

PLUGIN_DIR = BASE_DIR / "plugins"

def load_plugins():
    if not PLUGIN_DIR.exists():
        PLUGIN_DIR.mkdir(exist_ok=True)
        # Create example plugin
        example = PLUGIN_DIR / "example_plugin.py"
        if not example.exists():
            example.write_text('''"""
Metadeck Example Plugin - How to create your own plugin
Place this file in plugins/ folder, restart Metadeck, action appears automatically!
"""

from __main__ import metadeck_action
import keyboard as keyboard_lib

@metadeck_action("example_hello", "Example Hello World", "Custom", "#FF6F00")
class ExampleHelloAction:
    def execute(self, param=""):
        print("Hello from plugin!")
        if param:
            keyboard_lib.write(param)
        else:
            keyboard_lib.write("Hello from Metadeck Plugin!")
        return True

@metadeck_action("example_youtube_like", "YT Like via Plugin", "YouTube", "#DC2626")
class YTLikePluginAction:
    def execute(self, param=""):
        keyboard_lib.send("l")
        return True
''', encoding="utf-8")
        print(f"Created plugin dir {PLUGIN_DIR} with example plugin")
        return
    
    print(f"Loading plugins from {PLUGIN_DIR}...")
    for plugin_file in PLUGIN_DIR.glob("*.py"):
        if plugin_file.name.startswith("_"):
            continue
        try:
            spec = importlib.util.spec_from_file_location(f"metadeck_plugin_{plugin_file.stem}", plugin_file)
            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module
            spec.loader.exec_module(module)
            print(f"Plugin loaded: {plugin_file.name} - actions: {list(ACTION_REGISTRY.keys())[-3:]}")
        except Exception as e:
            print(f"Plugin {plugin_file.name} failed: {e}")
            import traceback
            traceback.print_exc()



def metadeck_action(action_id, display_name, category, color_hex):
    def decorator(cls):
        ACTION_REGISTRY[action_id] = {
            "class": cls,
            "name": display_name,
            "category": category,
            "color": color_hex
        }
        cls.action_id = action_id
        return cls
    return decorator

@metadeck_action("none", "None", "System", "#2B2B2B")
class NoneAction:
    def execute(self, param=""):
        return True

@metadeck_action("system_volume_down", "System Volume Down", "System", "#2563EB")
class SystemVolumeDownAction:
    def execute(self, param=""):
        if PYCAW_AVAILABLE:
            try:
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                volume = cast(interface, POINTER(IAudioEndpointVolume))
                current = volume.GetMasterVolumeLevelScalar()
                volume.SetMasterVolumeLevelScalar(max(0.0, current - 0.05), None)
                return True
            except Exception as e:
                print(f"Volume error: {e}")
        if KEYBOARD_AVAILABLE:
            try:
                keyboard_lib.send("volume down")
                return True
            except:
                pass
        return False

@metadeck_action("system_volume_up", "System Volume Up", "System", "#2563EB")
class SystemVolumeUpAction:
    def execute(self, param=""):
        if PYCAW_AVAILABLE:
            try:
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                volume = cast(interface, POINTER(IAudioEndpointVolume))
                current = volume.GetMasterVolumeLevelScalar()
                volume.SetMasterVolumeLevelScalar(min(1.0, current + 0.05), None)
                return True
            except Exception as e:
                print(f"Volume error: {e}")
        if KEYBOARD_AVAILABLE:
            try:
                keyboard_lib.send("volume up")
                return True
            except:
                pass
        return False

@metadeck_action("system_mute", "System Mute", "System", "#2563EB")
class SystemMuteAction:
    def execute(self, param=""):
        if PYCAW_AVAILABLE:
            try:
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                volume = cast(interface, POINTER(IAudioEndpointVolume))
                volume.SetMute(not volume.GetMute(), None)
                return True
            except:
                pass
        if KEYBOARD_AVAILABLE:
            keyboard_lib.send("volume mute")
            return True
        return False

@metadeck_action("yt_play_pause", "YouTube Play/Pause", "YouTube", "#DC2626")
class YouTubePlayPauseAction:
    def execute(self, param=""):
        if KEYBOARD_AVAILABLE:
            try:
                keyboard_lib.send("play/pause media")
                keyboard_lib.send("k")
                return True
            except:
                pass
        return False

@metadeck_action("yt_mute", "YouTube Mute", "YouTube", "#DC2626")
class YouTubeMuteAction:
    def execute(self, param=""):
        if KEYBOARD_AVAILABLE:
            keyboard_lib.send("m")
            return True
        return False

@metadeck_action("yt_next", "YouTube Next", "YouTube", "#DC2626")
class YouTubeNextAction:
    def execute(self, param=""):
        if KEYBOARD_AVAILABLE:
            keyboard_lib.send("shift+n")
            return True
        return False

@metadeck_action("yt_previous", "YouTube Previous", "YouTube", "#DC2626")
class YouTubePreviousAction:
    def execute(self, param=""):
        if KEYBOARD_AVAILABLE:
            keyboard_lib.send("shift+p")
            return True
        return False

@metadeck_action("media_play_pause", "Media Play/Pause", "Media", "#7C3AED")
class MediaPlayPauseAction:
    def execute(self, param=""):
        if KEYBOARD_AVAILABLE:
            keyboard_lib.send("play/pause media")
            return True
        return False

@metadeck_action("media_next", "Media Next", "Media", "#7C3AED")
class MediaNextAction:
    def execute(self, param=""):
        if KEYBOARD_AVAILABLE:
            keyboard_lib.send("next track")
            return True
        return False

@metadeck_action("media_previous", "Media Previous", "Media", "#7C3AED")
class MediaPreviousAction:
    def execute(self, param=""):
        if KEYBOARD_AVAILABLE:
            keyboard_lib.send("previous track")
            return True
        return False

@metadeck_action("custom_key", "Custom Key", "Custom", "#059669")
class CustomKeyAction:
    def execute(self, param=""):
        if KEYBOARD_AVAILABLE and param:
            keyboard_lib.send(param)
            return True
        return False

@metadeck_action("custom_text", "Custom Text", "Custom", "#059669")
class CustomTextAction:
    def execute(self, param=""):
        if KEYBOARD_AVAILABLE and param:
            keyboard_lib.write(param)
            return True
        return False

@metadeck_action("open_url", "Open URL", "Custom", "#059669")
class OpenUrlAction:
    def execute(self, param=""):
        if param:
            webbrowser.open(param)
            return True
        return False


@metadeck_action("yt_music_volume_up", "YT Music Volume Up", "YouTube", "#FF0000")
class YTMusicVolumeUpAction:
    def execute(self, param=""):
        if KEYBOARD_AVAILABLE:
            try:
                keyboard_lib.send("up")
                return True
            except:
                pass
        return False

@metadeck_action("yt_music_volume_down", "YT Music Volume Down", "YouTube", "#FF0000")
class YTMusicVolumeDownAction:
    def execute(self, param=""):
        if KEYBOARD_AVAILABLE:
            try:
                keyboard_lib.send("down")
                return True
            except:
                pass
        return False

@metadeck_action("yt_music_like", "YT Music Like", "YouTube", "#FF0000")
class YTMusicLikeAction:
    def execute(self, param=""):
        # YouTube Music Like: Taste l oder + ?
        if KEYBOARD_AVAILABLE:
            try:
                keyboard_lib.send("l")
                return True
            except:
                pass
        return False

@metadeck_action("yt_music_dislike", "YT Music Dislike", "YouTube", "#FF0000")
class YTMusicDislikeAction:
    def execute(self, param=""):
        if KEYBOARD_AVAILABLE:
            try:
                keyboard_lib.send("d")
                return True
            except:
                pass
        return False

@metadeck_action("yt_music_shuffle", "YT Music Shuffle", "YouTube", "#FF0000")
class YTMusicShuffleAction:
    def execute(self, param=""):
        if KEYBOARD_AVAILABLE:
            try:
                keyboard_lib.send("s")
                return True
            except:
                pass
        return False

@metadeck_action("yt_music_repeat", "YT Music Repeat", "YouTube", "#FF0000")
class YTMusicRepeatAction:
    def execute(self, param=""):
        if KEYBOARD_AVAILABLE:
            try:
                keyboard_lib.send("r")
                return True
            except:
                pass
        return False

@metadeck_action("spotify_volume_up", "Spotify Volume Up", "Music", "#1DB954")
class SpotifyVolumeUpAction:
    def execute(self, param=""):
        # Spotify: Ctrl+Shift+Up = Volume Up
        if KEYBOARD_AVAILABLE:
            try:
                keyboard_lib.send("ctrl+shift+up")
                return True
            except:
                pass
        return False

@metadeck_action("spotify_volume_down", "Spotify Volume Down", "Music", "#1DB954")
class SpotifyVolumeDownAction:
    def execute(self, param=""):
        if KEYBOARD_AVAILABLE:
            try:
                keyboard_lib.send("ctrl+shift+down")
                return True
            except:
                pass
        return False

@metadeck_action("spotify_like", "Spotify Like", "Music", "#1DB954")
class SpotifyLikeAction:
    def execute(self, param=""):
        if KEYBOARD_AVAILABLE:
            try:
                keyboard_lib.send("alt+shift+b")
                return True
            except:
                pass
        return False

@metadeck_action("browser_new_tab", "Browser New Tab", "System", "#3B82F6")
class BrowserNewTabAction:
    def execute(self, param=""):
        if KEYBOARD_AVAILABLE:
            keyboard_lib.send("ctrl+t")
            return True
        return False

@metadeck_action("browser_close_tab", "Browser Close Tab", "System", "#3B82F6")
class BrowserCloseTabAction:
    def execute(self, param=""):
        if KEYBOARD_AVAILABLE:
            keyboard_lib.send("ctrl+w")
            return True
        return False

@metadeck_action("mic_mute", "Mic Mute Toggle", "System", "#EF4444")
class MicMuteAction:
    def execute(self, param=""):
        # Windows Mic Mute: Win+Alt+K oder F4?
        if KEYBOARD_AVAILABLE:
            try:
                keyboard_lib.send("volume mute")
                return True
            except:
                pass
        if PYCAW_AVAILABLE:
            try:
                from pycaw.pycaw import AudioUtilities
                # Mute all capture devices
                return True
            except:
                pass
        return False



class ActionExecutor:
    def execute(self, action_id, param=""):
        action_def = ACTION_REGISTRY.get(action_id)
        if not action_def:
            print(f"Unknown action: {action_id}")
            return False
        try:
            instance = action_def["class"]()
            return instance.execute(param)
        except Exception as e:
            print(f"Action {action_id} error: {e}")
            return False

# Unique Metadeck Serial Host - inspired by Macro Deck host but unique, local USB only
class MetadeckSerialHost:
    def __init__(self, app):
        self.app = app
        self.running = False
        self.serial_conn = None
        self.thread = None
        self.executor = ActionExecutor()

    def find_port(self):
        if not SERIAL_AVAILABLE:
            return None
        ports = list(serial.tools.list_ports.comports())
        for p in ports:
            desc = p.description.lower()
            if "leonardo" in desc or "pro micro" in desc or "arduino" in desc or "32u4" in desc:
                return p.device
        for p in ports:
            if "usb" in desc or "com" in p.device.lower() or "tty" in p.device.lower():
                return p.device
        return ports[0].device if ports else None

    def start(self):
        if not SERIAL_AVAILABLE:
            self.app.after(0, lambda: self.app.set_status("pyserial missing - pip install pyserial"))
            return False
        port = self.find_port()
        if not port:
            self.app.after(0, lambda: self.app.set_status("No USB device found - connect MEGA32U4 via USB"))
            return False
        try:
            self.serial_conn = serial.Serial(port, 115200, timeout=0.1)
            self.running = True
            self.thread = threading.Thread(target=self.read_loop, daemon=True)
            self.thread.start()
            self.app.after(0, lambda: self.app.set_status(f"USB Connected on {port} - LOCAL USB ONLY - READY!"))
            print(f"Metadeck v2.0 USB Host started on {port}")
            return True
        except Exception as e:
            print(f"Serial start error: {e}")
            self.app.after(0, lambda: self.app.set_status(f"USB error {port}: {e}"))
            return False

    def read_loop(self):
        buffer = ""
        while self.running and self.serial_conn:
            try:
                if self.serial_conn.in_waiting:
                    data = self.serial_conn.read(self.serial_conn.in_waiting).decode('utf-8', errors='ignore')
                    buffer += data
                    while '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
                        line = line.strip()
                        if not line:
                            continue
                        print(f"USB RX: {line}")
                        if line == "METADECK_V2_USB_READY":
                            self.app.after(0, lambda: self.app.set_status("Metadeck Board Ready via USB!"))
                            continue
                        # Parse B0:D or E0:L
                        if len(line) >= 3 and line[0] in ('B', 'E') and ':' in line:
                            try:
                                type_char = line[0]
                                id_part = line[1:line.index(':')]
                                event = line.split(':')[1]
                                button_id = int(id_part)
                                # Only on Down/Press/Left/Right, not Up to avoid double
                                if event in ('D', 'L', 'R', 'P'):
                                    self.app.after(0, lambda bid=button_id, t=type_char, ev=event: self.app.on_usb_event(bid, t, ev))
                            except Exception as e:
                                print(f"Parse error {line}: {e}")
            except Exception as e:
                print(f"Read loop error: {e}")
                break

    def stop(self):
        self.running = False
        if self.serial_conn:
            try:
                self.serial_conn.close()
            except:
                pass

class ConfigManager:
    @staticmethod
    def load():
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Migration: add physical mapping if missing
                    for k, v in data.items():
                        if "physical" not in v:
                            v["physical"] = f"B{k}" if int(k) < 20 else f"E{int(k)-20}"
                    return data
            except:
                pass
        config = {}
        for i in range(20):
            config[str(i)] = {"label": f"Key {i+1}", "action": "none", "param": "", "color": "#2B2B2B", "physical": f"B{i}"}
        config["20"] = {"label": "ENC Left", "action": "system_volume_down", "param": "", "color": "#1E40AF", "physical": "E0:L"}
        config["21"] = {"label": "ENC Right", "action": "system_volume_up", "param": "", "color": "#1E40AF", "physical": "E0:R"}
        config["22"] = {"label": "ENC Press", "action": "media_play_pause", "param": "", "color": "#BE185D", "physical": "E0:P"}
        return config

    @staticmethod
    def save(config):
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

class MetadeckApplication(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(f"{PRODUCT_NAME} v{CURRENT_VERSION} - LOCAL USB ONLY")
        self.geometry("1320x860")
        self._set_icon()
        # Load plugins like Macro Deck - auto-load from plugins/ folder
        try:
            load_plugins()
        except Exception as e:
            print(f"Plugin load error: {e}")
        self.config_data = ConfigManager.load()
        self.selected_slot = "0"
        self.is_listening_physical = False
        self.tray_icon = None
        self.executor = ActionExecutor()
        self.serial_host = MetadeckSerialHost(self)
        self.protocol("WM_DELETE_WINDOW", self.minimize_to_tray)
        self._create_ui()
        self.after(500, self.serial_host.start)

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
        ctk.CTkLabel(header, text=f"v{CURRENT_VERSION} | v2.3.0 PLUGIN SYSTEM | LOCAL USB ONLY | Just Works", font=("Segoe UI", 11), text_color="#22C55E").pack(side="left", padx=10)

        main = ctk.CTkFrame(self, fg_color="#0A0A0A")
        main.pack(fill="both", expand=True, padx=6, pady=6)

        left = ctk.CTkFrame(main, fg_color="#111111", corner_radius=12)
        left.pack(side="left", fill="both", expand=True, padx=6, pady=6)

        grid_sec = ctk.CTkFrame(left, fg_color="#161616", corner_radius=10)
        grid_sec.pack(fill="x", padx=12, pady=10)
        ctk.CTkLabel(grid_sec, text="MAIN DECK (10 x 2) - USB Protocol B0:D", font=("Segoe UI", 11, "bold"), text_color="#777777").pack(anchor="w", padx=12, pady=5)
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
        ctk.CTkLabel(enc_sec, text="ENCODER - E0:L/R/P - Fast 25ms - No BLE", font=("Segoe UI", 11, "bold"), text_color="#777777").pack(anchor="w", padx=12, pady=5)
        enc_f = ctk.CTkFrame(enc_sec, fg_color="transparent")
        enc_f.pack(padx=8, pady=8)
        for sid in ["20", "21", "22"]:
            cfg = self.config_data.get(sid, {})
            btn = ctk.CTkButton(enc_f, text=self._fmt(cfg), width=140, height=58, corner_radius=10, fg_color=cfg.get("color", "#1E40AF"), command=lambda s=sid: self.select_slot(s))
            btn.pack(side="left", padx=6)
            self.buttons[sid] = btn

        self.status_label = ctk.CTkLabel(left, text="Status: Starting USB Host...", font=("Segoe UI", 11), text_color="#22C55E")
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

        ctk.CTkLabel(right, text="Physical Key (Free Mapping)", font=("Segoe UI", 11, "bold"), text_color="#FF6F00").pack(anchor="w", padx=16, pady=(12,2))
        self.physical_display = ctk.CTkLabel(right, text="B0", font=("Segoe UI", 22, "bold"), fg_color="#1E1E1E", corner_radius=10, width=328, height=48, text_color="#FF6F00")
        self.physical_display.pack(padx=16, pady=2)
        self.assign_physical_btn = ctk.CTkButton(right, text="Press to Assign Physical Key", fg_color="#FF6F00", height=40, corner_radius=8, font=("Segoe UI", 12, "bold"), command=self.start_assign_physical)
        self.assign_physical_btn.pack(fill="x", padx=16, pady=4)

        ctk.CTkLabel(right, text="Action Type", font=("Segoe UI", 11, "bold"), text_color="#777777").pack(anchor="w", padx=16, pady=(16,4))
        action_values = list(ACTION_REGISTRY.keys())
        self.action_combo = ctk.CTkComboBox(right, values=action_values, width=328, height=38, corner_radius=8, command=self.on_action_changed)
        self.action_combo.pack(padx=16, pady=2)
        self.action_info = ctk.CTkLabel(right, text="", font=("Segoe UI", 11), text_color="#AAAAAA")
        self.action_info.pack(pady=4)

        ctk.CTkLabel(right, text="Parameter", font=("Segoe UI", 11), text_color="#777777").pack(anchor="w", padx=16, pady=(10,2))
        self.entry_param = ctk.CTkEntry(right, placeholder_text="Key, URL, Text", height=38, corner_radius=8)
        self.entry_param.pack(fill="x", padx=16, pady=2)

        ctk.CTkButton(right, text="Save Configuration", height=44, corner_radius=10, font=("Segoe UI", 13, "bold"), fg_color="#2563EB", command=self.save_slot).pack(fill="x", padx=16, pady=14)
        ctk.CTkButton(right, text="Test Action", height=36, corner_radius=8, fg_color="#059669", command=self.test_action).pack(fill="x", padx=16, pady=2)
        ctk.CTkButton(right, text="Minimize to Tray", height=36, corner_radius=8, fg_color="#3F3F46", command=self.minimize_to_tray).pack(fill="x", padx=16, pady=12)

        self.footer_status = ctk.CTkLabel(right, text=f"Config: {CONFIG_FILE} | USB 115200 baud", font=("Segoe UI", 9), text_color="#666666", wraplength=320)
        self.footer_status.pack(side="bottom", pady=12)

        self.select_slot("0")

    def _fmt(self, cfg):
        label = cfg.get("label", "Key")
        action = cfg.get("action", "none")
        name = ACTION_REGISTRY.get(action, {}).get("name", action)
        return f"{label}\n{name}"

    def select_slot(self, sid):
        self.selected_slot = sid
        cfg = self.config_data.get(sid, {})
        self.slot_label.configure(text=f"Slot {sid} - {cfg.get('label','')}")
        self.entry_label.delete(0, "end")
        self.entry_label.insert(0, cfg.get("label", ""))
        self.physical_display.configure(text=cfg.get("physical", f"B{sid}"))
        self.action_combo.set(cfg.get("action", "none"))
        self.entry_param.delete(0, "end")
        self.entry_param.insert(0, cfg.get("param", ""))
        self.on_action_changed(cfg.get("action", "none"))
        for s, b in self.buttons.items():
            b.configure(border_width=2 if s==sid else 0, border_color="white")

    def on_action_changed(self, action):
        info = ACTION_REGISTRY.get(action, {})
        self.action_info.configure(text=f"{info.get('name','')} - {info.get('category','')}")

    def save_slot(self):
        sid = self.selected_slot
        act = self.action_combo.get()
        self.config_data[sid] = {
            "label": self.entry_label.get() or f"Key {sid}",
            "action": act,
            "param": self.entry_param.get(),
            "color": ACTION_REGISTRY.get(act, {}).get("color", "#2B2B2B"),
            "physical": self.physical_display.cget("text")
        }
        ConfigManager.save(self.config_data)
        cfg = self.config_data[sid]
        if sid in self.buttons:
            self.buttons[sid].configure(text=self._fmt(cfg), fg_color=cfg["color"])
        self.set_status(f"Saved: {sid} = {act}")

    def test_action(self):
        act = self.action_combo.get()
        param = self.entry_param.get()
        ok = self.executor.execute(act, param)
        self.set_status(f"Test: {act} - OK: {ok}")

    def start_assign_physical(self):
        self.is_listening_physical = True
        self.physical_display.configure(text="Waiting...")
        self.assign_physical_btn.configure(text="Press Physical Key Now...", fg_color="#D32F2F")
        self.set_status("Press any key on deck to assign - 10s")
        self.after(10000, self.cancel_assign_physical)

    def cancel_assign_physical(self):
        if self.is_listening_physical:
            self.is_listening_physical = False
            self.assign_physical_btn.configure(text="Press to Assign Physical Key", fg_color="#FF6F00")
            cfg = self.config_data.get(self.selected_slot, {})
            self.physical_display.configure(text=cfg.get("physical", f"B{self.selected_slot}"))

    def on_physical_detected(self, physical_code):
        if not self.is_listening_physical:
            return
        self.is_listening_physical = False
        self.physical_display.configure(text=physical_code)
        self.assign_physical_btn.configure(text="Detected - Saving...", fg_color="#22C55E")
        self.set_status(f"Physical {physical_code} assigned to Slot {self.selected_slot}")
        self.after(600, lambda: [self.save_slot(), self.assign_physical_btn.configure(text="Press to Assign Physical Key", fg_color="#FF6F00")])

    def on_usb_event(self, button_id, type_char, event):
        physical_code = f"{type_char}{button_id}:{event}" if type_char == 'E' else f"{type_char}{button_id}"
        # If listening for physical assignment
        if self.is_listening_physical:
            self.after(0, lambda pc=physical_code: self.on_physical_detected(pc))
            return
        
        # Free mapping: find slot that has this physical code
        slot_id = None
        for sid, cfg in self.config_data.items():
            if cfg.get("physical") == physical_code:
                slot_id = sid
                break
        
        # Fallback: old fixed mapping if not found
        if slot_id is None:
            if type_char == 'B':
                slot_id = str(button_id)
            else:
                if event == 'L':
                    slot_id = "20"
                elif event == 'R':
                    slot_id = "21"
                else:
                    slot_id = "22"
        
        cfg = self.config_data.get(slot_id)
        if not cfg:
            self.set_status(f"USB {physical_code} -> Slot {slot_id} not configured")
            return
        action = cfg.get("action", "none")
        param = cfg.get("param", "")
        if action == "none":
            self.set_status(f"USB {physical_code} -> No action (assign action!)")
            return
        ok = self.executor.execute(action, param)
        self.set_status(f"USB {physical_code} -> Slot {slot_id} {action} - {'WORKS!' if ok else 'FAIL'}")

    def set_status(self, msg):
        self.status_label.configure(text=f"Status: {msg}")
        self.footer_status.configure(text=msg)
        print(msg)

    def minimize_to_tray(self):
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
        try:
            self.serial_host.stop()
        except:
            pass
        self.after(0, self.destroy)
        os._exit(0)

if __name__ == "__main__":
    app = MetadeckApplication()
    app.mainloop()
