from PySide6.QtCore import Qt, QSettings, QTimer, Signal
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QFrame, QLabel,
    QPushButton, QVBoxLayout, QHBoxLayout, QStackedWidget, QCheckBox, QComboBox,
    QSlider, QLineEdit, QScrollArea, QSystemTrayIcon, QMenu, QProgressBar, QButtonGroup)
from .art import PetArt
from .device import PetWindow
from .state import SCENARIOS


def label(text, role=None, wrap=False):
    w = QLabel(text)
    if role:
        w.setObjectName(role)
    w.setWordWrap(wrap)
    return w


def button(text, callback, primary=False):
    w = QPushButton(text)
    if primary:
        w.setObjectName('primary')
    w.setCursor(Qt.CursorShape.PointingHandCursor)
    w.clicked.connect(callback)
    return w


def card(name='card'):
    w = QFrame()
    w.setObjectName(name)
    layout = QVBoxLayout(w)
    layout.setContentsMargins(22, 20, 22, 20)
    layout.setSpacing(12)
    return w, layout


class MainWindow(QMainWindow):
    def __init__(self, state, settings=None):
        super().__init__()
        self.state = state
        self.settings = settings or QSettings('Yangdongi', 'Companion')
        self.pet = PetWindow(state, self.settings)
        self.pet.open_requested.connect(self.open_settings)
        self.setWindowTitle('양동이 — 너의 하루에, 작은 친구')
        self.resize(1160, 820)
        self.setMinimumSize(1040, 760)
        root = QWidget()
        root.setObjectName('root')
        self.setCentralWidget(root)
        body = QHBoxLayout(root)
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)
        sidebar = QFrame()
        sidebar.setObjectName('sidebar')
        sidebar.setFixedWidth(210)
        nav = QVBoxLayout(sidebar)
        nav.setContentsMargins(22, 30, 22, 24)
        nav.setSpacing(9)
        nav.addWidget(label('양동이', 'brand'))
        nav.addWidget(label('YOUR LITTLE COMPANION', 'eyebrow'))
        nav.addSpacing(38)
        self.nav_group = QButtonGroup(self)
        for i, name in enumerate(['⌂   나의 양동이', '◷   집중 모드', '☏   대화 모아보기', '⚙   설정']):
            b = button(name, lambda checked=False, index=i: self.navigate(index))
            b.setObjectName('nav')
            b.setCheckable(True)
            self.nav_group.addButton(b, i)
            nav.addWidget(b)
        self.nav_group.button(0).setChecked(True)
        nav.addStretch()
        mini, ml = card()
        ml.setContentsMargins(15, 15, 15, 15)
        ml.addWidget(label('작고 조용한 동행', 'heading'))
        ml.addWidget(label('너의 속도에 맞춰\n곁에 있을게.', 'muted'))
        mini_art = PetArt()
        mini_art.setMinimumSize(110, 110)
        mini_art.setFixedHeight(115)
        ml.addWidget(mini_art)
        nav.addWidget(mini)
        nav.addSpacing(12)
        nav.addWidget(label('●  로컬 전용 · UI 미리보기', 'muted'))
        nav.addWidget(label('YANGDONGI  /  0.1.0', 'eyebrow'))
        body.addWidget(sidebar)
        content = QVBoxLayout()
        content.setContentsMargins(32, 27, 32, 22)
        content.setSpacing(20)
        top = QHBoxLayout()
        top.addWidget(label('MY DESKTOP FRIEND', 'eyebrow'))
        top.addStretch()
        top.addWidget(label('●  데모 모드', 'pill'))
        top.addWidget(button('데스크톱에 띄우기 ↗', self.show_pet))
        content.addLayout(top)
        self.pages = QStackedWidget()
        for page in (self.home_page(), self.focus_page(), self.chat_page(), self.settings_page()):
            scroll_page = QScrollArea()
            scroll_page.setWidgetResizable(True)
            scroll_page.setWidget(page)
            self.pages.addWidget(scroll_page)
        content.addWidget(self.pages, 1)
        footer = QHBoxLayout()
        footer.addWidget(label('작은 응원 하나가, 오늘을 조금 다르게.', 'muted'))
        footer.addStretch()
        footer.addWidget(label('화면 수집 없음  ·  모델 미연결', 'muted'))
        content.addLayout(footer)
        body.addLayout(content, 1)
        state.changed.connect(self.refresh)
        state.tick.connect(self.refresh_clock)
        state.message.connect(self.on_message)
        self.refresh()
        self.setup_tray()

    def page(self, title, subtitle):
        w = QWidget()
        w.setObjectName('page')
        v = QVBoxLayout(w)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(17)
        v.addWidget(label(title, 'title'))
        v.addWidget(label(subtitle, 'muted'))
        return w, v

    def home_page(self):
        w, v = self.page('오늘도, 함께 해볼까?', '집중하는 순간에도, 잠깐 쉬는 순간에도. 양동이가 곁에 있어요.')
        hero, h = card('hero')
        row = QHBoxLayout()
        left = QVBoxLayout()
        left.addWidget(label('작은 친구의 한마디', 'eyebrow'))
        self.greeting = label('한 시간째 열심히 코딩 중이네.\n잠깐 어깨도 펴고, 화이팅!', wrap=True)
        self.greeting.setStyleSheet('font-size: 21px; font-weight: 600; color: #535640;')
        left.addSpacing(9)
        left.addWidget(self.greeting)
        left.addSpacing(12)
        self.context = label('', 'pill')
        left.addWidget(self.context, alignment=Qt.AlignmentFlag.AlignLeft)
        left.addStretch()
        left.addWidget(label('나를 바탕화면으로 데려가 줘!  ↗', 'muted'))
        row.addLayout(left, 3)
        art = PetArt()
        art.setFixedSize(230, 190)
        row.addWidget(art, 2)
        h.addLayout(row)
        v.addWidget(hero)
        row = QHBoxLayout()
        focus, f = card()
        f.addWidget(label('◷  우리, 조금만 집중해 볼까', 'heading'))
        f.addWidget(label('한 번에 한 가지. 작은 시작이면 충분해요.', 'muted'))
        self.home_clock = label('25:00', 'clock')
        f.addWidget(self.home_clock)
        self.home_focus = button('집중 시작하기  →', self.state.toggle_focus, True)
        f.addWidget(self.home_focus)
        row.addWidget(focus, 1)
        sensing, s = card()
        s.addWidget(label('✧  양동이가 알아차리는 것', 'heading'))
        s.addWidget(label('이런 순간에 말을 걸어요', 'muted'))
        for a, b in [('⌨   몰입한 시간', '오래 코딩했다면, 작은 응원'), ('♫   쉬어 가는 순간', '음악과 함께 나누는 한마디'), ('◷   집중이 흐트러질 때', '다시 시작할 수 있게, 다정하게')]:
            s.addWidget(label(a))
            s.addWidget(label('      '+b, 'muted'))
        s.addStretch()
        row.addWidget(sensing, 1)
        v.addLayout(row)
        v.addWidget(label('상황 미리보기', 'heading'))
        v.addWidget(label('아래 상황을 누르면 양동이의 반응을 볼 수 있어요. 실제 PC 활동이 아닌 예시예요.', 'muted'))
        scenarios = QHBoxLayout()
        self.scenarios = QButtonGroup(self)
        for key, text in [('coding', '⌨  코딩 1시간'), ('music', '♫  음악 듣기'), ('youtube', '▷  유튜브 방문')]:
            b = button(text, lambda checked=False, k=key: self.state.simulate(k))
            b.setObjectName('scenario')
            b.setCheckable(True)
            b.setProperty('scenario', key)
            self.scenarios.addButton(b)
            scenarios.addWidget(b)
        v.addLayout(scenarios)
        v.addStretch()
        return w

    def focus_page(self):
        w, v = self.page('조금씩, 차곡차곡.', '양동이와 함께 나만의 집중 시간을 만들어요.')
        c, box = card('hero')
        box.addWidget(label('FOCUS SESSION', 'eyebrow'), alignment=Qt.AlignmentFlag.AlignHCenter)
        self.focus_status = label('시작할 준비가 됐어요', 'heading')
        box.addWidget(self.focus_status, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.focus_clock = label('25:00', 'clock')
        self.focus_clock.setStyleSheet('font-size: 82px; color: #596447; font-weight: 600;')
        box.addWidget(self.focus_clock, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.progress = QProgressBar()
        self.progress.setTextVisible(False)
        box.addWidget(self.progress)
        controls = QHBoxLayout()
        self.duration = QComboBox()
        self.duration.addItems(['25분 집중', '45분 집중', '50분 집중'])
        self.duration.currentIndexChanged.connect(lambda i: self.state.reset([25, 45, 50][i]))
        controls.addWidget(self.duration)
        self.focus_button = button('집중 시작하기', self.state.toggle_focus, True)
        controls.addWidget(self.focus_button)
        controls.addWidget(button('처음부터', lambda: self.state.reset()))
        box.addLayout(controls)
        v.addWidget(c)
        c, box = card()
        box.addWidget(label('다그치기보다, 다시 시작할 수 있게', 'heading'))
        box.addWidget(label('집중 모드에서 다른 길로 새면 양동이가 부드럽게 알려줘요.\n잠깐의 휴식도 괜찮아요. 준비되면 다시 돌아오면 되니까요.', wrap=True))
        box.addWidget(button('집중 중 유튜브 방문 반응 보기', lambda: self.state.simulate('youtube')))
        box.addWidget(label('집중 세션을 시작한 뒤 누르면 공부 모드의 대사를 확인할 수 있어요.', 'muted'))
        v.addWidget(c)
        v.addStretch()
        return w

    def chat_page(self):
        w, v = self.page('우리의 작은 대화', '오늘 나눈 응원을 여기 모아 두었어요. 대화는 앱을 종료하면 사라져요.')
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        inner = QWidget()
        self.messages = QVBoxLayout(inner)
        self.messages.setContentsMargins(0, 0, 8, 0)
        self.messages.setAlignment(Qt.AlignmentFlag.AlignTop)
        scroll.setWidget(inner)
        v.addWidget(scroll, 1)
        self.scroll = scroll
        self.add_message('양동이', '안녕! 나는 양동이야. 오늘은 어떤 하루를 보내고 있어?')
        v.addWidget(label('데모 응답 · 로컬 LLM을 연결하면 자유롭게 대화할 수 있어요.', 'muted'))
        row = QHBoxLayout()
        self.input = QLineEdit()
        self.input.setPlaceholderText('양동이에게 한마디 건네기…')
        self.input.setMaxLength(1000)
        self.input.returnPressed.connect(self.send_chat)
        row.addWidget(self.input)
        row.addWidget(button('보내기 ↑', self.send_chat, True))
        v.addLayout(row)
        return w

    def settings_page(self):
        w, v = self.page('우리에게 맞는 거리', '곁에 있는 방식도, 말을 거는 빈도도 편안하게.')
        c, box = card()
        box.addWidget(label('데스크톱의 양동이', 'heading'))
        self.topmost = QCheckBox('다른 창 위에 항상 표시')
        self.topmost.setChecked(self.settings.value('topmost', True, type=bool))
        self.topmost.toggled.connect(self.set_topmost)
        box.addWidget(self.topmost)
        self.quiet = QCheckBox('조용히 함께하기 · 말풍선 알림 끄기')
        self.quiet.setChecked(self.settings.value('quiet', False, type=bool))
        self.state.quiet = self.quiet.isChecked()
        self.quiet.toggled.connect(self.set_quiet)
        box.addWidget(self.quiet)
        box.addWidget(label('양동이 크기', 'muted'))
        self.size_slider = QSlider(Qt.Orientation.Horizontal)
        self.size_slider.setRange(75, 125)
        self.size_slider.setValue(self.settings.value('size', 100, type=int))
        self.size_slider.valueChanged.connect(self.resize_pet)
        box.addWidget(self.size_slider)
        v.addWidget(c)
        c, box = card()
        box.addWidget(label('로컬 AI 연결', 'heading'))
        row = QHBoxLayout()
        row.addWidget(label('EXAONE 3.5 · 4B 계열', 'heading'))
        row.addStretch()
        row.addWidget(label('연결 준비 중', 'pill'))
        box.addLayout(row)
        box.addWidget(label('모델 이름은 사용자가 제안한 예시예요. 실제 모델 선택과 추론 엔진 연결은\n다음 단계에서 구현해요. 현재 대화는 준비된 데모 문장으로 동작해요.', 'muted', True))
        v.addWidget(c)
        c, box = card()
        box.addWidget(label('가볍고 조용하게', 'heading'))
        box.addWidget(label('이 시안은 화면 캡처, OCR, 앱 활동 수집을 수행하지 않아요.\n집중 타이머는 실행 중에만 갱신하고, 펫 애니메이션은 보일 때만 재생해요.', wrap=True))
        box.addWidget(label('네 활동은 네 컴퓨터 안에. 필요한 순간에만, 조용히 말을 걸어요.', 'muted', True))
        v.addWidget(c)
        v.addStretch()
        self.set_topmost(self.topmost.isChecked())
        self.resize_pet(self.size_slider.value())
        return w

    def navigate(self, index):
        self.pages.setCurrentIndex(index)
        self.nav_group.button(index).setChecked(True)

    def set_topmost(self, checked):
        visible = self.pet.isVisible()
        self.pet.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, checked)
        if visible:
            self.pet.show()
        self.settings.setValue('topmost', checked)

    def set_quiet(self, checked):
        self.state.quiet = checked
        if checked:
            self.pet.update()
        self.settings.setValue('quiet', checked)

    def resize_pet(self, value):
        self.pet.setFixedSize(round(360*value/100), round(480*value/100))
        self.settings.setValue('size', value)

    def refresh_clock(self):
        self.home_clock.setText(self.state.clock)
        self.focus_clock.setText(self.state.clock)
        self.progress.setRange(0, self.state.duration*60)
        self.progress.setValue(self.state.duration*60-self.state.remaining)

    def refresh(self):
        self.context.setText('●  '+SCENARIOS[self.state.scenario][1])
        for b in self.scenarios.buttons():
            b.setChecked(b.property('scenario') == self.state.scenario)
        active = self.state.focus
        caption = '잠깐 멈추기  Ⅱ' if active else '집중 시작하기  →'
        self.home_focus.setText(caption)
        self.focus_button.setText(caption)
        self.focus_status.setText('양동이와 함께 집중하는 중' if active else '나의 속도로 시작해요')
        self.duration.setEnabled(not active)
        self.refresh_clock()

    def on_message(self, text):
        self.greeting.setText(text)
        self.add_message('양동이', text)

    def add_message(self, who, text):
        c, box = card('hero' if who == '양동이' else 'card')
        box.addWidget(label(who, 'eyebrow'))
        box.addWidget(label(text, wrap=True))
        self.messages.addWidget(c)
        while self.messages.count() > 100:
            self.messages.takeAt(0).widget().deleteLater()
        QTimer.singleShot(0, lambda: self.scroll.verticalScrollBar().setValue(self.scroll.verticalScrollBar().maximum()))

    def send_chat(self):
        text = self.input.text().strip()
        if not text:
            return
        self.add_message('나', text)
        self.input.clear()
        self.state.say('이야기해 줘서 고마워! 네 하루를 응원할게.\n(지금은 미리 준비된 데모 응답이에요.)')

    def show_pet(self):
        self.pet.show()
        if self.state.quiet:
            self.pet.update()
        self.pet.raise_()

    def open_settings(self):
        self.navigate(3)
        self.reveal()

    def reveal(self):
        self.showNormal()
        self.raise_()
        self.activateWindow()

    def setup_tray(self):
        pix = QPixmap(64, 64)
        pix.fill(Qt.GlobalColor.transparent)
        art = PetArt()
        art.resize(160, 160)
        pix = art.grab().scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.setWindowIcon(QIcon(pix))
        self.tray = QSystemTrayIcon(QIcon(pix), self)
        self.tray.setToolTip('양동이 · 너의 작은 친구')
        menu = QMenu(self)
        menu.addAction('양동이 열기', self.reveal)
        menu.addAction('데스크톱 펫 표시', self.show_pet)
        menu.addAction('종료', QApplication.quit)
        self.tray.setContextMenu(menu)
        self.tray.activated.connect(lambda reason: self.reveal() if reason == QSystemTrayIcon.ActivationReason.DoubleClick else None)
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray.show()

    def closeEvent(self, event):
        if self.tray.isVisible():
            self.hide()
            event.ignore()
        else:
            self.pet.close()
            event.accept()
            QApplication.quit()
