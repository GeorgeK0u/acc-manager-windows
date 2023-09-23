from PySide2.QtCore import Qt
from PySide2.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QComboBox, QSpinBox, QCheckBox, QVBoxLayout, QHBoxLayout, QSizePolicy, QShortcut
from PySide2.QtGui import QIcon, QKeySequence

from utils import xml_handler
from utils import view_handler

_window = None

class MyLineEdit(QLineEdit):
    def focusInEvent(self, e):
        super().focusInEvent(e)
        # Set cursor at end
        text_length = len(self.text())
        self.setSelection(text_length, text_length)

class _SettingsWindow(QWidget):
    def __init__(self):
        super().__init__(parent=None)
        view_handler.add_child_window_ref(self)
        self.init_ui()

    def init_ui(self):
        # Window properties 
        # Icon
        app_icon = QIcon(r'.\Resources\Icons\settings-icon.png')
        self.setWindowIcon(app_icon)
        # Size
        width = 500
        height = 400
        self.setFixedSize(width, height)
        self.setWindowTitle('Settings')
        # Widgets
        self.setStyleSheet("""
            *
            {
                font-size: 11pt;
            }

            .header
            {
                font-size: 14pt;
            }

            .gen-pwd-reset-btn
            {
                border: 1px solid #353535;
            }
        """)
        fixed_size_policy = QSizePolicy()
        fixed_size_policy.setHorizontalPolicy(QSizePolicy.Fixed)
        fixed_size_policy.setVerticalPolicy(QSizePolicy.Fixed)
        # Security header
        security_header = QLabel(parent=self, text='Security')
        security_header.setProperty('class', 'header')
        security_header.setSizePolicy(fixed_size_policy)
        # Security section
        # Lock app
        lock_lbl = QLabel(parent=self, text='Set lock code')
        lock_lbl.setSizePolicy(fixed_size_policy)
        self.lock_input = MyLineEdit(parent=self)
        self.lock_input.setSizePolicy(fixed_size_policy)
        self.lock_input.setPlaceholderText('Not locked')
        lockCode = xml_handler.get_lock_code()
        self.lock_input.setText(lockCode)
        # Default visibility for passwords
        pwd_vis_lbl = QLabel(parent=self, text='Password visibility')
        pwd_vis_lbl.setSizePolicy(fixed_size_policy)
        self.pwd_vis_dropdown = QComboBox(parent=self)
        self.pwd_vis_dropdown.addItems(['Hide', 'Show'])
        self.pwd_vis_dropdown.setSizePolicy(fixed_size_policy)
        pwd_vis_option_index = xml_handler.get_pwd_vis_option_index()
        self.pwd_vis_dropdown.setCurrentIndex(pwd_vis_option_index)
        # Password generation section
        gen_pwd_header = QLabel(parent=self, text='Password Generation')
        gen_pwd_header.setProperty('class', 'header')
        gen_pwd_header.setSizePolicy(fixed_size_policy)
        # Min len
        gen_pwd_min_len_lbl = QLabel(parent=self, text='Min length')
        gen_pwd_min_len_lbl.setSizePolicy(fixed_size_policy)
        self.gen_pwd_min_len_spinbox = QSpinBox(parent=self)
        self.gen_pwd_min_len_spinbox.setSizePolicy(fixed_size_policy)
        self.gen_pwd_min_len_spinbox.setFixedWidth(65)
        self.gen_pwd_min_len_spinbox.setFixedHeight(30)
        self.gen_pwd_min_len_spinbox.setMinimum(xml_handler.MIN_POSSIBLE_GEN_PWD_LEN)
        self.gen_pwd_min_len_spinbox.setMaximum(xml_handler.MAX_POSSIBLE_GEN_PWD_LEN)
        min_pwd_len = xml_handler.get_gen_pwd_min_len()
        self.gen_pwd_min_len_spinbox.setValue(min_pwd_len)
        # Max len
        gen_pwd_max_len_lbl = QLabel(parent=self, text='Max length')
        gen_pwd_max_len_lbl.setSizePolicy(fixed_size_policy)
        self.gen_pwd_max_len_spinbox = QSpinBox(parent=self)
        self.gen_pwd_max_len_spinbox.setSizePolicy(fixed_size_policy)
        self.gen_pwd_max_len_spinbox.setFixedWidth(65)
        self.gen_pwd_max_len_spinbox.setFixedHeight(30)
        self.gen_pwd_max_len_spinbox.setMinimum(xml_handler.MIN_POSSIBLE_GEN_PWD_LEN)
        self.gen_pwd_max_len_spinbox.setMaximum(xml_handler.MAX_POSSIBLE_GEN_PWD_LEN)
        max_pwd_len = xml_handler.get_gen_pwd_max_len()
        self.gen_pwd_max_len_spinbox.setValue(max_pwd_len)
        # Reset gen pwd len btn
        gen_pwd_reset_len_btn = QPushButton(parent=self, text='Reset')
        gen_pwd_reset_len_btn.setProperty('class', 'gen-pwd-reset-btn')
        gen_pwd_reset_len_btn.setSizePolicy(fixed_size_policy)
        gen_pwd_reset_len_btn.setFixedWidth(gen_pwd_reset_len_btn.width()-50)
        gen_pwd_reset_len_btn.setFixedHeight(30)
        gen_pwd_reset_len_btn.setDefault(True)
        gen_pwd_reset_len_btn.clicked.connect(self.reset_gen_pwd_len)
        # General section
        general_header = QLabel(parent=self, text='General')
        general_header.setProperty('class', 'header')
        general_header.setSizePolicy(fixed_size_policy)
        # Continue running on background
        self.run_on_bg_checkbox = QCheckBox(parent=self, text='Run on background')
        self.run_on_bg_checkbox.setSizePolicy(fixed_size_policy)
        run_on_bg = xml_handler.get_run_on_bg()
        self.run_on_bg_checkbox.setChecked(run_on_bg)
        # Layout
        # Security layout
        security_layout = QVBoxLayout()
        security_layout.setAlignment(Qt.AlignLeft)
        security_layout.addWidget(security_header)
        # Lock layout
        lock_layout = QHBoxLayout()
        lock_layout.setAlignment(Qt.AlignLeft)
        lock_layout.addWidget(lock_lbl)
        lock_layout.addWidget(self.lock_input)
        # Pwd visibility layout
        pwd_vis_layout = QHBoxLayout()
        pwd_vis_layout.setAlignment(Qt.AlignLeft)
        pwd_vis_layout.addWidget(pwd_vis_lbl)
        pwd_vis_layout.addWidget(self.pwd_vis_dropdown)
        security_layout.addLayout(lock_layout)
        security_layout.addSpacing(6)
        security_layout.addLayout(pwd_vis_layout)
        # Pwd gen layout
        gen_pwd_layout = QVBoxLayout()
        gen_pwd_layout.addWidget(gen_pwd_header)
        # Pwd gen len layout
        gen_pwd_len_layout = QHBoxLayout()
        gen_pwd_len_layout.setAlignment(Qt.AlignLeft)
        # Pwd gen min len layout
        gen_pwd_min_len_layout = QHBoxLayout()
        gen_pwd_min_len_layout.addWidget(gen_pwd_min_len_lbl)
        gen_pwd_min_len_layout.addWidget(self.gen_pwd_min_len_spinbox)
        # Pwd gen max len layout
        gen_pwd_max_len_layout = QHBoxLayout()
        gen_pwd_max_len_layout.addWidget(gen_pwd_max_len_lbl)
        gen_pwd_max_len_layout.addWidget(self.gen_pwd_max_len_spinbox)
        gen_pwd_len_layout.addLayout(gen_pwd_min_len_layout)
        gen_pwd_len_layout.addSpacing(20)
        gen_pwd_len_layout.addLayout(gen_pwd_max_len_layout)
        gen_pwd_len_layout.addSpacing(10)
        gen_pwd_len_layout.addWidget(gen_pwd_reset_len_btn)
        gen_pwd_layout.addLayout(gen_pwd_len_layout)
        # General layout
        general_layout = QVBoxLayout()
        general_layout.addWidget(general_header)
        general_layout.addWidget(self.run_on_bg_checkbox)
        # Window layout
        window_layout = QVBoxLayout()
        window_layout.setAlignment(Qt.AlignTop|Qt.AlignLeft)
        window_layout.addLayout(security_layout)
        window_layout.addSpacing(20)
        window_layout.addLayout(gen_pwd_layout)
        window_layout.addSpacing(20)
        window_layout.addLayout(general_layout)
        self.setLayout(window_layout)
        # Shortcuts
        close_window_sc = QShortcut(QKeySequence('Ctrl+W'), self)
        close_window_sc.setAutoRepeat(False)
        close_window_sc.activated.connect(self.close)

    def reset_gen_pwd_len(self):
        # Min len
        default_min_gen_pwd_len = xml_handler.get_gen_pwd_min_len()
        cur_min_gen_pwd_len = self.gen_pwd_min_len_spinbox.value()
        if cur_min_gen_pwd_len != default_min_gen_pwd_len:
            self.gen_pwd_min_len_spinbox.setValue(default_min_gen_pwd_len)
        # Max len
        default_max_gen_pwd_len = xml_handler.get_gen_pwd_max_len()
        cur_max_gen_pwd_len = self.gen_pwd_max_len_spinbox.value()
        if cur_max_gen_pwd_len != default_max_gen_pwd_len:
            self.gen_pwd_max_len_spinbox.setValue(default_max_gen_pwd_len)

    def update_settings(self):
        # Security section
        # Lock
        typed_code = self.lock_input.text()
        xml_handler.update_lock_code(typed_code)
        # Pwd visibility
        sel_index = self.pwd_vis_dropdown.currentIndex()
        xml_handler.update_pwd_vis_option_index(sel_index)
        # Password generation section
        typed_gen_pwd_min_len = self.gen_pwd_min_len_spinbox.value()
        typed_gen_pwd_max_len = self.gen_pwd_max_len_spinbox.value()
        if typed_gen_pwd_min_len <= typed_gen_pwd_max_len:
            xml_handler.update_gen_pwd_len(typed_gen_pwd_min_len, typed_gen_pwd_max_len)
        # General section
        # Run on bg
        state = self.run_on_bg_checkbox.isChecked()
        xml_handler.update_run_on_bg(state)

    def closeEvent(self, e):
        super().closeEvent(e)
        self.update_settings()
        view_handler.remove_child_window_ref(self)
        global _window
        _window = None

def create():
    global _window
    # Single instance
    if _window:
        return
    _window = _SettingsWindow()
    _window.show()
    _window.setFocus()
