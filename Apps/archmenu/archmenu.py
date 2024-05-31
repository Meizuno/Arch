import sys
import json
import subprocess
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTableWidget,
    QLineEdit,
    QTableWidgetItem,
    QGridLayout,
    QPushButton,
    QFrame,
)
from PyQt5.QtGui import QPixmap, QColor
from PyQt5.QtCore import Qt


class AppWidget(QFrame):
    def __init__(
        self,
        icon: str = None,
        label: str = None,
        shell: str = None,
        is_empty: bool = True,
    ):
        super().__init__()

        self.is_empty = is_empty

        self.setWindowTitle('Square Widget with Nested Widgets')
        self.setFixedSize(125, 125)  # Set the initial size of the main widget

        if not is_empty:
            # Main layout
            main_layout = QVBoxLayout()

            self.shell = shell

            # Create nested widgets
            self.icon = QLabel(self)
            pixmap = QPixmap(icon)
            self.icon.setPixmap(pixmap.scaled(64, 64, Qt.KeepAspectRatio))
            self.icon.setFixedSize(64, 64)
            self.icon.setAlignment(Qt.AlignCenter)

            # self.label = QWidget()
            self.label = QLabel(label, self)
            self.label.setWordWrap(True)
            self.label.setFixedWidth(100)
            self.label.setFixedHeight(40)
            self.label.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
            self.label.setStyleSheet("color: white; font-weight: 500")

            # Layout for nested widgets
            nested_layout = QVBoxLayout()
            nested_layout.addWidget(self.icon, alignment=Qt.AlignCenter)
            nested_layout.addWidget(self.label, alignment=Qt.AlignCenter)
            
            main_layout.addLayout(nested_layout)
            self.setLayout(main_layout)

    def activate(self):
        if not self.is_empty:
            self.setStyleSheet("background-color: rgba(64, 63, 78, 1); border-radius: 10px;")

    def deactivate(self):
        if not self.is_empty:
            self.setStyleSheet("background-color: none;")

    def run(self):
        if not self.is_empty:
            subprocess.Popen(self.shell)


class ListAppsWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.active_col = 0
        self.active_row = 0
        self.text = None

        with open("/home/yurii/Apps/archmenu/commands.json", "r", encoding="UTF-8") as file:
            self.commands = json.load(file)

        self.grid = QGridLayout()
        self.setLayout(self.grid)

        self.draw_grid(self.commands)

    def draw_grid(self, commands: list):
        num_rows = 2
        num_cols = 5
        total_slots = num_rows * num_cols
        self.clearLayout()

        for idx in range(total_slots):
            row = idx // num_cols
            col = idx % num_cols
            if idx < len(commands):
                command = commands[idx]
                widget = AppWidget(**command, is_empty=False)
                widget.deactivate()
            else:
                widget = AppWidget()
            self.grid.addWidget(widget, row, col)

        if commands:
            self.grid.itemAtPosition(self.active_row, self.active_col).widget().deactivate()
            self.active_col = 0
            self.active_row = 0
            self.grid.itemAtPosition(0, 0).widget().activate()

    def clearLayout(self):
        while self.grid.count():
            item = self.grid.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def keyPressEvent(self, event, text=None):

        if text != self.text:
            self.text = text
            new_commands = []
            for command in self.commands:
                if text in command.get("label").lower():
                    new_commands.append(command)

            self.draw_grid(new_commands)

        prev_row = self.active_row
        prev_col = self.active_col

        if event.key() == Qt.Key_Up and self.active_row > 0:
            self.active_row -= 1
        elif event.key() == Qt.Key_Down and self.active_row < 1:
            self.active_row += 1
        elif event.key() == Qt.Key_Left and self.active_col > 0:
            self.active_col -= 1
        elif event.key() == Qt.Key_Right and self.active_col < 4:
            self.active_col += 1
        elif event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.grid.itemAtPosition(prev_row, prev_col).widget().run()
            self.parentWidget().close()

        if self.grid.itemAtPosition(self.active_row, self.active_col).widget().is_empty:
            self.active_col = prev_col
            self.active_row = prev_row
        else:
            self.grid.itemAtPosition(prev_row, prev_col).widget().deactivate()
            self.grid.itemAtPosition(self.active_row, self.active_col).widget().activate()

        self.parentWidget().search_window.search_input.setFocus()


class SearchLine(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QLineEdit{
                border: none;
                border-bottom: 2px solid rgba(64, 63, 78, 1);
                font-size: 18px;
                padding: 10px;
            }
        """)

    def keyPressEvent(self, event):
        if event.key() not in (Qt.Key_Up, Qt.Key_Down, Qt.Key_Left, Qt.Key_Right, Qt.Key_Return, Qt.Key_Enter):
            super().keyPressEvent(event)

        self.parentWidget().keyPressEvent(event)


class SearchWidget(QWidget):
    def __init__(self):
        super().__init__()

        layout = QHBoxLayout()

        self.prompt = QLabel("  App", self)
        self.prompt.setStyleSheet("""
            background: #7aa2f7;
            padding: 10px;
            border-radius: 3px;
            color: #1E1D2F;
            font-size: 18px;
            font-weight: 500;
        """)
        layout.addWidget(self.prompt)

        # Создаем поле для ввода
        self.search_input = SearchLine()
        self.search_input.setPlaceholderText("Search...")
        layout.addWidget(self.search_input)

        self.setLayout(layout)

    def keyPressEvent(self, event):
        self.parentWidget().keyPressEvent(event)


class ArchMenu(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        self.search_window = SearchWidget()
        self.list_apps_widget = ListAppsWidget()

        layout.addWidget(self.search_window)
        layout.addWidget(self.list_apps_widget)

        self.setLayout(layout)
        self.setStyleSheet("""
            font-size: 16px;
            font-family: "JetBrainsMono Nerd Font";
            background: #1E1D2F;
            color: #D9E0EE;
        """)

        self.search_window.search_input.setFocus()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()

        self.list_apps_widget.keyPressEvent(event, self.search_window.search_input.text())
        self.search_window.search_input.setFocus()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = ArchMenu()
    window.show()
    sys.exit(app.exec_())
