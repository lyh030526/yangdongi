"""UI state and simulated events. No desktop capture or model inference."""
from PySide6.QtCore import QObject, Signal, QTimer

SCENARIOS = {
    'coding': ('코딩하는 중', 'VS Code · 1시간 12분', '한 시간째 열심히 코딩 중이네.\n잠깐 어깨도 펴고, 화이팅!'),
    'music': ('음악 듣는 중', '음악 재생 · 인디 / 데모', '오, 노래 듣네!\n나도 이런 잔잔한 인디 음악 좋아해.'),
    'youtube': ('잠깐 다른 길로', 'YouTube · 데모', '잠깐 쉬어 가는 거야?\n준비되면 하던 공부로 같이 돌아가자.'),
}

class CompanionState(QObject):
    changed = Signal()
    message = Signal(str)
    tick = Signal()

    def __init__(self):
        super().__init__()
        self.scenario = 'coding'
        self.focus = False
        self.remaining = 25 * 60
        self.duration = 25
        self.quiet = False
        self.history = []
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.advance)

    @property
    def clock(self):
        return f'{self.remaining // 60:02d}:{self.remaining % 60:02d}'

    def say(self, text):
        self.history.append(('양동이', text))
        self.history = self.history[-100:]
        self.message.emit(text)

    def simulate(self, key):
        self.scenario = key
        self.changed.emit()
        if not self.quiet:
            text = SCENARIOS[key][2]
            if key == 'youtube' and not self.focus:
                text = '재미있는 영상 찾았어?\n오늘은 어떤 이야기를 보고 있어?'
            self.say(text)

    def toggle_focus(self):
        self.focus = not self.focus
        if self.focus:
            if self.remaining <= 0:
                self.remaining = self.duration * 60
            self.timer.start()
        else:
            self.timer.stop()
        self.changed.emit()

    def reset(self, minutes=None):
        self.focus = False
        self.timer.stop()
        if minutes is not None:
            self.duration = minutes
        self.remaining = self.duration * 60
        self.changed.emit()
        self.tick.emit()

    def advance(self):
        if not self.focus:
            return
        self.remaining = max(0, self.remaining - 1)
        if self.remaining == 0:
            self.focus = False
            self.timer.stop()
            self.changed.emit()
            self.say('오늘도 한 걸음 해냈네! 이제 잠깐 쉬자 ☕')
        self.tick.emit()
