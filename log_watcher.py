import os
import time
import re
from PyQt6.QtCore import QThread, pyqtSignal

class LogWatcher(QThread):
    zone_changed = pyqtSignal(str)
    waypoint_discovered = pyqtSignal()

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
        self.running = True

    def run(self):
        if not self.file_path or not os.path.exists(self.file_path):
            return

        # Start at the end of the file
        file_size = os.path.getsize(self.file_path)
        last_position = file_size

        while self.running:
            current_size = os.path.getsize(self.file_path)
            if current_size < last_position:
                # File was truncated/cleared
                last_position = 0
            
            if current_size > last_position:
                with open(self.file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    f.seek(last_position)
                    lines = f.readlines()
                    last_position = f.tell()

                    for line in lines:
                        # Standard PoE zone entry log pattern
                        # Example: 2024/03/09 10:00:00 1234567 89 [INFO Client 1234] : You have entered The Coast.
                        zone_match = re.search(r" : You have entered (.*?)\.", line)
                        if zone_match:
                            zone_name = zone_match.group(1).strip()
                            self.zone_changed.emit(zone_name)
                        
                        # Waypoint discovery pattern
                        if " : You have discovered a waypoint" in line:
                            self.waypoint_discovered.emit()
            
            time.sleep(0.5)

    def stop(self):
        self.running = False
