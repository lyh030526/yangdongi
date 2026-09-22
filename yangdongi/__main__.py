import sys
from PySide6.QtWidgets import QApplication
from .state import CompanionState
from .theme import STYLE
from .ui import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName('양동이')
    app.setOrganizationName('Yangdongi')
    app.setStyle('Fusion')
    app.setStyleSheet(STYLE)
    state = CompanionState()
    window = MainWindow(state)
    window.show_pet()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
