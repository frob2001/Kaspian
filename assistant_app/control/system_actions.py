from __future__ import annotations

from services.datetime_service import DateTimeService


class SystemActions:
    def answer_datetime(self, normalized_text: str) -> str:
        if "hora" in normalized_text:
            return f"Son las {DateTimeService.formatted_time()}."
        return f"Hoy es {DateTimeService.formatted_date()}."
