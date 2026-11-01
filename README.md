# 🎛️ Metadeck - MEGA32U4 Stream Deck
![version](https://img.shields.io/badge/version-1.3.0-orange?style=for-the-badge)
[platform](https://img.shields.io/badge/Windows%2011-0078D6?style=for-the-badge&logo=windows&logoColor=white)
[chip](https://img.shields.io/badge/MEGA32U4-ATmega32U4-2ea44f?style=for-the-badge)
[license](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)
[Build](https://github.com/scargazeRR/Metadeck/actions/workflows/build.yml/badge.svg?style=for-the-badge)
[downloads](https://img.shields.io/github/downloads/scargazeRR/Metadeck/total?color=blue&style=for-the-badge)

[Logo](assets/MetaStreamdeck.png)

**Das professionelle Stream Deck für Creator - 10x2 Tasten + 3 Encoder - Drücken zum Belegen wie Elgato - Auto-Updater wie Steam**

---

## ✨ Was ist Metadeck?

Metadeck ist deine eigene Stream Deck Hardware mit **MEGA32U4 Chip** (Pro Micro / Leonardo) + **schöner Software** die aussieht wie die echte Elgato Software.

**Kein Löten, kein Programmieren für Nutzer - einfach EXE runterladen und loslegen!**

### 🎯 Für wen?

- **Streamer** - Szenen wechseln, Mute, Volume
- **YouTuber** - YouTube steuern ohne Maus
- **Gamer** - Media Keys, Shortcuts
- **Office** - Custom Texte, URLs, Keys
- **Musiker** - System Volume, Play/Pause

---

## 🚀 Installation für Nutzer (30 Sekunden)

### Du brauchst NICHTS installieren - nur die EXE!

**Schritt 1: Download**

Gehe auf 👉 **[Latest Release](https://github.com/scargazeRR/Metadeck/releases/latest)**

Lade runter: **`Metadeck.exe`** oder **`MetaStreamdeck.exe`** (ca. 40MB)

**Schritt 2: Starten**

1. Rechtsklick auf EXE -> **Als Administrator ausführen** (wichtig für F13-F24!)
2. Windows fragt "Unbekannter Herausgeber?" -> **Weitere Informationen** -> **Trotzdem ausführen**
3. Fertig! Das Fenster öffnet sich.

**Schritt 3: Fertig!**

Kein Installer, keine Registry, portabel - kannst du auch auf USB Stick mitnehmen!

> **Tipp:** Lege eine Verknüpfung in Autostart: `Win+R` -> `shell:startup` -> Verknüpfung reinziehen

---

## 🎮 So benutzt du Metadeck

### Das Grid

Du siehst ein **10x2 Grid** - 20 bunte Kacheln. Jede Kachel ist ein Button deines echten MEGA32U4 Decks.

- **Bunte Farben**: YouTube = Rot 🔴, System = Blau 🔵, Media = Lila 🟣, Custom = Grün 🟢
- **Icons**: Jede Aktion hat ein Icon (🔉 🔊 ⏯️ ⏭️ 📝 🌐)
- **Hover**: Maus drüber = heller

### Kachel belegen - Wie bei Elgato!

**So einfach:**

1. **Kachel klicken** im Grid (z.B. Button 1 oben links)
2. Rechts im Panel steht **PHYSISCHE TASTE** mit großem orangen `F14`
3. Klick auf **🎹 Taste drücken zum Belegen** (oranger Button)
4. Button wird rot: `⏳ Drücke Taste am Deck...`
5. **Drücke die Taste an deinem echten MEGA32U4 Deck**
6. Es erkennt automatisch: `✅ F14 erkannt!` -> speichert!
7. Fertig!

**Kein Dropdown, kein Suchen - einfach drücken wie beim echten Stream Deck!**

### Aktion wählen

Unter **AKTION** wählst du was die Taste machen soll:

| Kategorie | Aktionen | Was macht es? |
|-----------|----------|---------------|
| **YouTube** 🔴 | Leiser / Lauter / Mute / Play/Pause / Nächstes / Fullscreen | Steuert Browser (Chrome, Edge, Firefox) |
| **System** 🔵 | Sys Leiser / Lauter / Mute | Windows Lautstärke |
| **Media** 🟣 | Media Play / Next / Prev | Spotify, YouTube Music, etc. |
| **Custom** 🟢 | Custom Taste / Text / URL | Eigene Shortcuts, Texte, Webseiten |

**Beispiel:**
- Du willst YouTube leiser machen: Wähle `YT Leiser -5%`
- Du willst Spotify pausieren: Wähle `Media Play`
- Du willst `https://twitch.tv` öffnen: Wähle `URL Öffnen` + `https://twitch.tv` als Parameter

### Encoder (Drehknopf)

Unten hast du 3 Encoder Tasten:

- **ENC <<** = Links drehen (F20) - z.B. Leiser
- **ENC >>** = Rechts drehen (F21) - z.B. Lauter
- **ENC PRESS** = Drücken (F22) - z.B. Play/Pause

Belegst du genauso wie normale Tasten!

### Speichern & Testen

- **💾 Speichern**: Speichert deine Belegung (automatisch in `config.json`)
- **🧪 Test Aktion**: Testet die aktuelle Aktion ohne echte Taste zu drücken
- **Live Log**: Unten siehst du was passiert + YouTube Volume Bar + Status

---

## 🔧 Hardware Setup - MEGA32U4

### Was du brauchst

- **MEGA32U4 Board**: Arduino Pro Micro, Leonardo, oder kompatibel (ATmega32U4 Chip)
- **Tasten**: 20 Tasten + 3 für Encoder (oder weniger, geht auch)
- **Verkabelung**: Tasten an Pins 2,3,4,5,6,7,8,9,10,14,15,16,18,19,20,21,A0,A1,A2,A3 + Encoder an 37,38,39

### Arduino Code hochladen

1. **Arduino IDE** installieren (arduino.cc)
2. Board wählen: **Arduino Leonardo** oder **SparkFun Pro Micro**
3. Keine extra Library nötig! `Keyboard.h` ist schon drin
4. Datei öffnen: `firmware/mega32u4_sketch/mega32u4_sketch.ino` aus diesem Repo
5. **Hochladen** klicken
6. Fertig! Dein Board wird als Tastatur erkannt (sendet F13-F24)

**Warum MEGA32U4?**

- Natives USB HID (kein Treiber, kein Bluetooth)
- Unterstützt F13-F24 direkt (perfekt für Stream Deck)
- Sehr stabil, günstig, klein

---

## 🔄 Auto-Updater - Wie Steam

Metadeck prüft beim Start automatisch ob es ein Update gibt!

**Wenn Update verfügbar:**

- Pop-up: `🚀 Update verfügbar! v1.3.0 -> v1.3.1`
- Changelog wird angezeigt
- Klick **Jetzt updaten** -> lädt neue EXE runter -> ersetzt alte -> startet neu
- Fertig! Wie bei Steam, Epic, Battle.net

**Du musst nie wieder manuell runterladen!**

---

## 🎨 Features im Detail

- ✅ **10x2 Grid** - 20 Tasten frei belegbar
- ✅ **Beautiful Design** - Abgerundete Kacheln, Farben, Icons, wie Elgato Software
- ✅ **Press to Assign** - Drücken zum Belegen wie echtes Stream Deck
- ✅ **3 Encoder** - Drehknopf Support
- ✅ **MEGA32U4 Nativ** - ATmega32U4 Support
- ✅ **Auto-Updater** - Wie Steam/Epic
- ✅ **Auto-Build** - GitHub baut EXE automatisch
- ✅ **Portabel** - Kein Installer, USB Stick fähig
- ✅ **Icon + Herausgeber** - Sieht professionell aus
- ✅ **YouTube Integration** - Steuert Chrome/Edge/Firefox Lautstärke
- ✅ **System Volume** - Windows Lautstärke
- ✅ **Media Keys** - Spotify etc.
- ✅ **Custom** - Eigene Tasten, Texte, URLs

---

## ❓ FAQ - Häufige Fragen

**F: Windows sagt "Unbekannter Herausgeber"?**
A: Normal ohne teures Code Signing Zertifikat (80€/Jahr). Klick Weitere Informationen -> Trotzdem ausführen. Datei ist sicher, ist dein eigenes Tool!

**F: F13-F24 Tasten funktionieren nicht?**
A: Als Administrator starten! Rechtsklick -> Als Administrator ausführen. Sonst blockiert Windows F13-F24.

**F: YouTube Lautstärke geht nicht?**
A: Nur im Browser der gerade YouTube spielt? Chrome/Edge muss offen sein mit YouTube. Pycaw steuert nur Browser Audio Sessions.

**F: Mein MEGA32U4 wird nicht erkannt?**
A: Treiber installieren: Arduino IDE installieren, Board Leonardo wählen, Code hochladen. Dann sollte es als HID Tastatur erscheinen.

**F: Config geht verloren?**
A: `config.json` liegt neben EXE. Nicht löschen! Backup machen.

**F: Kann ich mehr als 20 Tasten?**
A: Ja! In `src/main.py` `range(20)` erhöhen und Pins im Arduino Code erweitern.

---

## 🛠️ Für Entwickler

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

---

## 📄 Lizenz

MIT License - Copyright (c) 2026 Metadeck - scargazeRR

Frei nutzbar, auch kommerziell!

---

## 🙏 Credits

- **Idee**: Elgato Stream Deck
- **Chip**: ATmega32U4 / Pro Micro
- **Design**: Inspired by Elgato Software + HTML Simulator
- **Icon**: Blaues M mit Grid
- **Updater**: Wie Steam/Epic Launcher

---

**Made with ❤️ - Metadeck v1.3.0 - Beautiful + Autonom**

**Download:** [Latest Release](https://github.com/scargazeRR/Metadeck/releases/latest) 🚀
