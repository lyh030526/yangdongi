"""Run from repository root: python -m docs.render_preview."""
import os
import tempfile
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QSettings
from yangdongi.state import CompanionState
from yangdongi.ui import MainWindow
from yangdongi.theme import STYLE

app = QApplication([])
app.setStyle('Fusion')
app.setStyleSheet(STYLE)
with tempfile.TemporaryDirectory() as directory:
    window = MainWindow(CompanionState(), QSettings(f'{directory}/preview.ini', QSettings.Format.IniFormat))
    window.show()
    app.processEvents()
    for i, name in enumerate(['home', 'focus', 'chat', 'settings']):
        window.navigate(i)
        app.processEvents()
        window.grab().save(f'docs/{name}.png')
    window.pet.show()
    app.processEvents()
    window.pet.grab().save('docs/pet.png')
