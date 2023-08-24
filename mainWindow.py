import ctypes
import pyperclip
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QWidget, QMessageBox, QShortcut, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QCheckBox, QTableWidget, QHeaderView, QTableWidgetItem, QMenu as QRightClickMenu, QSizePolicy, QComboBox
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
SORT_TIME_ADDED = 0
SORT_ALPH = 1
SORT_NUM_OF_FILLED_FIELDS = 2

class MyTable(QTableWidget):
    def __init__(self, parent):
        super().__init__(parent)
        # Shortcuts
        # Focus on header
        FocusOnHeader = QShortcut(QKeySequence('Ctrl+Up'), self)
        FocusOnHeader.setContext(Qt.WidgetShortcut)
        FocusOnHeader.setAutoRepeat(False)
        FocusOnHeader.activated.connect(self.FocusOnHeader)
        # Focus on table
        ExitHeaderFocus = QShortcut(QKeySequence('Ctrl+Down'), self.horizontalHeader())
        ExitHeaderFocus.setContext(Qt.WidgetShortcut)
        ExitHeaderFocus.setAutoRepeat(False)
        ExitHeaderFocus.activated.connect(self.ExitHeaderFocus)
        # Header click
        # Keyboard click
        Header = self.horizontalHeader()
        SortHeader1 = QShortcut(QKeySequence('Space'), Header)
        SortHeader1.setContext(Qt.WidgetShortcut)
        SortHeader1.setAutoRepeat(False)
        SortHeader1.activated.connect(lambda:self.OnHeaderClick(clickedColIndex=self.currentColumn()))
        SortHeader2 = QShortcut(QKeySequence('Return'), Header)
        SortHeader2.setContext(Qt.WidgetShortcut)
        SortHeader2.setAutoRepeat(False)
        SortHeader2.activated.connect(lambda:self.OnHeaderClick(clickedColIndex=self.currentColumn()))
        # Mouse click
        self.horizontalHeader().sectionClicked.connect(self.OnHeaderClick)

    def FocusOnHeader(self):
        HeaderSection = self.horizontalHeader()
        HeaderSection.setFocus()

    def ExitHeaderFocus(self):
        self.setFocus()

    def OnHeaderClick(self, clickedColIndex):
        if Window.sortColIndex == clickedColIndex:
            return
        # Update sort column
        Window.sortColIndex = clickedColIndex
        # Check if needed to update results
        itemCount = len(self.GetAllItems())
        if itemCount <= 1:
            return
        # The other sort options apply to all columns by default 
        if Window.selSortOptionIndex == SORT_ALPH:
            Window.SortResults()

    def GetRowItem(self, rowIndex):
        RowItem = []
        for colIndex in range(3):
            value = self.item(rowIndex, colIndex).text()
            RowItem.append(value)
        return RowItem
    
    def GetAllItems(self):
        Items = []
        for rowIndex in range(self.rowCount()):
            RowItem = self.GetRowItem(rowIndex) 
            Items.append(RowItem)
        return Items

    def SetRowItem(self, values):
        self.setRowCount(self.rowCount() + 1)
        colIndex = 0
        for value in values:
            item = QTableWidgetItem(value)
            self.setItem(self.rowCount()-1, colIndex, item)
            colIndex += 1

    def ClearAllItems(self):
        rowCount = self.rowCount()
        while rowCount >= 0:
            self.removeRow(rowCount)
            rowCount -= 1

class MainWindow(QWidget):
    EditInput = None
    # Set first column as default sort column 
    sortColIndex = 0
    # By default sort by time account added
    selSortOptionIndex = 0

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
        # Display order dropdown menu
        self.SortResultsLbl = QLabel(parent=self, text='Sort results')
        self.SortResultsLbl.setProperty('class', 'sort-results-label')
        self.SortResultsDropMenu = QComboBox(parent=self)
        self.SortResultsDropMenu.setProperty('class', 'sort-results-dropdown')
        self.SortResultsDropMenu.addItems(['Time added', 'Alphabetically', 'Number of filled fields'])
        self.SortResultsDropMenu.currentIndexChanged.connect(self.OnSortDropdownOptionChange)
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
        self.Table.verticalHeader().setProperty('class', 'table-number-row')
        Accs = xmlHandler.GetAccs()
        for acc in Accs:
            self.Table.SetRowItem(acc)
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
        self.setStyleSheet("""
            *
            {
                font-size: 10pt;
            }

            QTableWidget
            {
                font-size: 9pt;
            }

            .table-number-row
            {
                font-size: 8pt;
            }

            QPushButton 
            {
                border: 1px solid #333;
            }
        """)
        FixedSizePolicy = QSizePolicy()
        FixedSizePolicy.setHorizontalPolicy(QSizePolicy.Fixed)
        FixedSizePolicy.setVerticalPolicy(QSizePolicy.Fixed)
        ExpandingSizePolicy = QSizePolicy()
        ExpandingSizePolicy.setHorizontalPolicy(QSizePolicy.Expanding)
        ExpandingSizePolicy.setVerticalPolicy(QSizePolicy.Expanding)
        # Widgets
        # Search input
        self.SearchInput.setProperty('class', 'search-input')
        self.SearchInput.setFixedHeight(30)
        # Search match case checkbox
        self.SearchMatchCaseCheckbox.setSizePolicy(FixedSizePolicy)
        # Sort results widgets
        self.SortResultsLbl.setSizePolicy(FixedSizePolicy)
        self.SortResultsDropMenu.setSizePolicy(FixedSizePolicy)
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
        self.Table.setSizePolicy(ExpandingSizePolicy)
        TableNumberRow = self.Table.verticalHeader()
        tableNumRowWidth = TableNumberRow.width()
        # Increase number row width to fit content at all times
        TableNumberRow.setFixedWidth(tableNumRowWidth+10)
        # Layout
        # Search child layout
        SortLayout = QHBoxLayout()
        SortLayout.setAlignment(Qt.AlignLeft)
        SortLayout.setContentsMargins(12, 0, 0, 0)
        SortLayout.addWidget(self.SortResultsLbl)
        SortLayout.addWidget(self.SortResultsDropMenu)
        SearchLayout = QHBoxLayout()
        SearchLayout.setAlignment(Qt.AlignLeft)
        SearchLayout.addWidget(self.SearchInput)
        SearchLayout.addWidget(self.SearchMatchCaseCheckbox)
        SearchLayout.addLayout(SortLayout)
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

    def SortResults(self, results=None):
        # Get current items as the results
        if results == None:
            results = self.Table.GetAllItems()
        self.Table.ClearAllItems()
        # Handle no or 1 results
        if len(results) <= 1:
            if len(results) == 1:
                self.Table.SetRowItem(results[0])
            return
        optionIndex = self.selSortOptionIndex
        # Time added
        if optionIndex == 0:
            self.SortByTimeAdded(results, order=None)
        # Alphabetically 
        elif optionIndex == 1:
            # Ascending / descending
            # order = SortOrderBtn.value
            self.SortAlphabetically(results, order=None)
        # By number of filled fields
        elif optionIndex == 2:
            self.SortByNumberOfFilledFields(results, order=None)

    def OnSortDropdownOptionChange(self, optionIndex):
        # Update sort option
        self.selSortOptionIndex = optionIndex
        # Check if needed to update results
        itemCount = len(self.Table.GetAllItems())
        if itemCount <= 1:
            return
        # Apply sort
        self.SortResults()

    def GetTimeAddedItemIndexOf(self, Accs, item):
        index = Accs.index(item)
        return index

    def SortByTimeAdded(self, results, order):
        Items = results
        itemCount = len(Items)
        AccsSortedByTimeAdded = xmlHandler.GetAccs()
        # Sort
        i = 0
        while i < itemCount-1:
            topItem = Items[i]
            topItemIndex = self.GetTimeAddedItemIndexOf(AccsSortedByTimeAdded, topItem)
            topIndex = i
            j = i+1
            while j < itemCount:
                itemIndex = self.GetTimeAddedItemIndexOf(AccsSortedByTimeAdded, Items[j])
                if itemIndex < topItemIndex:
                    topItem = Items[j]
                    topIndex = j
                    topItemIndex = itemIndex
                j += 1
            # Transport
            if topIndex > i:
                tmpItem = Items[i]
                Items[topIndex] = tmpItem
                Items[i] = topItem
            # Display
            Item = Items[i]
            self.Table.SetRowItem(Item)
            i += 1
        # Set last item
        self.Table.SetRowItem(Items[-1])

    def Compare(self, a, b):
        # Ascending comparison
        aLen = len(a)
        bLen = len(b)
        chCount = min(aLen, bLen)
        # Decide by character ascii value
        for i in range(chCount):
            if a[i] == b[i]:
                continue
            if a[i] > b[i]: 
                return 1
            else:
                return 2
        # If the same characters in minimum count, compare by char length
        # Same
        if aLen == bLen:
            return 0
        if aLen > bLen:
            return 1
        return 2

    def SortAlphabetically(self, results, order):
        Items = results
        itemCount = len(Items)
        # Get sort column items
        ColItems = []
        for Item in Items:
            for colIndex in range(len(Item)):
                if colIndex != self.sortColIndex:
                    continue
                value = Item[colIndex]
                ColItems.append(value)
                break
        # Sort
        i = 0
        while i < itemCount-1:
            top = ColItems[i]
            topIndex = i
            j = i+1
            while j < itemCount:
                value = ColItems[j]
                res = self.Compare(top, value)
                if res == 1:
                    top = value
                    topIndex = j
                j += 1
            # Transport
            if topIndex > i:
                # Col item transport
                tmp = ColItems[i]
                ColItems[topIndex] = tmp
                ColItems[i] = top
                # Item transport
                tmpItem = Items[i]
                topItem = Items[topIndex]
                Items[topIndex] = tmpItem
                Items[i] = topItem
            # Display
            Item = Items[i]
            self.Table.SetRowItem(Item)
            i += 1
        # Set last item
        self.Table.SetRowItem(Items[-1])

    def GetCountOfFilledFields(self, Item):
        filledCount = 0
        for value in Item:
            if value == '-':
                continue
            filledCount += 1
        return filledCount

    def SortByNumberOfFilledFields(self, results, order):
        Items = results
        itemCount = len(Items)
        # Sort
        i = 0
        while i < itemCount-1:
            min = self.GetCountOfFilledFields(Items[i])
            minIndex = i
            j = i+1
            while j < itemCount:
                count = self.GetCountOfFilledFields(Items[j])
                if min > count:
                    min = count
                    minIndex = j
                j += 1
            # Transport
            if minIndex > i:
                tmpItem = Items[i]
                minItem = Items[minIndex]
                Items[minIndex] = tmpItem
                Items[i] = minItem
            # Display
            Item = Items[i]
            self.Table.SetRowItem(Item)
            i += 1
        # Set last item
        self.Table.SetRowItem(Items[-1])

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
        self.Table.ClearAllItems()
        searchQuery = self.SearchInput.text()
        matchCase = self.SearchMatchCaseCheckbox.isChecked()
        if not matchCase:
            searchQuery = searchQuery.lower()
        # Get search results
        Accs = xmlHandler.GetAccs()
        SearchResults = []
        for accTuple in Accs:
            for j in range(len(accTuple)):
                value = accTuple[j]
                if not matchCase:
                    value = value.lower()
                if value.__contains__(searchQuery):
                    SearchResults.append(accTuple)
                    break
        # Display search results
        # Default sorting
        if self.selSortOptionIndex == 0:
            for result in SearchResults:
                self.Table.SetRowItem(result)
        else:
            self.SortResults(results=SearchResults)
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
