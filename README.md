# 🐧 Tuxile ActRunner

Lightweight always-on-top overlay for Path of Exile 1 on Linux.
Tracks campaign progress automatically via Client.txt log parsing.
Inspired by [Lailloken UI](https://github.com/Lailloken/Lailloken-UI).

## ✨ Features

- Always-on-top borderless overlay
- Auto-tracking via Client.txt — zone changes update the overlay automatically
- Smart town/hideout logic — holds current step so you don't miss quest turn-ins
- Manual navigation with ▲/▼ arrows
- Multiple character profiles
- Adjustable font size (A- / A+)
- Persistent state — remembers your progress between sessions

## 🔧 Requirements

- Linux (tested on Linux Mint)
- Python 3.8+
- Git

## 🚀 Installation

### 1. Clone the repository
```bash
git clone https://github.com/dominikzone/Tuxile-ActRunner.git
cd Tuxile-ActRunner
```

### 2. Run setup
```bash
chmod +x setup.sh
./setup.sh
```

### 3. Configure your PoE path
```bash
cp poe_path.txt.example poe_path.txt
```

Open `poe_path.txt` and paste the full path to your `Client.txt`:
- Steam default: `/home/USERNAME/.steam/steam/steamapps/common/Path of Exile/logs/Client.txt`
- Custom library: `/mnt/YOUR_DRIVE/SteamLibrary/steamapps/common/Path of Exile/logs/Client.txt`

> **Tip:** Right-click Path of Exile in Steam → Properties → Local Files → Browse

### 4. Launch
```bash
chmod +x run.sh
./run.sh
```

## 🎮 How to use

- The overlay auto-updates when you enter a new zone
- ▲/▼ — manually browse steps
- ⚔ CharName — switch character profiles
- A- / A+ — adjust font size
- R — reset progress for current character

## 🛠 Troubleshooting

- Warning about missing path → check `poe_path.txt`
- Zones not updating → verify `Client.txt` path is correct
- Python not found → `sudo apt install python3 python3-pip`
- Permission denied → `chmod +x run.sh`

## 📄 License

MIT License — see [LICENSE](LICENSE) file.

---
*This product isn't affiliated with or endorsed by Grinding Gear Games in any way.*
