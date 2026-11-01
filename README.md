# 🎛️ Metadeck - MEGA32U4 Hotkey Deck
![version](https://img.shields.io/badge/version-1.3.0-orange?style=for-the-badge)
![platform](https://img.shields.io/badge/Windows%2011-0078D6?style=for-the-badge&logo=windows&logoColor=white)
![chip](https://img.shields.io/badge/MEGA32U4-ATmega32U4-2ea44f?style=for-the-badge)
![license](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)




## Installation 

**Schritt 1: Download**

Gehe auf **[Latest Release](https://github.com/scargazeRR/Metadeck/releases/latest)**

Lade runter: **`Metadeck.exe`** 

**Schritt 2: Starten**

1. Rechtsklick auf EXE -> **Als Administrator ausführen** (wichtig für F13-F24!)
2. Windows fragt "Unbekannter Herausgeber?" -> **Weitere Informationen** -> **Trotzdem ausführen**
3. Fertig! Das Fenster öffnet sich.


> **Tipp:** Lege eine Verknüpfung in Autostart: `Win+R` -> `shell:startup` -> Verknüpfung reinziehen

---

## So benutzt du Metadeck

### Kachel belegen

**So einfach:**

1. **Kachel klicken** im Grid (z.B. Button 1 oben links)
2. Rechts im Panel steht **PHYSISCHE TASTE** mit großem orangen `F14`
3. Klick auf ** Taste drücken zum Belegen** (oranger Button)
4. Button wird rot: ` Drücke Taste am Deck...`
5. **Drücke die Taste an deinem echten MEGA32U4 Deck**
6. Es erkennt automatisch: ` F14 erkannt!` -> speichert!
7. Fertig!


### Aktion wählen

Unter **AKTION** wählst du was die Taste machen soll:

| Kategorie | Aktionen | Was macht es? |
|-----------|----------|---------------|
| **YouTube**  | Leiser / Lauter / Mute / Play/Pause / Nächstes / Fullscreen | Steuert Browser (Chrome, Edge, Firefox) |
| **System**   | Sys Leiser / Lauter / Mute | Windows Lautstärke |
| **Media**    | Media Play / Next / Prev | Spotify, YouTube Music, etc. |
| **Custom**   | Custom Taste / Text / URL | Eigene Shortcuts, Texte, Webseiten |

**Beispiel:**
- Du willst YouTube leiser machen: Wähle `YT Leiser -5%`
- Du willst Spotify pausieren: Wähle `Media Play`
- Du willst `https://twitch.tv` öffnen: Wähle `URL Öffnen` + `https://twitch.tv` als Parameter


### Speichern & Testen

- ** Speichern**: Speichert deine Belegung (automatisch in `config.json`)
- ** Test Aktion**: Testet die aktuelle Aktion ohne echte Taste zu drücken
- **Live Log**: Unten siehst du was passiert + YouTube Volume Bar + Status

---

## Hardware Setup - MEGA32U4

### Was du brauchst

- **MEGA32U4 Board**: Arduino Pro Micro, Leonardo, oder kompatibel (ATmega32U4 Chip)
- **Tasten**: 20 Tasten + 3 für Encoder (oder weniger, geht auch)
- **Verkabelung**: Tasten an Pins 2,3,4,5,6,7,8,9,10,14,15,16,18,19,20,21,A0,A1,A2,A3 + Encoder an 37,38,39

### Arduino Code hochladen

1. **Arduino IDE** installieren (arduino.cc)
2. Board wählen: **Arduino Leonardo** oder **SparkFun Pro Micro**
3. Datei öffnen: `firmware/mega32u4_sketch/mega32u4_sketch.ino` aus diesem Repo
4. **Hochladen** klicken
5. Fertig! Dein Board wird als Tastatur erkannt (sendet F13-F24)


## Für Entwickler

```bash
# Clonen
git clone https://github.com/scargazeRR/Metadeck.git
cd Metadeck

# Installieren
pip install -r requirements.txt

# Starten
python src/main.py

# EXE bauen
python -m PyInstaller --onefile --windowed --name Metadeck --icon=assets/MetaStreamdeck.ico --version-file=build/version_info.txt --hidden-import=comtypes --hidden-import=pycaw --hidden-import=customtkinter --hidden-import=keyboard --hidden-import=requests src/main.py
```



## Lizenz

MIT License - Copyright (c) 2026 Metadeck - scargazeRR


**Download:** [Latest Release](https://github.com/scargazeRR/Metadeck/releases/latest) 🚀
