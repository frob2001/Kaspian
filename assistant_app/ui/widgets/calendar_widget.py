from __future__ import annotations

from PySide6.QtCore import QDate
from PySide6.QtWidgets import QCalendarWidget, QVBoxLayout, QWidget


class CalendarWidget(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("CalendarCard")

        self.calendar = QCalendarWidget()
        self.calendar.setObjectName("DashboardCalendar")
        self.calendar.setSelectedDate(QDate.currentDate())
        self.calendar.setGridVisible(False)
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        self.calendar.setNavigationBarVisible(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.addWidget(self.calendar)
