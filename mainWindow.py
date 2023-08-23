import ctypes
import pyperclip
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QWidget, QMessageBox, QShortcut, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QCheckBox, QTableWidget, QHeaderView, QTableWidgetItem, QMenu as QRightClickMenu, QSizePolicy
from PySide2.QtGui import QKeySequence, QIcon
# My files
import xmlHandler
import encoder
import clientSocket
import viewHandler
import systemTray
import addAcc
import settings

Window = None
TrayIcon = None

class MyTable(QTableWidget):
    def __init__(self, parent):
        super().__init__(parent)

    def setRowItem(self, values):
        self.setRowCount(self.rowCount() + 1)
        colIndex = 0
        for value in values:
            item = QTableWidgetItem(value)
            self.setItem(self.rowCount()-1, colIndex, item)
            colIndex += 1

    def clearItems(self):
        rowCount = self.rowCount()
        while rowCount >= 0:
            self.removeRow(rowCount)
            rowCount -= 1

class MainWindow(QWidget):
    EditInput = None

    def __init__(self):
        super().__init__(parent=None)
        self.InitUI()

    def InitUI(self): 
        # Windows required to add the icon as the app taskbar icon
        myappid = u'mycompany.myproduct.subproduct.version'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        # Window properties 
        # Icon
        AppIcon = QIcon('./Resources/app-icon32.png')
        self.setWindowIcon(AppIcon)
        self.setWindowTitle('Account Manager')
        # Size
        posX = 100
        posY = 100
        width = 800
        height = 600
        self.setObjectName('window')
        self.setGeometry(posX, posY, width, height)
        self.setMinimumSize(width, height)
        self.showMaximized()
        # Widgets
        # Search input
        self.SearchInput = QLineEdit(parent=self)
        self.SearchInput.setPlaceholderText('Search')
        self.SearchInput.returnPressed.connect(self.UpdateSearchResults)
        # Search match case checkbox
        self.SearchMatchCaseCheckbox = QCheckBox(parent=self, text='Match case')
        # Add btn
        self.AddAccBtn = QPushButton(parent=self, text='Add Account')
        # Trigger enter key press as click 
        self.AddAccBtn.setDefault(True)
        self.AddAccBtn.clicked.connect(addAcc.Create)
        # Manual sync btn
        self.ManualSyncBtn = QPushButton(parent=self, text='Sync')
        # Trigger enter key press as click 
        self.ManualSyncBtn.setDefault(True)
        self.ManualSyncBtn.clicked.connect(clientSocket.SendManualSyncMsg)
        # Settings btn
        self.SettingsBtn = QPushButton(parent=self, text='Settings')
        # Trigger enter key press as click 
        self.SettingsBtn.setDefault(True)
        self.SettingsBtn.clicked.connect(settings.Create)
        # Accounts table
        self.Table = MyTable(parent=self)
        self.colCount = 3
        self.Table.setColumnCount(self.colCount)
        self.Table.setSelectionMode(QTableWidget.SingleSelection)
        self.Table.setHorizontalHeaderLabels(['Account Name', 'Extra Info', 'Password'])
        self.Table.setContextMenuPolicy(Qt.CustomContextMenu)
        Accs = xmlHandler.GetAccs()
        for acc in Accs:
            self.Table.setRowItem(acc)
        # Set layout
        self.Style()
        # Shortcuts
        FocusOnSearchInput1 = QShortcut(QKeySequence('/'), self)
        FocusOnSearchInput1.setAutoRepeat(False)
        FocusOnSearchInput1.activated.connect(self.FocusOnSearchInput)
        FocusOnSearchInput2 = QShortcut(QKeySequence('Alt+D'), self)
        FocusOnSearchInput2.setAutoRepeat(False)
        FocusOnSearchInput2.activated.connect(self.FocusOnSearchInput)
        FocusOnSearchInput3 = QShortcut(QKeySequence('Ctrl+L'), self)
        FocusOnSearchInput3.setAutoRepeat(False)
        FocusOnSearchInput3.activated.connect(self.FocusOnSearchInput)
        self.Table.customContextMenuRequested.connect(self.ShowRightClickTableMenu)
        CopyValue = QShortcut(QKeySequence('Return'), self.Table)
        CopyValue.setContext(Qt.WidgetShortcut)
        CopyValue.setAutoRepeat(False)
        CopyValue.activated.connect(self.CopySelectedValue)
        CloseWindow = QShortcut(QKeySequence('Ctrl+W'), self)
        CloseWindow.setAutoRepeat(False)
        CloseWindow.activated.connect(self.close)

    def Style(self):
        FixedSizePolicy = QSizePolicy()
        FixedSizePolicy.setHorizontalPolicy(QSizePolicy.Fixed)
        FixedSizePolicy.setVerticalPolicy(QSizePolicy.Fixed)
        # Widgets
        # Search input
        self.SearchInput.setProperty('class', 'search-input')
        self.SearchInput.setFixedHeight(30)
        # Search match case checkbox
        self.SearchMatchCaseCheckbox.setSizePolicy(FixedSizePolicy)
        # Add acc btn
        self.AddAccBtn.setSizePolicy(FixedSizePolicy)
        # Set the button height as it was before attaching the fixed size policy
        self.AddAccBtn.setFixedWidth(self.AddAccBtn.width())
        self.AddAccBtn.setFixedHeight(30)
        # Manual sync btn
        self.ManualSyncBtn.setSizePolicy(FixedSizePolicy)
        # Set the button height as it was before attaching the fixed size policy
        self.ManualSyncBtn.setFixedWidth(self.ManualSyncBtn.width())
        self.ManualSyncBtn.setFixedHeight(30)
        # Settings btn
        self.SettingsBtn.setSizePolicy(FixedSizePolicy)
        # Set the button height as it was before attaching the fixed size policy
        self.SettingsBtn.setFixedWidth(self.SettingsBtn.width())
        self.SettingsBtn.setFixedHeight(30)
        # Accounts table
        # Expanding size policy for table columns
        for colIndex in range(self.colCount):
            self.Table.horizontalHeader().setSectionResizeMode(colIndex, QHeaderView.Stretch)
        # Layout
        self.setStyleSheet("""
            QPushButton 
            {
                font-size: 10pt;
                border: 1px solid #333;
            }
            QCheckBox
            {
                font-size: 10pt;
            }

            .search-input, edit-input
            {
                font-size: 11pt;
            }
        """)
        # Search child layout
        SearchLayout = QHBoxLayout()
        SearchLayout.setAlignment(Qt.AlignLeft)
        SearchLayout.addWidget(self.SearchInput)
        SearchLayout.addWidget(self.SearchMatchCaseCheckbox)
        # Push settings to the end
        SearchLayout.addStretch()
        SearchLayout.addWidget(self.SettingsBtn)
        SearchLayout.setContentsMargins(0, 0, 0, 10)
        # Features layout
        FeatureLayout = QHBoxLayout()
        FeatureLayout.setAlignment(Qt.AlignLeft)
        FeatureLayout.setSpacing(20)
        FeatureLayout.addWidget(self.AddAccBtn)
        FeatureLayout.addWidget(self.ManualSyncBtn)
        # Parent layout
        self.WindowLayout = QVBoxLayout()
        self.WindowLayout.setAlignment(Qt.AlignTop|Qt.AlignLeft)
        self.WindowLayout.addLayout(SearchLayout)
        self.WindowLayout.addLayout(FeatureLayout)
        self.WindowLayout.addWidget(self.Table)
        self.setLayout(self.WindowLayout)

    def CopySelectedValue(self):
        selItem = self.Table.selectedItems()[0]
        value = selItem.text()
        pyperclip.copy(value)

    def FocusOnSearchInput(self):
        if self.SearchInput.hasFocus() or self.EditInput != None:
            return
        self.SearchInput.setFocus()
        self.SearchInput.selectAll()

    def UpdateSearchResults(self):
        self.Table.clearItems()
        searchQuery = self.SearchInput.text().lower()
        # Get search results
        Accs = xmlHandler.GetAccs()
        SearchResults = []
        for accTuple in Accs:
            for j in range(len(accTuple)):
                if j == 2:
                    break
                value = accTuple[j].lower()
                if value.__contains__(searchQuery):
                    SearchResults.append(accTuple)
                    break
        # Display search results
        for result in SearchResults:
            self.Table.setRowItem(tuple(result))
        # Select and focus on the first table item
        if len(SearchResults) > 0:
            # Focus on table
            self.Table.setFocus()
            firstItem = self.Table.item(0, 0)
            # Focus on item
            self.Table.setCurrentItem(firstItem)
            # Select item
            self.Table.setItemSelected(firstItem, True)
        else:
            self.SearchInput.setFocus()

    def ShowRightClickTableMenu(self, pos):
        # Check if only one item is selected
        menu = QRightClickMenu()
        editAction = menu.addAction('Edit field')
        delAction = menu.addAction('Delete account')
        clickedAction = menu.exec_(self.Table.viewport().mapToGlobal(pos))
        if clickedAction == editAction:
            self.EditField()
        elif clickedAction == delAction:
            self.DeleteAcc()

    def DeleteAcc(self):
        selItem = self.Table.selectedIndexes()[0]
        self.selRow = selItem.row()
        # Sync
        operator = 'D'
        selAccName = self.Table.item(self.selRow, 0).text()
        encSelAccName = encoder.Encrypt(selAccName)
        msg = f'{clientSocket.SYNC_BC}, {operator}, {encSelAccName}'
        clientSocket.SendSyncBroadcastMsg(msg)
        # Update table
        self.Table.removeRow(self.selRow)

    def EditField(self):
        self.EditInput = QLineEdit(parent=self)
        self.EditInput.setProperty('class', 'edit-input')
        self.EditInput.setStyleSheet('font-size: 11pt;')
        self.EditInput.setPlaceholderText('New value')
        self.EditInput.setMinimumWidth(150)
        self.EditInput.setMaximumWidth(250)
        self.EditInput.setFixedHeight(30)
        self.EditInput.returnPressed.connect(self.UpdateFieldValue)
        self.EditInput.setFocus()
        # Get cur value
        selItem = self.Table.selectedIndexes()[0]
        self.selRow = selItem.row()
        self.selCol = selItem.column()
        self.curValue = self.Table.item(self.selRow, self.selCol).text()
        self.EditInput.setText(self.curValue)
        # Edit input shortcuts
        DeleteEditInput = QShortcut(QKeySequence('Esc'), self.EditInput)
        DeleteEditInput.setAutoRepeat(False)
        DeleteEditInput.activated.connect(self.FocusOnTableAfterEdit)
        PreventTabChange = QShortcut(QKeySequence('Tab'), self.EditInput)
        PreventTabChange.setAutoRepeat(False)
        PreventTabChange.activated.connect(None)
        PreventShiftTabChange = QShortcut(QKeySequence('Shift+Tab'), self.EditInput)
        PreventShiftTabChange.setAutoRepeat(False)
        PreventShiftTabChange.activated.connect(None)
        self.WindowLayout.addWidget(self.EditInput)

    def UpdateFieldValue(self):
        nValue = self.EditInput.text()
        if self.curValue == nValue:
            self.FocusOnTableAfterEdit()
            return
        # Account name value update  
        if self.selCol == 0:
            # Check if already exists
            AccNames = xmlHandler.GetAccNames()
            if AccNames.__contains__(nValue):
                QMessageBox.critical(self, 'Not Added', 'This account name already exists')
                self.FocusOnTableAfterEdit()
                return
        # Sync
        operator = 'U'
        selAccName = self.Table.item(self.selRow, 0).text()
        encSelAccName = encoder.Encrypt(selAccName)
        encSelCol = encoder.Encrypt(self.selCol)
        encNewValue = encoder.Encrypt(nValue)
        msg = f'{clientSocket.SYNC_BC}, {operator}, {encSelAccName}, {encSelCol}, {encNewValue}'
        clientSocket.SendSyncBroadcastMsg(msg)
        # Update table value
        selItem = self.Table.item(self.selRow, self.selCol)
        selItem.setText(nValue)
        self.FocusOnTableAfterEdit()

    def FocusOnTableAfterEdit(self):
        self.EditInput.deleteLater()
        self.EditInput = None
        self.Table.setFocus()

    def show(self):
        super().show()

    def closeEvent(self, e):
        viewHandler.CloseChildWindows()
        # Hide or close
        if not xmlHandler.GetRunOnBg() or systemTray.closeBg:
            super().closeEvent(e)
            viewHandler.OnExit()
        else:
            e.ignore()
            self.hide()
        
def Create():
    global Window
    Window = MainWindow()
    Window.show()
    Window.setFocus()
    return Window
