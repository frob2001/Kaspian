from __future__ import annotations

import shutil
import subprocess


class AppController:
    def open_application(self, candidates: list[str]) -> tuple[bool, str]:
        for candidate in candidates:
            executable = shutil.which(candidate)
            if executable:
                subprocess.Popen([executable], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return True, f"Abrí {candidate}."
        return False, f"No encontré ninguna de estas aplicaciones: {', '.join(candidates)}."
