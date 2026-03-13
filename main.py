import sys
import os
import re
from math import ceil
from PyQt6.QtWidgets import QApplication, QFileDialog
from PyQt6.QtCore import Qt, QObject, pyqtProperty, pyqtSignal, pyqtSlot, QUrl, QTimer
from PyQt6.QtQml import QQmlApplicationEngine

from config_manager import load_config, save_config
from walkthrough_data import WALKTHROUGH, TOWNS, ICON_MAPPING
from log_watcher import LogWatcher


def _compute_act_boundaries():
    boundaries = []
    current_act = None
    current_start = 0
    for i, step in enumerate(WALKTHROUGH):
        m = re.search(r'ACT (\d+)', step['text'])
        if m:
            if current_act is not None:
                boundaries.append((current_act, current_start, i - 1))
            current_act = int(m.group(1))
            current_start = i
    if current_act is not None:
        boundaries.append((current_act, current_start, len(WALKTHROUGH) - 1))
    return boundaries

ACT_BOUNDARIES = _compute_act_boundaries()


class OverlayBridge(QObject):
    currentStepIndexChanged = pyqtSignal()
    actTitleChanged         = pyqtSignal()
    actInfoChanged          = pyqtSignal()
    substepsChanged         = pyqtSignal()
    windowPosChanged        = pyqtSignal()
    windowSizeChanged       = pyqtSignal()
    opacityChanged          = pyqtSignal()
    baseFontSizeChanged     = pyqtSignal()
    currentZoneChanged      = pyqtSignal()

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.completed_data = self.config.get("completed_data", {})
        self.auto_completed_steps = set(int(k) for k in self.completed_data.keys())
        self._window = None
        self._current_zone = "Waiting..."
        self._substeps = []
        self._html_cache = {}
        self.update_substeps()

        self.save_timer = QTimer()
        self.save_timer.setSingleShot(True)
        self.save_timer.setInterval(1000)
        self.save_timer.timeout.connect(self.save_config_to_disk)

    @pyqtSlot()
    def save_config_to_disk(self):
        save_config(self.config)
        self.save_timer.stop()

    def request_save(self):
        self.save_timer.start()

    # ── Step index ────────────────────────────────────────────────────

    @pyqtProperty(int, notify=currentStepIndexChanged)
    def currentStepIndex(self):
        return self.config.get("current_step", 0)

    @currentStepIndex.setter
    def currentStepIndex(self, value):
        if self.config.get("current_step") != value:
            self.config["current_step"] = value
            self.currentStepIndexChanged.emit()
            self.actTitleChanged.emit()
            self.actInfoChanged.emit()
            self.update_substeps()
            self.request_save()

    @pyqtProperty(int, notify=currentStepIndexChanged)
    def totalSteps(self):
        return len(WALKTHROUGH)

    # ── Current zone ──────────────────────────────────────────────────

    @pyqtProperty(str, notify=currentZoneChanged)
    def currentZone(self):
        return self._current_zone

    @currentZone.setter
    def currentZone(self, value):
        if self._current_zone != value:
            self._current_zone = value
            self.currentZoneChanged.emit()

    # ── Act title (legacy) ────────────────────────────────────────────

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

    # ── Act info ──────────────────────────────────────────────────────

    def _get_act_info(self, step_idx):
        for act_num, start, end in ACT_BOUNDARIES:
            if start <= step_idx <= end:
                return act_num, step_idx - start, end - start + 1
        return 1, 0, 1

    @pyqtProperty(int, notify=actInfoChanged)
    def currentActNumber(self):
        act_num, _, _ = self._get_act_info(self.currentStepIndex)
        return act_num

    @pyqtProperty(int, notify=actInfoChanged)
    def currentActStepIndex(self):
        _, act_step, _ = self._get_act_info(self.currentStepIndex)
        return act_step

    @pyqtProperty(int, notify=actInfoChanged)
    def currentActTotalSteps(self):
        _, _, total = self._get_act_info(self.currentStepIndex)
        return total

    @pyqtProperty(str, notify=actInfoChanged)
    def stepZoneName(self):
        idx = self.currentStepIndex
        if 0 <= idx < len(WALKTHROUGH):
            return WALKTHROUGH[idx]["zone"].upper()
        return ""

    # ── HTML cache ────────────────────────────────────────────────────

    def _ensure_cached(self, idx):
        if idx < 0 or idx >= len(WALKTHROUGH) or idx in self._html_cache:
            return
        step = WALKTHROUGH[idx]
        text = step["text"]
        zone_name = step["zone"]

        text = re.sub(r"ACT \d+\n?", "", text)
        text = re.sub(r'\[ICON:[^\]]+\]', '', text)

        replacements = {
            "[WP]":         "<span style='color:#00ffff;font-weight:bold'>[WP]</span>",
            "[Q]":          "<span style='color:#ffcc00;font-weight:bold'>[QUEST]</span>",
            "[SKILL_POINT]":"<span style='color:#00ff88;font-weight:bold'>[SKILL]</span>",
            "[TRIAL":       "<span style='color:#ff4466;font-weight:bold'>[LAB TRIAL",
        }
        for k, v in replacements.items():
            text = text.replace(k, v)

        action_map = {
            "Kill": "#ff4466", "Defeat": "#ff4466", "Clear": "#ff4466", "Slay": "#ff4466",
            "Help": "#00ff88", "Talk": "#00ff88", "Quest": "#00ff88", "Reward": "#00ff88",
            "Go to": "#00ffff", "Enter": "#00ffff", "Travel": "#00ffff",
        }
        for action, color in action_map.items():
            text = re.sub(
                rf"\b{action}\b",
                f"<span style='color:{color};font-weight:bold'>{action}</span>",
                text
            )

        boss_matches = re.findall(r"Kill ([A-Za-z][a-zA-Z' -]+?)(?:\.|,| for |\[SKILL\]|\n)", text)
        for boss in boss_matches:
            text = text.replace(boss, f"<span style='color:#00ffff;font-weight:bold'>{boss}</span>")

        if zone_name in text:
            text = text.replace(zone_name, f"<span style='color:#00ffff;font-weight:bold'>{zone_name}</span>")

        self._html_cache[idx] = [line.strip() for line in text.split(".") if line.strip()]

    def _get_step_html(self, idx):
        if idx < 0 or idx >= len(WALKTHROUGH):
            return ""
        self._ensure_cached(idx)
        return ".<br/>".join(self._html_cache[idx]) + "."

    # ── Substep properties ────────────────────────────────────────────

    @pyqtProperty('QVariantList', notify=substepsChanged)
    def substeps(self):
        return self._substeps

    @pyqtProperty(str, notify=substepsChanged)
    def previousSubstep(self):
        return self._get_step_html(self.currentStepIndex - 1)

    @pyqtProperty(str, notify=substepsChanged)
    def currentSubstep(self):
        return self._get_step_html(self.currentStepIndex)

    @pyqtProperty(str, notify=substepsChanged)
    def nextSubstep(self):
        return self._get_step_html(self.currentStepIndex + 1)

    def update_substeps(self):
        idx = self.currentStepIndex
        if 0 <= idx < len(WALKTHROUGH):
            self._ensure_cached(idx)
            lines = self._html_cache[idx]
            completed_indices = self.completed_data.get(str(idx), [])
            self._substeps = [
                {"text": line + ".", "isCompleted": i in completed_indices}
                for i, line in enumerate(lines)
            ]
            self.substepsChanged.emit()
            self.recalculate_height()

    # ── Substep completion ────────────────────────────────────────────

    def mark_substep_completed(self, index, auto=False):
        idx = self.currentStepIndex
        idx_str = str(idx)
        if auto and idx in self.auto_completed_steps:
            return
        if idx_str not in self.completed_data:
            self.completed_data[idx_str] = []
        for i in range(index + 1):
            if i not in self.completed_data[idx_str]:
                self.completed_data[idx_str].append(i)
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
        idx_str = str(self.currentStepIndex)
        if idx_str not in self.completed_data:
            self.completed_data[idx_str] = []
        if index in self.completed_data[idx_str]:
            self.completed_data[idx_str].remove(index)
            self.auto_completed_steps.discard(self.currentStepIndex)
        else:
            self.mark_substep_completed(index, auto=False)
            return
        self.config["completed_data"] = self.completed_data
        self.request_save()
        self.update_substeps()

    # ── Navigation ────────────────────────────────────────────────────

    @pyqtSlot()
    def onPrevStep(self):
        if self.currentStepIndex > 0:
            self.currentStepIndex -= 1

    @pyqtSlot()
    def onNextStep(self):
        if self.currentStepIndex < len(WALKTHROUGH) - 1:
            self.currentStepIndex += 1

    # ── Font size (step 1, min 9, max 16) ────────────────────────────

    @pyqtSlot()
    def increaseFontSize(self):
        new_size = min(16, self.config.get("base_font_size", 12) + 1)
        self.config["base_font_size"] = new_size
        self.request_save()
        self.baseFontSizeChanged.emit()
        self.recalculate_height()

    @pyqtSlot()
    def decreaseFontSize(self):
        new_size = max(9, self.config.get("base_font_size", 12) - 1)
        self.config["base_font_size"] = new_size
        self.request_save()
        self.baseFontSizeChanged.emit()
        self.recalculate_height()

    # ── Drag ──────────────────────────────────────────────────────────

    @pyqtSlot()
    def start_drag(self):
        if self._window:
            self._window.startSystemMove()

    def _on_window_moved(self):
        if self._window:
            self.config["window_x"] = self._window.x()
            self.config["window_y"] = self._window.y()
            self.request_save()

    # ── Window geometry properties ────────────────────────────────────

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

    # ── Height auto-sizing ────────────────────────────────────────────

    @pyqtSlot()
    def recalculate_height(self):
        # Height is driven by QML's implicitHeight chain; Python just persists the value.
        # The actual save happens via PoEApp._save_window_size connected to heightChanged.
        pass

    # ── Reset ─────────────────────────────────────────────────────────

    @pyqtSlot()
    def resetProgress(self):
        self.config["current_step"] = 0
        self.completed_data = {}
        self.config["completed_data"] = {}
        self.auto_completed_steps = set()
        self.request_save()
        self.currentStepIndexChanged.emit()
        self.actTitleChanged.emit()
        self.actInfoChanged.emit()
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
        self.bridge._window = root
        root.xChanged.connect(self.bridge._on_window_moved)
        root.yChanged.connect(self.bridge._on_window_moved)
        root.widthChanged.connect(self._save_window_size)
        root.heightChanged.connect(self._save_window_size)
        root.setProperty("width", self.config.get("window_width", 400))
        root.setProperty("x", self.config.get("window_x", 100))
        root.setProperty("y", self.config.get("window_y", 100))
        root.requestActivate()
        root.raise_()

        self.setup_log_watcher()
        QTimer.singleShot(0, self.scan_log_history)

    def setup_log_watcher(self):
        path = self.config.get("client_txt_path")
        if path and os.path.exists(path):
            boss_names = set()
            for step in WALKTHROUGH:
                text = step.get("text", "")
                boss_matches = re.findall(r"Kill ([A-Za-z][a-zA-Z' -]+?)(?:\.|,| for |\[SKILL\]|\n)", text)
                for boss in boss_matches:
                    if (boss.strip().lower() not in
                            ["hillock", "crab", "spider", "guards", "general",
                             "overseer", "puppet mistress"]
                            and len(boss.strip()) > 2):
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
                    if zone_match:
                        found_zone = zone_match.group(1).strip()
                if found_zone:
                    self.on_zone_changed(found_zone)
        except: pass

    def _save_window_size(self):
        w = self.bridge._window
        if w:
            self.config["window_width"]  = w.width()
            self.config["window_height"] = w.height()
            self.bridge.request_save()

    def on_zone_changed(self, zone_name):
        self.bridge.currentZone = zone_name
        idx = self.bridge.currentStepIndex
        if 0 <= idx < len(WALKTHROUGH):
            text = WALKTHROUGH[idx]["text"]
            lines = [line.strip() for line in text.split(".") if line.strip()]
            for i, line in enumerate(lines):
                if zone_name.lower() in line.lower() or (
                        "town" in line.lower() and zone_name in TOWNS):
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
                    self.bridge.mark_substep_completed(i, auto=True)
                    break

    def run(self):
        return self.app.exec()


if __name__ == "__main__":
    poe_app = PoEApp()
    sys.exit(poe_app.run())
