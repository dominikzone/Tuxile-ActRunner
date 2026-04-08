# Tuxile ActRunner — Installation Guide

This guide is written for players who may not have much experience with the terminal or Python. Just follow the steps in order and you'll be up and running in a few minutes.

---

## Requirements

Before you start, make sure you have the following:

- A **Linux** system (tested on Linux Mint)
- **Python 3.8 or newer** — check by running: `python3 --version`
- **Git** — check by running: `git --version`
- **Path of Exile** installed via Steam

If Python or Git is missing, install them with:
```bash
sudo apt install python3 python3-pip git
```

---

## Step 1 — Download the app

Open a terminal and run:

```bash
git clone https://github.com/dominikzone/Tuxile-ActRunner.git
cd Tuxile-ActRunner
```

This downloads the app into a folder called `Tuxile-ActRunner` and enters it.

---

## Step 2 — Run the setup script

```bash
chmod +x setup.sh
./setup.sh
```

This script will:
- Create a Python virtual environment (`venv/`)
- Install all required dependencies automatically

You only need to do this once.

---

## Step 3 — Configure poe_path.txt

The app needs to know where your Path of Exile log file is located.

1. Copy the example file:
   ```bash
   cp poe_path.txt.example poe_path.txt
   ```

2. Open `poe_path.txt` in any text editor and replace the placeholder with the **full path** to your `Client.txt` file.

**Common paths:**

- Steam default install:
  ```
  /home/USERNAME/.steam/steam/steamapps/common/Path of Exile/logs/Client.txt
  ```
- Custom Steam library on another drive:
  ```
  /mnt/YOUR_DRIVE/SteamLibrary/steamapps/common/Path of Exile/logs/Client.txt
  ```

> **Tip:** Not sure where your `Client.txt` is? In Steam, right-click Path of Exile → Properties → Local Files → Browse Local Files. The `logs/` folder is inside that directory.

Replace `USERNAME` (or `YOUR_DRIVE`) with the correct value for your system. Save the file when done.

---

## Step 4 — Launch the app

```bash
chmod +x run.sh
./run.sh
```

The overlay will launch in the background. The terminal will close automatically after a short countdown — that's normal.

To launch the app in the future, just run `./run.sh` from the `Tuxile-ActRunner` folder (or create a desktop shortcut to it).

---

## How to use

Once the overlay is running:

- **Zone tracking is automatic** — when you enter a new area in-game, the overlay advances to the correct step on its own.
- **Ctrl + ▲ / ▼** (sidebar arrows) — manually go to the previous or next step.
- **Click the character button** (`⚔ CharName` in the top-left) — switch between character profiles.
- **Ctrl + A- / A+** — make the text smaller or larger.
- **Ctrl + R** — reset progress for the current character.
- **Ctrl + LMB on the titlebar** — drag the overlay to a new position on screen.
- **Ctrl + Scroll** — adjust background opacity.

The window is always-on-top and stays visible while you play.

---

## Troubleshooting

**"Warning about missing path" or zones not updating**
→ Check that `poe_path.txt` contains the correct, full path to `Client.txt` and that the file exists.

**Python not found**
```bash
sudo apt install python3 python3-pip
```

**Git not found**
```bash
sudo apt install git
```

**Permission denied on `run.sh` or `setup.sh`**
```bash
chmod +x run.sh setup.sh
```

**App doesn't start after setup**
→ Make sure `setup.sh` completed without errors. You can re-run it safely at any time.

---

*This product isn't affiliated with or endorsed by Grinding Gear Games in any way.*
