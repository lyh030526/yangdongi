"""Animated handheld-style desktop pet; a single small, visibility-bound canvas."""
import math
import time
from PySide6.QtCore import Qt, QRectF, QPointF, QTimer, Signal
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen, QFont
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QMenu

INK = '#40543c'

class PetWindow(QWidget):
    open_requested = Signal()

    def __init__(self, state, settings):
        super().__init__()
        self.state, self.settings = state, settings
        self.setWindowTitle('양동이 · 포켓 프렌드')
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setFixedSize(360, 480)
        self.drag = None
        self.start_time = time.monotonic()
        self.last_tap = -100.0
        self.preview_time = None
        self.text = '안녕! 나는 양동이야.\n오늘도 같이 놀자!'
        self.text_until = time.monotonic()+12
        self.last_state = state.scenario
        self.buttons = []
        for name, callback in [('집중', self.toggle_focus), ('놀아줘', self.play), ('설정', self.open_requested.emit)]:
            b = QPushButton(name, self)
            b.setAccessibleName('양동이 '+name)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.clicked.connect(callback)
            b.setStyleSheet('QPushButton { background: #fff0d8; color: #7c5b49; border: 2px solid #b88366; border-bottom: 5px solid #b88366; border-radius: 22px; padding: 0; font-size: 10px; font-weight: 700; } QPushButton:hover { background: #fff9e8; } QPushButton:pressed { background: #e6b48c; border-bottom: 2px solid #b88366; padding-top: 3px; }')
            self.buttons.append(b)
        self.frame_timer = QTimer(self)
        self.frame_timer.setInterval(42)  # 24 fps, only this 360 × 480 canvas.
        self.frame_timer.timeout.connect(self.update)
        state.message.connect(self.speak)
        state.changed.connect(self.react)
        state.tick.connect(self.update)
        self.restore_position()
        self.setToolTip('드래그해서 이동 · 양동이를 두 번 클릭하면 반응해요 · 우클릭 메뉴')

    def restore_position(self):
        area = QApplication.primaryScreen().availableGeometry()
        point = self.settings.value('petPosition')
        if point is not None and any(s.availableGeometry().contains(point) for s in QApplication.screens()):
            self.move(point)
        else:
            self.move(area.right()-self.width()-30, area.bottom()-self.height()-25)

    def resizeEvent(self, event):
        s = self.width()/360
        for i, b in enumerate(self.buttons):
            b.setGeometry(round((83+75*i)*s), round(380*s), round(46*s), round(46*s))
        super().resizeEvent(event)

    def showEvent(self, event):
        self.frame_timer.start()
        super().showEvent(event)

    def hideEvent(self, event):
        self.frame_timer.stop()
        super().hideEvent(event)

    def changeEvent(self, event):
        if self.isMinimized():
            self.frame_timer.stop()
        elif self.isVisible():
            self.frame_timer.start()
        super().changeEvent(event)

    def speak(self, text):
        if not self.state.quiet:
            self.text = text
            self.text_until = time.monotonic()+12
        self.update()

    def react(self):
        if self.last_state != self.state.scenario:
            self.last_tap = time.monotonic()-self.start_time
            self.last_state = self.state.scenario
        self.update()

    def toggle_focus(self):
        self.state.toggle_focus()
        self.state.say('좋아, 같이 집중해 보자!' if self.state.focus else '잠깐 쉬자! 내가 기다릴게.')

    def play(self):
        self.last_tap = time.monotonic()-self.start_time
        self.state.say('앗, 간지러워! 헤헤 ♡\n너랑 노는 게 제일 좋아.')
        self.update()

    @staticmethod
    def font(p, size, bold=False):
        f = QApplication.font()
        f.setPixelSize(size)
        f.setBold(bold)
        p.setFont(f)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.scale(self.width()/360, self.height()/480)
        t = self.preview_time if self.preview_time is not None else time.monotonic()-self.start_time
        self.paint_shell(p)
        p.save()
        clip = QPainterPath()
        clip.addRoundedRect(QRectF(49, 113, 262, 234), 17, 17)
        p.setClipPath(clip)
        self.paint_screen(p, t)
        p.restore()
        p.end()

    def paint_shell(self, p):
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(65, 43, 31, 28))
        p.drawEllipse(QRectF(44, 450, 274, 20))
        shell = QPainterPath(QPointF(180, 15))
        shell.cubicTo(282, 15, 333, 90, 338, 224)
        shell.cubicTo(345, 365, 303, 459, 180, 459)
        shell.cubicTo(57, 459, 15, 365, 22, 224)
        shell.cubicTo(27, 90, 78, 15, 180, 15)
        p.setBrush(QColor('#efb892'))
        p.setPen(QPen(QColor('#956a52'), 2.5))
        p.drawPath(shell)
        p.setPen(QPen(QColor('#ffdfb9'), 4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        p.drawArc(QRectF(36, 31, 288, 250), 35*16, 110*16)
        p.setPen(QColor('#795a47'))
        self.font(p, 22, True)
        p.drawText(QRectF(70, 49, 220, 30), Qt.AlignmentFlag.AlignCenter, '양 동 이')
        self.font(p, 8, True)
        p.drawText(QRectF(70, 80, 220, 14), Qt.AlignmentFlag.AlignCenter, 'L I T T L E   P O C K E T   F R I E N D')
        p.setBrush(QColor('#c19070'))
        p.setPen(QPen(QColor('#ad7c5f'), 2))
        p.drawRoundedRect(QRectF(39, 101, 282, 258), 25, 25)
        p.setBrush(QColor('#d6dfb3'))
        p.setPen(QPen(QColor('#766d4e'), 3))
        p.drawRoundedRect(QRectF(48, 112, 264, 236), 17, 17)
        p.setPen(QColor('#966c53'))
        self.font(p, 8, True)
        p.drawText(QRectF(90, 363, 180, 13), Qt.AlignmentFlag.AlignCenter, '♥   M A D E   T O   B E   W I T H   Y O U')
        p.setPen(QPen(QColor('#b98363'), 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        for x in range(156, 208, 9):
            p.drawLine(x, 440, x+3, 437)
        p.setBrush(QColor('#eee8d2'))
        p.setPen(QPen(QColor('#b88769'), 2))
        p.drawEllipse(QRectF(270, 66, 8, 8))

    def paint_screen(self, p, t):
        p.fillRect(QRectF(49, 113, 262, 234), QColor('#d6dfb3'))
        # Sparse static LCD grid; no image capture or model work per frame.
        p.setPen(QColor('#ccd7a8'))
        for x in range(54, 310, 8):
            for y in range(117, 347, 8):
                p.drawPoint(x, y)
        p.setPen(QColor(INK))
        self.font(p, 10, True)
        status = '집중 중  '+self.state.clock if self.state.focus else {'coding':'코딩 친구', 'music':'음악이 좋아', 'youtube':'잠깐 쉬는 중'}[self.state.scenario]
        p.drawText(QRectF(64, 124, 175, 18), Qt.AlignmentFlag.AlignLeft, '●  '+status)
        self.font(p, 8)
        p.drawText(QRectF(238, 126, 59, 14), Qt.AlignmentFlag.AlignRight, 'DEMO')
        p.setPen(QPen(QColor('#a9bb8b'), 1))
        p.drawLine(64, 150, 296, 150)
        # Tiny room: picture/window, plant and a floor.
        p.setPen(QPen(QColor('#9fb27f'), 2))
        p.drawRoundedRect(QRectF(72, 168, 35, 38), 2, 2)
        p.drawLine(89, 168, 89, 206)
        p.drawLine(72, 187, 107, 187)
        p.drawLine(65, 270, 298, 270)
        p.setBrush(QColor('#a4b986'))
        p.drawRect(QRectF(266, 248, 16, 20))
        p.drawLine(274, 249, 274, 226)
        p.drawEllipse(QRectF(259, 228, 15, 8))
        p.drawEllipse(QRectF(274, 234, 15, 8))
        excited = 0 <= t-self.last_tap < 2.4
        music = self.state.scenario == 'music'
        speed = 9 if music or excited else 3.5
        hop = abs(math.sin(t*speed))*(15 if excited else 9 if music else 3)
        sway = math.sin(t*(6 if music else 2))*(7 if music else 2)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor('#b6c596'))
        p.drawEllipse(QRectF(135+hop/3, 261, 91-hop/2, 8))
        p.save()
        p.translate(180+sway, 216-hop)
        p.rotate(math.sin(t*speed)*(8 if music or excited else 2))
        self.paint_pet(p, t, excited)
        p.restore()
        self.paint_particles(p, t, music, excited)
        p.setPen(QColor(INK))
        self.font(p, 11, True)
        default = '네 옆에 있으니까 좋아.' if not self.state.focus else '하나씩 천천히. 할 수 있어!'
        text = self.text if not self.state.quiet and time.monotonic() < self.text_until else default
        p.drawText(QRectF(64, 282, 232, 50), Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap, text.replace('\n', ' '))
        if self.state.quiet:
            self.font(p, 8)
            p.drawText(QRectF(64, 330, 230, 12), Qt.AlignmentFlag.AlignCenter, '조용히 곁에 있을게')

    def paint_pet(self, p, t, excited):
        # Chunky pixel silhouette with LCD ink, 2-tone shading and animated limbs.
        p.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        p.setPen(QPen(QColor(INK), 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.SquareCap, Qt.PenJoinStyle.MiterJoin))
        p.setBrush(QColor('#c4d39c'))
        p.drawArc(QRectF(-36, -56, 72, 74), 0, 180*16)
        ear = QPainterPath(QPointF(-39,-28)); ear.lineTo(-37,-49); ear.lineTo(-18,-30)
        p.drawPath(ear)
        ear = QPainterPath(QPointF(18,-30)); ear.lineTo(37,-49); ear.lineTo(39,-28)
        p.drawPath(ear)
        body=QPainterPath(QPointF(-45,-27)); body.lineTo(45,-27); body.lineTo(38,35); body.lineTo(30,41); body.lineTo(-30,41); body.lineTo(-38,35); body.closeSubpath()
        p.setBrush(QColor('#e6edc5'))
        p.drawPath(body)
        p.fillRect(QRectF(28,-15,7,44), QColor('#b8c990'))
        p.drawRect(QRectF(-48,-30,96,13))
        limb = math.sin(t*(11 if self.state.scenario == 'coding' else 7))*6
        p.drawLine(-44, 7, -56, round(5+limb))
        p.drawLine(44, 7, 56, round(5-limb))
        p.drawRect(QRectF(-31, 38, 21, 7))
        p.drawRect(QRectF(12, 38, 21, 7))
        blink = t % 4.1 < .16
        if blink or excited:
            for x in (-23, 18):
                p.drawLine(x, 0, x+8, 0)
                if excited:
                    p.drawLine(x, 0, x+4, -4)
        else:
            p.fillRect(QRectF(-23,-3,6,10), QColor(INK))
            p.fillRect(QRectF(18,-3,6,10), QColor(INK))
        p.setPen(QPen(QColor('#9db077'),3))
        p.drawLine(-32, 12, -21,12); p.drawLine(21,12,32,12)
        p.setPen(QPen(QColor(INK),3))
        p.drawLine(-7,14,-3,19); p.drawLine(-3,19,3,19); p.drawLine(3,19,7,14)
        if self.state.scenario == 'coding' and not excited:
            p.setBrush(QColor('#b6c894'))
            p.drawRect(QRectF(-35,29,70,16))
            for x in range(-27,30,10):
                p.drawPoint(x, 35)
            p.drawLine(-21,40,21,40)
        if self.state.scenario == 'music':
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.setPen(QPen(QColor(INK),5))
            p.drawArc(QRectF(-47,-43,94,66),0,180*16)
            p.drawLine(-47,-10,-47,8); p.drawLine(47,-10,47,8)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)

    def paint_particles(self, p, t, music, excited):
        p.setPen(QColor('#697f50'))
        self.font(p, 20, True)
        for i in range(3):
            phase = (t*.65+i*.33)%1
            x = 112+i*65+math.sin(t*2+i)*5
            y = 220-phase*56
            symbol = '♥' if excited else '♪' if music else '·'
            p.setOpacity((1-phase)*.85)
            p.drawText(QPointF(x,y), symbol)
        p.setOpacity(1)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag = event.globalPosition().toPoint()-self.pos()

    def mouseMoveEvent(self, event):
        if self.drag is not None:
            self.move(event.globalPosition().toPoint()-self.drag)

    def mouseReleaseEvent(self, event):
        self.drag = None
        screen = QApplication.screenAt(self.geometry().center()) or QApplication.primaryScreen()
        r = screen.availableGeometry()
        self.move(max(r.left(), min(self.x(),r.right()-self.width()+1)), max(r.top(),min(self.y(),r.bottom()-self.height()+1)))
        self.settings.setValue('petPosition',self.pos())

    def mouseDoubleClickEvent(self, event):
        self.play()

    def contextMenuEvent(self, event):
        menu=QMenu(self)
        menu.addAction('설정 / 대화 열기',self.open_requested.emit)
        menu.addAction('집중 시작 / 일시정지',self.toggle_focus)
        scenes=menu.addMenu('상황 미리보기')
        for key,name in [('coding','코딩하는 양동이'),('music','음악 듣는 양동이'),('youtube','쉬는 양동이')]:
            scenes.addAction(name,lambda k=key:self.state.simulate(k))
        menu.addSeparator()
        menu.addAction('종료',QApplication.quit)
        menu.exec(event.globalPos())
