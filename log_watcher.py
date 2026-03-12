import os
import re
from PyQt6.QtCore import QThread, pyqtSignal, QThread

class LogWatcher(QThread):
    zone_changed = pyqtSignal(str)
    waypoint_discovered = pyqtSignal()
    quest_item_found = pyqtSignal(str) # Emits item name
    quest_completed = pyqtSignal(str) # Emits quest name
    boss_slain = pyqtSignal(str) # Emits boss name
    trial_completed = pyqtSignal(str) # Emits trial name

    def __init__(self, file_path, boss_names_list=None):
        super().__init__()
        self.file_path = file_path

        self.boss_names = set(name.lower() for name in boss_names_list) if boss_names_list else set()

    def run(self):
        print("LogWatcher: Thread starting.")
        if not self.file_path or not os.path.exists(self.file_path):
            print(f"LogWatcher: File path error: {self.file_path}")
            return

        # Detect encoding
        encoding = 'utf-8'
        try:
            with open(self.file_path, 'rb') as f:
                chunk = f.read(1024)
                if b'\xff\xfe' in chunk or b'\xfe\xff' in chunk:
                    encoding = 'utf-16'
                    print("LogWatcher: Detected UTF-16 with BOM.")
                elif b'\x00' in chunk:
                    encoding = 'utf-16-le' # Common for PoE on Proton
                    print("LogWatcher: Detected UTF-16-LE (no BOM).")
                else:
                    print("LogWatcher: Detected UTF-8 encoding.")
        except Exception as e:
            print(f"LogWatcher: Encoding detection error: {e}")

        # Start at the end of the file
        file_size = os.path.getsize(self.file_path)
        last_position = file_size

        while not self.isInterruptionRequested():
            current_size = os.path.getsize(self.file_path)
            if current_size < last_position:
                # File was truncated/cleared
                last_position = 0
            
            if current_size > last_position:
                try:
                    with open(self.file_path, 'r', encoding=encoding, errors='ignore') as f:
                        f.seek(last_position)
                        lines = f.readlines()
                        last_position = f.tell()

                        for line in lines:
                            # Standard PoE zone entry log pattern
                            zone_match = re.search(r" : You have entered (.*?)\.", line)
                            if zone_match:
                                zone_name = zone_match.group(1).strip()
                                self.zone_changed.emit(zone_name)
                            
                            # Waypoint discovery pattern
                            if " : You have discovered a waypoint" in line:
                                self.waypoint_discovered.emit()

                            # Quest item found pattern
                            quest_item_match = re.search(r" : You have received the (.*?) quest item\.", line)
                            if quest_item_match:
                                item_name = quest_item_match.group(1).strip()
                                self.quest_item_found.emit(item_name)

                            # Quest completed pattern (more generic)
                            quest_completed_match = re.search(r" : Quest Complete: (.*?)\.", line)
                            if quest_completed_match:
                                quest_name = quest_completed_match.group(1).strip()
                                self.quest_completed.emit(quest_name)

                            # Boss slain pattern (using dynamic boss names)
                            for boss in self.boss_names:
                                if f" : You have slain {boss}" in line.lower():
                                    self.boss_slain.emit(boss.capitalize())
                                    break
                            
                            # Trial completed pattern
                            trial_match = re.search(r" : You have completed the Trial of (.*?)", line)
                            if trial_match:
                                trial_name = trial_match.group(1).strip()
                                self.trial_completed.emit(trial_name)
                except Exception as e:
                    print(f"LogWatcher: Error reading log file: {e}")
            
            self.msleep(500)
        print("LogWatcher: Thread exiting.")


