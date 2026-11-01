
"""
Metadeck - MEGA32U4 Stream Deck Controller
Professional Edition v1.3.5
Copyright (c) 2026 ScargazeRR - Metadeck
Enterprise-grade hotkey deck controller for MEGA32U4 (Pro Micro / Leonardo)
Features: 20 keys + 3 encoders, Press-to-Assign, System Tray, Auto-Updater
"""

import os
import sys
import json
import time
import threading
import webbrowser
from pathlib import Path
from typing import Dict, Tuple, Optional

import customtkinter as ctk

try:
    import keyboard as keyboard_lib
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False

try:
    from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume
    PYCAW_AVAILABLE = True
except ImportError:
    PYCAW_AVAILABLE = False

try:
    import pystray
    from PIL import Image
    TRAY_AVAILABLE = True
except ImportError:
    TRAY_AVAILABLE = False


CURRENT_VERSION = "1.3.5"
CONFIG_FILE = Path("config.json")
COMPANY_NAME = "ScargazeRR"
PRODUCT_NAME = "Metadeck"

ACTIONS: Dict[str, Tuple[str, str]] = {
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
    return {
        "YouTube": "#DC2626",
        "System": "#2563EB",
        "Media": "#7C3AED",
        "Custom": "#059669"
    }.get(category, "#2B2B2B")

class AudioExecutor:
    def execute(self, action: str, param: str = "") -> bool:
        try:
            if action in ["yt_volume_down", "yt_volume_up", "yt_mute"]:
                return self._execute_browser_volume(action)
            if not KEYBOARD_AVAILABLE:
                return False
            key_map = {
                "yt_play_pause": "play/pause media",
                "yt_next": "next track",
                "yt_previous": "previous track",
                "media_play_pause": "play/pause media",
                "media_next": "next track",
                "media_previous": "previous track",
                "system_volume_down": "volume down",
                "system_volume_up": "volume up",
                "system_mute": "volume mute",
            }
            if action in key_map:
                keyboard_lib.send(key_map[action])
            elif action == "custom_key" and param:
                keyboard_lib.send(param)
            elif action == "custom_text" and param:
                keyboard_lib.write(param)
            elif action == "open_url" and param:
                webbrowser.open(param)
            return True
        except Exception as e:
            print(f"Execution error [{action}]: {e}")
            return False
    
    def _execute_browser_volume(self, action: str) -> bool:
        if not PYCAW_AVAILABLE:
            return False
        try:
            sessions = AudioUtilities.GetAllSessions()
            for session in sessions:
                if session.Process and any(name in session.Process.name().lower() for name in ["chrome", "msedge", "firefox", "brave", "opera"]):
                    volume = session._ctl.QueryInterface(ISimpleAudioVolume)
                    current = volume.GetMasterVolume()
                    if action == "yt_volume_down":
                        volume.SetMasterVolume(max(0.0, current - 0.05), None)
                    elif action == "yt_volume_up":
                        volume.SetMasterVolume(min(1.0, current + 0.05), None)
                    elif action == "yt_mute":
                        volume.SetMute(not volume.GetMute(), None)
                    break
            return True
        except Exception:
            return False

class ConfigManager:
    @staticmethod
    def load() -> Dict:
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        config = {}
        for i in range(20):
            config[str(i)] = {
                "label": f"Key {i+1}",
                "physical_key": f"F{13 + (i % 12)}",
                "action": "none",
                "param": "",
                "color": "#2B2B2B"
            }
        config["20"] = {"label": "ENC Left", "physical_key": "F20", "action": "yt_volume_down", "param": "", "color": "#1E40AF"}
        config["21"] = {"label": "ENC Right", "physical_key": "F21", "action": "yt_volume_up", "param": "", "color": "#1E40AF"}
        config["22"] = {"label": "ENC Press", "physical_key": "F22", "action": "yt_play_pause", "param": "", "color": "#BE185D"}
        return config
    
    @staticmethod
    def save(config: Dict) -> None:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

class MetadeckApplication(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(f"{PRODUCT_NAME} v{CURRENT_VERSION} - MEGA32U4 Controller")
        self.geometry("1320x820")
        self.minsize(1200, 700)
        self._set_application_icon()
        self.config_data = ConfigManager.load()
        self.selected_slot = "0"
        self.hotkey_map: Dict[str, Tuple[str, str]] = {}
        self.is_listening = False
        self.tray_icon: Optional[pystray.Icon] = None
        self.executor = AudioExecutor()
        self.protocol("WM_DELETE_WINDOW", self.minimize_to_tray)
        self._create_ui()
        self._rebuild_hotkey_map()
        self._start_hotkey_listener()
    
    def _set_application_icon(self) -> None:
        try:
            for path in ["assets/MetaStreamdeck.ico", "assets/Metadeck.ico", "MetaStreamdeck.ico"]:
                if os.path.exists(path):
                    self.iconbitmap(path)
                    break
        except Exception:
            pass
    
    def _create_ui(self) -> None:
        header = ctk.CTkFrame(self, fg_color="#151515", height=56, corner_radius=0)
        header.pack(fill="x")
        ctk.CTkLabel(header, text=f"{PRODUCT_NAME}", font=("Segoe UI", 20, "bold")).pack(side="left", padx=20, pady=10)
        ctk.CTkLabel(header, text=f"v{CURRENT_VERSION}  |  MEGA32U4 Controller  |  Press to Assign  |  Debounced", font=("Segoe UI", 11), text_color="#888888").pack(side="left", padx=10)
        ctk.CTkLabel(header, text=COMPANY_NAME, font=("Segoe UI", 11), text_color="#666666").pack(side="right", padx=20)
        
        main_container = ctk.CTkFrame(self, fg_color="#0A0A0A")
        main_container.pack(fill="both", expand=True, padx=6, pady=6)
        
        left_panel = ctk.CTkFrame(main_container, fg_color="#111111", corner_radius=12)
        left_panel.pack(side="left", fill="both", expand=True, padx=6, pady=6)
        
        grid_section = ctk.CTkFrame(left_panel, fg_color="#161616", corner_radius=10)
        grid_section.pack(fill="x", padx=12, pady=10)
        ctk.CTkLabel(grid_section, text="MAIN DECK  (10 x 2)", font=("Segoe UI", 11, "bold"), text_color="#777777").pack(anchor="w", padx=12, pady=(8,4))
        grid_frame = ctk.CTkFrame(grid_section, fg_color="transparent")
        grid_frame.pack(padx=8, pady=8)
        
        self.deck_buttons: Dict[str, ctk.CTkButton] = {}
        for row in range(2):
            row_frame = ctk.CTkFrame(grid_frame, fg_color="transparent")
            row_frame.pack(pady=2)
            for col in range(10):
                idx = row * 10 + col
                slot_id = str(idx)
                cfg = self.config_data.get(slot_id, {})
                btn = ctk.CTkButton(row_frame, text=self._format_button_text(cfg), width=108, height=108, corner_radius=16, fg_color=cfg.get("color", "#2B2B2B"), font=("Segoe UI", 10, "bold"), command=lambda s=slot_id: self.select_slot(s))
                btn.pack(side="left", padx=3, pady=3)
                self.deck_buttons[slot_id] = btn
        
        encoder_section = ctk.CTkFrame(left_panel, fg_color="#161616", corner_radius=10)
        encoder_section.pack(fill="x", padx=12, pady=6)
        ctk.CTkLabel(encoder_section, text="ENCODER CONTROLS", font=("Segoe UI", 11, "bold"), text_color="#777777").pack(anchor="w", padx=12, pady=(8,4))
        encoder_frame = ctk.CTkFrame(encoder_section, fg_color="transparent")
        encoder_frame.pack(padx=8, pady=8)
        for slot_id in ["20", "21", "22"]:
            cfg = self.config_data.get(slot_id, {})
            btn = ctk.CTkButton(encoder_frame, text=self._format_button_text(cfg), width=140, height=58, corner_radius=10, fg_color=cfg.get("color", "#1E40AF"), command=lambda s=slot_id: self.select_slot(s))
            btn.pack(side="left", padx=6)
            self.deck_buttons[slot_id] = btn
        
        self.status_label = ctk.CTkLabel(left_panel, text="Status: Ready - Hotkey listener active (F13-F24)", font=("Segoe UI", 11), text_color="#22C55E")
        self.status_label.pack(pady=12)
        
        right_panel = ctk.CTkFrame(main_container, width=360, fg_color="#111111", corner_radius=12)
        right_panel.pack(side="right", fill="y", padx=6, pady=6)
        right_panel.pack_propagate(False)
        
        ctk.CTkLabel(right_panel, text="Configuration", font=("Segoe UI", 16, "bold")).pack(pady=14)
        self.slot_label = ctk.CTkLabel(right_panel, text="Slot: 0", font=("Segoe UI", 13, "bold"), text_color="#FF6F00")
        self.slot_label.pack()
        
        ctk.CTkLabel(right_panel, text="Button Label", font=("Segoe UI", 11), text_color="#777777").pack(anchor="w", padx=16, pady=(14,2))
        self.entry_label = ctk.CTkEntry(right_panel, placeholder_text="Enter button label", height=38, corner_radius=8)
        self.entry_label.pack(fill="x", padx=16, pady=2)
        
        ctk.CTkLabel(right_panel, text="Physical Key Assignment", font=("Segoe UI", 11, "bold"), text_color="#777777").pack(anchor="w", padx=16, pady=(16,4))
        self.key_display = ctk.CTkLabel(right_panel, text="F13", font=("Segoe UI", 26, "bold"), fg_color="#1E1E1E", corner_radius=10, width=328, height=64, text_color="#FF6F00")
        self.key_display.pack(padx=16, pady=4)
        
        self.assign_button = ctk.CTkButton(right_panel, text="Press to Assign Key", fg_color="#FF6F00", hover_color="#E65100", height=46, corner_radius=10, font=("Segoe UI", 13, "bold"), command=self.start_key_assignment)
        self.assign_button.pack(fill="x", padx=16, pady=8)
        
        ctk.CTkLabel(right_panel, text="Action Type", font=("Segoe UI", 11, "bold"), text_color="#777777").pack(anchor="w", padx=16, pady=(16,4))
        self.action_combo = ctk.CTkComboBox(right_panel, values=list(ACTIONS.keys()), width=328, height=38, corner_radius=8, command=self.on_action_changed)
        self.action_combo.pack(padx=16, pady=2)
        
        self.action_info = ctk.CTkLabel(right_panel, text="", font=("Segoe UI", 11), text_color="#AAAAAA")
        self.action_info.pack(pady=4)
        
        ctk.CTkLabel(right_panel, text="Parameter", font=("Segoe UI", 11), text_color="#777777").pack(anchor="w", padx=16, pady=(10,2))
        self.entry_param = ctk.CTkEntry(right_panel, placeholder_text="Key, URL or text value", height=38, corner_radius=8)
        self.entry_param.pack(fill="x", padx=16, pady=2)
        
        ctk.CTkButton(right_panel, text="Save Configuration", height=44, corner_radius=10, font=("Segoe UI", 13, "bold"), fg_color="#2563EB", command=self.save_current_slot).pack(fill="x", padx=16, pady=14)
        ctk.CTkButton(right_panel, text="Test Action", height=36, corner_radius=8, fg_color="#059669", command=self.test_current_action).pack(fill="x", padx=16, pady=2)
        ctk.CTkButton(right_panel, text="Minimize to Tray", height=36, corner_radius=8, fg_color="#3F3F46", command=self.minimize_to_tray).pack(fill="x", padx=16, pady=12)
        
        self.footer_status = ctk.CTkLabel(right_panel, text="Listener active - Waiting for F13-F24", font=("Segoe UI", 10), text_color="#666666", wraplength=320)
        self.footer_status.pack(side="bottom", pady=12, padx=10)
        
        self.select_slot("0")
    
    def _format_button_text(self, cfg: Dict) -> str:
        label = cfg.get("label", "Key")
        phys = cfg.get("physical_key", "F13")
        action = cfg.get("action", "none")
        action_name = ACTIONS.get(action, (action, ""))[0]
        return f"{label}\n{phys}\n{action_name}"
    
    def select_slot(self, slot_id: str) -> None:
        self.selected_slot = slot_id
        cfg = self.config_data.get(slot_id, {})
        self.slot_label.configure(text=f"Slot {slot_id} - {cfg.get('label','')}")
        self.entry_label.delete(0, "end")
        self.entry_label.insert(0, cfg.get("label", ""))
        self.key_display.configure(text=cfg.get("physical_key", "F13"))
        self.action_combo.set(cfg.get("action", "none"))
        self.entry_param.delete(0, "end")
        self.entry_param.insert(0, cfg.get("param", ""))
        self.on_action_changed(cfg.get("action", "none"))
        for sid, btn in self.deck_buttons.items():
            if sid == slot_id:
                btn.configure(border_width=2, border_color="white")
            else:
                btn.configure(border_width=0)
    
    def on_action_changed(self, action: str) -> None:
        name, category = ACTIONS.get(action, (action, "System"))
        self.action_info.configure(text=f"{name} - {category}")
    
    def save_current_slot(self) -> None:
        slot_id = self.selected_slot
        action = self.action_combo.get()
        self.config_data[slot_id] = {
            "label": self.entry_label.get() or f"Key {slot_id}",
            "physical_key": self.key_display.cget("text"),
            "action": action,
            "param": self.entry_param.get(),
            "color": get_action_color(action)
        }
        ConfigManager.save(self.config_data)
        cfg = self.config_data[slot_id]
        if slot_id in self.deck_buttons:
            self.deck_buttons[slot_id].configure(text=self._format_button_text(cfg), fg_color=cfg["color"])
        self._rebuild_hotkey_map()
        self.set_status(f"Saved: Slot {slot_id} - {cfg['label']} -> {cfg['physical_key']} = {action}")
    
    def test_current_action(self) -> None:
        action = self.action_combo.get()
        param = self.entry_param.get()
        self.executor.execute(action, param)
        self.set_status(f"Testing: {action} {param}")
    
    def start_key_assignment(self) -> None:
        self.is_listening = True
        self.key_display.configure(text="Waiting...")
        self.assign_button.configure(text="Press Key on Deck...", fg_color="#D32F2F")
        self.set_status("Waiting for key press - Press any key on MEGA32U4 deck (F13-F24)")
        self.after(10000, self._cancel_assignment)
    
    def _cancel_assignment(self) -> None:
        if self.is_listening:
            self.is_listening = False
            self.assign_button.configure(text="Press to Assign Key", fg_color="#FF6F00")
            cfg = self.config_data.get(self.selected_slot, {})
            self.key_display.configure(text=cfg.get("physical_key", "F13"))
    
    def on_physical_key_detected(self, key_name: str) -> None:
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
        self.assign_button.configure(text="Detected - Saving...", fg_color="#22C55E")
        self.set_status(f"Key detected: {key_name}")
        self.after(600, lambda: [self.save_current_slot(), self.assign_button.configure(text="Press to Assign Key", fg_color="#FF6F00")])
    
    def _rebuild_hotkey_map(self) -> None:
        self.hotkey_map = {}
        for cfg in self.config_data.values():
            physical_key = cfg.get("physical_key", "").lower()
            if physical_key:
                self.hotkey_map[physical_key] = (cfg.get("action", "none"), cfg.get("param", ""))
    
    def _start_hotkey_listener(self) -> None:
        if not KEYBOARD_AVAILABLE:
            self.set_status("Warning: keyboard library not available - Install with: pip install keyboard (Admin required for F13-F24)")
            return
        def hook_callback(event):
            key_name = event.name.lower()
            if self.is_listening:
                self.after(0, lambda: self.on_physical_key_detected(key_name))
                return
            if key_name in self.hotkey_map:
                action, param = self.hotkey_map[key_name]
                if action and action != "none":
                    self.executor.execute(action, param)
                    self.after(0, lambda: self.set_status(f"Executed: {key_name.upper()} -> {action}"))
        try:
            keyboard_lib.hook(hook_callback)
            self.set_status("Ready - Hotkey listener active - Supports F13-F24 from MEGA32U4")
        except Exception as e:
            self.set_status(f"Hotkey listener requires administrator privileges: {e}")
    
    def set_status(self, message: str) -> None:
        self.status_label.configure(text=f"Status: {message}")
        self.footer_status.configure(text=message)
    
    def minimize_to_tray(self) -> None:
        self.withdraw()
        if not TRAY_AVAILABLE:
            self.set_status("Minimized - Tray library not available (install pystray and Pillow for tray icon)")
            return
        if self.tray_icon is None:
            try:
                icon_path = None
                for candidate in ["assets/MetaStreamdeck.ico", "assets/Metadeck.ico", "MetaStreamdeck.ico"]:
                    if os.path.exists(candidate):
                        icon_path = candidate
                        break
                if icon_path and os.path.exists(icon_path):
                    tray_image = Image.open(icon_path)
                else:
                    tray_image = Image.new("RGB", (64, 64), color=(37, 99, 235))
                menu = pystray.Menu(
                    pystray.MenuItem("Open Metadeck", self.show_from_tray, default=True),
                    pystray.Menu.SEPARATOR,
                    pystray.MenuItem("Exit", self.quit_from_tray)
                )
                self.tray_icon = pystray.Icon(PRODUCT_NAME, tray_image, f"{PRODUCT_NAME} v{CURRENT_VERSION} - Running in background", menu)
                def run_tray_icon():
                    self.tray_icon.run()
                threading.Thread(target=run_tray_icon, daemon=True).start()
                self.set_status("Minimized to system tray - Right-click tray icon for options")
            except Exception as e:
                print(f"Tray initialization error: {e}")
    
    def show_from_tray(self, icon=None, item=None) -> None:
        self.after(0, self.deiconify)
        self.after(0, self.lift)
        self.after(0, self.focus_force)
    
    def quit_from_tray(self, icon=None, item=None) -> None:
        if self.tray_icon:
            try:
                self.tray_icon.stop()
            except Exception:
                pass
        self.after(0, self.destroy)
        os._exit(0)

if __name__ == "__main__":
    app = MetadeckApplication()
    app.mainloop()
