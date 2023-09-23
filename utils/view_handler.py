from PySide2.QtCore import Qt
from PySide2.QtWidgets import QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QDialog, QStyle, QShortcut
from PySide2.QtGui import QKeySequence

from . import client
from . import tray_handler
from . import xml_handler

_child_windows = None
_main_window = None

def init():
    global _child_windows
    _child_windows = []

def on_login(main_window):
    global _main_window
    _main_window = main_window
    client.create_conn()
    # Run on background
    if xml_handler.get_run_on_bg():
        tray_handler.show()

def show():
    if _main_window.isVisible():
        return
    _main_window.show()

def add_child_window_ref(window_ref):
    _child_windows.append(window_ref)

def update_manual_pwd_vis():
    # Update manual vis pwd check 
    if _main_window.manual_pwd_vis_count == len(_main_window.accs_copy):
        # Update btn text and operation
        _main_window.update_all_pwds_vis_btn()
        _main_window.reset_manual_pwd_vis_count()

def update_acc_table(op, acc):
    _main_window.update_table(op, acc)

def close_child_windows():
    # Closing a child window, automatically removes it from my list  
    i = len(_child_windows) - 1
    while i >= 0:
        child = _child_windows[i]
        child.close()
        i -= 1

def close():
    _main_window.close()

def remove_child_window_ref(window_ref):
    _child_windows.remove(window_ref)

def on_exit():
    client.send_close_socket_msg()

# DEBUG
def set_conn_text(value):
    _main_window.update_conn_status.emit(value)

def show_info_msg_box(title, details='', conn_error=False):
    _main_window.show_info_msg_box.emit(title, details, conn_error)

class PwdExistsDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        # Window properties
        width = 420
        height = 150
        self.setFixedSize(width, height)
        self.setWindowTitle('Warning')
        # Widgets
        self.text_lbl = QLabel(parent=self, text='This password already exists')
        self.details_lbl = QLabel(parent=self, text="Using the same password for multiple accounts isn't recommended.\nContinue ?")
        # Action buttons 
        # Yes
        self.yes_btn = QPushButton(parent=self, text='Yes')
        self.yes_btn.setDefault(True)
        self.yes_btn.clicked.connect(self.accept)
        # No
        self.no_btn = QPushButton(parent=self, text='No')
        self.no_btn.setDefault(True)
        self.no_btn.clicked.connect(self.reject)
        # Style
        self._style()
        # Shortcuts
        close_dialog_sc = QShortcut(QKeySequence('Esc'), self)
        close_dialog_sc.setContext(Qt.WidgetShortcut)
        close_dialog_sc.setAutoRepeat(False)
        close_dialog_sc.activated.connect(self.reject)

    def _style(self):
        # Window icon
        window_icon = self.style().standardIcon(QStyle.SP_MessageBoxInformation)
        self.setWindowIcon(window_icon)
        # Widgets
        self.setStyleSheet("""
            QDialog *
            {
                font-size: 10pt;
            }
        """)
        # Button layout
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.yes_btn)
        btn_layout.addWidget(self.no_btn)
        # Dialog layout
        dialog_layout = QVBoxLayout() 
        dialog_layout.addWidget(self.text_lbl)
        dialog_layout.addWidget(self.details_lbl)
        dialog_layout.addLayout(btn_layout)
        self.setLayout(dialog_layout)
