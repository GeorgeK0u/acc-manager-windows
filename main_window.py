from PySide2.QtCore import Qt, Signal, Slot, QSize
from PySide2.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QCheckBox, QComboBox, QTableWidget, QHeaderView, QTableWidgetItem, QMenu, QMessageBox, QHBoxLayout, QVBoxLayout, QSizePolicy, QShortcut
from PySide2.QtGui import QIcon, QKeySequence, QCursor, QClipboard

from utils import xml_handler
from utils import view_handler
from utils import tray_handler
from utils import cryptor
from utils import client
import add_acc
import edit_acc
import settings

_SORT_TIME_ADDED = 0
_SORT_ALPH = 1
_SORT_NUM_OF_FILLED_FIELDS = 2
_ASC_ORDER = 0
_DESC_ORDER = 1
# DEBUG_WIDGET Server connection result values
CLIENT_CONNECTING = 'Connecting...'
CLIENT_CONNECTED = 'Connected'
CLIENT_NOT_CONNECTED = 'Not connected'
#
_window = None
_sort_col_index = None
_all_pwds_vis_bool = None

class MyLineEdit(QLineEdit):
    def focusInEvent(self, e):
        # Get cursor position before the focus-in event overrides it
        cursor_pos = self.cursorPosition()
        super().focusInEvent(e)
        # Remove default select all on focus
        self.setCursorPosition(cursor_pos)

class _TableHeaderWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        expanding_size_policy = QSizePolicy()
        expanding_size_policy.setHorizontalPolicy(QSizePolicy.Expanding)
        expanding_size_policy.setVerticalPolicy(QSizePolicy.Expanding)
        self.setStyleSheet("""
            .header
            {
                font-size: 10pt;
                border: 1px solid black;
            }
        """)
        # Header 1
        header1 = QWidget(parent=self)
        header1.setProperty('class', 'header')
        header1.setSizePolicy(expanding_size_policy)
        # Header 2
        header2 = QWidget(parent=self)
        header2.setProperty('class', 'header')
        header2.setSizePolicy(expanding_size_policy)
        # Header 3
        header3 = QWidget(parent=self)
        header3.setProperty('class', 'header')
        header3.setSizePolicy(expanding_size_policy)
        # Layout
        widget_layout = QHBoxLayout()
        widget_layout.setAlignment(Qt.AlignTop)
        widget_layout.setContentsMargins(0, 0, 0, 0)
        widget_layout.setSpacing(0)
        widget_layout.addWidget(header1)
        widget_layout.addWidget(header2)
        widget_layout.addWidget(header3)
        self.setLayout(widget_layout)
        self.headers = [header1, header2, header3]

    def set_sort_column(self, new_index):
        if _sort_col_index == new_index:
            return
        self.remove_cur_sort_column()
        _set_sort_col_index(new_index)
        parent = self.headers[new_index]
        # Add a visual to sort header column
        fixed_size_policy = QSizePolicy()
        fixed_size_policy.setHorizontalPolicy(QSizePolicy.Fixed)
        fixed_size_policy.setVerticalPolicy(QSizePolicy.Fixed)
        # Sort visual label
        sort_col_visual_icon = QLabel(parent)
        sort_col_visual_icon.setSizePolicy(fixed_size_policy)
        sort_col_visual_icon.setFixedSize(24, 24)
        icon_pixmap = QIcon(r'.\Resources\Icons\sort-col-icon.png').pixmap(24, 24)
        sort_col_visual_icon.setPixmap(icon_pixmap)
        # Add to layout
        parent_layout = QHBoxLayout()
        parent_layout.setContentsMargins(0, 0, 8, 0)
        parent_layout.addStretch()
        parent_layout.setAlignment(Qt.AlignCenter)
        parent_layout.addWidget(sort_col_visual_icon)
        parent.setLayout(parent_layout)

    def remove_cur_sort_column(self):
        # First time
        if _sort_col_index == None:
            return
        parent = self.headers[_sort_col_index]
        for child in parent.children():
            child.deleteLater()
        parent.setLayout(None)

class _Table(QTableWidget):
    def __init__(self, parent):
        super().__init__(parent)
        # Table height manual resize
        self.NO_ROWS_MIN_HEIGHT = 150
        self.last_window_height = None
        self.row_height = 0
        self.min_height = 0
        self.max_height = None
        self.last_fixed_height = None
        self.set_max_height = True
        self.window_bottom_offset = 50
        self.above_layouts_height = 0
        # Re-focus on last focused cell
        self.apply_custom_focus = True
        self.can_update_last_focused = True
        self.last_focused_acc_name = None
        self.currentCellChanged.connect(self.on_cell_focus_change)
        # Shortcuts
        # Focus on header
        focus_on_header_sc = QShortcut(QKeySequence('Ctrl+Up'), self)
        focus_on_header_sc.setContext(Qt.WidgetShortcut)
        focus_on_header_sc.setAutoRepeat(False)
        focus_on_header_sc.activated.connect(self.focus_on_header)
        # Exit header focus shortcuts
        header = self.horizontalHeader()
        # Main exit header focus shortcut
        main_exit_header_focus_sc = QShortcut(QKeySequence('Ctrl+Down'), header)
        main_exit_header_focus_sc.setContext(Qt.WidgetShortcut)
        main_exit_header_focus_sc.setAutoRepeat(False)
        main_exit_header_focus_sc.activated.connect(self.exit_header_focus)
        # Tab exit header focus shortcut
        tab_exit_header_focus_sc = QShortcut(QKeySequence('Tab'), header)
        tab_exit_header_focus_sc.setContext(Qt.WidgetShortcut)
        tab_exit_header_focus_sc.setAutoRepeat(False)
        tab_exit_header_focus_sc.activated.connect(self.exit_header_focus)
        # Shift+Tab exit header focus shortcut
        shift_tab_exit_header_focus_sc = QShortcut(QKeySequence('Shift+Tab'), header)
        shift_tab_exit_header_focus_sc.setContext(Qt.WidgetShortcut)
        shift_tab_exit_header_focus_sc.setAutoRepeat(False)
        shift_tab_exit_header_focus_sc.activated.connect(self.exit_header_focus)
        # When focused widget is header, user can still navigate through the rows with up/down arrow keys
        # Up arrow key exit header shortcut
        up_key_exit_header_focus_sc = QShortcut(QKeySequence('Up'), header)
        up_key_exit_header_focus_sc.setContext(Qt.WidgetShortcut)
        up_key_exit_header_focus_sc.setAutoRepeat(False)
        up_key_exit_header_focus_sc.activated.connect(self.exit_header_focus)
        # Down arrow key exit header shortcut
        down_key_exit_header_focus_sc = QShortcut(QKeySequence('Down'), header)
        down_key_exit_header_focus_sc.setContext(Qt.WidgetShortcut)
        down_key_exit_header_focus_sc.setAutoRepeat(False)
        down_key_exit_header_focus_sc.activated.connect(self.exit_header_focus)
        # Header click
        # Space key
        sort_header_sc1 = QShortcut(QKeySequence('Space'), header)
        sort_header_sc1.setContext(Qt.WidgetShortcut)
        sort_header_sc1.setAutoRepeat(False)
        sort_header_sc1.activated.connect(self.on_header_click)
        # Enter key
        sort_header_sc2 = QShortcut(QKeySequence('Return'), header)
        sort_header_sc2.setContext(Qt.WidgetShortcut)
        sort_header_sc2.setAutoRepeat(False)
        sort_header_sc2.activated.connect(self.on_header_click)
        # Mouse click
        header.sectionClicked.connect(self.on_header_click)
        # Replace table default tab key cell nav
        # Next widget
        focus_on_next_widget_sc = QShortcut(QKeySequence('Tab'), self)
        focus_on_next_widget_sc.setContext(Qt.WidgetShortcut)
        focus_on_next_widget_sc.setAutoRepeat(False)
        focus_on_next_widget_sc.activated.connect(self.focus_on_next_widget)
        # Previous widget 
        focus_on_prev_widget_sc = QShortcut(QKeySequence('Shift+Tab'), self)
        focus_on_prev_widget_sc.setContext(Qt.WidgetShortcut)
        focus_on_prev_widget_sc.setAutoRepeat(False)
        focus_on_prev_widget_sc.activated.connect(self.focus_on_prev_widget)

    def get_updated_last_focused_row_index(self):
        cur_acc_names = list(map(lambda acc:acc[0], _window.accs_copy))
        for i in range(len(cur_acc_names)):
            acc_name = cur_acc_names[i]
            if acc_name != self.last_focused_acc_name:
                continue
            return i
        return -1
        
    def focusInEvent(self, e):
        super().focusInEvent(e)
        if self.rowCount() == 0:
            return
        if not self.apply_custom_focus:
            # Reset bool automatically
            self.apply_custom_focus = True
            return
        refocus_index = self.get_updated_last_focused_row_index()
        item = None
        if refocus_index > -1:
            item = self.item(refocus_index, 0) 
        else:
            # By default if an item is focused and table updates, it doesn't focus on any item  
            item = self.item(0, 0)
        self.setCurrentItem(item)
        self.setItemSelected(item, True)

    def focus_on_header(self):
        self.horizontalHeader().setFocus()

    def exit_header_focus(self):
        self.setFocus()

    def focus_on_next_widget(self):
        _window.focusNextChild()

    def focus_on_prev_widget(self):
        _window.focusPreviousChild()

    def on_header_click(self, clicked_col_index=None):
        # Keyboard click
        if clicked_col_index == None:
            clicked_col_index = self.currentColumn()
        # Don't know why but keyboard clicking on a header after already clicked triggers a column index of -1
        if clicked_col_index < 0 or _sort_col_index == clicked_col_index:
            return
        # Update sort column
        self.horizontalHeader().viewport().set_sort_column(clicked_col_index)
        # Check if needed to update results
        # The other sort options apply to all columns by default
        if _window.sort_option_index != _SORT_ALPH:
            return
        itemCount = len(self.get_all_accs())
        if itemCount <= 1:
            return
        # Update sort
        _window.sort_results()

    def on_cell_focus_change(self, cur_cell_row_index, cur_cell_col_index, prev_cell_row_index, prev_cell_col_index):
        if not self.can_update_last_focused:
            return
        focused_acc_name = self.item(cur_cell_row_index, 0)
        self.last_focused_acc_name = focused_acc_name.text()

    def get_acc(self, row_index):
        row_item = []
        for col_index in range(self.columnCount()):
            value = self.item(row_index, col_index).text()
            row_item.append(value)
        return row_item
    
    def get_all_accs(self):
        # get copy instead of retrieving the table items
        # due to working with password mask
        return _window.accs_copy

    def insert_acc(self, row_index, values):
        self.insertRow(row_index)
        col_index = 0
        for value in values:
            # Default visibility for all pwds setting
            if col_index == self.columnCount()-1 and not _all_pwds_vis_bool:
                value = cryptor.mask_pwd(value)
            item = QTableWidgetItem(value)
            # Prevent direct item editing
            item.setFlags(Qt.ItemIsSelectable | ~Qt.ItemIsEditable)
            self.setItem(row_index, col_index, item)
            col_index += 1
        self.on_rows_changed()

    def append_acc(self, values):
        row_index = self.rowCount()
        self.insert_acc(row_index, values)

    def removeRow(self, row):
        super().removeRow(row)
        self.on_rows_changed()

    def clear_all_accs(self):
        # Clearing the table replaces the focused item
        self.can_update_last_focused = False
        row_index = self.rowCount()-1
        while row_index >= 0:
            self.removeRow(row_index)
            row_index -= 1
        self.can_update_last_focused = True

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self.on_rows_changed()
 
    def on_rows_changed(self):
        parent = self.parentWidget()
        parent_layout = parent.layout()
        if not parent_layout:
            return
        # Manual table resizing based on num of rows
        # Set if first time or table has no rows
        if self.row_height == 0:
            self.row_height = self.rowHeight(0) if self.rowCount() > 0 else 0
        # First row is the header
        row_count = self.rowCount() + 1
        rows_height = self.row_height * row_count
        # Set once
        # (need to set this value as static otherwise the first programmatic maximize gets the above layout sum as 0)
        if self.above_layouts_height == 0:
            # Get above layout widgets height sum 
            layout_height_sum = 0
            for i in range(len(parent_layout.children())):
                layout_height_sum += parent_layout.children()[i].geometry().height()
            if layout_height_sum > 0:
                self.above_layouts_height = layout_height_sum
        window_height = parent.height()
        # Set if first time or table has no rows to determine min height
        if self.min_height == 0 or self.min_height == self.horizontalHeader().height()+self.NO_ROWS_MIN_HEIGHT:
            # First row is the header
            self.min_height = self.row_height * (4+1) if self.row_height > 0 else self.horizontalHeader().height()+self.NO_ROWS_MIN_HEIGHT
        # Check if table height reached max size before resizing it
        if self.above_layouts_height + rows_height + self.window_bottom_offset <= window_height:
            fixed_height = rows_height if rows_height >= self.min_height else self.min_height
            if fixed_height != self.last_fixed_height:
                # Update last fixed height before resizing it
                self.last_fixed_height = fixed_height
                self.setFixedHeight(fixed_height)
                if not self.set_max_height:
                    self.set_max_height = True
        else:
            # Window height changed
            if window_height != self.last_window_height:
                self.last_window_height = window_height
                if self.max_height:
                    self.max_height = None
                    self.set_max_height = True
            # Calc max size
            if not self.max_height:
                max_size = window_height - self.above_layouts_height - self.window_bottom_offset
                # Hide last row if partially displayed
                get_round_scalar = max_size // self.row_height
                max_size_rounded = get_round_scalar * self.row_height
                self.max_height = max_size_rounded
            # Set max size
            if self.set_max_height:
                self.setFixedHeight(self.max_height)
                self.set_max_height = False
                if self.last_fixed_height:
                    self.last_fixed_height = None
            # Scroll to selected item, in case the item was no longer visible
            cur_item = self.currentItem()
            self.scrollToItem(cur_item)

class _MainWindow(QWidget):
    update_conn_status = Signal(str)
    show_info_msg_box = Signal(str, str, bool)

    def __init__(self):
        super().__init__(parent=None)
        self.no_accs_layout = None
        self.accs_copy = None
        # Get global pwd vis setting option
        _set_all_pwds_vis_bool(xml_handler.get_pwd_vis_option_index())
        # Keep a count of manually switched password visibility fields
        # to check update global password visibility btn operation
        self.manual_pwd_vis_count = 0
        # By default sort by time account added
        self.sort_option_index = _SORT_TIME_ADDED
        # By default ascending
        self.sort_order = _ASC_ORDER
        # Update client module connection status from main thread
        self.update_conn_status.connect(self.set_conn_res_text)
        self.show_info_msg_box.connect(self.show_info_msg)
        # Call GUI thread members from client module
        client.sync_instance.sync_msg_received.connect(sync)
        client.sync_instance.manual_sync_completed.connect(self.show_manual_sync_completed_msg_box)
        # Clipboard instance 
        self.clipboard = QClipboard()
        self.init_ui()

    def init_ui(self): 
        # Window properties 
        # Icon
        app_icon = QIcon(r'.\Resources\Icons\app-icon.png')
        self.setWindowIcon(app_icon)
        self.setWindowTitle('Account Manager')
        # Size
        pos_x = 100
        pos_y = 100
        width = 885
        height = 650
        # I have to set a starting pos to re-show it as maximized, otherwise it only renders the minimum size
        self.setGeometry(pos_x, pos_y, width, height)
        self.setMinimumSize(width, height)
        if xml_handler.get_last_window_state() == xml_handler.WINDOW_MAXIMIZED_STATE:
            self.showMaximized()
        # Widgets
        # Search input
        self.search_input = MyLineEdit(parent=self)
        self.search_input.textChanged.connect(self.update_search_results)
        self.search_input.setFocus()
        # Search match case checkbox
        self.search_match_case_checkbox = QCheckBox(parent=self, text='Match case')
        self.search_match_case_checkbox.clicked.connect(self.update_search_results)
        # Display sort dropdown menu
        self.sort_results_lbl = QLabel(parent=self, text='Sort results')
        self.sort_results_dropdown = QComboBox(parent=self)
        self.sort_results_dropdown.addItems(['Time added', 'Alphabetically', 'Number of filled fields'])
        self.sort_results_dropdown.currentIndexChanged.connect(self.on_sort_dropdown_option_change)
        # Sort order button 
        self.sort_order_btn = QPushButton(parent=self)
        # Trigger enter key press as click 
        self.sort_order_btn.setDefault(True)
        self.sort_order_btn.clicked.connect(self.on_sort_order_btn_click)
        # DEBUG_WIDGET Server connection label
        self.conn_label = QLabel(parent=self, text='Client:')
        # DEBUG_WIDGET Server connection result label
        self.conn_res_label = QLabel(parent=self)
        self.update_conn_status.emit(CLIENT_CONNECTING)
        # Settings btn
        self.settings_btn = QPushButton(parent=self)
        # Trigger enter key press as click 
        self.settings_btn.setDefault(True)
        self.settings_btn.clicked.connect(self.show_settings_window)
        # Add btn
        self.add_acc_btn = QPushButton(parent=self)
        # Trigger enter key press as click 
        self.add_acc_btn.setDefault(True)
        self.add_acc_btn.clicked.connect(self.show_add_acc_window)
        # Manual sync btn
        self.manual_sync_btn = QPushButton(parent=self)
        # Trigger enter key press as click 
        self.manual_sync_btn.setDefault(True)
        self.manual_sync_btn.clicked.connect(client.send_manual_sync_msg)
        # Pwd visibility btn
        self.all_pwds_vis_btn = QPushButton(parent=self)
        # Trigger enter key press as click 
        self.all_pwds_vis_btn.setDefault(True)
        self.all_pwds_vis_btn.clicked.connect(self.on_all_pwds_vis_click)
        # Accounts table
        self.table = _Table(parent=self)
        self.col_count = 3
        self.table.setColumnCount(self.col_count)
        self.table.setHorizontalHeaderLabels(['Account Name', 'Extra Info', 'Password'])
        self.table.horizontalHeader().setViewport(_TableHeaderWidget(self.table))
        # By default set the first col for sorting 
        # Visualize default sort column
        self.table.horizontalHeader().viewport().set_sort_column(0)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        accs = xml_handler.get_accs()
        if len(accs) > 0:
            for acc in accs:
                self.table.append_acc(acc)
        else:
            self.table.setMinimumSize(200, 100)
            self.set_no_accs_header_vis(text='No Accounts Added', visible=True)
        # Init pwd copy list
        self.update_accs_copy_list(accs)
        # Set layout
        self.style()
        # Shortcuts
        # Focus on search input
        # '/'
        focus_on_search_input_sc1 = QShortcut(QKeySequence('/'), self)
        focus_on_search_input_sc1.setAutoRepeat(False)
        focus_on_search_input_sc1.activated.connect(self.focus_on_search_input)
        # Alt+D
        focus_on_search_input_sc2 = QShortcut(QKeySequence('Alt+D'), self)
        focus_on_search_input_sc2.setAutoRepeat(False)
        focus_on_search_input_sc2.activated.connect(self.focus_on_search_input)
        # Ctrl+L
        focus_on_search_input_sc3 = QShortcut(QKeySequence('Ctrl+L'), self)
        focus_on_search_input_sc3.setAutoRepeat(False)
        focus_on_search_input_sc3.activated.connect(self.focus_on_search_input)
        # Table right click menu 
        self.table.customContextMenuRequested.connect(self.show_table_right_click_menu)
        # Copy to clipboard
        copy_to_clipboard_sc = QShortcut(QKeySequence('Return'), self.table)
        copy_to_clipboard_sc.setContext(Qt.WidgetShortcut)
        copy_to_clipboard_sc.setAutoRepeat(False)
        copy_to_clipboard_sc.activated.connect(self.copy_to_clipboard)
        # Single item password visibility toggle
        show_hide_pwd_sc = QShortcut(QKeySequence('Space'), self.table)
        show_hide_pwd_sc.setContext(Qt.WidgetShortcut)
        show_hide_pwd_sc.setAutoRepeat(False)
        show_hide_pwd_sc.activated.connect(self.show_hide_pwd)
        # Close window
        close_window_sc = QShortcut(QKeySequence('Ctrl+W'), self)
        close_window_sc.setAutoRepeat(False)
        close_window_sc.activated.connect(self.close)
        # Open window shortcuts
        # Settings
        open_settings_window_sc = QShortcut(QKeySequence('Alt+S'), self)
        open_settings_window_sc.setAutoRepeat(False)
        open_settings_window_sc.activated.connect(self.show_settings_window)
        # Add acc
        open_add_acc_window_sc = QShortcut(QKeySequence('Alt+N'), self)
        open_add_acc_window_sc.setAutoRepeat(False)
        open_add_acc_window_sc.activated.connect(self.show_add_acc_window)
        # Edit acc
        update_acc_sc = QShortcut(QKeySequence('F2'), self.table)
        update_acc_sc.setContext(Qt.WidgetShortcut)
        update_acc_sc.setAutoRepeat(False)
        update_acc_sc.activated.connect(self.show_edit_acc_window)
        # Delete acc
        delete_acc_sc = QShortcut(QKeySequence('Del'), self.table)
        delete_acc_sc.setContext(Qt.WidgetShortcut)
        delete_acc_sc.setAutoRepeat(False)
        delete_acc_sc.activated.connect(self.del_acc)

    def set_conn_res_text(self, value):
        self.conn_res_label.setText(value)
        stylesheet = None
        if value == CLIENT_CONNECTING:
            stylesheet = 'font-size: 10pt; color: #333;'
        elif value == CLIENT_CONNECTED:
            stylesheet = 'font-size: 10pt; color: green;'
        elif value == CLIENT_NOT_CONNECTED:
            stylesheet = 'font-size: 10pt; color: #F11;'
        self.conn_res_label.setStyleSheet(stylesheet)

    def style(self):
        self.setStyleSheet("""
            *
            {
                font-size: 10pt;
            }

            .no-accs-header
            {
                font-size: 14pt;
            }

            QTableWidget
            {
                font-size: 9pt;
            }

            .search-btn, .sort-order-btn, .settings-btn, .add-acc-btn, .manual-sync-btn, .all-pwds-visibility-btn
            {
                border: none;
            }
        """)
        fixed_size_policy = QSizePolicy()
        fixed_size_policy.setHorizontalPolicy(QSizePolicy.Fixed)
        fixed_size_policy.setVerticalPolicy(QSizePolicy.Fixed)
        expanding_size_policy = QSizePolicy()
        expanding_size_policy.setHorizontalPolicy(QSizePolicy.Expanding)
        expanding_size_policy.setVerticalPolicy(QSizePolicy.Expanding)
        # Widgets
        # Search input
        self.search_input.setProperty('class', 'search-input')
        self.search_input.setMinimumWidth(200)
        self.search_input.setFixedHeight(30)
        self.search_input.setPlaceholderText('Search')
        # Search match case checkbox
        self.search_match_case_checkbox.setSizePolicy(fixed_size_policy)
        # Sort widgets 
        # Sort results
        self.sort_results_lbl.setProperty('class', 'sort-results-label')
        self.sort_results_lbl.setSizePolicy(fixed_size_policy)
        self.sort_results_dropdown.setProperty('class', 'sort-results-dropdown')
        self.sort_results_dropdown.setSizePolicy(fixed_size_policy)
        # Sort order btn
        self.sort_order_btn.setProperty('class', 'sort-order-btn')
        self.sort_order_btn.setSizePolicy(fixed_size_policy)
        self.sort_order_btn.setFixedSize(24, 24)
        self.sort_order_btn.setIcon(QIcon(r'.\Resources\Icons\asc-button-icon.png'))
        self.sort_order_btn.setIconSize(QSize(24, 24))
        self.sort_order_btn.setCursor(QCursor(Qt.PointingHandCursor))
        # DEBUG_WIDGET Server connection label
        self.conn_label.setSizePolicy(fixed_size_policy)
        self.conn_label.setStyleSheet('font-size: 10pt; color: black;')
        # DEBUG_WIDGET Server connection result label
        self.conn_res_label.setSizePolicy(fixed_size_policy)
        # Settings btn
        self.settings_btn.setProperty('class', 'settings-btn')
        self.settings_btn.setSizePolicy(fixed_size_policy)
        self.settings_btn.setFixedSize(28, 28)
        self.settings_btn.setIcon(QIcon(r'.\Resources\Icons\settings-icon.png'))
        self.settings_btn.setIconSize(QSize(28, 28))
        self.settings_btn.setCursor(QCursor(Qt.PointingHandCursor))
        # Add acc btn
        self.add_acc_btn.setProperty('class', 'add-acc-btn')
        self.add_acc_btn.setSizePolicy(fixed_size_policy)
        self.add_acc_btn.setFixedSize(32, 32)
        self.add_acc_btn.setIcon(QIcon(r'.\Resources\Icons\add-acc-button-icon.png'))
        self.add_acc_btn.setIconSize(QSize(32, 32))
        self.add_acc_btn.setCursor(QCursor(Qt.PointingHandCursor))
        # Manual sync btn
        self.manual_sync_btn.setProperty('class', 'manual-sync-btn')
        self.manual_sync_btn.setSizePolicy(fixed_size_policy)
        self.manual_sync_btn.setFixedSize(24, 24)
        self.manual_sync_btn.setIcon(QIcon(r'.\Resources\Icons\manual-sync-button-icon.png'))
        self.manual_sync_btn.setIconSize(QSize(24, 24))
        self.manual_sync_btn.setCursor(QCursor(Qt.PointingHandCursor))
        # Pwd visibility btn
        self.all_pwds_vis_btn.setProperty('class', 'all-pwds-visibility-btn')
        self.all_pwds_vis_btn.setSizePolicy(fixed_size_policy)
        self.all_pwds_vis_btn.setFixedSize(24, 24)
        icon_path = r'.\Resources\Icons\show-pwd-icon.png' if not _all_pwds_vis_bool else r'.\Resources\Icons\hide-pwd-icon.png'
        self.all_pwds_vis_btn.setIcon(QIcon(icon_path))
        self.all_pwds_vis_btn.setIconSize(QSize(24, 24))
        self.all_pwds_vis_btn.setCursor(QCursor(Qt.PointingHandCursor))
        # Accounts table
        # Expanding size policy for table columns
        for col_index in range(self.col_count):
            self.table.horizontalHeader().setSectionResizeMode(col_index, QHeaderView.Stretch)
        # Set expanding horizontal policy and fixed vertical
        table_size_policy = QSizePolicy()
        table_size_policy.setHorizontalPolicy(QSizePolicy.Expanding)
        table_size_policy.setVerticalPolicy(QSizePolicy.Fixed)
        self.table.setSizePolicy(table_size_policy)
        # Layout
        # Sort layout
        sort_layout = QHBoxLayout()
        sort_layout.setAlignment(Qt.AlignLeft)
        sort_layout.setContentsMargins(12, 0, 0, 0)
        sort_layout.addWidget(self.sort_results_lbl)
        sort_layout.addWidget(self.sort_results_dropdown)
        sort_layout.addWidget(self.sort_order_btn)
        # Search layout
        top_layout = QHBoxLayout()
        top_layout.setAlignment(Qt.AlignLeft)
        top_layout.setContentsMargins(0, 0, 0, 10)
        top_layout.addWidget(self.search_input)
        top_layout.addWidget(self.search_match_case_checkbox)
        top_layout.addLayout(sort_layout)
        # Push to the screen width end
        top_layout.addStretch()
        # DEBUG_WIDGET Server connection label
        top_layout.addWidget(self.conn_label)
        # DEBUG_WIDGET Server connection result label
        top_layout.addWidget(self.conn_res_label)
        top_layout.addSpacing(10)
        top_layout.addWidget(self.settings_btn)
        # Features layout
        feature_layout = QHBoxLayout()
        feature_layout.setAlignment(Qt.AlignLeft)
        feature_layout.addWidget(self.add_acc_btn)
        feature_layout.addSpacing(15)
        feature_layout.addWidget(self.manual_sync_btn)
        feature_layout.addStretch()
        feature_layout.addWidget(self.all_pwds_vis_btn)
        # Parent layout
        self.window_layout = QVBoxLayout()
        self.window_layout.setAlignment(Qt.AlignTop|Qt.AlignLeft)
        self.window_layout.addLayout(top_layout)
        self.window_layout.addLayout(feature_layout)
        self.window_layout.addWidget(self.table)
        self.setLayout(self.window_layout)

    def show_hide_pwd(self):
        col_index = self.table.currentColumn()
        if col_index < self.table.columnCount() - 1: 
            return
        # Show/hide password
        pwd_text = self.table.currentItem().text()
        if pwd_text.__contains__(cryptor.PWD_MASK_CHAR):
            row_index = self.table.currentRow()
            pwd_text = self.get_pwd_of_row(row_index)
            self.check_update_all_pwds_vis_btn(operation_bool=True)
        else:
            pwd_text = cryptor.mask_pwd(pwd_text)
            self.check_update_all_pwds_vis_btn(operation_bool=False)
        self.table.currentItem().setText(pwd_text)
        # Cause a re-paint to update cell value
        # Prevent applying table custom focus on repaint focus trigger
        self.table.apply_custom_focus = False
        self.table.horizontalHeader().setFocus()
        self.table.setFocus()

    def update_all_pwds_vis_btn(self):
        _set_all_pwds_vis_bool(not _all_pwds_vis_bool)
        # Update btn text
        icon_path = r'.\Resources\Icons\show-pwd-icon.png' if not _all_pwds_vis_bool else r'.\Resources\Icons\hide-pwd-icon.png'
        self.all_pwds_vis_btn.setIcon(QIcon(icon_path))

    def reset_manual_pwd_vis_count(self):
        self.manual_pwd_vis_count = 0

    def check_update_all_pwds_vis_btn(self, operation_bool):
        # Important because if the table items are low and the user manually toggles the password visibility shortcut for each item, then the global one will keep its current operation, which will be doing the same on the first click 
        cur_global_operation_bool = _all_pwds_vis_bool
        if cur_global_operation_bool ^ operation_bool:
            self.manual_pwd_vis_count += 1
            if self.manual_pwd_vis_count == len(self.accs_copy):
                # Update btn text and operation
                self.update_all_pwds_vis_btn()
                self.reset_manual_pwd_vis_count()
        else:
            self.manual_pwd_vis_count -= 1

    def on_all_pwds_vis_click(self):
        self.update_all_pwds_vis_btn()
        # Update visibility
        new_value = _all_pwds_vis_bool
        acc_count = len(self.accs_copy)
        # Handle no accounts case
        if acc_count > 0:
            for i in range(acc_count):
                item = self.table.item(i, self.table.columnCount()-1)
                pwd_value = None
                if new_value:
                    pwd_value = self.get_pwd_of_row(i)
                else:
                    pwd_text = item.text()
                    pwd_value = cryptor.mask_pwd(pwd_text)
                item.setText(pwd_value)
            # Cause a re-paint to update table values
            # Prevent applying table custom focus on repaint focus trigger
            self.table.apply_custom_focus = False
            self.table.setFocus()
            self.all_pwds_vis_btn.setFocus()
            # Reset manual count
            self.reset_manual_pwd_vis_count()

    def update_accs_copy_list(self, accs):
        self.accs_copy = accs
        
    def get_pwd_of_row(self, row_index):
        pwd = self.accs_copy[row_index][-1]
        return pwd

    def sort_results(self, results=None):
        self.table.clear_all_accs()
        # Get current items as the results
        if results == None:
            results = self.table.get_all_accs()
        option_index = self.sort_option_index
        sorted_results = None
        if option_index == _SORT_TIME_ADDED:
            sorted_results = self.sort_by_time_added(results)
        elif option_index == _SORT_ALPH:
            sorted_results = self.sort_alphabetically(results)
        elif option_index == _SORT_NUM_OF_FILLED_FIELDS:
            sorted_results = self.sort_by_num_of_filled_fields(results)
        # Return the results here to get the list without the password mask
        # Display sorted results 
        for result in sorted_results:
            self.table.append_acc(result)
        # Update pwd copy list
        self.update_accs_copy_list(sorted_results)
        self.reset_manual_pwd_vis_count()

    def on_sort_dropdown_option_change(self, option_index):
        # Update sort option
        self.sort_option_index = option_index
        # Check if needed to update results
        item_count = len(self.table.get_all_accs())
        if item_count <= 1:
            return
        # Apply sort
        self.sort_results()

    def on_sort_order_btn_click(self):
        self.sort_order = _DESC_ORDER if self.sort_order == _ASC_ORDER else _ASC_ORDER
        # Update icon
        icon_path = r'.\Resources\Icons\desc-button-icon.png' if self.sort_order == _DESC_ORDER else r'.\Resources\Icons\asc-button-icon.png'
        self.sort_order_btn.setIcon(QIcon(icon_path))
        # Check if needed to update results
        item_count = len(self.table.get_all_accs())
        if item_count <= 1:
            return
        # Update sort
        self.sort_results()

    def get_time_added_item_index_of(self, accs, item):
        index = accs.index(item)
        return index

    def sort_by_time_added(self, results):
        item_count = len(results)
        accs_sorted_by_time_added = xml_handler.get_accs()
        # Sort
        i = 0
        while i < item_count - 1:
            top_item = results[i]
            top_item_index = self.get_time_added_item_index_of(accs_sorted_by_time_added, top_item)
            top_index = i
            j = i + 1
            while j < item_count:
                item_index = self.get_time_added_item_index_of(accs_sorted_by_time_added, results[j])
                if (self.sort_order == _ASC_ORDER and item_index < top_item_index) or (self.sort_order == _DESC_ORDER and item_index > top_item_index):
                    top_item = results[j]
                    top_index = j
                    top_item_index = item_index
                j += 1
            # Transport
            if top_index > i:
                tmp_item = results[i]
                results[top_index] = tmp_item
                results[i] = top_item
            i += 1
        return results

    def greater(self, a, b):
        # Ascending comparison
        a_len = len(a)
        b_len = len(b)
        ch_count = min(a_len, b_len)
        # Decide by character ascii value
        for i in range(ch_count):
            if a[i] == b[i]:
                continue
            if a[i] > b[i]: 
                return 1
            else:
                return 2
        # If the same characters in minimum count, compare by char length
        # Same
        if a_len == b_len:
            return 0
        if a_len > b_len:
            return 1
        return 2

    def sort_alphabetically(self, results):
        item_count = len(results)
        # Get sort column items
        col_values = []
        for item in results:
            for col_index in range(len(item)):
                if col_index != _sort_col_index:
                    continue
                value = item[col_index]
                col_values.append(value)
                break
        # Sort
        i = 0
        while i < item_count - 1:
            top = col_values[i]
            top_index = i
            j = i + 1
            while j < item_count:
                value = col_values[j]
                res = self.greater(top, value)
                if (self.sort_order == _ASC_ORDER and res == 1) or (self.sort_order == _DESC_ORDER and res == 2):
                    top = value
                    top_index = j
                j += 1
            # Transport
            if top_index > i:
                # Col value transport
                tmp_value = col_values[i]
                col_values[top_index] = tmp_value
                col_values[i] = top
                # Item transport
                tmp_item = results[i]
                top_item = results[top_index]
                results[top_index] = tmp_item
                results[i] = top_item
            i += 1
        return results 

    def get_count_of_filled_values(self, item):
        filled_count = 0
        for value in item:
            if value == '-':
                continue
            filled_count += 1
        return filled_count

    def sort_by_num_of_filled_fields(self, results):
        item_count = len(results)
        # Sort
        i = 0
        while i < item_count - 1:
            top = self.get_count_of_filled_values(results[i])
            top_index = i
            j = i + 1
            while j < item_count:
                count = self.get_count_of_filled_values(results[j])
                if (self.sort_order == _ASC_ORDER and count < top) or (self.sort_order == _DESC_ORDER and count > top):
                    top = count
                    top_index = j
                j += 1
            # Transport
            if top_index > i:
                tmp_item = results[i]
                top_item = results[top_index]
                results[top_index] = tmp_item
                results[i] = top_item
            i += 1
        return results

    def copy_to_clipboard(self):
        value = self.table.currentItem().text()
        if value.__contains__(cryptor.PWD_MASK_CHAR):
            # Get password
            row_index = self.table.currentRow()
            value = self.get_pwd_of_row(row_index)
        self.clipboard.setText(value)

    def focus_on_search_input(self):
        if self.search_input.hasFocus():
            return
        self.search_input.setFocus()
        self.search_input.selectAll()

    def update_search_results(self):
        search_query = self.search_input.text()
        match_case = self.search_match_case_checkbox.isChecked()
        if not match_case:
            search_query = search_query.lower()
        # Get search results
        accs = xml_handler.get_accs()
        search_results = []
        for acc in accs:
            for j in range(len(acc)):
                value = acc[j]
                if not match_case:
                    value = value.lower()
                if value.__contains__(search_query):
                    search_results.append(acc)
                    break
        # Display search results
        # Default sorting
        if self.sort_option_index == _SORT_TIME_ADDED or len(search_results) <= 1:
            self.table.clear_all_accs()
            for result in search_results:
                self.table.append_acc(result)
            # Update pwd copy list
            self.update_accs_copy_list(search_results)
            if len(search_results) > 0:
                self.reset_manual_pwd_vis_count()
        else:
            self.sort_results(search_results)
        if len(search_results) > 0:
            # Remove no accs header
            self.set_no_accs_header_vis(visible=False)
        else:
            # Show no accs header
            self.set_no_accs_header_vis(text='No search results', visible=True)

    def show_table_right_click_menu(self, pos):
        menu = QMenu()
        edit_action = menu.addAction('Edit field')
        del_action = menu.addAction('Delete account')
        clicked_action = menu.exec_(self.table.viewport().mapToGlobal(pos))
        if clicked_action == edit_action:
            self.show_edit_acc_window()
        elif clicked_action == del_action:
            self.del_acc()

    def show_edit_acc_window(self):
        # No server connection
        if not client.is_connected() or client.sync_instance.manual_sync_in_progress:
            if not client.is_connected():
                self.show_info_msg_box.emit('Cannot Edit', None, True)
            else:
                self.show_info_msg_box.emit('Cannot Edit', 'Please wait for the sync to finish', False)
            return
        # Get selected row details to show in the edit window
        edit_details = []
        for j in range(self.col_count):
            sel_row_index = self.table.currentRow()
            detail = self.accs_copy[sel_row_index][j]
            edit_details.append(detail)
        edit_acc.create(edit_details)
    
    def del_acc(self):
        # No server connection
        if not client.is_connected() or client.sync_instance.manual_sync_in_progress:
            if not client.is_connected():
                self.show_info_msg_box.emit('Cannot Delete', None, True)
            else:
                self.show_info_msg_box.emit('Cannot Delete', 'Please wait for the sync to finish', False)
            return
        row_index = self.table.currentRow()
        # Sync
        operator = 'D'
        acc_name = self.table.item(row_index, 0).text()
        enc_acc_name = cryptor.encrypt(acc_name)
        msg = [client.SYNC_BC, operator, enc_acc_name]
        msg_json_string = cryptor.convert_to_json_string(msg)
        ok = client.send_sync_broadcast_msg(msg_json_string)
        if ok:
            # Handle this device delete broadcast locally
            xml_handler.del_acc(enc_acc_name)
            # Update manual vis pwd check 
            if self.manual_pwd_vis_count == len(self.accs_copy):
                # Update btn text and operation
                self.update_all_pwds_vis_btn()
                self.reset_manual_pwd_vis_count()

    def get_cur_accs_row_sort_index(self, new_acc_details, _update=False):
        # Check if currently the user has filtered the results with a search and the account shouldn't be added to the table currently
        def filter(unfiltered_row_index):
            search_query = self.search_input.text()
            match_case = self.search_match_case_checkbox.isChecked()
            if not match_case:
                search_query = search_query.lower()
            for acc_detail in new_acc_details:
                if not match_case: 
                    acc_detail = acc_detail.lower()
                if not acc_detail.__contains__(search_query):
                    continue
                return unfiltered_row_index
            return -1
        # First acc
        if len(self.accs_copy) == 0:
            return filter(len(self.accs_copy))
        # Remove acc name before update var
        if _update:
            cur_acc_name = new_acc_details.pop(0)
            # Time added update operation sorting
            if self.sort_option_index == _SORT_TIME_ADDED:
                # Get cur row index
                cur_acc_names = list(map(lambda acc_details: acc_details[0], self.accs_copy))
                return filter(cur_acc_names.index(cur_acc_name))
        # Time added create operation sorting
        if self.sort_option_index == _SORT_TIME_ADDED:
            if self.sort_order == _ASC_ORDER:
                return filter(len(self.accs_copy))
            return filter(0)
        new_detail = None
        new_filled_fields_count = None
        # Alphabetically sorting
        if self.sort_option_index == _SORT_ALPH:
            new_detail = new_acc_details[_sort_col_index]
        # Num of filled fields sorting
        elif self.sort_option_index == _SORT_NUM_OF_FILLED_FIELDS:
            new_filled_fields_count = self.get_count_of_filled_values(new_acc_details)
        for i in range(len(self.accs_copy)): 
            for j in range(self.col_count):
                if j != _sort_col_index:
                    continue
                # Alphabetically sorting
                if self.sort_option_index == _SORT_ALPH:
                    cur_detail = self.accs_copy[i][j]
                    if (self.sort_order == _ASC_ORDER and self.greater(new_detail, cur_detail) == 2) or (self.sort_order == _DESC_ORDER and self.greater(new_detail, cur_detail) == 1):
                        return filter(i)
                # Num of filled fields sorting
                if self.sort_option_index == _SORT_NUM_OF_FILLED_FIELDS:
                    cur_acc = self.accs_copy[i]
                    cur_filled_fields_count = self.get_count_of_filled_values(cur_acc)
                    if (self.sort_order == _ASC_ORDER and new_filled_fields_count < cur_filled_fields_count) or (self.sort_order == _DESC_ORDER and new_filled_fields_count > cur_filled_fields_count):
                        return filter(i)
        return filter(len(self.accs_copy))

    def update_table(self, op, details, _update=False):
        if op == 'C':
            # Get acc sort index
            row_index = self.get_cur_accs_row_sort_index(details, _update)
            if row_index > -1:
                # Add acc row
                self.table.insert_acc(row_index, details)
                if not _update:
                    # Update accs copy list
                    self.accs_copy.insert(row_index, details)
                    # Hide no accs header
                    if len(self.accs_copy) == 1:
                        self.set_no_accs_header_vis(visible=False)
                    # Focus on added acc
                    added_acc = self.table.item(row_index, 0)
                    self.table.setCurrentItem(added_acc)
                    # Select added acc
                    self.table.setItemSelected(added_acc, True)
            self.table.setFocus()
            return row_index
        elif op == 'U':
            cur_acc_name = details[0]
            # Get row index
            cur_acc_names = list(map(lambda acc_details:acc_details[0], self.accs_copy))
            row_index = cur_acc_names.index(cur_acc_name)
            pwd = self.table.item(row_index, 2).text()
            pwd_vis_bool = not pwd.__contains__(cryptor.PWD_MASK_CHAR)
            # Delete
            self.update_table('D', cur_acc_name, _update=True)
            # Add
            filtered_row_index = self.update_table('C', details, _update=True)
            if filtered_row_index > -1:
                # Update accs copy list
                self.accs_copy[row_index] = details
                # Match the pwd mask before update
                if _all_pwds_vis_bool ^ pwd_vis_bool:
                    updated_pwd = self.accs_copy[row_index][2]
                    updated_pwd_item = self.table.item(filtered_row_index, 2)
                    updated_pwd_item.setText(updated_pwd if pwd_vis_bool else cryptor.mask_pwd(updated_pwd))
                # Focus on updated item
                updated_item = self.table.item(filtered_row_index, _sort_col_index)
                self.table.setCurrentItem(updated_item)
                # Select added acc
                self.table.setItemSelected(updated_item, True)
            else:
                # Update accs copy list
                self.accs_copy.pop(row_index)
                # Show no search results header
                if len(self.accs_copy) == 0:
                    self.set_no_accs_header_vis(text='No search results', visible=True)
        # Delete
        elif op == 'D':
            acc_name = details
            # Get acc name row
            cur_acc_names = list(map(lambda acc_details: acc_details[0], self.accs_copy))
            row_index = cur_acc_names.index(acc_name)
            # Remove table row
            self.table.removeRow(row_index)
            if not _update: 
                # Update accs copy list
                self.accs_copy.pop(row_index)
                # Show no accs header
                if len(self.accs_copy) == 0:
                    self.set_no_accs_header_vis(text='No accounts added' if self.search_input.text() == '' else 'No search results', visible=True)
                # Focus on table
                self.table.setFocus()

    def set_no_accs_header_vis(self, visible, text=''):
        if (visible and self.no_accs_layout != None) or (not visible and self.no_accs_layout == None):
            return
        # Update
        if visible:
            no_accs_lbl = QLabel(parent=self.table, text=text)
            no_accs_lbl.setProperty('class', 'no-accs-header')
            self.no_accs_layout = QVBoxLayout()
            self.no_accs_layout.setAlignment(Qt.AlignTop|Qt.AlignHCenter)
            self.no_accs_layout.addSpacing(35)
            self.no_accs_layout.addWidget(no_accs_lbl)
            self.table.setLayout(self.no_accs_layout)
        else:
            item_count = self.no_accs_layout.count()
            i = item_count - 1
            while i >= 0:
                item = self.no_accs_layout.itemAt(i)
                item.layout
                widget = item.widget()
                # QSpacerItem widget is none
                if widget:
                    widget.deleteLater()
                i -= 1
            self.no_accs_layout.deleteLater()
            self.table.setLayout(None)
            self.no_accs_layout = None

    def show_add_acc_window(self):
        # No server connection
        if not client.is_connected() or client.sync_instance.manual_sync_in_progress:
            if not client.is_connected():
                self.show_info_msg_box.emit('Cannot Add', None, True)
            else:
                self.show_info_msg_box.emit('Cannot Add', 'Please wait for the sync to finish', False)
            return
        add_acc.create()

    def show_settings_window(self):
        settings.create()

    def show_info_msg(self, title, details, conn_error):
        conn_error_msg = 'The device has lost connection with server' if self.conn_res_label.text() == CLIENT_NOT_CONNECTED else 'Wait for device to connect with server'
        QMessageBox.information(self, title, details if not conn_error else conn_error_msg)

    def show_manual_sync_completed_msg_box(self):
        QMessageBox.information(self, 'Sync Info', 'Sync completed successfully')

    def closeEvent(self, e):
        view_handler.close_child_windows()
        # Close
        if not xml_handler.get_run_on_bg() or tray_handler.close_bg:
            # Update last window state
            is_maximized = self.isMaximized()
            cur_state = xml_handler.WINDOW_MAXIMIZED_STATE if is_maximized else xml_handler.WINDOW_NORMAL_STATE
            xml_handler.update_last_window_state(cur_state)
            super().closeEvent(e)
            view_handler.on_exit()
        # Hide
        else:
            e.ignore()
            self.hide()
        
def _set_all_pwds_vis_bool(value):
    global _all_pwds_vis_bool
    _all_pwds_vis_bool = value

def _set_sort_col_index(index):
    global _sort_col_index
    _sort_col_index = index

def sync(op, enc_acc_details):
    # Create acc
    if op == 'C':
        print('Create operation type sync message received')
        xml_handler.save_acc(enc_acc_details)
    # Rename acc detail
    elif op == 'U':
        print('Update operation type sync message received')
        xml_handler.update_acc_value(enc_acc_details)
    # Delete acc
    elif op == 'D':
        print('Delete operation type sync message received')
        enc_acc_name = enc_acc_details[0]
        xml_handler.del_acc(enc_acc_name)

def create():
    global _window
    _window = _MainWindow()
    _window.show()
    _window.setFocus()
    return _window
