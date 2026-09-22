"""Optional preview generation: pip install Pillow; python -m docs.render_animation."""
import os
import tempfile
from io import BytesIO
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
from PIL import Image
from PySide6.QtCore import QSettings, QBuffer, QIODevice
from PySide6.QtWidgets import QApplication
from yangdongi.device import PetWindow
from yangdongi.state import CompanionState
from yangdongi.theme import STYLE

app = QApplication([])
app.setStyle('Fusion')
app.setStyleSheet(STYLE)
frames=[]
with tempfile.TemporaryDirectory() as directory:
    state=CompanionState()
    pet=PetWindow(state,QSettings(f'{directory}/demo.ini',QSettings.Format.IniFormat))
    pet.show()
    app.processEvents()
    pet.frame_timer.stop()
    for scene in ('coding','music','play'):
        if scene == 'play':
            pet.play()
            pet.last_tap=0
        else:
            state.simulate(scene)
            pet.last_tap=-100
        for frame in range(48):
            pet.preview_time=frame/20
            buf=QBuffer()
            buf.open(QIODevice.OpenModeFlag.WriteOnly)
            pet.grab().save(buf,'PNG')
            im=Image.open(BytesIO(bytes(buf.data()))).convert('RGBA')
            background=Image.new('RGBA', im.size, '#f7f8f3')
            background.alpha_composite(im)
            frames.append(background.convert('RGB'))
    frames[0].save('docs/device-animation.gif',save_all=True,append_images=frames[1:],duration=50,loop=0)
