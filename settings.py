from PySide2.QtCore import Qt
from PySide2.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QComboBox, QSpinBox, QCheckBox, QTabWidget, QVBoxLayout, QHBoxLayout, QSizePolicy, QShortcut
from PySide2.QtGui import QIcon, QKeySequence

from utils import xml_handler
from utils import view_handler

_window = None

class MyLineEdit(QLineEdit):
    def focusInEvent(self, e):
        # Get cursor position before the focus-in event overrides it
        cursor_pos = self.cursorPosition()
        super().focusInEvent(e)
        # Remove default select all on focus
        self.setCursorPosition(cursor_pos)

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
        self.tabs = QTabWidget(parent=self)
        self.tabs.setTabsClosable(False)
        # General tab
        self.general_tab = QWidget(parent=self.tabs)
        # Continue running on background
        self.run_on_bg_checkbox = QCheckBox(parent=self.general_tab, text='Run on background')
        run_on_bg = xml_handler.get_run_on_bg()
        self.run_on_bg_checkbox.setChecked(run_on_bg)
        # Add tab
        self.tabs.addTab(self.general_tab, 'General') 
        # Security tab
        self.security_tab = QWidget(parent=self.tabs)
        # Lock lbl
        self.lock_lbl = QLabel(parent=self.security_tab, text='Set lock code')
        # Lock input
        self.lock_input = MyLineEdit(parent=self.security_tab)
        self.lock_input.setPlaceholderText('Not locked')
        lockCode = xml_handler.get_lock_code()
        self.lock_input.setText(lockCode)
        # Default visibility for passwords
        self.pwd_vis_lbl = QLabel(parent=self.security_tab, text='Password visibility')
        self.pwd_vis_dropdown = QComboBox(parent=self.security_tab)
        self.pwd_vis_dropdown.addItems(['Hide', 'Show'])
        pwd_vis_option_index = xml_handler.get_pwd_vis_option_index()
        self.pwd_vis_dropdown.setCurrentIndex(pwd_vis_option_index)
        # Add tab
        self.tabs.addTab(self.security_tab, 'Security')
        # # Password generation tab
        self.pwd_gen_tab = QWidget(parent=self.tabs)
        # Min len
        self.gen_pwd_min_len_lbl = QLabel(parent=self.pwd_gen_tab, text='Min length')
        self.gen_pwd_min_len_spinbox = QSpinBox(parent=self.pwd_gen_tab)
        self.gen_pwd_min_len_spinbox.setMinimum(xml_handler.MIN_POSSIBLE_GEN_PWD_LEN)
        self.gen_pwd_min_len_spinbox.setMaximum(xml_handler.MAX_POSSIBLE_GEN_PWD_LEN)
        min_pwd_len = xml_handler.get_gen_pwd_min_len()
        self.gen_pwd_min_len_spinbox.setValue(min_pwd_len)
        # Max len
        self.gen_pwd_max_len_lbl = QLabel(parent=self.pwd_gen_tab, text='Max length')
        self.gen_pwd_max_len_spinbox = QSpinBox(parent=self.pwd_gen_tab)
        self.gen_pwd_max_len_spinbox.setMinimum(xml_handler.MIN_POSSIBLE_GEN_PWD_LEN)
        self.gen_pwd_max_len_spinbox.setMaximum(xml_handler.MAX_POSSIBLE_GEN_PWD_LEN)
        max_pwd_len = xml_handler.get_gen_pwd_max_len()
        self.gen_pwd_max_len_spinbox.setValue(max_pwd_len)
        # Reset gen pwd len btn
        self.gen_pwd_reset_len_btn = QPushButton(parent=self.pwd_gen_tab, text='Reset')
        self.gen_pwd_reset_len_btn.setProperty('class', 'gen-pwd-reset-btn')
        self.gen_pwd_reset_len_btn.clicked.connect(self.reset_gen_pwd_len)
        # Add tab
        self.tabs.addTab(self.pwd_gen_tab, 'Password generation')
        # Style window
        self.style()
        # Shortcuts
        close_window_sc = QShortcut(QKeySequence('Ctrl+W'), self)
        close_window_sc.setAutoRepeat(False)
        close_window_sc.activated.connect(self.close)

    def style(self):
        self.setStyleSheet("""
            *
            {
                font-size: 11pt;
            }

            .gen-pwd-reset-btn
            {
                border: 1px solid #353535;
            }
        """)
        fixed_size_policy = QSizePolicy()
        fixed_size_policy.setHorizontalPolicy(QSizePolicy.Fixed)
        fixed_size_policy.setVerticalPolicy(QSizePolicy.Fixed)
        # Tabs
        tabs_size_policy = QSizePolicy()
        tabs_size_policy.setHorizontalPolicy(QSizePolicy.Expanding)
        tabs_size_policy.setVerticalPolicy(QSizePolicy.Fixed)
        self.tabs.setSizePolicy(tabs_size_policy)
        self.tabs.setFixedHeight(150)
        # General tab
        # Run on bg checkbox
        self.run_on_bg_checkbox.setSizePolicy(fixed_size_policy)
        # Add widgets to tab 
        general_tab_layout = QVBoxLayout()
        general_tab_layout.setAlignment(Qt.AlignTop|Qt.AlignLeft)
        general_tab_layout.addWidget(self.run_on_bg_checkbox)
        self.general_tab.setLayout(general_tab_layout)
        # Security tab
        # Lock lbl
        self.lock_lbl.setSizePolicy(fixed_size_policy)
        # Lock input
        self.lock_input.setSizePolicy(fixed_size_policy)
        # Pwd vis lbl
        self.pwd_vis_lbl.setSizePolicy(fixed_size_policy)
        # Pwd vis dropdown
        self.pwd_vis_dropdown.setSizePolicy(fixed_size_policy)
        # Add widgets to tab
        security_tab_layout = QVBoxLayout() 
        security_tab_layout.setAlignment(Qt.AlignTop|Qt.AlignLeft)
        security_tab_lock_layout = QHBoxLayout()
        security_tab_lock_layout.setAlignment(Qt.AlignTop|Qt.AlignLeft)
        security_tab_lock_layout.addWidget(self.lock_lbl)
        security_tab_lock_layout.addWidget(self.lock_input)
        security_tab_layout.addLayout(security_tab_lock_layout)
        security_tab_pwd_vis_layout = QHBoxLayout()
        security_tab_pwd_vis_layout.setAlignment(Qt.AlignTop|Qt.AlignLeft)
        security_tab_pwd_vis_layout.addWidget(self.pwd_vis_lbl)
        security_tab_pwd_vis_layout.addWidget(self.pwd_vis_dropdown)
        security_tab_layout.addLayout(security_tab_pwd_vis_layout)
        self.security_tab.setLayout(security_tab_layout)
        # Pwd generation tab
        # Gen min len
        self.gen_pwd_min_len_lbl.setSizePolicy(fixed_size_policy)
        self.gen_pwd_min_len_spinbox.setSizePolicy(fixed_size_policy)
        self.gen_pwd_min_len_spinbox.setFixedWidth(65)
        self.gen_pwd_min_len_spinbox.setFixedHeight(30)
        # Gen max len
        self.gen_pwd_max_len_lbl.setSizePolicy(fixed_size_policy)
        self.gen_pwd_max_len_spinbox.setSizePolicy(fixed_size_policy)
        self.gen_pwd_max_len_spinbox.setFixedWidth(65)
        self.gen_pwd_max_len_spinbox.setFixedHeight(30)
        # Reset gen pwd len btn
        self.gen_pwd_reset_len_btn.setSizePolicy(fixed_size_policy)
        self.gen_pwd_reset_len_btn.setFixedWidth(self.gen_pwd_reset_len_btn.width()-50)
        self.gen_pwd_reset_len_btn.setFixedHeight(30)
        self.gen_pwd_reset_len_btn.setDefault(True)
        # Add widgets to tab
        pwd_gen_tab_layout = QVBoxLayout()
        pwd_gen_tab_layout.setAlignment(Qt.AlignTop|Qt.AlignLeft)
        pwd_gen_tab_min_len_layout = QHBoxLayout()
        pwd_gen_tab_min_len_layout.setAlignment(Qt.AlignTop|Qt.AlignLeft)
        pwd_gen_tab_min_len_layout.addWidget(self.gen_pwd_min_len_lbl)
        pwd_gen_tab_min_len_layout.addWidget(self.gen_pwd_min_len_spinbox)
        pwd_gen_tab_layout.addLayout(pwd_gen_tab_min_len_layout)
        pwd_gen_tab_max_len_layout = QHBoxLayout()
        pwd_gen_tab_max_len_layout.setAlignment(Qt.AlignTop|Qt.AlignLeft)
        pwd_gen_tab_max_len_layout.addWidget(self.gen_pwd_max_len_lbl)
        pwd_gen_tab_max_len_layout.addWidget(self.gen_pwd_max_len_spinbox)
        pwd_gen_tab_layout.addLayout(pwd_gen_tab_max_len_layout)
        pwd_gen_tab_layout.addWidget(self.gen_pwd_reset_len_btn)
        self.pwd_gen_tab.setLayout(pwd_gen_tab_layout)
        # Window layout
        window_layout = QVBoxLayout()
        window_layout.setAlignment(Qt.AlignTop|Qt.AlignLeft)
        window_layout.addWidget(self.tabs)
        self.setLayout(window_layout)

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
        # General section
        # Run on bg
        state = self.run_on_bg_checkbox.isChecked()
        xml_handler.update_run_on_bg(state)
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
