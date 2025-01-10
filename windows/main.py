from PySide2.QtWidgets import QApplication

import ctypes

from utils import client
from utils import xml_handler
from utils import view_handler
from utils import cryptor
import login
import main_window
import add_acc
import edit_acc

main_window_ref = None

def on_active_window_change(active_window):
    if not main_window_ref:
        return
    # Prevent table custom focus from applying on window re-focus 
    if not active_window or active_window.winId() != main_window_ref.winId(): 
        main_window_ref.table.apply_custom_focus = False

if __name__ == '__main__':
    # Windows required to add the icon as the app taskbar icon
    app_id = u'mycompany.myproduct.subproduct.version'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
    #
    app = QApplication()
    client.init()
    cryptor.init()
    xml_handler.init()
    view_handler.init()
    add_acc.init()
    edit_acc.init()
    if xml_handler.is_locked():
        login.create()
    else:
        main_window_ref = main_window.create()
        view_handler.on_login(main_window_ref)
    app.focusWindowChanged.connect(on_active_window_change)
    app.exec_()
