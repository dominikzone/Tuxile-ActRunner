import sys
import os
import re
from PyQt6.QtWidgets import QApplication, QFileDialog
from PyQt6.QtCore import Qt, QObject, pyqtProperty, pyqtSignal, pyqtSlot, QPoint, QUrl, QTimer
from PyQt6.QtQml import QQmlApplicationEngine

from config_manager import load_config, save_config
from walkthrough_data import WALKTHROUGH, TOWNS, ICON_MAPPING
from log_watcher import LogWatcher

class OverlayBridge(QObject):
    currentStepIndexChanged = pyqtSignal()
    actTitleChanged = pyqtSignal()
    substepsChanged = pyqtSignal()
    windowPosChanged = pyqtSignal()
    windowSizeChanged = pyqtSignal()
    opacityChanged = pyqtSignal()
    baseFontSizeChanged = pyqtSignal()
    currentZoneChanged = pyqtSignal()

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.completed_data = self.config.get("completed_data", {})
        # FIX #1: Track which steps were auto-completed by log watcher
        # so we don't re-complete them when player backtracks
        self.auto_completed_steps = set(
            int(k) for k in self.completed_data.keys()
        )
        self._window = None  # set by PoEApp after QML loads
        self._current_zone = "Waiting..."
        self._substeps = []
        self._html_cache = {}  # {step_idx: [processed html lines]} — avoids re-running regex on every substep refresh
        self.update_substeps()

        # Timer for debouncing config saves
        self.save_timer = QTimer()
        self.save_timer.setSingleShot(True)
        self.save_timer.setInterval(1000)  # Save after 1s of inactivity
        self.save_timer.timeout.connect(self.save_config_to_disk)

    @pyqtSlot()
    def save_config_to_disk(self):
        save_config(self.config)
        self.save_timer.stop() # Cancel any pending save

    def request_save(self):
        if not self.save_timer.isActive():
            self.save_timer.start()
        else:
            self.save_timer.start() # Restart timer

    @pyqtProperty(int, notify=currentStepIndexChanged)
    def currentStepIndex(self):
        return self.config.get("current_step", 0)

    @currentStepIndex.setter
    def currentStepIndex(self, value):
        if self.config.get("current_step") != value:
            self.config["current_step"] = value
            self.currentStepIndexChanged.emit()
            self.actTitleChanged.emit()
            self.update_substeps()
            self.request_save()

    @pyqtProperty(int, notify=currentStepIndexChanged)
    def totalSteps(self):
        return len(WALKTHROUGH)

    @pyqtProperty(str, notify=currentZoneChanged)
    def currentZone(self):
        return self._current_zone

    @currentZone.setter
    def currentZone(self, value):
        if self._current_zone != value:
            self._current_zone = value
            self.currentZoneChanged.emit()

    @pyqtProperty(str, notify=actTitleChanged)
    def actTitle(self):
        idx = self.currentStepIndex
        if 0 <= idx < len(WALKTHROUGH):
            step = WALKTHROUGH[idx]
            text = step.get("text", "")
            act_match = re.search(r"ACT (\d+)", text)
            if act_match:
                return f"◈ ACT {act_match.group(1)} · {step['zone']}"
            return f"◈ {step['zone']}"
        return "◈ UNKNOWN"

    @pyqtProperty('QVariantList', notify=substepsChanged)
    def substeps(self):
        return self._substeps

    def update_substeps(self):
        idx = self.currentStepIndex
        if 0 <= idx < len(WALKTHROUGH):
            # Build HTML lines only once per step — cache result to avoid repeated regex
            if idx not in self._html_cache:
                step = WALKTHROUGH[idx]
                text = step["text"]
                zone_name = step["zone"]

                # Remove ACT X header
                text = re.sub(r"ACT \d+\n?", "", text)

                # Process badges/tags with neon colors
                replacements = {
                    "[WP]": "<span style='color: #00ffff; font-weight: bold;'>[WP]</span>",
                    "[Q]": "<span style='color: #ffcc00; font-weight: bold;'>[QUEST]</span>",
                    "[SKILL_POINT]": "<span style='color: #00ff88; font-weight: bold;'>[SKILL]</span>",
                    "[TRIAL": "<span style='color: #ff4466; font-weight: bold;'>[LAB TRIAL",
                }
                for k, v in replacements.items():
                    text = text.replace(k, v)

                # Action keywords
                action_map = {
                    "Kill": "#ff4466", "Defeat": "#ff4466", "Clear": "#ff4466", "Slay": "#ff4466",
                    "Help": "#00ff88", "Talk": "#00ff88", "Quest": "#00ff88", "Reward": "#00ff88",
                    "Go to": "#00ffff", "Enter": "#00ffff", "Travel": "#00ffff"
                }
                for action, color in action_map.items():
                    text = re.sub(rf"\b{action}\b", f"<span style='color: {color}; font-weight: bold;'>{action}</span>", text)

                # Highlight zone names and boss names in Cyan
                boss_matches = re.findall(r"Kill ([A-Za-z][a-zA-Z' -]+?)(?:\.|,| for |\[SKILL\]|\n)", text)
                for boss in boss_matches:
                    text = text.replace(boss, f"<span style='color: #00ffff; font-weight: bold;'>{boss}</span>")

                if zone_name in text:
                    text = text.replace(zone_name, f"<span style='color: #00ffff; font-weight: bold;'>{zone_name}</span>")

                self._html_cache[idx] = [line.strip() for line in text.split(".") if line.strip()]

            # Rebuild substep list with current completion state (fast — no regex)
            lines = self._html_cache[idx]
            completed_indices = self.completed_data.get(str(idx), [])
            self._substeps = [
                {"text": line + ".", "isCompleted": i in completed_indices}
                for i, line in enumerate(lines)
            ]
            self.substepsChanged.emit()

    def mark_substep_completed(self, index, auto=False):
        """
        Mark a substep as completed.
        auto=True means triggered by log watcher (zone entry, boss kill etc.)
        auto=False means triggered by player clicking manually.
        
        FIX #1: If auto=True and the step was already visited before
        (player backtracked), do NOT auto-complete — leave it for the
        player to check manually or use Reset (R).
        """
        idx = self.currentStepIndex
        idx_str = str(idx)

        # FIX #1 CORE LOGIC:
        # If this is an auto-completion AND the step was previously completed
        # (i.e. player is backtracking), skip the auto-completion entirely.
        if auto and idx in self.auto_completed_steps:
            return

        if idx_str not in self.completed_data:
            self.completed_data[idx_str] = []
        
        for i in range(index + 1):
            if i not in self.completed_data[idx_str]:
                self.completed_data[idx_str].append(i)
        
        # Mark this step as having been auto-completed at least once
        if auto:
            self.auto_completed_steps.add(idx)

        self.config["completed_data"] = self.completed_data
        self.request_save()
        
        if len(self.completed_data[idx_str]) >= len(self._substeps):
            if self.currentStepIndex < len(WALKTHROUGH) - 1:
                self.currentStepIndex += 1
            else:
                self.update_substeps()
        else:
            self.update_substeps()

    @pyqtSlot(int)
    def onSubstepClicked(self, index):
        """Player manually clicks a substep — always toggle regardless of backtrack state."""
        idx_str = str(self.currentStepIndex)
        if idx_str not in self.completed_data:
            self.completed_data[idx_str] = []
        
        if index in self.completed_data[idx_str]:
            # Uncheck — also remove from auto_completed so log can re-trigger if needed
            self.completed_data[idx_str].remove(index)
            self.auto_completed_steps.discard(self.currentStepIndex)
        else:
            self.mark_substep_completed(index, auto=False)
            return

        self.config["completed_data"] = self.completed_data
        self.request_save()
        self.update_substeps()

    @pyqtSlot()
    def onPrevStep(self):
        if self.currentStepIndex > 0:
            self.currentStepIndex -= 1

    @pyqtSlot()
    def onNextStep(self):
        if self.currentStepIndex < len(WALKTHROUGH) - 1:
            self.currentStepIndex += 1

    @pyqtSlot()
    def increaseFontSize(self):
        new_size = min(24, self.config.get("base_font_size", 12) + 2)
        self.config["base_font_size"] = new_size
        self.request_save()
        self.baseFontSizeChanged.emit()

    @pyqtSlot()
    def decreaseFontSize(self):
        new_size = max(7, self.config.get("base_font_size", 12) - 2)
        self.config["base_font_size"] = new_size
        self.request_save()
        self.baseFontSizeChanged.emit()

    @pyqtSlot()
    def start_drag(self):
        """Hand window movement to the X11/Wayland compositor via startSystemMove().
        Sends a single _NET_WM_MOVERESIZE event to the WM. The WM moves the window
        natively — no per-pixel Python callbacks, no setX/setY storm, zero lag."""
        if self._window:
            self._window.startSystemMove()

    def _on_window_moved(self):
        """Called whenever the WM repositions the window (xChanged / yChanged)."""
        if self._window:
            self.config["window_x"] = self._window.x()
            self.config["window_y"] = self._window.y()
            self.request_save()  # debounced — won't spam disk during live drag

    @pyqtProperty(int, notify=windowPosChanged)
    def windowX(self): return self.config.get("window_x", 100)
    @pyqtProperty(int, notify=windowPosChanged)
    def windowY(self): return self.config.get("window_y", 100)
    @pyqtProperty(int, notify=windowSizeChanged)
    def windowWidth(self): return self.config.get("window_width", 400)
    @pyqtProperty(int, notify=windowSizeChanged)
    def windowHeight(self): return self.config.get("window_height", 250)

    @pyqtSlot(int, int)
    def updateWindowPos(self, x, y):
        self.config["window_x"] = x
        self.config["window_y"] = y
        self.request_save()
        self.windowPosChanged.emit()

    @pyqtSlot(int, int)
    def updateWindowSize(self, w, h):
        self.config["window_width"] = w
        self.config["window_height"] = h
        self.request_save()
        self.windowSizeChanged.emit()

    @pyqtProperty(float, notify=opacityChanged)
    def opacity(self): return self.config.get("opacity", 0.85)

    @pyqtSlot(float)
    def adjustOpacity(self, delta):
        new_op = max(0.2, min(1.0, self.opacity + delta))
        self.config["opacity"] = new_op
        self.request_save()
        self.opacityChanged.emit()

    @pyqtProperty(int, notify=baseFontSizeChanged)
    def baseFontSize(self): return self.config.get("base_font_size", 12)

    @pyqtSlot()
    def resetProgress(self):
        """Full reset — clears all completed data and backtrack tracking."""
        self.config["current_step"] = 0
        self.completed_data = {}
        self.config["completed_data"] = {}
        self.auto_completed_steps = set()  # FIX #1: also reset backtrack tracking
        self.request_save()
        self.currentStepIndexChanged.emit()
        self.actTitleChanged.emit()
        self.update_substeps()


class PoEApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.config = load_config()
        self.bridge = OverlayBridge(self.config)
        
        self.engine = QQmlApplicationEngine()
        self.engine.rootContext().setContextProperty("bridge", self.bridge)
        
        qml_file = os.path.join(os.path.dirname(__file__), "overlay.qml")
        self.engine.load(QUrl.fromLocalFile(qml_file))
        
        if not self.engine.rootObjects():
            sys.exit(-1)

        root = self.engine.rootObjects()[0]
        self.bridge._window = root  # needed by start_drag() and _on_window_moved()
        # Save position whenever the WM moves the window (e.g. after startSystemMove)
        root.xChanged.connect(self.bridge._on_window_moved)
        root.yChanged.connect(self.bridge._on_window_moved)
        root.setProperty("width", self.config.get("window_width", 400))
        root.setProperty("height", self.config.get("window_height", 250))
        root.setProperty("x", self.config.get("window_x", 100))
        root.setProperty("y", self.config.get("window_y", 100))
        root.requestActivate()
        root.raise_()

        self.setup_log_watcher()
        # Defer log scan to after the event loop starts — avoids blocking UI during init
        QTimer.singleShot(0, self.scan_log_history)

    def setup_log_watcher(self):
        path = self.config.get("client_txt_path")
        if path and os.path.exists(path):
            boss_names = set()
            for step in WALKTHROUGH:
                text = step.get("text", "")
                boss_matches = re.findall(r"Kill ([A-Za-z][a-zA-Z' -]+?)(?:\.|,| for |\[SKILL\]|\n)", text)
                for boss in boss_matches:
                    if boss.strip().lower() not in ["hillock", "crab", "spider", "guards", "general", "overseer", "puppet mistress"] and len(boss.strip()) > 2:
                        boss_names.add(boss.strip())
            
            self.watcher = LogWatcher(path, list(boss_names))
            self.watcher.zone_changed.connect(self.on_zone_changed)
            self.watcher.waypoint_discovered.connect(self.on_waypoint_discovered)
            self.watcher.quest_item_found.connect(self.on_quest_item_found)
            self.watcher.quest_completed.connect(self.on_quest_completed)
            self.watcher.boss_slain.connect(self.on_boss_slain)
            self.watcher.trial_completed.connect(self.on_trial_completed)
            self.watcher.start()

    def scan_log_history(self):
        path = self.config.get("client_txt_path")
        if not path or not os.path.exists(path): return
        try:
            file_size = os.path.getsize(path)
            read_size = min(file_size, 50000)
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                f.seek(file_size - read_size)
                lines = f.readlines()
                found_zone = None
                for line in lines:
                    zone_match = re.search(r" : You have entered (.*?)\.", line)
                    if zone_match: found_zone = zone_match.group(1).strip()
                if found_zone:
                    self.on_zone_changed(found_zone)
        except: pass

    def select_client_txt(self):
        f, _ = QFileDialog.getOpenFileName(None, "Select Path of Exile Client.txt", os.path.expanduser("~"), "Text Files (*.txt);;All Files (*)")
        if f:
            self.config["client_txt_path"] = f
            save_config(self.config)

    def on_zone_changed(self, zone_name):
        self.bridge.currentZone = zone_name
        idx = self.bridge.currentStepIndex
        if 0 <= idx < len(WALKTHROUGH):
            text = WALKTHROUGH[idx]["text"]
            lines = [line.strip() for line in text.split(".") if line.strip()]
            for i, line in enumerate(lines):
                if zone_name.lower() in line.lower() or ("town" in line.lower() and zone_name in TOWNS):
                    # FIX #1: pass auto=True so backtrack guard kicks in
                    self.bridge.mark_substep_completed(i, auto=True)
                    break
        
        if zone_name in TOWNS: return
        for i, step in enumerate(WALKTHROUGH):
            if step["zone"].lower() == zone_name.lower():
                if self.bridge.currentStepIndex != i:
                    self.bridge.currentStepIndex = i
                break

    def on_waypoint_discovered(self):
        self._check_and_complete("[WP]")
        self._check_and_complete("waypoint")

    def on_quest_item_found(self, item_name):
        self._check_and_complete(item_name)

    def on_quest_completed(self, quest_name):
        self._check_and_complete(quest_name)

    def on_boss_slain(self, boss_name):
        self._check_and_complete(boss_name)

    def on_trial_completed(self, trial_name):
        self._check_and_complete(trial_name)
        self._check_and_complete("TRIAL")

    def _check_and_complete(self, keyword):
        idx = self.bridge.currentStepIndex
        if 0 <= idx < len(WALKTHROUGH):
            text = WALKTHROUGH[idx]["text"]
            lines = [line.strip() for line in text.split(".") if line.strip()]
            for i, line in enumerate(lines):
                if keyword.lower() in line.lower():
                    # FIX #1: pass auto=True
                    self.bridge.mark_substep_completed(i, auto=True)
                    break

    def run(self):
        return self.app.exec()

if __name__ == "__main__":
    poe_app = PoEApp()
    sys.exit(poe_app.run())
