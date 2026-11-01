# MetaStreamdeck

![Build](https://github.com/scargazeRR/MetaStreamdeck/actions/workflows/build.yml/badge.svg)
![downloads](https://img.shields.io/github/downloads/scargazeRR/MetaStreamdeck/total?color=blue)

![Logo](assets/MetaStreamdeck.png)

**Download fertige App:** [Latest Release](https://github.com/scargazeRR/MetaStreamdeck/releases/latest) -> `MetaStreamdeck.exe` -> Als Admin starten!

## Für Kollegen: Fertige App downloaden

1. Auf [Releases](https://github.com/scargazeRR/MetaStreamdeck/releases/latest) gehen
2. `MetaStreamdeck.exe` runterladen (40MB)
3. Rechtsklick -> Als Administrator ausführen
4. Fertig! Kein Python, kein Bauen nötig!

## Auto-Upload wie es funktioniert

Jedes mal wenn ich `v1.3.1` als Tag pushe, baut GitHub automatisch die EXE:

```bash
git tag v1.3.1
git push origin v1.3.1
```

Nach 3 Minuten liegt die neue EXE unter Releases - Kollege lädt einfach neu runter!
