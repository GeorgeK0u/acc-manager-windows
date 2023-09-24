from PySide2.QtCore import Qt, QSize
from PySide2.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QGroupBox, QSpinBox, QMessageBox, QHBoxLayout, QVBoxLayout, QSizePolicy, QShortcut
from PySide2.QtGui import QIcon, QKeySequence, QCursor, QClipboard

import random

from utils import xml_handler
from utils import view_handler
from utils import cryptor
from utils import client

_window = None 
clipboard = None
_gen_pwd_characters = None

class MyLineEdit(QLineEdit):
    def focusInEvent(self, e):
        # Get cursor position before the focus-in event overrides it
        cursor_pos = self.cursorPosition()
        super().focusInEvent(e)
        # Remove default select all on focus
        self.setCursorPosition(cursor_pos)

    def keyPressEvent(self, e):
        # Copy selection (PySide prevents copying masked pwd)
        if e.modifiers() == Qt.ControlModifier and e.key() == Qt.Key_C:
            if not e.isAutoRepeat() and self.selectionLength() > 0:
                selStartIndex = self.selectionStart()
                selEnd = self.selectionEnd()
                text = self.text()
                selection = text[selStartIndex:selEnd]
                clipboard.setText(selection)
            e.ignore()
            return
        super().keyPressEvent(e)

class _OptionMenu(QWidget):
    def __init__(self, parent, text, sub_menu):
        super().__init__(parent)
        # Widgets
        # Create custom widget
        self.setStyleSheet("""
            .gen-option-menu-lbl, .gen-option-menu-arrow-btn
            {
                font-size: 11pt;
            }

            .gen-option-menu-arrow-btn
            {
                border: none;
            }
        """)
        fixed_size_policy = QSizePolicy()
        fixed_size_policy.setHorizontalPolicy(QSizePolicy.Fixed)
        fixed_size_policy.setVerticalPolicy(QSizePolicy.Fixed)
        # Generate label
        gen_lbl = QLabel(parent=self, text=text)
        gen_lbl.setProperty('class', 'gen-option-menu-lbl')
        # Arrow toggle submenu vis btn 
        self.arrow_btn = QPushButton(parent=self, text='>') 
        self.arrow_btn.setProperty('class', 'gen-option-menu-arrow-btn')
        self.arrow_btn.setSizePolicy(fixed_size_policy)
        self.arrow_btn.setFixedWidth(30)
        self.arrow_btn.setFixedHeight(30)
        self.arrow_btn.setDefault(True)
        self.arrow_btn.clicked.connect(self.on_arrow_btn_click)
        self.arrow_btn.setCursor(QCursor(Qt.PointingHandCursor))
        # Layout
        widget_layout = QHBoxLayout()
        widget_layout.setAlignment(Qt.AlignTop)
        widget_layout.setContentsMargins(0, 0, 0, 0)
        widget_layout.addWidget(gen_lbl)
        widget_layout.addWidget(self.arrow_btn)
        self.setLayout(widget_layout)
        self.sub_menu = sub_menu
        # Start hidden
        self.is_menu_visible = False
        self.sub_menu.setVisible(self.is_menu_visible)

    def on_arrow_btn_click(self):
        self.is_menu_visible = not self.is_menu_visible
        self.arrow_btn.setText('V' if self.is_menu_visible else '>')
        self.sub_menu.setVisible(self.is_menu_visible)

class _AddAccWindow(QWidget):
    def __init__(self):
        super().__init__(parent=None)
        view_handler.add_child_window_ref(self)
        self.init_ui()

    def init_ui(self):
        # Window properties 
        # Icon
        app_icon = QIcon(r'.\Resources\Icons\add-window-icon.png')
        self.setWindowIcon(app_icon)
        # Size
        width = 500
        height = 400
        self.setFixedSize(width, height)
        self.setWindowTitle('Add Account')
        # Widgets
        # Account name input
        self.acc_name_input = MyLineEdit(parent=self)
        self.acc_name_input.setText('')
        # Extra info input
        self.extra_info_input = MyLineEdit(parent=self)
        # Password input
        self.pwd_input = MyLineEdit(parent=self)
        # Password toggle visibility btn
        self.pwd_vis_toggle_btn = QPushButton(parent=self.pwd_input)
        # Trigger enter key as click 
        self.pwd_vis_toggle_btn.setDefault(True)
        self.pwd_vis_toggle_btn.clicked.connect(self.toggle_pwd_vis)
        # Generate group menu
        self.gen_menu = QGroupBox(parent=self)
        # Generate toggle menu visibility btn
        self.gen_menu_toggle_vis_btn = _OptionMenu(parent=self, text='Generate', sub_menu=self.gen_menu)
        # Generate pwd btn
        self.gen_btn = QPushButton(parent=self.gen_menu, text='Generate')
        # Trigger enter key as click 
        self.gen_btn.setDefault(True)
        self.gen_btn.clicked.connect(self.gen_pwd)
        # Min len
        self.gen_pwd_min_len_lbl = QLabel(parent=self, text='Min length')
        self.gen_pwd_min_len_spinbox = QSpinBox(parent=self)
        self.gen_pwd_min_len_spinbox.setMinimum(xml_handler.MIN_POSSIBLE_GEN_PWD_LEN)
        self.gen_pwd_min_len_spinbox.setMaximum(xml_handler.MAX_POSSIBLE_GEN_PWD_LEN)
        min_pwd_len = xml_handler.get_gen_pwd_min_len()
        self.gen_pwd_min_len_spinbox.setValue(min_pwd_len)
        # Max len
        self.gen_pwd_max_len_lbl = QLabel(parent=self, text='Max length')
        self.gen_pwd_max_len_spinbox = QSpinBox(parent=self)
        self.gen_pwd_max_len_spinbox.setMinimum(xml_handler.MIN_POSSIBLE_GEN_PWD_LEN)
        self.gen_pwd_max_len_spinbox.setMaximum(xml_handler.MAX_POSSIBLE_GEN_PWD_LEN)
        max_pwd_len = xml_handler.get_gen_pwd_max_len()
        self.gen_pwd_max_len_spinbox.setValue(max_pwd_len)
        # Reset gen pwd len btn
        self.gen_pwd_reset_len_btn = QPushButton(parent=self, text='Reset')
        self.gen_pwd_reset_len_btn.setDefault(True)
        self.gen_pwd_reset_len_btn.clicked.connect(self.reset_gen_pwd_len)
        # Add acc btn
        self.add_acc_btn = QPushButton(parent=self, text='Add Account')
        self.add_acc_btn.setDefault(True)
        self.add_acc_btn.clicked.connect(self.add_account)
        # Style
        self.style()
        # Shortcuts
        # Close window
        close_window_sc = QShortcut(QKeySequence('Ctrl+W'), self)
        close_window_sc.setAutoRepeat(False)
        close_window_sc.activated.connect(self.close)
        
    def style(self):
        self.setStyleSheet("""
            .acc-name-input, .extra-info-input, .pwd-input, .pwd-vis-toggle-btn, .add-acc-btn
            {
                font-size: 11pt;
            }

            .gen-submenu-input, .gen-pwd-btn
            {
                font-size: 10pt;
            }

            .gen-pwd-reset-btn, .gen-pwd-btn, .add-acc-btn
            {
                border: 1px solid #353535;
            }

            .pwd-vis-toggle-btn
            {
                border: none;
            }
        """)
        fixed_size_policy = QSizePolicy()
        fixed_size_policy.setHorizontalPolicy(QSizePolicy.Fixed)
        fixed_size_policy.setVerticalPolicy(QSizePolicy.Fixed)
        # Widgets
        # Acc name input
        self.acc_name_input.setProperty('class', 'acc-name-input')
        self.acc_name_input.setSizePolicy(fixed_size_policy)
        self.acc_name_input.setFixedWidth(250)
        self.acc_name_input.setFixedHeight(30)
        self.acc_name_input.setPlaceholderText('Account name')
        # Extra info input
        self.extra_info_input.setProperty('class', 'extra-info-input')
        self.extra_info_input.setSizePolicy(fixed_size_policy)
        self.extra_info_input.setFixedWidth(250)
        self.extra_info_input.setFixedHeight(30)
        self.extra_info_input.setPlaceholderText('Extra info e.g. email')
        # Password input
        self.pwd_input.setProperty('class', 'pwd-input')
        self.pwd_input.setSizePolicy(fixed_size_policy)
        self.pwd_input.setFixedWidth(250)
        self.pwd_input.setFixedHeight(30)
        self.pwd_input.setPlaceholderText('Password')
        self.pwd_input.setEchoMode(QLineEdit.Password)
        # Password toggle visibility btn
        self.pwd_vis_toggle_btn.setProperty('class', 'pwd-vis-toggle-btn')
        self.pwd_vis_toggle_btn.setSizePolicy(fixed_size_policy)
        self.pwd_vis_toggle_btn.setFixedSize(24, 24)
        self.pwd_vis_toggle_btn.setIcon(QIcon(r'.\Resources\Icons\show-pwd-icon.png'))
        self.pwd_vis_toggle_btn.setIconSize(QSize(24, 24))
        self.pwd_vis_toggle_btn.setCursor(QCursor(Qt.PointingHandCursor))
        # Gen menu toggle vis btn
        self.gen_menu_toggle_vis_btn.setSizePolicy(fixed_size_policy)
        # Gen btn
        self.gen_btn.setProperty('class', 'gen-pwd-btn')
        self.gen_btn.setSizePolicy(fixed_size_policy)
        self.gen_btn.setFixedWidth(self.gen_btn.width()-25)
        self.gen_btn.setFixedHeight(30)
        self.gen_btn.setCursor(QCursor(Qt.PointingHandCursor))
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
        # Reset gen len btn
        self.gen_pwd_reset_len_btn.setProperty('class', 'gen-pwd-reset-btn')
        self.gen_pwd_reset_len_btn.setSizePolicy(fixed_size_policy)
        self.gen_pwd_reset_len_btn.setFixedWidth(self.gen_pwd_reset_len_btn.width()-50)
        self.gen_pwd_reset_len_btn.setFixedHeight(30)
        self.gen_pwd_reset_len_btn.setCursor(QCursor(Qt.PointingHandCursor))
        # Add acc btn
        self.add_acc_btn.setProperty('class', 'add-acc-btn')
        self.add_acc_btn.setSizePolicy(fixed_size_policy)
        self.add_acc_btn.setFixedWidth(self.add_acc_btn.width())
        self.add_acc_btn.setFixedHeight(30)
        self.add_acc_btn.setCursor(QCursor(Qt.PointingHandCursor))
        # Layout
        # Pwd input layout
        pwd_input_layout = QHBoxLayout()
        pwd_input_layout.setContentsMargins(0, 0, 8, 0)
        pwd_input_layout.setAlignment(Qt.AlignCenter)
        pwd_input_layout.addStretch()
        pwd_input_layout.addWidget(self.pwd_vis_toggle_btn)
        self.pwd_input.setLayout(pwd_input_layout)
        # Gen menu layout
        gen_menu_layout = QVBoxLayout()
        gen_menu_layout.setSpacing(20)
        # Gen pwd len layout
        gen_pwd_len_layout = QHBoxLayout()
        gen_pwd_len_layout.setAlignment(Qt.AlignLeft)
        gen_pwd_len_layout.setSpacing(0)
        gen_menu_layout.addWidget(self.gen_btn)
        # Gen pwd min len layout
        gen_pwd_min_len_layout = QHBoxLayout()
        gen_pwd_min_len_layout.setSpacing(5)
        gen_pwd_min_len_layout.addWidget(self.gen_pwd_min_len_lbl)
        gen_pwd_min_len_layout.addWidget(self.gen_pwd_min_len_spinbox)
        # Gen pwd max len layout
        gen_pwd_max_len_layout = QHBoxLayout()
        gen_pwd_max_len_layout.setSpacing(5)
        gen_pwd_max_len_layout.addWidget(self.gen_pwd_max_len_lbl)
        gen_pwd_max_len_layout.addWidget(self.gen_pwd_max_len_spinbox)
        gen_pwd_len_layout.addLayout(gen_pwd_min_len_layout)
        gen_pwd_len_layout.addSpacing(20)
        gen_pwd_len_layout.addLayout(gen_pwd_max_len_layout)
        gen_pwd_len_layout.addSpacing(10)
        gen_pwd_len_layout.addWidget(self.gen_pwd_reset_len_btn)
        gen_menu_layout.addLayout(gen_pwd_len_layout)
        self.gen_menu.setLayout(gen_menu_layout)
        # Window layout
        window_layout = QVBoxLayout()
        window_layout.setAlignment(Qt.AlignTop|Qt.AlignLeft)
        window_layout.setSpacing(15)
        window_layout.addWidget(self.acc_name_input)
        window_layout.addWidget(self.extra_info_input)
        window_layout.addWidget(self.pwd_input)
        window_layout.addWidget(self.gen_menu_toggle_vis_btn)
        window_layout.addWidget(self.gen_menu)
        window_layout.addWidget(self.add_acc_btn)
        self.setLayout(window_layout)

    def toggle_pwd_vis(self):
        show_pwd = True if self.pwd_input.echoMode() == QLineEdit.Password else False
        # Update pwd masking
        echo_mode = QLineEdit.Normal if show_pwd else QLineEdit.Password
        self.pwd_input.setEchoMode(echo_mode)
        # Update icon
        icon_path = r'.\Resources\Icons\hide-pwd-icon.png' if show_pwd else r'.\Resources\Icons\show-pwd-icon.png'
        self.pwd_vis_toggle_btn.setIcon(QIcon(icon_path))

    def gen_pwd(self):
        min_pwd_len = self.gen_pwd_min_len_spinbox.value()
        max_pwd_len = self.gen_pwd_max_len_spinbox.value()
        # Min gen pwd len cannot be greater than max
        if min_pwd_len > max_pwd_len:
            QMessageBox.information(self, 'Generate Failed', 'Minimum selected range is greater than maximum')
            return
        pwd_len = random.randint(min_pwd_len, max_pwd_len)
        pwd = ''
        for _ in range(pwd_len):
            arr_index = random.randrange(0, len(_gen_pwd_characters))
            ch_arr = _gen_pwd_characters[arr_index]
            ch = chr(random.randint(ch_arr[0], ch_arr[1])) if (len(ch_arr) == 2) else ch_arr[random.randint(0, len(ch_arr) - 1)]
            pwd += ch
        # Check if password already exists 
        pwds = xml_handler.get_acc_pwds() 
        if pwds.__contains__(pwd):
            self.gen_pwd()
            return
        self.pwd_input.setText(pwd)

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

    def add_account(self):
        acc_name = self.acc_name_input.text()
        # Empty acc name
        if acc_name == '':
            QMessageBox.critical(self, 'Not Added', 'The account name cannot be empty')
            return
        # Acc name already exists
        accs = xml_handler.get_accs()
        acc_names = list(map(lambda acc_details:acc_details[0], accs))
        if acc_names.__contains__(acc_name):
            QMessageBox.critical(self, 'Not Added', 'This account name already exists')
            return
        # Replace empty fields with '-'
        extra_info = self.extra_info_input.text()
        pwd = self.pwd_input.text()
        if extra_info == '':
            extra_info = '-'
        if pwd == '':
            pwd = '-'
        # Check if pwd already exists
        if pwd != '-':
            pwds = list(map(lambda acc_details:acc_details[2], accs))
            if pwds.__contains__(pwd):
                warning_dialog = view_handler.PwdExistsDialog(parent=self)
                ret_value = warning_dialog.exec_()
                # User pressed no
                if ret_value == 0:
                    return
        # Sync
        enc_acc_name = cryptor.encrypt(acc_name)
        enc_extra_info = cryptor.encrypt(extra_info)
        enc_pwd = cryptor.encrypt(pwd)
        operation = 'C'
        msg = [client.SYNC_BC, operation, enc_acc_name, enc_extra_info, enc_pwd]
        msg_json_string = cryptor.convert_to_json_string(msg)
        ok = client.send_sync_broadcast_msg(msg_json_string)
        if ok:
            # Handle this device create broadcast locally
            enc_acc_details = [enc_acc_name, enc_extra_info, enc_pwd]
            xml_handler.save_acc(enc_acc_details)
        # Clear fields
        self.acc_name_input.setText('')
        self.extra_info_input.setText('')
        self.pwd_input.setText('')
        self.acc_name_input.setFocus()

    def closeEvent(self, e):
        super().closeEvent(e)
        view_handler.remove_child_window_ref(self)
        global _window
        _window = None

def init():
    global clipboard, _gen_pwd_characters
    clipboard = QClipboard()
    _gen_pwd_characters = [[48, 57], [65, 90], [97, 122], ['-', '_', '.', ',', '/', ';']]

def create():
    global _window
    # Single instance
    if _window != None:
        return
    _window = _AddAccWindow()
    _window.show()
