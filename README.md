# 🐧 Tuxile ActRunner

> A Path of Exile 1 campaign walkthrough overlay for Linux — built natively with Python & PyQt6.

![Platform](https://img.shields.io/badge/platform-Linux-blue?style=flat-square)
![Python](https://img.shields.io/badge/python-3.8+-yellow?style=flat-square)
![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)
![Status](https://img.shields.io/badge/status-released-brightgreen?style=flat-square)

---

## 🎯 What is Tuxile ActRunner?

Tuxile ActRunner is a lightweight, native Linux overlay for **Path of Exile 1** that guides you through all 10 acts without ever alt-tabbing. It automatically tracks your progress by reading the PoE `Client.txt` log file — when you enter a new zone, the overlay updates instantly.

Inspired by [Lailloken UI](https://github.com/Lailloken/Lailloken-UI).
Built as part of the **Tuxile** ecosystem alongside [Tuxile PriceChecker](https://github.com/dominikzone/Tuxile-PriceChecker).

---

## ✨ Features

- 🗺️ **Step-by-step campaign guide** — all 10 acts with quest and passive point locations
- 🤖 **Auto-tracking** — reads `Client.txt` to update the overlay when you change zones
- 🏙️ **Smart town logic** — holds the current step in towns so you never miss a quest turn-in
- 👤 **Multiple character profiles** — switch between characters without losing progress
- 🔼 **Manual navigation** — use ▲/▼ arrows to browse steps freely
- 🔤 **Adjustable font size** — A- / A+ buttons to fit any screen
- 💾 **Persistent state** — remembers your progress, window position, and size between sessions
- ⚡ **Always-on-top overlay** — borderless, transparent, stays above the game
- 🔒 **No login required** — no OAuth, no account, no registration

---

## 🚀 Installation

See [INSTALL.md](INSTALL.md) for full setup instructions.

### Quick start

```bash
git clone https://github.com/dominikzone/Tuxile-ActRunner.git
cd Tuxile-ActRunner
chmod +x setup.sh && ./setup.sh
./run.sh
```

---

## 🕹️ How to use

1. Launch **Tuxile ActRunner** via `./run.sh`
2. On first launch — select your `Client.txt` file when prompted
3. Open **Path of Exile 1** and enter a zone
4. The overlay updates automatically to the correct step
5. Use ▲/▼ to browse steps manually if needed

### Controls

| Control | Action |
|---------|--------|
| ▲ / ▼ | Navigate steps manually |
| ⚔ CharName | Switch character profile |
| A- / A+ | Adjust font size |
| R | Reset progress for current character |

---

## 📡 Data Sources

| Source | Purpose |
|--------|---------|
| `Client.txt` (local file) | Zone change detection |
| Built-in walkthrough data | Campaign steps and quest info |

No internet connection required — everything runs locally.

---

## 🗺️ Roadmap

- [x] Client.txt log parsing — automatic zone tracking
- [x] Full 10-act campaign walkthrough data
- [x] Smart town/hideout logic
- [x] Multiple character profiles
- [x] Persistent state (progress, position, size)
- [x] Adjustable overlay (font size, position)
- [ ] PoE2 support *(future — separate project)*

---

## ⚠️ Disclaimer

Tuxile ActRunner reads a local log file (`Client.txt`) only — it does **not** interact with the PoE client process, make any network requests, or modify any game files. Use at your own risk.

*This product isn't affiliated with or endorsed by Grinding Gear Games in any way.*

---

## 🛠️ Built with

- [PyQt6](https://pypi.org/project/PyQt6/) — UI framework & QML rendering

---

*Part of the **Tuxile** tools ecosystem for Path of Exile on Linux* ⚔️
