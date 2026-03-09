import sys
import os
import re
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFileDialog, QGraphicsDropShadowEffect, QProgressBar
from PyQt6.QtCore import Qt, QPoint, QRect, QSize, QPropertyAnimation, QEasingCurve
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
        
        # Geometry
        self.setGeometry(
            self.config["window_x"], 
            self.config["window_y"], 
            self.config["window_width"], 
            self.config["window_height"]
        )

        # Layout
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(self.main_layout)

        # Content Widget (for background styling)
        self.content_container = QWidget()
        self.container_layout = QVBoxLayout()
        self.container_layout.setSpacing(2)
        self.container_layout.setContentsMargins(15, 5, 15, 10)
        self.content_container.setLayout(self.container_layout)
        self.main_layout.addWidget(self.content_container)

        # Controls Row (Moved to Top)
        self.controls_widget = QWidget()
        self.controls_widget.setFixedHeight(35)
        self.controls_layout = QHBoxLayout()
        self.controls_layout.setContentsMargins(10, 0, 10, 0)
        self.controls_layout.setSpacing(10)
        self.controls_widget.setLayout(self.controls_layout)
        
        self.btn_prev = QLabel(" < ")
        self.btn_prev.setToolTip("Ctrl + LMB to go back")
        
        self.move_label = QLabel("MOVE")
        self.move_label.setToolTip("Ctrl + LMB to move")
        
        self.btn_next = QLabel(" > ")
        self.btn_next.setToolTip("Ctrl + LMB to go forward")
        
        self.scale_label = QLabel("SCALE")
        self.scale_label.setToolTip("Ctrl + LMB to resize")

        self.close_btn = QLabel("X")
        self.close_btn.setToolTip("Click to close")
        self.close_btn.setStyleSheet("color: #ff4d4d; font-weight: bold; font-size: 14px; padding: 2px;")
        
        self.controls_layout.addStretch()
        self.controls_layout.addWidget(self.btn_prev)
        self.controls_layout.addWidget(self.move_label)
        self.controls_layout.addWidget(self.btn_next)
        self.controls_layout.addStretch()
        self.controls_layout.addWidget(self.scale_label)
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
        self.step_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.step_label.linkActivated.connect(self.on_task_clicked)
        
        # Text Shadow (Point 1)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(6)
        shadow.setXOffset(1)
        shadow.setYOffset(1)
        shadow.setColor(QColor(0, 0, 0, 255))
        self.step_label.setGraphicsEffect(shadow)
        
        self.container_layout.addWidget(self.step_label)

        # Progress Bar (Point 4)
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(5)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar { border: 1px solid rgba(255, 215, 0, 30); background-color: rgba(0,0,0,100); border-radius: 2px; }
            QProgressBar::chunk { background-color: #FFD700; }
        """)
        self.container_layout.addWidget(self.progress_bar)

        # Auto-hide controls (Point 2)
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
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
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
        self.btn_prev.setStyleSheet(f"color: {accent_color}; font-weight: bold; font-size: 18px; padding: 0 5px;")
        self.btn_next.setStyleSheet(f"color: {accent_color}; font-weight: bold; font-size: 18px; padding: 0 5px;")
        self.move_label.setStyleSheet(control_style)
        self.scale_label.setStyleSheet(f"color: {accent_color}; font-weight: bold; font-size: 11px; border: 1px solid {accent_color}; border-radius: 3px; padding: 2px 4px;")

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
            
            # Keyword Highlighting with Badges (Point 5)
            text = text.replace("[WP]", f"<span style='{wp_style}'>WP</span>")
            text = text.replace("[Q]", f"<span style='{q_style}'>Q</span>")
            text = text.replace("[SKILL]", f"<span style='{skill_style}'>SKILL</span>")
            text = text.replace("ACT ", "<b><span style='color: #FFD700;'>ACT </span></b>")

            # Action Color Palette (Point 3)
            actions_red = ["Kill", "Defeat", "Clear", "Slay"]
            actions_green = ["Help", "Talk", "Quest", "Reward"]
            actions_blue = ["Go to", "Enter", "Travel"]
            
            # Bandit Check (Point 12)
            if any(bandit in text for bandit in ["Bandits", "Kraityn", "Alira", "Oak"]):
                text += "<br><br><b style='color: #ff4d4d;'>➜ KILL ALL or CHECK YOUR POB</b>"

            for action in actions_red:
                text = re.sub(rf"\b{action}\b", f"<span style='color: #ff4d4d; font-weight: bold;'>{action}</span>", text)
            for action in actions_green:
                text = re.sub(rf"\b{action}\b", f"<span style='color: #50fa7b; font-weight: bold;'>{action}</span>", text)
            for action in actions_blue:
                text = re.sub(rf"\b{action}\b", f"<span style='color: #4da6ff; font-weight: bold;'>{action}</span>", text)

            # Bullet points and Line Height (Point 2 & 4)
            lines = [line.strip() for line in text.split('.') if line.strip()]
            if len(lines) > 1:
                formatted_text = "<ul style='margin-left: -20px; line-height: 130%;'>"
                for i, line in enumerate(lines):
                    style = "color: #f8f8f2;" # Default color
                    if i in self.completed_substeps:
                        style = "text-decoration: line-through; color: #555555;"
                    formatted_text += f"<li style='margin-bottom: 4px;'><a href='{i}' style='text-decoration: none; {style}'>{line}</a></li>"
                formatted_text += "</ul>"
            else:
                style = "color: #f8f8f2;"
                if 0 in self.completed_substeps:
                    style = "text-decoration: line-through; color: #555555;"
                formatted_text = f"<div style='line-height: 130%;'><a href='0' style='text-decoration: none; {style}'>{text}</a></div>"
            
            # Town status check
            if hasattr(self, 'current_zone') and self.current_zone in TOWNS:
                formatted_text += "<br><div style='font-size: 11px; color: #FFD700; border-top: 1px solid rgba(255,215,0,30); padding-top: 4px;'>➜ IN TOWN: Get Quests</div>"

            self.step_label.setText(f"<html><body>{formatted_text}</body></html>")
            
            # Progress Bar (Point 4)
            self.progress_bar.setMaximum(len(WALKTHROUGH) - 1)
            self.progress_bar.setValue(idx)
        
        self.scale_font()

    def scale_font(self):
        # Dynamic font scaling based on window height and width
        height = self.height()
        width = self.width()
        # Better scaling logic (Point 9) - Harmonized with headers
        base_size = min(width / 22, height / 9)
        font_size = max(11, min(13, int(base_size)))
        
        font = QFont("Segoe UI", font_size)
        if not font.exactMatch():
            font = QFont("Sans Serif", font_size)
        
        self.step_label.setFont(font)

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
            self.watcher = LogWatcher(path)
            self.watcher.zone_changed.connect(self.on_zone_changed)
            self.watcher.waypoint_discovered.connect(self.on_waypoint_discovered)
            self.watcher.start()

    def on_waypoint_discovered(self):
        # Mark WP tasks as done
        idx = self.config["current_step"]
        if 0 <= idx < len(WALKTHROUGH):
            step = WALKTHROUGH[idx]
            text = step["text"]
            lines = [line.strip() for line in text.split('.') if line.strip()]
            for i, line in enumerate(lines):
                if "[WP]" in line or "waypoint" in line.lower():
                    self.completed_substeps.add(i)
            
            self.update_step_ui()
            self.check_auto_advance()

    def check_auto_advance(self):
        idx = self.config["current_step"]
        if 0 <= idx < len(WALKTHROUGH):
            step = WALKTHROUGH[idx]
            text = step["text"]
            total_lines = len([line.strip() for line in text.split('.') if line.strip()])
            if len(self.completed_substeps) >= total_lines and total_lines > 0:
                if idx < len(WALKTHROUGH) - 1:
                    self.config["current_step"] += 1
                    self.completed_substeps = set() # Reset for next step
                    self.update_step_ui()
                    save_config(self.config)

    def on_zone_changed(self, zone_name):
        self.current_zone = zone_name
        self.zone_display.setText(f"Location: {zone_name}")
        
        # Check if this zone completion marks a substep as done
        idx = self.config["current_step"]
        if 0 <= idx < len(WALKTHROUGH):
            step = WALKTHROUGH[idx]
            text = step["text"]
            lines = [line.strip() for line in text.split('.') if line.strip()]
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
                break

    def enterEvent(self, event):
        # Show controls on hover (Point 2)
        self.controls_widget.setVisible(True)
        self.close_btn.setVisible(True)
        super().enterEvent(event)

    def leaveEvent(self, event):
        # Hide controls when not hovering (Point 2)
        self.controls_widget.setVisible(False)
        self.close_btn.setVisible(False)
        super().leaveEvent(event)

    def wheelEvent(self, event: QWheelEvent):
        # Change opacity with Ctrl + Scroll (Point 3)
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
        # Always allow closing with X even without Ctrl (Point 1)
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
            
            elif self.btn_next.underMouse():
                if self.config["current_step"] < len(WALKTHROUGH) - 1:
                    self.config["current_step"] += 1
                    self.update_step_ui()
                    save_config(self.config)

            # Check for Move label
            elif self.move_label.underMouse():
                self.is_moving = True
                self.drag_start_pos = event.globalPosition().toPoint()
                self.window_start_rect = self.geometry()
            
            # Check for Scale label
            elif self.scale_label.underMouse():
                self.is_resizing = True
                self.drag_start_pos = event.globalPosition().toPoint()
                self.window_start_rect = self.geometry()

    def keyPressEvent(self, event: QKeyEvent):
        ctrl = event.modifiers() == Qt.KeyboardModifier.ControlModifier
        
        # Exit (Ctrl + Q)
        if ctrl and event.key() == Qt.Key.Key_Q:
            self.close()
        
        # Click-through toggle (Ctrl + T) (Point 3)
        elif ctrl and event.key() == Qt.Key.Key_T:
            self.config["click_through"] = not self.config.get("click_through", False)
            self.apply_click_through()
            save_config(self.config)
            
        # Compact mode toggle (Ctrl + M) (Point 3)
        elif ctrl and event.key() == Qt.Key.Key_M:
            self.config["compact_mode"] = not self.config.get("compact_mode", False)
            self.step_label.setVisible(not self.config["compact_mode"])
            self.progress_bar.setVisible(not self.config["compact_mode"])
            self.quest_label.setVisible(not self.config["compact_mode"])
            self.target_zone_label.setVisible(not self.config["compact_mode"])
            save_config(self.config)

        # Navigation shortcuts (Ctrl + Left/Right) (Point 3)
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
        elif self.is_resizing:
            delta = event.globalPosition().toPoint() - self.drag_start_pos
            new_width = max(200, self.window_start_rect.width() + delta.x())
            new_height = max(100, self.window_start_rect.height() + delta.y())
            self.resize(new_width, new_height)

    def mouseReleaseEvent(self, event):
        if self.is_moving or self.is_resizing:
            self.is_moving = False
            self.is_resizing = False
            # Save new geometry
            self.config["window_x"] = self.x()
            self.config["window_y"] = self.y()
            self.config["window_width"] = self.width()
            self.config["window_height"] = self.height()
            save_config(self.config)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.scale_font()

    def closeEvent(self, event):
        # Stop log watcher thread before exiting
        if hasattr(self, 'watcher'):
            self.watcher.stop()
            self.watcher.wait()
        event.accept()

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
