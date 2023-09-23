from PySide2.QtCore import Qt
from PySide2.QtWidgets import QWidget, QLineEdit, QPushButton, QMessageBox, QHBoxLayout, QShortcut
from PySide2.QtGui import QIcon, QKeySequence, QCursor

from utils import xml_handler
from utils import view_handler
import main_window

_window = None

class MyLineEdit(QLineEdit):
    def focusInEvent(self, e):
        super().focusInEvent(e)
        # Set cursor at end
        text_length = len(self.text())
        self.setSelection(text_length, text_length)

class _LoginWindow(QWidget):
    def __init__(self):
        super().__init__(parent=None)
        self.init_ui()

    def init_ui(self):
        # Window properties 
        self.setWindowTitle('Login')
        # Icon
        app_icon = QIcon(r'.\Resources\Icons\app-icon.png')
        self.setWindowIcon(app_icon)
        # Size
        width = 300
        height = 120
        # Prevent resizing
        self.setMinimumSize(width, height)
        self.setMaximumSize(width, height)
        # Widgets
        # Code input
        self.code_input = MyLineEdit(parent=self)
        self.code_input.returnPressed.connect(self.validate)
        self.code_input.setFocus()
        # Login btn 
        self.login_btn = QPushButton(parent=self, text='Login')
        # Trigger enter key press as click 
        self.login_btn.setDefault(True)
        self.login_btn.clicked.connect(self.validate)
        # Set layout
        self.style()
        # Shortcuts
        close_window_sc = QShortcut(QKeySequence('Ctrl+W'), self)
        close_window_sc.setAutoRepeat(False)
        close_window_sc.activated.connect(self.close)

    def style(self):
        self.code_input.setPlaceholderText('Code')
        self.login_btn.setCursor(QCursor(Qt.PointingHandCursor))
        # Layout
        window_layout = QHBoxLayout()
        window_layout.addWidget(self.code_input, stretch=2)
        window_layout.addWidget(self.login_btn, stretch=1)
        self.setLayout(window_layout)

    def validate(self):
        cur_code = xml_handler.get_lock_code()
        typed_code = self.code_input.text()
        # Incorrect code
        if typed_code != cur_code:
            QMessageBox.critical(self, 'Error', 'Incorrect code')
            return
        # Correct code
        main_window_ref = main_window.create()
        view_handler.on_login(main_window_ref)
        # Close login window
        self.close()

def create():
    global _window
    _window = _LoginWindow()
    _window.show()
