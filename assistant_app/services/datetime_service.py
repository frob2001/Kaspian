from __future__ import annotations

from datetime import datetime


MONTHS_ES = [
    "enero",
    "febrero",
    "marzo",
    "abril",
    "mayo",
    "junio",
    "julio",
    "agosto",
    "septiembre",
    "octubre",
    "noviembre",
    "diciembre",
]

WEEKDAYS_ES = [
    "lunes",
    "martes",
    "miércoles",
    "jueves",
    "viernes",
    "sábado",
    "domingo",
]


class DateTimeService:
    """Provides presentation-friendly Spanish date strings."""

    @staticmethod
    def now() -> datetime:
        return datetime.now()

    @classmethod
    def formatted_time(cls) -> str:
        return cls.now().strftime("%H:%M")

    @classmethod
    def formatted_date(cls) -> str:
        current = cls.now()
        weekday = WEEKDAYS_ES[current.weekday()]
        month = MONTHS_ES[current.month - 1]
        return f"{weekday.capitalize()}, {current.day} de {month} de {current.year}"
