import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import pytest
from PySide6.QtCore import QSettings, Qt
from PySide6.QtWidgets import QApplication
from yangdongi.state import CompanionState
from yangdongi.ui import MainWindow
from yangdongi.theme import STYLE

@pytest.fixture(scope='session')
def app():
    app = QApplication.instance() or QApplication([])
    app.setStyle('Fusion')
    app.setStyleSheet(STYLE)
    return app


def test_focus_pause_and_completion(app):
    state = CompanionState()
    state.toggle_focus()
    state.advance()
    assert state.remaining == 1499
    state.toggle_focus()
    state.advance()
    assert state.remaining == 1499
    state.remaining = 1
    state.toggle_focus()
    state.advance()
    assert not state.focus and not state.timer.isActive()
    assert state.remaining == 0
    assert len(state.history) == 1
    state.toggle_focus()
    assert state.remaining == 1500
    state.reset(45)
    assert state.remaining == 2700 and not state.timer.isActive()


def test_context_and_quiet(app):
    state = CompanionState()
    state.simulate('youtube')
    assert '재미있는' in state.history[-1][1]
    state.toggle_focus()
    state.simulate('youtube')
    assert '공부' in state.history[-1][1]
    state.quiet = True
    state.simulate('music')
    assert state.scenario == 'music' and len(state.history) == 2
    state.reset()


def test_window_interactions(app, tmp_path):
    settings = QSettings(str(tmp_path/'test.ini'), QSettings.Format.IniFormat)
    state = CompanionState()
    window = MainWindow(state, settings)
    window.show()
    app.processEvents()
    for index in range(4):
        window.navigate(index)
        assert window.pages.currentIndex() == index
    window.home_focus.click()
    assert state.focus and not window.duration.isEnabled()
    window.scenarios.buttons()[1].click()
    assert '노래' in window.greeting.text()
    window.input.setText('안녕')
    window.send_chat()
    assert not window.input.text()
    assert '데모' in state.history[-1][1]
    window.quiet.setChecked(True)
    assert state.quiet and settings.value('quiet', type=bool)
    window.size_slider.setValue(125)
    assert window.pet.width() == round(360*1.25)
    window.topmost.setChecked(False)
    assert not window.pet.windowFlags() & Qt.WindowType.WindowStaysOnTopHint
    state.reset()
    window.tray.hide()
    window.pet.hide()
    window.hide()


def test_device_animation_lifecycle(app, tmp_path):
    from yangdongi.device import PetWindow
    state = CompanionState()
    pet = PetWindow(state, QSettings(str(tmp_path/'pet.ini'), QSettings.Format.IniFormat))
    assert not pet.frame_timer.isActive()
    pet.show()
    app.processEvents()
    assert pet.frame_timer.isActive()
    pet.play()
    assert '간지러워' in pet.text
    for scene in ('coding', 'music', 'youtube'):
        state.simulate(scene)
        for t in (0.0, 0.5, 1.5):
            pet.preview_time = t
            assert not pet.grab().isNull()
    pet.hide()
    assert not pet.frame_timer.isActive()
