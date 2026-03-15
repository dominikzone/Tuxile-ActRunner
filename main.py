import sys
import os
import re
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QObject, pyqtProperty, pyqtSignal, pyqtSlot, QUrl, QTimer
from PyQt6.QtGui import QFontDatabase
from PyQt6.QtQml import QQmlApplicationEngine

from config_manager import load_config, save_config
from character_manager import (
    load_characters, save_characters, get_active_character,
    set_active_character, add_character, delete_character, CHARACTERS_FILE
)
from walkthrough_data import WALKTHROUGH, TOWNS, ICON_MAPPING
from log_watcher import LogWatcher

# Maps [ICON:TYPE] tags in walkthrough text to icon type strings used by QML
_ICON_TO_TYPE = {
    "WAYPOINT":     "waypoint",
    "KILL_BOSS":    "boss",
    "QUEST_ITEM":   "item",
    "COLLECT_ITEM": "item",
    "TAKE_REWARD":  "quest",
    "TRIAL":        "trial",
    "ENTER_TOWN":   "town",
    "ENTER_ZONE":   "zone",
    "OPEN_PASSAGE": "zone",
    "SKILL_POINT":  "quest",
}


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
    if not boundaries:
        return [(1, 0, len(WALKTHROUGH) - 1)]
    return boundaries

ACT_BOUNDARIES = _compute_act_boundaries()


def _read_poe_path():
    path_file = os.path.join(os.path.dirname(__file__), "poe_path.txt")
    if not os.path.exists(path_file):
        return ""
    with open(path_file, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                return line
    return ""


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
    targetHeightChanged     = pyqtSignal()
    characterListChanged    = pyqtSignal()
    updateAvailable         = pyqtSignal()

    def __init__(self, char_data, global_config):
        super().__init__()
        self.char_data = char_data
        self.global_config = global_config
        active = char_data["active"]
        self.config = char_data["characters"][active]
        self.completed_data = self.config.get("completed_data", {})
        self.auto_completed_steps = set(int(k) for k in self.completed_data.keys())
        self.highwater_mark = self.config.get("highwater_mark", 0)
        self._window = None
        self._current_zone = "Waiting..."
        self._substeps = []
        self._html_cache = {}
        self._target_height = 200
        self._update_current = ""
        self._update_latest = ""
        self._show_update_bar = False
        self._fulfilled = set()
        self.update_substeps()

        self.save_timer = QTimer()
        self.save_timer.setSingleShot(True)
        self.save_timer.setInterval(1000)
        self.save_timer.timeout.connect(self.save_config_to_disk)

    @pyqtSlot()
    def save_config_to_disk(self):
        save_characters(self.char_data)
        save_config(self.global_config)
        self.save_timer.stop()

    def request_save(self):
        self.save_timer.start()

    # ── Target height (Python-computed, QML binds to this) ────────────

    @pyqtProperty(int, notify=targetHeightChanged)
    def targetHeight(self):
        return self._target_height

    # ── Step index ────────────────────────────────────────────────────

    @pyqtProperty(int, notify=currentStepIndexChanged)
    def currentStepIndex(self):
        return self.config.get("current_step", 0)

    @currentStepIndex.setter
    def currentStepIndex(self, value):
        if self.config.get("current_step") != value:
            self.config["current_step"] = value
            if value > self.highwater_mark:
                self.highwater_mark = value
                self.config["highwater_mark"] = value
            self._fulfilled = set()
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

    # ── Requirement tracking ──────────────────────────────────────────

    def mark_fulfilled(self, req_type, value=""):
        key = f"{req_type}:{value.lower().strip()}"
        self._fulfilled.add(key)

    def is_step_requirement_met(self, step_idx):
        if step_idx < 0 or step_idx >= len(WALKTHROUGH):
            return True
        req = WALKTHROUGH[step_idx].get("required")
        if not req:
            return True
        if req.get("quest_item"):
            key = f"quest_item:{req['quest_item'].lower().strip()}"
            if key not in self._fulfilled:
                return False
        if req.get("boss"):
            key = f"boss:{req['boss'].lower().strip()}"
            if key not in self._fulfilled:
                return False
        if req.get("trial"):
            key = f"trial:{step_idx}"
            if key not in self._fulfilled:
                return False
        if req.get("waypoint"):
            key = f"waypoint:{step_idx}"
            if key not in self._fulfilled:
                return False
        return True

    @pyqtProperty(bool, notify=substepsChanged)
    def stepRequirementMet(self):
        return self.is_step_requirement_met(self.currentStepIndex)

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
        return (1, step_idx, len(WALKTHROUGH))

    def _step_to_act(self, step_idx):
        for act_num, start, end in ACT_BOUNDARIES:
            if start <= step_idx <= end:
                return act_num
        return 1

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
    # Cache format: {idx: [{"icon": str, "text": str}, ...]}

    def _ensure_cached(self, idx):
        if idx < 0 or idx >= len(WALKTHROUGH) or idx in self._html_cache:
            return
        step = WALKTHROUGH[idx]
        text = step["text"]
        zone_name = step["zone"]

        text = re.sub(r"ACT \d+\n?", "", text)

        raw_lines = [line.strip() for line in text.split(".") if line.strip()]
        result = []

        for line in raw_lines:
            # Extract icon type from first [ICON:...] tag before stripping
            icon_match = re.search(r'\[ICON:([^\]]+)\]', line)
            icon_type = ""
            if icon_match:
                icon_type = _ICON_TO_TYPE.get(icon_match.group(1).upper(), "")

            # Strip all [ICON:...] tags
            line = re.sub(r'\[ICON:[^\]]+\]', '', line).strip()

            replacements = {
                "[WP]":         "<span style='color:#00ffff;font-weight:bold'>[WP]</span>",
                "[Q]":          "<span style='color:#ffcc00;font-weight:bold'>[QUEST]</span>",
                "[SKILL_POINT]":"<span style='color:#00ff88;font-weight:bold'>[SKILL]</span>",
                "[TRIAL":       "<span style='color:#ff4466;font-weight:bold'>[LAB TRIAL",
            }
            for k, v in replacements.items():
                line = line.replace(k, v)

            action_map = {
                "Kill": "#ff4466", "Defeat": "#ff4466", "Clear": "#ff4466", "Slay": "#ff4466",
                "Help": "#00ff88", "Talk": "#00ff88", "Quest": "#00ff88", "Reward": "#00ff88",
                "Go to": "#00ffff", "Enter": "#00ffff", "Travel": "#00ffff",
            }
            for action, color in action_map.items():
                line = re.sub(
                    rf"\b{action}\b",
                    f"<span style='color:{color};font-weight:bold'>{action}</span>",
                    line
                )

            boss_matches = re.findall(r"Kill ([A-Za-z][a-zA-Z' -]+?)(?:,| for |$)", line)
            for boss in boss_matches:
                line = line.replace(boss, f"<span style='color:#00ffff;font-weight:bold'>{boss}</span>")

            if zone_name in line:
                line = line.replace(zone_name, f"<span style='color:#00ffff;font-weight:bold'>{zone_name}</span>")

            result.append({"icon": icon_type, "text": line})

        self._html_cache[idx] = result

    # ── Substep properties ────────────────────────────────────────────

    @pyqtProperty('QVariantList', notify=substepsChanged)
    def substeps(self):
        return self._substeps

    def update_substeps(self):
        idx = self.currentStepIndex
        if 0 <= idx < len(WALKTHROUGH):
            self._ensure_cached(idx)
            lines = self._html_cache[idx]
            completed_set = set(self.completed_data.get(str(idx), []))
            first_active = next((i for i in range(len(lines)) if i not in completed_set), -1)
            self._substeps = [
                {
                    "text":        item["text"] + ".",
                    "isCompleted": i in completed_set,
                    "isCurrent":   i == first_active,
                    "iconType":    item["icon"],
                }
                for i, item in enumerate(lines)
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
        new_size = min(16, self.config.get("base_font_size", 9) + 1)
        self.config["base_font_size"] = new_size
        self.request_save()
        self.baseFontSizeChanged.emit()
        self.recalculate_height()

    @pyqtSlot()
    def decreaseFontSize(self):
        new_size = max(9, self.config.get("base_font_size", 9) - 1)
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
    def baseFontSize(self): return self.config.get("base_font_size", 9)

    # ── Height auto-sizing ────────────────────────────────────────────
    # Formula: titlebar(26) + updateBar(22 if visible) + topbar(22) + divider(1)
    #          + topPadding(6) + n*(fs+6) + spacing*(n-1)*3 + bottomPadding(6)

    @pyqtSlot()
    def recalculate_height(self):
        n = len(self._substeps)
        fs = self.config.get("base_font_size", 9)
        extra = 22 if self._show_update_bar else 0
        h = max(120, 26 + extra + 22 + 1 + 6 + n * (fs + 6) + max(0, n - 1) * 3 + 6)
        if h != self._target_height:
            if self._window:
                # Keep bottom edge fixed: window grows/shrinks upward
                current_bottom = self._window.y() + self._window.height()
                new_y = current_bottom - h
                self.config["window_y"] = new_y
                self.windowPosChanged.emit()
            self._target_height = h
            self.targetHeightChanged.emit()

    # ── Reset ─────────────────────────────────────────────────────────

    @pyqtSlot()
    def resetProgress(self):
        self.config["current_step"] = 0
        self.highwater_mark = 0
        self.config["highwater_mark"] = 0
        self.completed_data = {}
        self.config["completed_data"] = {}
        self.auto_completed_steps = set()
        self._fulfilled = set()
        self.request_save()
        self.currentStepIndexChanged.emit()
        self.actTitleChanged.emit()
        self.actInfoChanged.emit()
        self.update_substeps()

    # ── Character management ──────────────────────────────────────────

    @pyqtProperty(str, notify=characterListChanged)
    def activeCharacterName(self):
        return self.char_data.get("active", "Default")

    @pyqtProperty('QVariantList', notify=characterListChanged)
    def characterList(self):
        active = self.char_data.get("active", "Default")
        result = []
        for name, cfg in self.char_data.get("characters", {}).items():
            step_idx = cfg.get("current_step", 0)
            act_num = self._step_to_act(step_idx)
            result.append({
                "name": name,
                "actNumber": act_num,
                "isActive": name == active,
            })
        return result

    @pyqtSlot(str)
    def switchCharacter(self, name):
        if name not in self.char_data.get("characters", {}):
            return
        set_active_character(self.char_data, name)
        self.config = self.char_data["characters"][name]
        self.completed_data = self.config.get("completed_data", {})
        self.auto_completed_steps = set(int(k) for k in self.completed_data.keys())
        self.highwater_mark = self.config.get("highwater_mark", 0)
        self._html_cache = {}
        save_characters(self.char_data)
        if self._window:
            self._window.setProperty("x", self.config.get("window_x", 100))
            self._window.setProperty("y", self.config.get("window_y", 100))
            self._window.setProperty("width", self.config.get("window_width", 400))
        self.currentStepIndexChanged.emit()
        self.actTitleChanged.emit()
        self.actInfoChanged.emit()
        self.windowPosChanged.emit()
        self.windowSizeChanged.emit()
        self.opacityChanged.emit()
        self.baseFontSizeChanged.emit()
        self.characterListChanged.emit()
        self.update_substeps()

    @pyqtSlot(str)
    def addCharacter(self, name):
        name = name.strip()
        if not name:
            return
        add_character(self.char_data, name)
        save_characters(self.char_data)
        self.characterListChanged.emit()

    @pyqtSlot(str)
    def deleteCharacter(self, name):
        chars = self.char_data.get("characters", {})
        if len(chars) <= 1:
            return
        active = self.char_data.get("active")
        delete_character(self.char_data, name)
        save_characters(self.char_data)
        if name == active:
            new_active = self.char_data.get("active")
            self.config = self.char_data["characters"][new_active]
            self.completed_data = self.config.get("completed_data", {})
            self.auto_completed_steps = set(int(k) for k in self.completed_data.keys())
            self.highwater_mark = self.config.get("highwater_mark", 0)
            self._html_cache = {}
            self.currentStepIndexChanged.emit()
            self.actTitleChanged.emit()
            self.actInfoChanged.emit()
            self.windowPosChanged.emit()
            self.windowSizeChanged.emit()
            self.opacityChanged.emit()
            self.baseFontSizeChanged.emit()
            self.update_substeps()
        self.characterListChanged.emit()

    # ── Update checker ────────────────────────────────────────────────

    @pyqtProperty(bool, notify=updateAvailable)
    def showUpdateBar(self):
        return self._show_update_bar

    @pyqtProperty(str, notify=updateAvailable)
    def updateText(self):
        return f"v{self._update_current} → v{self._update_latest} available"

    @pyqtSlot(str, str)
    def setUpdateAvailable(self, current, latest):
        self._update_current = current
        self._update_latest = latest
        self._show_update_bar = True
        self.updateAvailable.emit()
        self.recalculate_height()

    @pyqtSlot()
    def dismissUpdate(self):
        self._show_update_bar = False
        self.updateAvailable.emit()
        self.recalculate_height()

    @pyqtSlot()
    def openGithub(self):
        import subprocess
        subprocess.Popen(["xdg-open",
            "https://github.com/dominikzone/Tuxile-ActRunner/releases/latest"])


class PoEApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        font_id = QFontDatabase.addApplicationFont(
            os.path.join(os.path.dirname(__file__),
                         "assets/fonts/BarlowCondensed-SemiBold.ttf")
        )
        if font_id == -1:
            print("Font not found locally — will use system fallback")
        self.global_config = load_config()

        # Load characters; migrate from config.json on first run
        char_file_exists = os.path.exists(CHARACTERS_FILE)
        self.char_data = load_characters()
        if not char_file_exists:
            active = self.char_data["active"]
            char_cfg = self.char_data["characters"][active]
            for key in ["current_step", "completed_data", "highwater_mark",
                        "opacity", "base_font_size", "window_x", "window_y", "window_width"]:
                if key in self.global_config:
                    char_cfg[key] = self.global_config[key]
            save_characters(self.char_data)

        self.bridge = OverlayBridge(self.char_data, self.global_config)

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
        root.setProperty("width", self.bridge.config.get("window_width", 400))
        root.setProperty("x", self.bridge.config.get("window_x", 100))
        root.setProperty("y", self.bridge.config.get("window_y", 100))
        root.requestActivate()
        root.raise_()

        # Trigger initial height calculation now that _window is set
        self.bridge.recalculate_height()

        self.app.aboutToQuit.connect(self.cleanup)
        poe_path = _read_poe_path()
        if poe_path:
            self.global_config["client_txt_path"] = poe_path
        self.setup_log_watcher()
        QTimer.singleShot(0, self.scan_log_history)
        QTimer.singleShot(3000, self.check_for_updates)

    def setup_log_watcher(self):
        path = self.global_config.get("client_txt_path", "")
        if not path or not os.path.exists(path):
            return
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
        path = self.global_config.get("client_txt_path")
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
            self.bridge.config["window_width"] = w.width()
            self.bridge.request_save()

    def check_for_updates(self):
        try:
            import urllib.request
            import json
            url = "https://api.github.com/repos/dominikzone/Tuxile-ActRunner/releases/latest"
            req = urllib.request.Request(url, headers={"User-Agent": "TuxileActRunner"})
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read())
                latest = data.get("tag_name", "").lstrip("v")
                current = open(os.path.join(
                    os.path.dirname(__file__), "version.txt")).read().strip()
                if latest and latest != current:
                    self.bridge.setUpdateAvailable(current, latest)
        except:
            pass  # silently fail — no internet or no releases yet

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
        current_idx = self.bridge.currentStepIndex
        if not self.bridge.is_step_requirement_met(current_idx):
            return
        for i, step in enumerate(WALKTHROUGH):
            if step["zone"].lower() == zone_name.lower():
                if i < self.bridge.highwater_mark:
                    continue  # backtracking into an old zone — ignore
                if self.bridge.currentStepIndex != i:
                    self.bridge.currentStepIndex = i
                break

    def on_waypoint_discovered(self):
        idx = self.bridge.currentStepIndex
        self.bridge.mark_fulfilled("waypoint", str(idx))
        self._check_and_complete("[WP]")
        self._check_and_complete("waypoint")

    def on_quest_item_found(self, item_name):
        self.bridge.mark_fulfilled("quest_item", item_name)
        self._check_and_complete(item_name)

    def on_quest_completed(self, quest_name):
        self._check_and_complete(quest_name)

    def on_boss_slain(self, boss_name):
        self.bridge.mark_fulfilled("boss", boss_name)
        self._check_and_complete(boss_name)

    def on_trial_completed(self, trial_name):
        idx = self.bridge.currentStepIndex
        self.bridge.mark_fulfilled("trial", str(idx))
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

    def cleanup(self):
        if hasattr(self, 'watcher'):
            self.watcher.requestInterruption()
            self.watcher.wait(2000)

    def run(self):
        return self.app.exec()


if __name__ == "__main__":
    poe_app = PoEApp()
    sys.exit(poe_app.run())
