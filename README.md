## Quick Setup

1. Open `poe_path.txt` in the Tuxile folder
2. Paste the full path to your Path of Exile `Client.txt` file
3. Save the file and launch Tuxile

**How to find Client.txt:**
- Steam default: `/home/$USER/.steam/steam/steamapps/common/Path of Exile/logs/Client.txt`
- Proton/custom library: `/mnt/YOUR_DRIVE/SteamLibrary/steamapps/common/Path of Exile/logs/Client.txt`
- You can find the exact path by right-clicking Path of Exile in Steam → Properties → Local Files → Browse

**If you move or reinstall Path of Exile:**
Simply edit `poe_path.txt` with the new path and restart Tuxile.

---

🐧 Tuxile ActRunner

Tuxile ActRunner is a lightweight, minimalist desktop overlay designed specifically for Path of Exile 1 players on Linux. Heavily inspired by the popular "Lailloken UI", it acts as an interactive, step-by-step campaign walkthrough to help you breeze through all 10 acts efficiently without ever alt-tabbing out of the game.

The app provides precise instructions on where to go, which quests to complete (especially those rewarding Passive Skill Points), and where to find Labyrinth Trials.
✨ Key Features

    👁️ Always-on-Top Overlay: A borderless, transparent, and unobtrusive window that sits perfectly over your game.

    🤖 Auto-Tracking (Log Parsing): Actively monitors your PoE Client.txt log file. Whenever you enter a new zone, the app automatically updates the overlay to the correct walkthrough step.

    🧠 Smart Town Logic: When you enter a town or hideout, the app intentionally holds the last instruction. This ensures you never forget to turn in quests or claim your Skill Points before moving on.

    📐 Custom UI Controls:

        Hold Ctrl + Left Mouse Button on the "MOVE" label to drag the overlay anywhere on your screen.

        Hold Ctrl + LMB on the "scale" label to resize the window (the text font scales dynamically!).

        Use Ctrl + LMB on the "<" and ">" arrows to manually navigate the steps.

    💾 Persistent State: Automatically saves your current walkthrough progress, window coordinates, and window size. Launch the app again, and pick up exactly where you left off.

🐧 Built for Linux

Developed with Linux gamers in mind (playing via Steam Proton/Wine), Tuxile ActRunner utilizes Python and PyQt to provide a native, hassle-free overlay experience. It's the perfect companion for league starts, optimizing your leveling process, and making sure you never miss a crucial skill point or trial again.

## Installation

### Prerequisites

Before running Tuxile ActRunner, ensure you have the following installed:

*   **Python 3.8+**
*   **pip** (Python package installer)

### Automated Setup and Running

To simplify the setup and running of the application, two scripts have been prepared:

1.  **`setup.sh`**: This script automatically creates a virtual environment, installs all required dependencies, and checks if Python and `pip` are installed.

2.  **`run.sh`**: This script activates the virtual environment (if it exists) and runs the main `main.py` application.

### First-time Setup (Configuration)

1.  **Clone the repository (if you haven't already):**
    ```bash
    git clone https://github.com/dominikzone/Tuxile-ActRunner.git
    cd Tuxile-ActRunner
    ```

2.  **Run the setup script:**
    ```bash
    ./setup.sh
    ```
    This script will guide you through the dependency installation process. On the first launch of the application, you will be prompted to select the Path of Exile `Client.txt` file. The application will also attempt to automatically locate this file in common directories.

### Subsequent Runs

After the initial setup and configuration, you can run the application directly using:

```bash
./run.sh
```

<!-- updated -->
