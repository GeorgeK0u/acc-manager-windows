from PySide2.QtCore import Qt, QSize
from PySide2.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QGroupBox, QSlider, QCheckBox, QMessageBox, QHBoxLayout, QVBoxLayout, QSizePolicy, QShortcut
from PySide2.QtGui import QIcon, QKeySequence, QCursor, QClipboard

import random

from utils import xml_handler
from utils import view_handler
from utils import cryptor
from utils import client

_window = None 
clipboard = None
_gen_pwd_characters = None
_similar_characters = None

class _MyLineEdit(QLineEdit):
    def __init__(self, parent):
        super().__init__(parent)
        self.is_password_type = False

    def focusInEvent(self, e):
        # Get cursor position before the focus-in event overrides it
        cursor_pos = self.cursorPosition()
        super().focusInEvent(e)
        # Remove default select all on focus
        self.setCursorPosition(cursor_pos)

    def keyPressEvent(self, e):
        key = e.key()
        # Copy selection (PySide prevents copying masked pwd)
        if e.modifiers() == Qt.ControlModifier and key == Qt.Key_C:
            if not e.isAutoRepeat() and self.selectionLength() > 0:
                selStartIndex = self.selectionStart()
                selEnd = self.selectionEnd()
                text = self.text()
                selection = text[selStartIndex:selEnd]
                clipboard.setText(selection)
            return True
        if self.is_password_type and e.key() == Qt.Key_Space:
            return True
        super().keyPressEvent(e)

    def set_is_password_type(self, value):
        self.is_password_type = value

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
        self.arrow_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.arrow_btn.clicked.connect(self.on_arrow_btn_click)
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
        self.first_open = True
        self.sub_menu.setVisible(self.is_menu_visible)

    def on_arrow_btn_click(self):
        self.is_menu_visible = not self.is_menu_visible
        if self.is_menu_visible:
            self.show_menu()
        else:
            self.hide_menu()
        
    def show_menu(self):
        # Check for shortcut
        if self.sub_menu.isVisible():
            return
        self.arrow_btn.setText('v')
        self.sub_menu.setVisible(True)
        # Gen pwd on first gen menu open, if no pwd is entered
        if self.first_open:
            if _window.pwd_input.text() == '':
                _window.gen_pwd()
            self.first_open = False
        # Update from shortcut
        if not self.is_menu_visible:
            self.is_menu_visible = True

    def hide_menu(self):
        # Check for shortcut
        if not self.sub_menu.isVisible():
            return
        self.arrow_btn.setText('>')
        self.sub_menu.setVisible(False)
        # Update from shortcut
        if self.is_menu_visible:
            self.is_menu_visible = False
            self.arrow_btn.setFocus()

class _MySlider(QWidget):
    def __init__(self, parent, orientation):
        super().__init__(parent)
        self.orientation = orientation
        self.init_ui()

    def init_ui(self):
        self.value_lbl = QLabel(parent=self)
        self.slider = QSlider(parent=self, orientation=self.orientation)
        self.slider.valueChanged.connect(self.on_value_change)
        # Style widget
        self.style_widget()
        # Shortcuts
        page_step_back_sc = QShortcut(QKeySequence('Ctrl+Left'), self.slider)
        page_step_back_sc.setContext(Qt.WidgetShortcut)
        page_step_back_sc.activated.connect(lambda:self.setValue(self.value()-self.pageStep()))
        page_step_forward_sc = QShortcut(QKeySequence('Ctrl+Right'), self.slider)
        page_step_forward_sc.setContext(Qt.WidgetShortcut)
        page_step_forward_sc.activated.connect(lambda:self.setValue(self.value()+self.pageStep()))

    def style_widget(self):
        # Widget layout 
        widget_layout = QHBoxLayout()
        widget_layout.setAlignment(Qt.AlignTop|Qt.AlignLeft) 
        widget_layout.setSpacing(10)
        widget_layout.addWidget(self.slider)
        widget_layout.addWidget(self.value_lbl)
        self.setLayout(widget_layout)

    def setRange(self, min_value, max_value):
        self.slider.setRange(min_value, max_value)

    def setSingleStep(self, step_value):
        self.slider.setSingleStep(step_value)

    def pageStep(self):
        return self.slider.pageStep()

    def setPageStep(self, page_value):
        self.slider.setPageStep(page_value)

    def value(self):
        return self.slider.value()

    def setValue(self, value):
        self.slider.setValue(value)

    def setFixedWidth(self, width):
        self.slider.setFixedWidth(width)

    def setCursor(self, cursor):
        self.slider.setCursor(cursor)

    def on_value_change(self):
        self.value_lbl.setText(str(self.value()))
        # Gen pwd on slider value change
        if _window:
            _window.gen_pwd()

class _EditAccWindow(QWidget):
    def __init__(self, edit_details):
        super().__init__(parent=None)
        self.edit_details = edit_details
        view_handler.add_child_window_ref(self)
        self.init_ui()

    def init_ui(self):
        # Window properties 
        # Icon
        app_icon = QIcon(f'{xml_handler.resources_dir}/Icons/edit-window-icon')
        self.setWindowIcon(app_icon)
        # Size
        width = 500
        height = 400
        self.setFixedSize(width, height)
        self.setWindowTitle('Edit Account')
        # Widgets
        # Account name input
        self.acc_name_input = _MyLineEdit(parent=self)
        # Extra info input
        self.extra_info_input = _MyLineEdit(parent=self)
        # Password input
        self.pwd_input = _MyLineEdit(parent=self)
        # Password toggle visibility btn
        self.pwd_vis_toggle_btn = QPushButton(parent=self.pwd_input)
        # Trigger enter key as click 
        self.pwd_vis_toggle_btn.setDefault(True)
        self.pwd_vis_toggle_btn.clicked.connect(self.toggle_pwd_vis)
        # Copy pwd btn
        self.copy_pwd_btn = QPushButton(parent=self)
        self.copy_pwd_btn.setDefault(True)
        self.copy_pwd_btn.clicked.connect(self.copy_pwd)
        # Generate group menu
        self.gen_menu = QGroupBox(parent=self)
        # Generate toggle menu visibility btn
        self.gen_menu_toggle_vis_btn = _OptionMenu(parent=self, text='Generate', sub_menu=self.gen_menu)
        # Gen def pwd len
        self.gen_def_pwd_len_lbl = QLabel(parent=self.gen_menu, text='Length')
        self.gen_def_pwd_len_slider = _MySlider(parent=self.gen_menu, orientation=Qt.Horizontal)
        self.gen_def_pwd_len_slider.setRange(xml_handler.MIN_POSSIBLE_GEN_PWD_LEN, xml_handler.MAX_POSSIBLE_GEN_PWD_LEN)
        self.gen_def_pwd_len_slider.setSingleStep(1)
        self.gen_def_pwd_len_slider.setPageStep(5)
        def_pwd_len = xml_handler.get_gen_def_pwd_len()
        self.gen_def_pwd_len_slider.setValue(def_pwd_len)
        # Char list group checkboxes
        # Uppercase
        gen_upper_chars_cbx = QCheckBox(parent=self, text='A-Z')
        gen_upper_chars_cbx.setChecked(True)
        gen_upper_chars_cbx.stateChanged.connect(self.on_char_group_cbx_state_change)
        # Lowercase
        gen_lower_chars_cbx = QCheckBox(parent=self, text='a-z')
        gen_lower_chars_cbx.setChecked(True)
        gen_lower_chars_cbx.stateChanged.connect(self.on_char_group_cbx_state_change)
        # Number
        gen_number_chars_cbx = QCheckBox(parent=self, text='0-9')
        gen_number_chars_cbx.setChecked(True)
        gen_number_chars_cbx.stateChanged.connect(self.on_char_group_cbx_state_change)
        # Special
        gen_special_chars_cbx = QCheckBox(parent=self, text='(!, #, $)')
        gen_special_chars_cbx.setChecked(True)
        gen_special_chars_cbx.stateChanged.connect(self.on_char_group_cbx_state_change)
        self.char_group_cbx_list = [gen_upper_chars_cbx, gen_lower_chars_cbx, gen_number_chars_cbx, gen_special_chars_cbx]
        # Generate pwd btn
        self.gen_btn = QPushButton(parent=self.gen_menu, text='Generate')
        # Trigger enter key as click 
        self.gen_btn.setDefault(True)
        self.gen_btn.clicked.connect(self.gen_pwd)
        # Update btn
        self.update_btn = QPushButton(parent=self, text='Update')
        self.update_btn.setDefault(True)
        self.update_btn.clicked.connect(self.update)
        # Load details
        self.acc_name_input.setText(self.edit_details[0])
        self.extra_info_input.setText(self.edit_details[1])
        self.pwd_input.setText(self.edit_details[2])
        # Style
        self.style()
        # Shortcuts
        # Close window
        close_window_sc = QShortcut(QKeySequence('Ctrl+W'), self)
        close_window_sc.setAutoRepeat(False)
        close_window_sc.activated.connect(self.close)
        # Toggle gen menu
        # From arrow
        show_gen_menu_arrow_sc = QShortcut(QKeySequence('Alt+Right'), self.gen_menu_toggle_vis_btn)
        show_gen_menu_arrow_sc.setContext(Qt.WidgetWithChildrenShortcut)
        show_gen_menu_arrow_sc.setAutoRepeat(False)
        show_gen_menu_arrow_sc.activated.connect(self.gen_menu_toggle_vis_btn.show_menu)
        hide_gen_menu_arrow_sc = QShortcut(QKeySequence('Alt+Left'), self.gen_menu_toggle_vis_btn)
        hide_gen_menu_arrow_sc.setContext(Qt.WidgetWithChildrenShortcut)
        hide_gen_menu_arrow_sc.setAutoRepeat(False)
        hide_gen_menu_arrow_sc.activated.connect(self.gen_menu_toggle_vis_btn.hide_menu)
        # From inside sub-menu
        show_gen_menu_sc = QShortcut(QKeySequence('Alt+Right'), self.gen_menu)
        show_gen_menu_sc.setContext(Qt.WidgetWithChildrenShortcut)
        show_gen_menu_sc.setAutoRepeat(False)
        show_gen_menu_sc.activated.connect(self.gen_menu_toggle_vis_btn.show_menu)
        hide_gen_menu_sc = QShortcut(QKeySequence('Alt+Left'), self.gen_menu)
        hide_gen_menu_sc.setContext(Qt.WidgetWithChildrenShortcut)
        hide_gen_menu_sc.setAutoRepeat(False)
        hide_gen_menu_sc.activated.connect(self.gen_menu_toggle_vis_btn.hide_menu)
        
    def style(self):
        self.setStyleSheet("""
            *
            {
                font-size: 10pt;
            }

            .gen-pwd-btn, .update-btn
            {
                border: 1px solid #353535;
            }

            .pwd-vis-toggle-btn, .copy-pwd-btn
            {
                border: none;
            }

            QSlider::groove:horizontal
            {
                background-color: #AAA; 
                border-radius: 4px;
                height: 10px;
            }
            QSlider::handle:horizontal   
            {
                background-color: #353535;
                width: 20px;
                height: 20px;
                border-radius: 8px;
                margin: -5px 0;
            }
            QSlider::handle:horizontal:hover, QSlider::handle:horizontal:focus
            {
                width: 16px;
                border: 2px solid #88F;
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
        # Copy pwd btn
        self.copy_pwd_btn.setProperty('class', 'copy-pwd-btn')
        self.copy_pwd_btn.setSizePolicy(fixed_size_policy)
        self.copy_pwd_btn.setFixedSize(QSize(28, 28))
        self.copy_pwd_btn.setIcon(QIcon(f'{xml_handler.resources_dir}/Icons/copy-to-clipboard-icon.png'))
        self.pwd_vis_toggle_btn.setIconSize(QSize(28, 28))
        self.copy_pwd_btn.setCursor(QCursor(Qt.PointingHandCursor))
        # Password toggle visibility btn
        self.pwd_vis_toggle_btn.setProperty('class', 'pwd-vis-toggle-btn')
        self.pwd_vis_toggle_btn.setSizePolicy(fixed_size_policy)
        self.pwd_vis_toggle_btn.setFixedSize(24, 24)
        self.pwd_vis_toggle_btn.setIcon(QIcon(f'{xml_handler.resources_dir}/Icons/show-pwd-icon.png'))
        self.pwd_vis_toggle_btn.setIconSize(QSize(24, 24))
        self.pwd_vis_toggle_btn.setCursor(QCursor(Qt.PointingHandCursor))
        # Gen menu toggle vis btn
        self.gen_menu_toggle_vis_btn.setSizePolicy(fixed_size_policy)
        # Gen def pwd len
        self.gen_def_pwd_len_lbl.setSizePolicy(fixed_size_policy)
        self.gen_def_pwd_len_slider.setFixedWidth(200)
        self.gen_def_pwd_len_slider.setCursor(Qt.CursorShape.PointingHandCursor)
        # Char list group checkboxes
        for char_group_cbx in self.char_group_cbx_list:
            char_group_cbx.setSizePolicy(fixed_size_policy)
        # Gen btn
        self.gen_btn.setProperty('class', 'gen-pwd-btn')
        self.gen_btn.setSizePolicy(fixed_size_policy)
        self.gen_btn.setFixedWidth(self.gen_btn.width()-25)
        self.gen_btn.setFixedHeight(30)
        self.gen_btn.setCursor(QCursor(Qt.PointingHandCursor))
        # Update
        self.update_btn.setProperty('class', 'update-btn')
        self.update_btn.setSizePolicy(fixed_size_policy)
        self.update_btn.setFixedWidth(self.update_btn.width())
        self.update_btn.setFixedHeight(30)
        self.update_btn.setCursor(QCursor(Qt.PointingHandCursor))
        # Layout
        # Pwd input layout
        pwd_input_layout = QHBoxLayout()
        pwd_input_layout.setContentsMargins(0, 0, 8, 0)
        pwd_input_layout.setAlignment(Qt.AlignCenter)
        pwd_input_layout.addStretch()
        pwd_input_layout.addWidget(self.pwd_vis_toggle_btn)
        self.pwd_input.setLayout(pwd_input_layout)
        # Pwd layout
        pwd_layout = QHBoxLayout()
        pwd_layout.setAlignment(Qt.AlignTop|Qt.AlignLeft)
        pwd_layout.setSpacing(8)
        pwd_layout.addWidget(self.pwd_input)
        pwd_layout.addWidget(self.copy_pwd_btn)
        # Gen menu layout
        gen_menu_layout = QVBoxLayout()
        gen_menu_layout.setSpacing(20)
        # Gen pwd def len layout
        gen_def_pwd_len_layout = QHBoxLayout()
        gen_def_pwd_len_layout.setSpacing(5)
        gen_def_pwd_len_layout.addWidget(self.gen_def_pwd_len_lbl)
        gen_def_pwd_len_layout.addWidget(self.gen_def_pwd_len_slider)
        gen_menu_layout.addLayout(gen_def_pwd_len_layout)
        # Char list group checkbox layout
        gen_char_group_cbx_layout = QHBoxLayout()
        gen_char_group_cbx_layout.setAlignment(Qt.AlignTop|Qt.AlignLeft)
        for char_group_cbx in self.char_group_cbx_list:
            gen_char_group_cbx_layout.addWidget(char_group_cbx)
        gen_menu_layout.addLayout(gen_char_group_cbx_layout)
        # Gen btn
        gen_menu_layout.addWidget(self.gen_btn)
        self.gen_menu.setLayout(gen_menu_layout)
        # Window layout
        window_layout = QVBoxLayout()
        window_layout.setAlignment(Qt.AlignTop|Qt.AlignLeft)
        window_layout.setSpacing(15)
        window_layout.addWidget(self.acc_name_input)
        window_layout.addWidget(self.extra_info_input)
        window_layout.addLayout(pwd_layout)
        window_layout.addWidget(self.gen_menu_toggle_vis_btn)
        window_layout.addWidget(self.gen_menu)
        window_layout.addWidget(self.update_btn)
        self.setLayout(window_layout)

    def toggle_pwd_vis(self):
        show_pwd = True if self.pwd_input.echoMode() == QLineEdit.Password else False
        # Update pwd masking
        echo_mode = QLineEdit.Normal if show_pwd else QLineEdit.Password
        self.pwd_input.setEchoMode(echo_mode)
        # Update icon
        icon_path = f'{xml_handler.resources_dir}/Icons/hide-pwd-icon.png' if show_pwd else f'{xml_handler.resources_dir}/Icons/show-pwd-icon.png'
        self.pwd_vis_toggle_btn.setIcon(QIcon(icon_path))

    def copy_pwd(self):
        pwd = self.pwd_input.text() 
        if len(pwd) == 0:
            return
        clipboard.setText(pwd)

    def get_only_checked_char_group_cbx(self):
        only_cbx_checked = None
        for char_group_cbx in self.char_group_cbx_list:
            if not char_group_cbx.isChecked():
                continue
            if only_cbx_checked != None:
                return
            only_cbx_checked = char_group_cbx
        return only_cbx_checked

    def get_char_group_cbx_checked_count(self):
        checked_count = 0
        for char_group_cbx in self.char_group_cbx_list:
            if not char_group_cbx.isChecked():
                continue
            checked_count += 1
        return checked_count

    def on_char_group_cbx_state_change(self, value):
        if value == 0:
            # Prevent last checkbox from being unchecked
            only_cbx_checked = self.get_only_checked_char_group_cbx()
            if only_cbx_checked:
                # Disable it
                only_cbx_checked.setEnabled(False)
        else:
            checked_count = self.get_char_group_cbx_checked_count()
            if checked_count == 2:
                # Undo disabled checkbox
                for char_group_cbx in self.char_group_cbx_list:
                    if char_group_cbx.isEnabled(): 
                        continue
                    char_group_cbx.setEnabled(True)
                    break
        # Gen pwd on char group cbx state change
        self.gen_pwd()

    def get_rand_char_from_range_list(self, range_list):
        start = range_list[0]
        end = range_list[1]
        while 1:
            ascii_ = random.randrange(start, end)
            ch = chr(ascii_)
            # Filter char
            if not _similar_characters.__contains__(ch):
                return ch

    def gen_pwd(self):
        pwd_len = self.gen_def_pwd_len_slider.value()
        pwd = ''
        sel_char_group_list = []
        for i in range(len(self.char_group_cbx_list)):
            char_group_cbx = self.char_group_cbx_list[i]
            if not char_group_cbx.isChecked():
                continue
            sel_char_group_list.append(_gen_pwd_characters[i])
        for _ in range(pwd_len):
            list_index = random.randrange(len(sel_char_group_list))
            char_list = sel_char_group_list[list_index]
            ch = self.get_rand_char_from_range_list(char_list) if type(char_list[0]) == int else char_list[random.randrange(len(char_list))]
            pwd += ch
        # Check if password already exists 
        pwds = xml_handler.get_acc_pwds() 
        if pwds.__contains__(pwd):
            self.gen_pwd()
            return
        self.pwd_input.setText(pwd)

    def update(self):
        acc_name = self.acc_name_input.text()
        extra_info = self.extra_info_input.text()
        pwd = self.pwd_input.text()
        # Replace empty fields with '-'
        if extra_info == '':
            extra_info = '-'
        if pwd == '':
            pwd = '-'
        # Check if the details are the same
        acc_details = [acc_name, extra_info, pwd]
        if acc_details == self.edit_details:
            return
        # Empty acc name
        if acc_name == '':
            QMessageBox.critical(self, 'Not Updated', 'The account name cannot be empty')
            return 
        # Acc name already exists
        accs = xml_handler.get_accs()
        acc_names = list(map(lambda acc_details:acc_details[0], accs))
        prev_acc_name = self.edit_details[0]
        acc_name_exists = None
        # Raises a ValueError if the value does not exist in the list 
        try:
            acc_name_exists_index = acc_names.index(acc_name)
            # Check if it exists due to itself
            acc_name_exists = acc_names[acc_name_exists_index] != prev_acc_name
        except ValueError:
            acc_name_exists = False
        if acc_name_exists:
            QMessageBox.critical(self, 'Not Updated', 'This account name already exists')
            return
        # Pwd already exists
        if pwd != '-':
            pwds = list(map(lambda acc_details:acc_details[2], accs))
            pwd_exists = None
            # Raises a ValueError if the value does not exist in the list 
            try:
                pwd_exists_index = pwds.index(pwd)
                # Check if it exists due to itself
                pwd_exists = acc_names[pwd_exists_index] != prev_acc_name
            except ValueError:
                pwd_exists = False
            if pwd_exists:
                warning_dialog = view_handler.PwdExistsDialog(parent=self)
                ret_value = warning_dialog.exec_()
                # User pressed no
                if ret_value == 0:
                    return
        # Send update sync broadcast msg and close window
        operation = 'U'
        enc_prev_acc_name = cryptor.encrypt(prev_acc_name)
        # Get updated details
        msg = [client.SYNC_BC, operation, enc_prev_acc_name]
        for i in range(len(acc_details)):
            detail = acc_details[i]
            if detail == self.edit_details[i]:
                continue
            enc_index = cryptor.encrypt(str(i))
            enc_detail = cryptor.encrypt(detail)
            msg.append([enc_index, enc_detail])
        msg_json_string = cryptor.convert_to_json_string(msg)
        ok = client.send_sync_broadcast_msg(msg_json_string)
        if ok:
            # Handle this device update broadcast locally
            # Remove sync part
            msg.pop(0)
            # Remove operation type part
            msg.pop(0)
            enc_details = msg
            xml_handler.update_acc_value(enc_details)
            # Update manual pwd vis (in case in search results)
            view_handler.update_manual_pwd_vis()
        self.close()

    def closeEvent(self, e):
        super().closeEvent(e)
        view_handler.remove_child_window_ref(self)
        global _window
        _window = None

def init():
    global clipboard, _gen_pwd_characters, _similar_characters
    clipboard = QClipboard()
    _gen_pwd_characters = [
        [65, 90], 
        [97, 122], 
        [48, 57], 
        ['!', '@', '#', '$', '%', '^', '*', '(', ')', '-', '_', '=', '+', '[', '{', ']', '}', '\\', ';', ':', ',', '<', '.', '>', '/', '?']
    ]
    _similar_characters = ['I', 'l']

def create(edit_details):
    global _window
    # Single instance
    if _window != None:
        return
    _window = _EditAccWindow(edit_details)
    _window.show()
