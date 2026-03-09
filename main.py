import sys
import os
import re
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFileDialog, QGraphicsDropShadowEffect, QProgressBar, QSizePolicy
from PyQt6.QtCore import Qt, QPoint, QRect, QSize, QPropertyAnimation, QEasingCurve, QTimer
from PyQt6.QtGui import QFont, QPalette, QColor, QKeyEvent, QWheelEvent

from config_manager import load_config, save_config
from walkthrough_data import WALKTHROUGH, TOWNS
from log_watcher import LogWatcher

class PoEOverlay(QWidget):
    def __init__(self):
        super().__init__()
        self.config = load_config()
        self.is_moving = False
        self.is_resizing = False
        self.drag_start_pos = QPoint()
        self.window_start_rect = QRect()
        
        # Load persistent completion data
        self.completed_data = self.config.get("completed_data", {})
        self.sync_current_completed_set()
        self.app_version = "v00.02" # Application version

        self.boss_names_for_log_watcher = set()
        for step_data in WALKTHROUGH:
            text = step_data.get("text", "")
            # More specific regex for boss names, avoiding common words or numbers
            # This regex will capture words or phrases after "Kill " and before a punctuation or keyword
            boss_matches = re.findall(r"Kill ([A-Za-z][a-zA-Z' -]+?)(?:\.|,| for |\[SKILL\]|\n)", text)
            for boss in boss_matches:
                # Exclude generic terms and ensure it's not just a number or very short word
                if boss.strip().lower() not in ["hillock", "crab", "spider", "guards", "general", "overseer", "puppet mistress", "brutus & shavronne", "solaris & lunaris", "depraved trinity", "all monsters", "justicar", "gemling legion", "infernal king", "dusk", "dawn"] and len(boss.strip()) > 2: # Added more exclusions and length check
                    self.boss_names_for_log_watcher.add(boss.strip())
            
            # Additional extraction for specific boss names explicitly mentioned
            specific_bosses_list = ["Hillock", "Hailrake", "Brutus", "Merveil", "Fidelitas", "White Beast", "Vaal Oversoul", "Doedre", "Maligaro", "Shavronne", "Malachai", "Avarius", "Kitava", "Dishonored Queen", "Tukohama", "Abberath", "Puppet Mistress", "Brine King", "Greust", "Gruthkul", "Arakaali", "Dusk", "Dawn", "Shakari", "Basilisk", "Depraved Trinity", "Vilenta", "Gemling Legion", "Infernal King"]
            for boss in specific_bosses_list:
                if f"Kill {boss}" in text:
                    self.boss_names_for_log_watcher.add(boss)


        self.init_ui()
        self.setup_log_watcher()
        self.scan_log_history()

    def sync_current_completed_set(self):
        step_idx = str(self.config["current_step"])
        self.completed_substeps = set(self.completed_data.get(step_idx, []))

    def save_completed_data(self):
        step_idx = str(self.config["current_step"])
        self.completed_data[step_idx] = list(self.completed_substeps)
        self.config["completed_data"] = self.completed_data
        save_config(self.config)

    def init_ui(self):
        # Window Flags
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.apply_click_through()
        
        # Initial Geometry (will be adjusted dynamically)
        self.setGeometry(
            self.config["window_x"], 
            self.config["window_y"], 
            self.config.get("window_width", 400), # Default width
            self.config.get("window_height", 200) # Default height
        )
        self.setMinimumWidth(300)

        # Animation for smooth resizing
        self.size_animation = QPropertyAnimation(self, b"size")
        self.size_animation.setDuration(150)  # milliseconds
        self.size_animation.setEasingCurve(QEasingCurve.Type.OutQuad)

        # Layout
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout)

        # Content Widget (for background styling)
        self.content_container = QWidget()
        self.container_layout = QVBoxLayout()
        self.container_layout.setSpacing(2)
        self.container_layout.setContentsMargins(15, 15, 15, 15)
        self.content_container.setLayout(self.container_layout)
        self.main_layout.addWidget(self.content_container)

        # Controls Row (Moved to Top)
        self.controls_widget = QWidget()
        self.controls_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.controls_widget.setFixedHeight(30)
        self.controls_layout = QHBoxLayout()
        self.controls_layout.setContentsMargins(10, 0, 10, 0)
        self.controls_layout.setSpacing(10)
        self.controls_widget.setLayout(self.controls_layout)
        
        self.move_label = QLabel("MOVE")
        self.move_label.setToolTip("Ctrl + LMB to move")
        self.move_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.btn_prev = QLabel("<")
        self.btn_prev.setToolTip("Ctrl + LMB to go back")
        self.btn_prev.setFixedWidth(20)
        self.btn_prev.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.btn_next = QLabel(">")
        self.btn_next.setToolTip("Ctrl + LMB to go forward")
        self.btn_next.setFixedWidth(20)
        self.btn_next.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.btn_font_decrease = QLabel("-")
        self.btn_font_decrease.setToolTip("Ctrl + LMB to decrease font size")
        self.btn_font_decrease.setFixedWidth(20)
        self.btn_font_decrease.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.label_font_f = QLabel("F")
        self.label_font_f.setFixedWidth(20)
        self.label_font_f.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.btn_font_increase = QLabel("+")
        self.btn_font_increase.setToolTip("Ctrl + LMB to increase font size")
        self.btn_font_increase.setFixedWidth(20)
        self.btn_font_increase.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.close_btn = QLabel("X")
        self.close_btn.setToolTip("Click to close")
        self.close_btn.setFixedWidth(20)
        self.close_btn.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.close_btn.setStyleSheet("color: #ff4d4d; font-weight: bold; font-size: 14px; padding: 2px;")
        
        self.controls_layout.addWidget(self.move_label)
        self.controls_layout.addWidget(self.btn_prev)
        self.controls_layout.addWidget(self.btn_next)
        self.controls_layout.addSpacing(10)
        self.controls_layout.addWidget(self.btn_font_decrease)
        self.controls_layout.addWidget(self.label_font_f)
        self.controls_layout.addWidget(self.btn_font_increase)
        self.controls_layout.addStretch()
        self.btn_reset = QLabel("R")
        self.btn_reset.setToolTip("Ctrl + LMB to reset player progress")
        self.btn_reset.setFixedWidth(20)
        self.btn_reset.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.controls_layout.addWidget(self.btn_reset)
        self.controls_layout.addWidget(self.close_btn)
        
        self.container_layout.addWidget(self.controls_widget)

        # Top Row (Zone Display)
        self.top_layout = QHBoxLayout()
        self.top_layout.setContentsMargins(0, 0, 0, 0)
        
        # Zone Display
        self.zone_display = QLabel("Location: Waiting...")
        self.zone_display.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.zone_display.setStyleSheet("font-size: 10px; color: #888888;")
        self.top_layout.addWidget(self.zone_display)
        
        self.container_layout.addLayout(self.top_layout)

        # Target Info Row (New)
        self.target_info_layout = QVBoxLayout()
        self.target_info_layout.setSpacing(2)
        
        self.quest_label = QLabel("")
        self.quest_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.quest_label.setStyleSheet("color: #FFD700; font-weight: bold; font-size: 13px; letter-spacing: 1px;")
        
        self.target_zone_label = QLabel("")
        self.target_zone_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.target_zone_label.setStyleSheet("color: #888888; font-style: italic; font-size: 11px;")
        
        self.target_info_layout.addWidget(self.quest_label)
        self.target_info_layout.addWidget(self.target_zone_label)
        
        # Separator line
        self.line = QLabel()
        self.line.setFixedHeight(1)
        self.line.setStyleSheet("background-color: rgba(255, 215, 0, 40);")
        self.target_info_layout.addWidget(self.line)
        
        self.container_layout.addLayout(self.target_info_layout)

        # Step Text
        self.step_label = QLabel()
        self.step_label.setWordWrap(True)
        self.step_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.step_label.linkActivated.connect(self.on_task_clicked)
        self.step_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.MinimumExpanding)
        self.step_label.adjustSize()
        
        # Text Shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(6)
        shadow.setXOffset(1)
        shadow.setYOffset(1)
        shadow.setColor(QColor(0, 0, 0, 255))
        self.step_label.setGraphicsEffect(shadow)
        
        self.container_layout.addWidget(self.step_label)

        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(5)
        self.version_layout = QHBoxLayout()
        self.version_label = QLabel(self.app_version)
        self.version_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)
        self.version_label.setStyleSheet("font-size: 8px; color: #555555; margin-right: 5px; margin-bottom: 2px;")
        self.version_layout.addStretch()
        self.version_layout.addWidget(self.version_label)
        self.container_layout.addLayout(self.version_layout)

        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(5)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar { border: 1px solid rgba(255, 215, 0, 30); background-color: rgba(0,0,0,100); border-radius: 2px; }
            QProgressBar::chunk { background-color: #FFD700; }
        """)
        self.container_layout.addWidget(self.progress_bar)


        # Auto-hide controls
        self.controls_widget.setGraphicsEffect(None) # Reset
        self.controls_widget.setVisible(False)

        self.apply_theme()
        self.update_step_ui()

    def on_task_clicked(self, link):
        try:
            task_idx = int(link)
            if task_idx in self.completed_substeps:
                self.completed_substeps.remove(task_idx)
            else:
                self.completed_substeps.add(task_idx)
            
            self.save_completed_data()
            self.update_step_ui()
            self.check_auto_advance()
        except ValueError:
            pass

    def scan_log_history(self):
        path = self.config.get("client_txt_path")
        if not path or not os.path.exists(path):
            return

        try:
            # Read last 50KB of log to catch recent context
            file_size = os.path.getsize(path)
            read_size = min(file_size, 50000)
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                f.seek(file_size - read_size)
                lines = f.readlines()
                
                found_zone = None
                found_wps = False
                
                for line in lines:
                    # Zone check
                    zone_match = re.search(r" : You have entered (.*?)\.", line)
                    if zone_match:
                        found_zone = zone_match.group(1).strip()
                    
                    # WP check
                    if " : You have discovered a waypoint" in line:
                        found_wps = True
                
                if found_zone:
                    # Silently update zone logic
                    self.current_zone = found_zone
                    self.zone_display.setText(f"Location: {found_zone}")
                    for i, step in enumerate(WALKTHROUGH):
                        if step["zone"].lower() == found_zone.lower():
                            if self.config["current_step"] != i:
                                self.config["current_step"] = i
                                self.sync_current_completed_set()
                            break
                
                if found_wps:
                    self.on_waypoint_discovered()
                    
            self.update_step_ui()
        except Exception as e:
            print(f"Error scanning log history: {e}")

    def apply_click_through(self):
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, self.config.get("click_through", False))

    def apply_theme(self):
        # Exile Dark Theme Colors
        alpha = int(self.config.get("opacity", 0.85) * 255)
        bg_color = f"rgba(25, 25, 25, {alpha})" # Slightly darker
        text_color = "#f8f8f2" # Cleaner white-ish
        accent_color = "#FFD700" # Gold

        self.content_container.setStyleSheet(f"""
            QWidget {{
                background-color: {bg_color};
                border: 2px solid {accent_color};
                border-radius: 8px;
            }}
            QLabel {{
                color: {text_color};
                background: transparent;
                border: none;
            }}
        """)
        
        # Highlight interactive labels
        control_style = f"color: {accent_color}; font-weight: bold; font-size: 13px;"
        hover_style = f"background-color: rgba(255, 215, 0, 30); border-radius: 3px;"

        self.move_label.setStyleSheet(f"QLabel {{ {control_style} }} QLabel:hover {{ {hover_style} }}")
        self.btn_prev.setStyleSheet(f"QLabel {{ color: {accent_color}; font-weight: bold; font-size: 18px; padding: 0 5px; }} QLabel:hover {{ {hover_style} }}")
        self.btn_next.setStyleSheet(f"QLabel {{ color: {accent_color}; font-weight: bold; font-size: 18px; padding: 0 5px; }} QLabel:hover {{ {hover_style} }}")
        self.btn_font_decrease.setStyleSheet(f"QLabel {{ {control_style} }} QLabel:hover {{ {hover_style} }}")
        self.label_font_f.setStyleSheet(f"QLabel {{ {control_style} }}")
        self.btn_font_increase.setStyleSheet(f"QLabel {{ {control_style} }} QLabel:hover {{ {hover_style} }}")
        self.btn_reset.setStyleSheet(f"QLabel {{ color: #4da6ff; font-weight: bold; font-size: 14px; padding: 2px; }} QLabel:hover {{ background-color: rgba(77, 166, 255, 50); border-radius: 3px; }}")
        self.close_btn.setStyleSheet(f"QLabel {{ color: #ff4d4d; font-weight: bold; font-size: 14px; padding: 2px; }} QLabel:hover {{ background-color: rgba(255, 77, 77, 50); border-radius: 3px; }}")


    def update_step_ui(self):
        idx = self.config["current_step"]
        if 0 <= idx < len(WALKTHROUGH):
            step = WALKTHROUGH[idx]
            text = step["text"]
            
            # Update Quest and Target Zone labels
            self.quest_label.setText(step.get("quest", "Main Quest").upper())
            self.target_zone_label.setText(f"OBJECTIVE: {step['zone']}")
            
            # Styling constants
            wp_style = "background-color: #2b5b84; color: #4da6ff; border-radius: 3px; padding: 1px 3px; font-weight: bold;"
            q_style = "background-color: #5b5b00; color: #ffff00; border-radius: 3px; padding: 1px 3px; font-weight: bold;"
            skill_style = "background-color: #1e4620; color: #33ff33; border-radius: 3px; padding: 1px 3px; font-weight: bold;"
            
            # Keyword Highlighting with Badges
            text = text.replace("[WP]", f"<span style=\'{wp_style}\'>WP</span>")
            text = text.replace("[Q]", f"<span style=\'{q_style}\'>Q</span>")
            text = text.replace("[SKILL]", f"<span style=\'{skill_style}\'>SKILL</span>")
            text = text.replace("ACT ", "<b><span style=\'color: #FFD700;\'>ACT </span></b>")

            # Action Color Palette
            actions_red = ["Kill", "Defeat", "Clear", "Slay"]
            actions_green = ["Help", "Talk", "Quest", "Reward"]
            actions_blue = ["Go to", "Enter", "Travel"]
            
            # Bandit Check
            if any(bandit in text for bandit in ["Bandits", "Kraityn", "Alira", "Oak"]):
                text += "<br><br><b style=\'color: #ff4d4d;\'>➜ KILL ALL or CHECK YOUR POB</b>"

            for action in actions_red:
                text = re.sub(rf"\b{action}\b", f"<span style=\'color: #ff4d4d; font-weight: bold;\'>{action}</span>", text)
            for action in actions_green:
                text = re.sub(rf"\b{action}\b", f"<span style=\'color: #50fa7b; font-weight: bold;\'>{action}</span>", text)
            for action in actions_blue:
                text = re.sub(rf"\b{action}\b", f"<span style=\'color: #4da6ff; font-weight: bold;\'>{action}</span>", text)

            # Bullet points and Line Height
            lines = [line.strip() for line in text.split(".") if line.strip()]
            if len(lines) > 1:
                formatted_text = "<ul style=\'margin-left: -20px; line-height: 130%;\'>"
                for i, line in enumerate(lines):
                    style = "color: #f8f8f2;" # Default color
                    if i in self.completed_substeps:
                        style = "text-decoration: line-through; color: #555555;"
                    formatted_text += f"<li style=\'margin-bottom: 4px;\'><a href=\'{i}\' style=\'text-decoration: none; {style}\'>{line}</a></li>"
                formatted_text += "</ul>"
            else:
                style = "color: #f8f8f2;"
                if 0 in self.completed_substeps:
                    style = "text-decoration: line-through; color: #555555;"
                formatted_text = f"<div style=\'line-height: 130%;\'><a href=\'0\' style=\'text-decoration: none; {style}\'>{text}</a></div>"
            
            # Town status check
            if hasattr(self, 'current_zone') and self.current_zone in TOWNS:
                formatted_text += "<br><div style=\'font-size: 11px; color: #FFD700; border-top: 1px solid rgba(255,215,0,30); padding-top: 4px;\'>➜ IN TOWN: Get Quests</div>"

            self.step_label.setText(f"<html><body>{formatted_text}</body></html>")
            
            # Progress Bar
            self.progress_bar.setMaximum(len(WALKTHROUGH) - 1)
            self.progress_bar.setValue(idx)
        self.adjust_window_size()
        
        self.scale_font()

    def scale_font(self):
        # Base font size and scaling factor
        base_font_size = self.config.get("base_font_size", 12)
        current_width = self.width()

        # Simple scaling based on width, can be refined
        scale_factor = current_width / 400 # Assuming 400 is a good base width
        new_font_size = max(8, int(base_font_size * scale_factor))

        font = QFont()
        font.setPointSize(new_font_size)

        # Apply to relevant labels
        self.step_label.setFont(font)

        # Scale other labels proportionally or with different base sizes if needed
        quest_font = QFont()
        quest_font.setPointSize(max(8, int(13 * scale_factor)))
        self.quest_label.setFont(quest_font)

        target_zone_font = QFont()
        target_zone_font.setPointSize(max(8, int(11 * scale_factor)))
        self.target_zone_label.setFont(target_zone_font)

        # Update other labels as necessary
        control_font = QFont()
        control_font.setPointSize(max(8, int(13 * scale_factor)))
        self.move_label.setFont(control_font)
        self.btn_prev.setFont(control_font)
        self.btn_next.setFont(control_font)
        self.btn_font_decrease.setFont(control_font)
        self.label_font_f.setFont(control_font)
        self.btn_font_increase.setFont(control_font)

        reset_font = QFont()
        reset_font.setPointSize(max(8, int(14 * scale_factor)))
        self.btn_reset.setFont(reset_font)

        close_font = QFont()
        close_font.setPointSize(max(8, int(14 * scale_factor)))
        self.close_btn.setFont(close_font)

        zone_display_font = QFont()
        zone_display_font.setPointSize(max(6, int(10 * scale_factor)))
        self.zone_display.setFont(zone_display_font)


    def setup_log_watcher(self):
        path = self.config["client_txt_path"]
        if not path or not os.path.exists(path):
            # Try common paths
            home = os.path.expanduser("~")
            common_paths = [
                "/mnt/a24ff19e-fc7e-47ad-a274-4c1eb1999c3a/SteamLibrary/steamapps/common/Path of Exile/logs/Client.txt",
                f"{home}/.local/share/Steam/steamapps/compatdata/238960/pfx/drive_c/Program Files (x86)/Grinding Gear Games/Path of Exile/logs/Client.txt",
                f"{home}/.steam/steam/steamapps/compatdata/238960/pfx/drive_c/Program Files (x86)/Grinding Gear Games/Path of Exile/logs/Client.txt"
            ]
            for p in common_paths:
                if os.path.exists(p):
                    path = p
                    self.config["client_txt_path"] = path
                    save_config(self.config)
                    break
        
        if not path or not os.path.exists(path):
            # We will prompt later or just wait for manual selection
            pass
        else:
            self.watcher = LogWatcher(path, list(self.boss_names_for_log_watcher)) # Pass boss names
            self.watcher.zone_changed.connect(self.on_zone_changed)
            self.watcher.waypoint_discovered.connect(self.on_waypoint_discovered)
            self.watcher.quest_item_found.connect(self.on_quest_item_found) # New connection
            self.watcher.quest_completed.connect(self.on_quest_completed)     # New connection
            self.watcher.boss_slain.connect(self.on_boss_slain)               # New connection
            self.watcher.trial_completed.connect(self.on_trial_completed)     # New connection
            self.watcher.start()

    def on_waypoint_discovered(self):
        # Mark WP tasks as done
        idx = self.config["current_step"]
        if 0 <= idx < len(WALKTHROUGH):
            step = WALKTHROUGH[idx]
            text = step["text"]
            lines = [line.strip() for line in text.split(".") if line.strip()]
            for i, line in enumerate(lines):
                if "[WP]" in line or "waypoint" in line.lower():
                    self.completed_substeps.add(i)
            
            self.save_completed_data() # Save after marking completion
            self.update_step_ui()
            self.check_auto_advance()

    def on_quest_item_found(self, item_name):
        idx = self.config["current_step"]
        if 0 <= idx < len(WALKTHROUGH):
            step = WALKTHROUGH[idx]
            text = step["text"]
            lines = [line.strip() for line in text.split(".") if line.strip()]
            for i, line in enumerate(lines):
                if item_name.lower() in line.lower() and "[Q]" in line:
                    self.completed_substeps.add(i)
            
            self.save_completed_data()
            self.update_step_ui()
            self.check_auto_advance()

    def on_quest_completed(self, quest_name):
        idx = self.config["current_step"]
        if 0 <= idx < len(WALKTHROUGH):
            step = WALKTHROUGH[idx]
            text = step["text"]
            lines = [line.strip() for line in text.split(".") if line.strip()]
            for i, line in enumerate(lines):
                # Match quest name from log to quest in walkthrough text or quest field
                if quest_name.lower() in line.lower() or (step.get("quest", "").lower() == quest_name.lower()):
                    self.completed_substeps.add(i)
            
            self.save_completed_data()
            self.update_step_ui()
            self.check_auto_advance()

    def on_boss_slain(self, boss_name):
        idx = self.config["current_step"]
        if 0 <= idx < len(WALKTHROUGH):
            step = WALKTHROUGH[idx]
            text = step["text"]
            lines = [line.strip() for line in text.split(".") if line.strip()]
            for i, line in enumerate(lines):
                if boss_name.lower() in line.lower():
                    self.completed_substeps.add(i)
            
            self.save_completed_data()
            self.update_step_ui()
            self.check_auto_advance()

    def on_trial_completed(self, trial_name):
        idx = self.config["current_step"]
        if 0 <= idx < len(WALKTHROUGH):
            step = WALKTHROUGH[idx]
            text = step["text"]
            lines = [line.strip() for line in text.split(".") if line.strip()]
            for i, line in enumerate(lines):
                if trial_name.lower() in line.lower() and "[TRIAL" in line.upper():
                    self.completed_substeps.add(i)
            
            self.save_completed_data()
            self.update_step_ui()
            self.check_auto_advance()

    def check_auto_advance(self):
        idx = self.config["current_step"]
        if 0 <= idx < len(WALKTHROUGH):
            step = WALKTHROUGH[idx]
            text = step["text"]
            total_lines = len([line.strip() for line in text.split(".") if line.strip()])
            if len(self.completed_substeps) >= total_lines and total_lines > 0:
                if idx < len(WALKTHROUGH) - 1:
                    self.config["current_step"] += 1
                    self.completed_substeps = set() # Reset for next step
                    self.update_step_ui()
                    save_config(self.config)
                    self.adjust_window_size()

    def on_zone_changed(self, zone_name):
        self.current_zone = zone_name
        self.zone_display.setText(f"Location: {zone_name}")
        
        # Check if this zone completion marks a substep as done
        idx = self.config["current_step"]
        if 0 <= idx < len(WALKTHROUGH):
            step = WALKTHROUGH[idx]
            text = step["text"]
            lines = [line.strip() for line in text.split(".") if line.strip()]
            for i, line in enumerate(lines):
                if zone_name.lower() in line.lower() or ("town" in line.lower() and zone_name in TOWNS):
                    self.completed_substeps.add(i)
        
        self.update_step_ui()
        self.check_auto_advance()
        
        # Town Logic: If it's a town, don't change anything but update UI status
        if zone_name in TOWNS:
            return

        # Find the step for this zone (original auto-sync logic)
        for i, step in enumerate(WALKTHROUGH):
            if step["zone"].lower() == zone_name.lower():
                if self.config["current_step"] != i:
                    self.config["current_step"] = i
                    self.completed_substeps = set() # Reset on major zone change
                    self.update_step_ui()
                    save_config(self.config)
                    self.adjust_window_size()
                break

    def enterEvent(self, event):
        # Show controls on hover
        self.controls_widget.setVisible(True)
        self.close_btn.setVisible(True)
        super().enterEvent(event)

    def leaveEvent(self, event):
        # Hide controls when not hovering
        self.controls_widget.setVisible(False)
        self.close_btn.setVisible(False)
        super().leaveEvent(event)
        self.adjust_window_size()

    def wheelEvent(self, event: QWheelEvent):
        # Change opacity with Ctrl + Scroll
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            delta = event.angleDelta().y()
            current_op = self.config.get("opacity", 0.85)
            if delta > 0:
                current_op = min(1.0, current_op + 0.05)
            else:
                current_op = max(0.2, current_op - 0.05)
            
            self.config["opacity"] = current_op
            self.apply_theme()
            save_config(self.config)
        super().wheelEvent(event)

    def mousePressEvent(self, event):
        # Always allow closing with X even without Ctrl
        if event.button() == Qt.MouseButton.LeftButton:
            if self.close_btn.underMouse():
                self.close()
                return

        # Support for navigation and interactions (Require Ctrl)
        if event.button() == Qt.MouseButton.LeftButton and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            pos = event.position().toPoint()
            
            # Check for Navigation
            if self.btn_prev.underMouse():
                if self.config["current_step"] > 0:
                    self.config["current_step"] -= 1
                    self.update_step_ui()
                    save_config(self.config)
                    self.adjust_window_size()
            
            elif self.btn_next.underMouse():
                if self.config["current_step"] < len(WALKTHROUGH) - 1:
                    self.config["current_step"] += 1
                    self.update_step_ui()
                    save_config(self.config)
                    self.adjust_window_size()

            # Check for Move label
            elif self.move_label.underMouse():
                self.is_moving = True
                self.drag_start_pos = event.globalPosition().toPoint()
                self.window_start_rect = self.geometry()
            
            elif self.btn_reset.underMouse():
                self.reset_player_progress()

            elif self.btn_font_decrease.underMouse():
                current_font_size = self.config.get("base_font_size", 12)
                new_font_size = max(8, current_font_size - 2)
                if new_font_size != current_font_size:
                    self.config["base_font_size"] = new_font_size
                    save_config(self.config)
                    self.scale_font()
                    self.adjust_window_size()

            elif self.btn_font_increase.underMouse():
                current_font_size = self.config.get("base_font_size", 12)
                new_font_size = min(30, current_font_size + 2)
                if new_font_size != current_font_size:
                    self.config["base_font_size"] = new_font_size
                    save_config(self.config)
                    self.scale_font()
                    self.adjust_window_size()


    def keyPressEvent(self, event: QKeyEvent):
        ctrl = event.modifiers() == Qt.KeyboardModifier.ControlModifier
        
        # Exit (Ctrl + Q)
        if ctrl and event.key() == Qt.Key.Key_Q:
            self.close()
        
        # Click-through toggle (Ctrl + T)
        elif ctrl and event.key() == Qt.Key.Key_T:
            self.config["click_through"] = not self.config.get("click_through", False)
            self.apply_click_through()
            save_config(self.config)
            
        # Compact mode toggle (Ctrl + M)
        elif ctrl and event.key() == Qt.Key.Key_M:
            self.config["compact_mode"] = not self.config.get("compact_mode", False)
            self.step_label.setVisible(not self.config["compact_mode"])
            self.progress_bar.setVisible(not self.config["compact_mode"])
            self.quest_label.setVisible(not self.config["compact_mode"])
            self.target_zone_label.setVisible(not self.config["compact_mode"])
            save_config(self.config)
            self.adjust_window_size()

        # Navigation shortcuts (Ctrl + Left/Right)
        elif ctrl and event.key() == Qt.Key.Key_Left:
            if self.config["current_step"] > 0:
                self.config["current_step"] -= 1
                self.update_step_ui()
                save_config(self.config)
        elif ctrl and event.key() == Qt.Key.Key_Right:
            if self.config["current_step"] < len(WALKTHROUGH) - 1:
                self.config["current_step"] += 1
                self.update_step_ui()
                save_config(self.config)

    def mouseMoveEvent(self, event):
        if self.is_moving:
            delta = event.globalPosition().toPoint() - self.drag_start_pos
            self.move(self.window_start_rect.topLeft() + delta)

    def mouseReleaseEvent(self, event):
        if self.is_moving:
            self.is_moving = False
            # Save new geometry
            self.config["window_x"] = self.x()
            self.config["window_y"] = self.y()
            self.config["window_width"] = self.width() # Save width
            self.config["window_height"] = self.height() # Save height
            save_config(self.config)
            
    def adjust_window_size(self):
        # Ensure all labels have updated content before calculating sizes
        self.quest_label.adjustSize()
        self.target_zone_label.adjustSize()
        self.zone_display.adjustSize()
        self.step_label.adjustSize() # Ensure it's adjusted to its content, considering word wrap and current width.
        self.version_label.adjustSize()

        # Calculate content widths to determine ideal_width
        # The controls_widget should dictate a minimum width for the window contents.
        min_content_width = self.controls_widget.sizeHint().width()
        
        # Calculate margins/padding that contribute to overall window size
        horizontal_margins = self.container_layout.contentsMargins().left() + self.container_layout.contentsMargins().right() + \
                             self.main_layout.contentsMargins().left() + self.main_layout.contentsMargins().right()
        vertical_margins = self.container_layout.contentsMargins().top() + self.container_layout.contentsMargins().bottom() + \
                           self.main_layout.contentsMargins().top() + self.main_layout.contentsMargins().bottom() + \
                           self.container_layout.spacing() * 4 # Adjust for spacing between elements

        # Calculate ideal width: Start with minimum width, then allow to expand based on content
        step_label_effective_width = self.step_label.minimumSizeHint().width()

        # Take the maximum preferred width from all top-level widgets that influence horizontal space
        # and add horizontal margins/padding.
        ideal_width = max(min_content_width, step_label_effective_width, self.quest_label.sizeHint().width(),
                          self.target_zone_label.sizeHint().width(), self.zone_display.sizeHint().width()) + horizontal_margins + 30 # Extra padding
        
        # Ensure ideal_width respects the overall window's minimum width
        ideal_width = max(self.minimumWidth(), ideal_width)

        # Now calculate the ideal height. For step_label, its height will depend on the width it's given.
        # Temporarily set the calculated ideal_width (minus margins) to the step_label to get its correct height.
        
        # Now calculate the ideal height. For step_label, its height will depend on the width it\"s given.
        # Temporarily set the calculated ideal_width (minus internal margins) to the step_label to get its correct height.

        content_height = self.controls_widget.height() + \
                         self.zone_display.height() + \
                         self.quest_label.height() + \
                         self.target_zone_label.height() + \
                         self.line.height() + \
                         self.progress_bar.height() + \
                         self.version_label.height() + \
                         vertical_margins + 20 # Extra padding
        
        # Ensure the total height is at least a reasonable minimum, e.g., for controls only
        content_height = max(self.controls_widget.height() + vertical_margins, content_height)

        new_size = QSize(ideal_width, content_height)
        
        # Animate resize if size actually changes
        if self.size() != new_size:
            self.size_animation.setStartValue(self.size())
            self.size_animation.setEndValue(new_size)
            self.size_animation.start()

    def resizeEvent(self, event):
        super().resizeEvent(event)

    def closeEvent(self, event):
        # Stop log watcher thread before exiting
        if hasattr(self, 'watcher'):
            self.watcher.stop()
            self.watcher.wait()
        event.accept()

    def reset_player_progress(self):
        self.config["current_step"] = 0
        self.completed_data = {}
        self.sync_current_completed_set()
        save_config(self.config)
        self.update_step_ui()
        self.scan_log_history() # Re-scan to potentially activate first hint/zone

    def select_client_txt(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Path of Exile Client.txt", 
            os.path.expanduser("~"), "Text Files (*.txt);;All Files (*)"
        )
        if file_path:
            self.config["client_txt_path"] = file_path
            save_config(self.config)
            # Restart watcher
            if hasattr(self, 'watcher'):
                self.watcher.stop()
                self.watcher.wait()
            self.setup_log_watcher()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    overlay = PoEOverlay()
    
    # Check if we need to select Client.txt
    if not overlay.config["client_txt_path"] or not os.path.exists(overlay.config["client_txt_path"]):
        overlay.show() # Show it first so dialog has parent
        overlay.select_client_txt()
    else:
        overlay.show()
        
    sys.exit(app.exec())
