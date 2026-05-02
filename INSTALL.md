# Tuxile ActRunner — Installation & Setup

## Prerequisites

**Python 3.8 or newer**
```bash
python3 --version
```

If Python is missing:
```bash
sudo apt install python3 python3-pip
```

---

## Step 1 — Clone the repository

```bash
git clone https://github.com/dominikzone/Tuxile-ActRunner.git
cd Tuxile-ActRunner
```

---

## Step 2 — Run setup

The included `setup.sh` script automatically creates a virtual environment
and installs all required dependencies (PyQt6):

```bash
chmod +x setup.sh
./setup.sh
```

---

## Step 3 — Configure your PoE Client.txt path

On first launch the app will ask you to locate your `Client.txt` file.
It will also attempt to find it automatically in common Steam locations.

Common paths:
- **Default Steam library:**
  `/home/USERNAME/.steam/steam/steamapps/common/Path of Exile/logs/Client.txt`
- **Custom Steam library:**
  `/mnt/YOUR_DRIVE/SteamLibrary/steamapps/common/Path of Exile/logs/Client.txt`

> **Tip:** Right-click Path of Exile in Steam → Properties → Local Files → Browse
> to find your install location.

---

## Step 4 — Launch

```bash
chmod +x run.sh
./run.sh
```

The terminal will close automatically after 10 seconds — the app runs in the background.

---

## Verifying it works

After launching, the overlay should appear on screen with campaign walkthrough steps.
Open Path of Exile and enter a zone — the overlay automatically updates to the correct step.

---

## Troubleshooting

**`Warning: missing path`**
The app cannot find `Client.txt`. Follow Step 3 to configure the path manually.

**Zones not updating automatically**
Verify that the `Client.txt` path is correct and the file exists at that location.

**`Python not found`**
Install Python: `sudo apt install python3 python3-pip`

**`Permission denied` on run.sh or setup.sh**
Make the scripts executable: `chmod +x run.sh setup.sh`

**`ModuleNotFoundError` when starting**
Run `./setup.sh` again to reinstall dependencies.

**Overlay appears but is blank**
Check that you are running Path of Exile 1 (not PoE2). ActRunner supports PoE1 only.

---

## Updating the app

```bash
cd Tuxile-ActRunner
git pull
./setup.sh
./run.sh
```

