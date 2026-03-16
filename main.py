import sys
import os
import re
import math
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
    updateAvailableChanged  = pyqtSignal()
    profileModalOpenChanged = pyqtSignal()

    def __init__(self, char_data, global_config):
        super().__init__()
        self.char_data = char_data
        self.global_config = global_config
        active = char_data["active"]
        self.config = char_data["characters"][active]
        self.completed_data = self.config.get("completed_data", {})
        self.auto_completed_steps = set(int(k) for k in self.completed_data.keys())
        self.highwater_mark = self.config.get("highwater_mark", 0)
        self._auto_step = self.config.get("auto_step", self.config.get("current_step", 0))
        self._view_step = self._auto_step
        self._window = None
        self._current_zone = "Waiting..."
        self._substeps = []
        self._html_cache = {}
        self._target_height = 200
        self._update_current = ""
        self._update_latest = ""
        self._update_changelog = ""
        self._update_release_url = ""
        self._show_update_popup = False
        self._profile_modal_open = False
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
        return self._view_step

    @pyqtProperty(int, notify=currentStepIndexChanged)
    def totalSteps(self):
        return len(WALKTHROUGH)

    @pyqtProperty(bool, notify=currentStepIndexChanged)
    def isBrowsing(self):
        return self._view_step != self._auto_step

    def set_auto_step(self, value):
        if value < 0 or value >= len(WALKTHROUGH):
            return
        if value > self.highwater_mark:
            self.highwater_mark = value
            self.config["highwater_mark"] = value
        self._auto_step = value
        self.config["auto_step"] = value
        self._view_step = value
        self.config["current_step"] = value
        self.request_save()
        self.currentStepIndexChanged.emit()
        self.actTitleChanged.emit()
        self.actInfoChanged.emit()
        self.update_substeps()

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
        if 0 <= step_idx < len(WALKTHROUGH):
            act_num = WALKTHROUGH[step_idx].get("act", 1)
            act_steps = [i for i, s in enumerate(WALKTHROUGH) if s.get("act", 1) == act_num]
            act_pos = act_steps.index(step_idx) if step_idx in act_steps else 0
            return act_num, act_pos, len(act_steps)
        return (1, 0, len(WALKTHROUGH))

    def _step_to_act(self, step_idx):
        for act_num, start, end in ACT_BOUNDARIES:
            if start <= step_idx <= end:
                return act_num
        return 1

    @pyqtProperty(int, notify=actInfoChanged)
    def currentActNumber(self):
        idx = self.currentStepIndex
        if 0 <= idx < len(WALKTHROUGH):
            return WALKTHROUGH[idx].get("act", 1)
        return 1

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
            if self._view_step < len(WALKTHROUGH) - 1:
                self._view_step += 1
                self.currentStepIndexChanged.emit()
                self.actTitleChanged.emit()
                self.actInfoChanged.emit()
                self.update_substeps()
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
        if self._view_step > 0:
            self._view_step -= 1
            self.currentStepIndexChanged.emit()
            self.actTitleChanged.emit()
            self.actInfoChanged.emit()
            self.update_substeps()

    @pyqtSlot()
    def onNextStep(self):
        if self._view_step < len(WALKTHROUGH) - 1:
            self._view_step += 1
            self.currentStepIndexChanged.emit()
            self.actTitleChanged.emit()
            self.actInfoChanged.emit()
            self.update_substeps()

    # ── Font size (step 1, min 9, max 16) ────────────────────────────

    @pyqtSlot()
    def increaseFontSize(self):
        new_size = min(16, self.global_config.get("base_font_size", 13) + 1)
        self.global_config["base_font_size"] = new_size
        self.request_save()
        self.baseFontSizeChanged.emit()
        self.recalculate_height()

    @pyqtSlot()
    def decreaseFontSize(self):
        new_size = max(9, self.global_config.get("base_font_size", 13) - 1)
        self.global_config["base_font_size"] = new_size
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
            self.global_config["window_x"] = self._window.x()
            self.global_config["window_y"] = self._window.y()
            self.request_save()

    # ── Window geometry properties ────────────────────────────────────

    @pyqtProperty(int, notify=windowPosChanged)
    def windowX(self): return self.global_config.get("window_x", 100)
    @pyqtProperty(int, notify=windowPosChanged)
    def windowY(self): return self.global_config.get("window_y", 100)
    @pyqtProperty(int, notify=windowSizeChanged)
    def windowWidth(self): return self.global_config.get("window_width", 400)
    @pyqtProperty(int, notify=windowSizeChanged)
    def windowHeight(self): return self.global_config.get("window_height", 250)

    @pyqtSlot(int, int)
    def updateWindowPos(self, x, y):
        self.global_config["window_x"] = x
        self.global_config["window_y"] = y
        self.request_save()
        self.windowPosChanged.emit()

    @pyqtProperty(float, notify=opacityChanged)
    def opacity(self): return self.global_config.get("opacity", 0.85)

    @pyqtSlot(float)
    def adjustOpacity(self, delta):
        new_op = max(0.2, min(1.0, self.opacity + delta))
        self.global_config["opacity"] = new_op
        self.request_save()
        self.opacityChanged.emit()

    @pyqtProperty(int, notify=baseFontSizeChanged)
    def baseFontSize(self): return self.global_config.get("base_font_size", 13)

    # ── Height auto-sizing ────────────────────────────────────────────
    # Formula: titlebar(26) + updateBar(22 if visible) + topbar(22) + divider(1)
    #          + topPadding(6) + n*(fs+6) + spacing*(n-1)*3 + bottomPadding(6)

    @pyqtSlot()
    def recalculate_height(self):
        n = len(self._substeps)
        fs = self.global_config.get("base_font_size", 13)
        w = self.global_config.get("window_width", 400)
        sidebar_width = 36
        padding = 16
        icon_width = 20
        available = max(1, w - sidebar_width - padding - icon_width)
        chars_per_line = max(1, int(available / (fs * 0.55)))
        h = 32 + 22 + 1 + 6
        for substep in self._substeps:
            plain = re.sub(r'<[^>]+>', '', substep["text"])
            line_count = max(1, math.ceil(len(plain) / chars_per_line))
            h += (fs + 4) * line_count + 6
        h += max(0, n - 1) * 6
        h += 6
        h = max(120, h)
        if h != self._target_height:
            if self._window:
                # Keep bottom edge fixed: window grows/shrinks upward
                current_bottom = self._window.y() + self._target_height
                new_y = current_bottom - h
                self.global_config["window_y"] = new_y
                self.windowPosChanged.emit()
            self._target_height = h
            self.targetHeightChanged.emit()

    # ── Reset ─────────────────────────────────────────────────────────

    @pyqtSlot()
    def resetProgress(self):
        self._auto_step = 0
        self._view_step = 0
        self.config["auto_step"] = 0
        self.config["current_step"] = 0
        self.highwater_mark = 0
        self.config["highwater_mark"] = 0
        self.completed_data = {}
        self.config["completed_data"] = {}
        self.auto_completed_steps = set()
        self.request_save()
        self.currentStepIndexChanged.emit()
        self.actTitleChanged.emit()
        self.actInfoChanged.emit()
        self.update_substeps()

    # ── Profile modal ─────────────────────────────────────────────────

    @pyqtProperty(bool, notify=profileModalOpenChanged)
    def profileModalOpen(self):
        return self._profile_modal_open

    @pyqtSlot()
    def openProfileModal(self):
        self._profile_modal_open = True
        self.profileModalOpenChanged.emit()

    @pyqtSlot()
    def closeProfileModal(self):
        self._profile_modal_open = False
        self.profileModalOpenChanged.emit()

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
        self._auto_step = self.config.get("auto_step", self.config.get("current_step", 0))
        self._view_step = self._auto_step
        self._html_cache = {}
        save_characters(self.char_data)
        self.currentStepIndexChanged.emit()
        self.actTitleChanged.emit()
        self.actInfoChanged.emit()
        self.characterListChanged.emit()
        self.closeProfileModal()
        self.update_substeps()

    @pyqtSlot(str)
    def addCharacter(self, name):
        name = name.strip()
        if not name:
            return
        add_character(self.char_data, name)
        save_characters(self.char_data)
        self.characterListChanged.emit()
        self.switchCharacter(name)

    @pyqtSlot(str)
    def deleteCharacter(self, name):
        chars = self.char_data.get("characters", {})
        if len(chars) <= 1:
            return
        active = self.char_data.get("active")
        delete_character(self.char_data, name)
        # Safety net: ensure at least one profile always exists
        if not self.char_data.get("characters"):
            self.char_data["characters"] = {"Default": {
                "current_step": 0,
                "completed_data": {},
                "highwater_mark": 0,
            }}
            self.char_data["active"] = "Default"
        save_characters(self.char_data)
        if name == active:
            new_active = self.char_data.get("active")
            self.config = self.char_data["characters"][new_active]
            self.completed_data = self.config.get("completed_data", {})
            self.auto_completed_steps = set(int(k) for k in self.completed_data.keys())
            self.highwater_mark = self.config.get("highwater_mark", 0)
            self._auto_step = self.config.get("auto_step", self.config.get("current_step", 0))
            self._view_step = self._auto_step
            self._html_cache = {}
            self.currentStepIndexChanged.emit()
            self.actTitleChanged.emit()
            self.actInfoChanged.emit()
            self.update_substeps()
        self.characterListChanged.emit()

    # ── Update checker ────────────────────────────────────────────────

    @pyqtProperty(bool, notify=updateAvailableChanged)
    def showUpdatePopup(self):
        return self._show_update_popup

    @pyqtProperty(str, notify=updateAvailableChanged)
    def updateCurrent(self):
        return self._update_current

    @pyqtProperty(str, notify=updateAvailableChanged)
    def updateLatest(self):
        return self._update_latest

    @pyqtProperty(str, notify=updateAvailableChanged)
    def updateChangelog(self):
        return self._update_changelog

    @pyqtSlot(str, str, str, str)
    def setUpdateAvailable(self, current, latest, changelog, url):
        self._update_current = current
        self._update_latest = latest
        self._update_changelog = changelog
        self._update_release_url = url
        self._show_update_popup = True
        self.updateAvailableChanged.emit()

    @pyqtSlot()
    def acceptUpdate(self):
        import subprocess
        subprocess.Popen(["xdg-open", self._update_release_url])
        self._show_update_popup = False
        self.updateAvailableChanged.emit()

    @pyqtSlot()
    def dismissUpdate(self):
        self.global_config["update_dismissed_version"] = self._update_latest
        self.request_save()
        self._show_update_popup = False
        self.updateAvailableChanged.emit()


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
            for key in ["current_step", "completed_data", "highwater_mark"]:
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
        root.setProperty("width", self.bridge.global_config.get("window_width", 400))
        root.setProperty("x", self.bridge.global_config.get("window_x", 100))
        root.setProperty("y", self.bridge.global_config.get("window_y", 100))
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
        QTimer.singleShot(4000, self.check_for_updates)

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
            self.bridge.global_config["window_width"] = w.width()
            self.bridge.request_save()

    def check_for_updates(self):
        try:
            import urllib.request
            import json

            version_file = os.path.join(os.path.dirname(__file__), "version.txt")
            if not os.path.exists(version_file):
                return
            with open(version_file) as f:
                current_version = f.read().strip()

            dismissed = self.global_config.get("update_dismissed_version", "")

            url = "https://api.github.com/repos/dominikzone/Tuxile-ActRunner/releases/latest"
            req = urllib.request.Request(
                url, headers={"User-Agent": "TuxileActRunner/" + current_version}
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read())

            latest_version = data.get("tag_name", "").lstrip("v").strip()
            changelog = data.get("body", "No changelog available.").strip()
            release_url = data.get("html_url",
                "https://github.com/dominikzone/Tuxile-ActRunner/releases/latest")

            if not latest_version:
                return
            if latest_version == current_version:
                return
            if latest_version == dismissed:
                return

            self.bridge.setUpdateAvailable(
                current_version, latest_version, changelog, release_url
            )

        except Exception as e:
            print(f"Update check failed (no internet?): {e}")

    def _get_act_for_step(self, step_idx):
        if 0 <= step_idx < len(WALKTHROUGH):
            return WALKTHROUGH[step_idx].get("act", 1)
        return 1

    def on_zone_changed(self, zone_name):
        self.bridge.currentZone = zone_name

        # Get current act
        current_act = WALKTHROUGH[self.bridge._auto_step].get("act", 1) \
            if 0 <= self.bridge._auto_step < len(WALKTHROUGH) else 1

        for i, step in enumerate(WALKTHROUGH):
            # Match by zone name
            log_name = step.get("log_zone", step["zone"])
            if log_name.lower() != zone_name.lower():
                # Also check also_triggers_on list
                also = step.get("also_triggers_on", [])
                if not any(z.lower() == zone_name.lower() for z in also):
                    continue

            step_act = step.get("act", 1)

            # Skip steps from previous acts
            if step_act < current_act:
                continue

            # Skip steps too far ahead (more than 1 act forward)
            if step_act > current_act + 1:
                continue

            # Only advance forward — never go back automatically
            if i < self.bridge._auto_step:
                continue

            # Match found — advance
            self.bridge.set_auto_step(i)
            break

    def on_waypoint_discovered(self): pass
    def on_quest_item_found(self, item_name): pass
    def on_quest_completed(self, quest_name): pass
    def on_boss_slain(self, boss_name): pass
    def on_trial_completed(self, trial_name): pass

    def cleanup(self):
        if hasattr(self, 'watcher'):
            self.watcher.requestInterruption()
            self.watcher.wait(2000)

    def run(self):
        return self.app.exec()


if __name__ == "__main__":
    poe_app = PoEApp()
    sys.exit(poe_app.run())
