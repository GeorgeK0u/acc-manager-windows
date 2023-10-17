from PySide2.QtCore import Qt
from PySide2.QtWidgets import QWidget, QLabel, QLineEdit, QComboBox, QSlider, QCheckBox, QTabWidget, QVBoxLayout, QHBoxLayout, QSizePolicy, QShortcut
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

class _SettingsWindow(QWidget):
    def __init__(self):
        super().__init__(parent=None)
        view_handler.add_child_window_ref(self)
        self.init_ui()

    def init_ui(self):
        # Window properties 
        # Icon
        app_icon = QIcon(f'{xml_handler.resources_dir}/Icons/settings-icon.png')
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
        # Gen def pwd len
        self.gen_def_pwd_len_lbl = QLabel(parent=self.pwd_gen_tab, text='Length')
        self.gen_def_pwd_len_slider = _MySlider(parent=self.pwd_gen_tab, orientation=Qt.Horizontal)
        self.gen_def_pwd_len_slider.setRange(xml_handler.MIN_POSSIBLE_GEN_PWD_LEN, xml_handler.MAX_POSSIBLE_GEN_PWD_LEN)
        self.gen_def_pwd_len_slider.setSingleStep(1)
        self.gen_def_pwd_len_slider.setPageStep(5)
        def_pwd_len = xml_handler.get_gen_def_pwd_len()
        self.gen_def_pwd_len_slider.setValue(def_pwd_len)
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
        # Gen def pwd len
        self.gen_def_pwd_len_lbl.setSizePolicy(fixed_size_policy)
        self.gen_def_pwd_len_slider.setFixedWidth(200)
        self.gen_def_pwd_len_slider.setCursor(Qt.CursorShape.PointingHandCursor)
        # Add widgets to tab
        pwd_gen_tab_layout = QVBoxLayout()
        pwd_gen_tab_layout.setAlignment(Qt.AlignTop|Qt.AlignLeft)
        pwd_gen_tab_def_len_layout = QHBoxLayout()
        pwd_gen_tab_def_len_layout.setAlignment(Qt.AlignTop|Qt.AlignLeft)
        pwd_gen_tab_def_len_layout.setSpacing(15)
        pwd_gen_tab_def_len_layout.addWidget(self.gen_def_pwd_len_lbl)
        pwd_gen_tab_def_len_layout.addWidget(self.gen_def_pwd_len_slider)
        pwd_gen_tab_layout.addLayout(pwd_gen_tab_def_len_layout)
        self.pwd_gen_tab.setLayout(pwd_gen_tab_layout)
        # Window layout
        window_layout = QVBoxLayout()
        window_layout.setAlignment(Qt.AlignTop|Qt.AlignLeft)
        window_layout.addWidget(self.tabs)
        self.setLayout(window_layout)

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
        sel_def_pwd_len = self.gen_def_pwd_len_slider.value()
        xml_handler.update_gen_def_pwd_len(sel_def_pwd_len)

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
