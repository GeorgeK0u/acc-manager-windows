import ctypes
import pyperclip
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QWidget, QMessageBox, QShortcut, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QCheckBox, QTableWidget, QHeaderView, QTableWidgetItem, QMenu as QRightClickMenu, QSizePolicy, QComboBox, QDialog, QStyle
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
allPwdsVisibilityBool = None
SORT_TIME_ADDED = 0
SORT_ALPH = 1
SORT_NUM_OF_FILLED_FIELDS = 2
ASC_ORDER = 0
DESC_ORDER = 1
ASC_TEXT = '/\\\n|'
DESC_TEXT = '|\n\\/'
SHOW_PWDS_TEXT = 'Show passwords'
HIDE_PWDS_TEXT = 'Hide passwords'

class MyTable(QTableWidget):
    lastSelValue = None
    lastSelCol = None

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
            Window.StoreCurTableSelection()
            # Update sort
            Window.SortResults()
            # Focus on selected item before sort
            Window.FocusOnLastTableSelection()

    def GetRowItem(self, rowIndex):
        RowItem = []
        for colIndex in range(3):
            value = self.item(rowIndex, colIndex).text()
            RowItem.append(value)
        return RowItem
    
    def GetAllItems(self):
        # get copy instead of retrieving the table items
        # due to working with password mask and trying to access indexes, values etc. 
        return Window.AccsCopy

    def SetRowItem(self, values):
        self.setRowCount(self.rowCount() + 1)
        colIndex = 0
        for value in values:
            # Default visibility for all pwds setting
            if colIndex == 2 and not GetAllPwdsVisibilityBool():
                value = encoder.MaskPassword(value)
            item = QTableWidgetItem(value)
            # Prevent direct item editing
            item.setFlags(Qt.ItemIsSelectable | ~Qt.ItemIsEditable)
            self.setItem(self.rowCount()-1, colIndex, item)
            colIndex += 1

    def ClearAllItems(self):
        rowCount = self.rowCount()
        while rowCount >= 0:
            self.removeRow(rowCount)
            rowCount -= 1

class InformationDialog(QDialog):
    def __init__(self, parent, size, title, text, details):
        super().__init__(parent=parent)
        self.size = size
        self.title = title
        self.text = text
        self.details = details
        self.InitUI()

    def InitUI(self):
        # Window properties
        width = self.size[0]
        height = self.size[1]
        self.setFixedSize(width, height)
        self.setWindowTitle(self.title)
        # Icon
        WarningIcon = self.style().standardIcon(QStyle.SP_MessageBoxInformation)
        self.setWindowIcon(WarningIcon)
        # Widgets
        # Text
        Text = QLabel(parent=self, text=self.text)
        Details = QLabel(parent=self, text=self.details)
        # Action buttons 
        self.YesBtn = QPushButton(parent=self, text='Yes')
        self.YesBtn.setDefault(True)
        self.YesBtn.clicked.connect(lambda:self.OnDialogBtnClick(clickedBtn=self.YesBtn))
        self.NoBtn = QPushButton(parent=self, text='No')
        self.NoBtn.setDefault(True)
        self.NoBtn.clicked.connect(lambda:self.OnDialogBtnClick(clickedBtn=self.NoBtn))
        # Button layout
        BtnLayout = QHBoxLayout()
        BtnLayout.addWidget(self.YesBtn)
        BtnLayout.addWidget(self.NoBtn)
        # Dialog layout
        DialogLayout = QVBoxLayout() 
        DialogLayout.addWidget(Text)
        DialogLayout.addWidget(Details)
        DialogLayout.addLayout(BtnLayout)
        self.setLayout(DialogLayout)
        # Shortcuts
        CloseDialog = QShortcut(QKeySequence('Esc'), self)
        CloseDialog.setContext(Qt.WidgetShortcut)
        CloseDialog.setAutoRepeat(False)
        CloseDialog.activated.connect(self.reject)
        # Show dialog
        self.show()

    def OnDialogBtnClick(self, clickedBtn):
        if clickedBtn == self.YesBtn:
            self.accept()
        else:
            self.reject()

class MainWindow(QWidget):
    EditInput = None
    AccsCopy = None
    # Keep a count of manually switched password visibility fields
    # to check update global password visibility btn operation
    manualPwdVisCount = 0
    # Set first column as default sort column 
    sortColIndex = 0
    # By default sort by time account added
    selSortOptionIndex = 0
    # By default ascending
    sortOrder = ASC_ORDER

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
        # Display sort dropdown menu
        self.SortResultsLbl = QLabel(parent=self, text='Sort results')
        self.SortResultsLbl.setProperty('class', 'sort-results-label')
        self.SortResultsDropMenu = QComboBox(parent=self)
        self.SortResultsDropMenu.setProperty('class', 'sort-results-dropdown')
        self.SortResultsDropMenu.addItems(['Time added', 'Alphabetically', 'Number of filled fields'])
        self.SortResultsDropMenu.currentIndexChanged.connect(self.OnSortDropdownOptionChange)
        # Sort order button 
        self.SortOrderBtn = QPushButton(parent=self, text=ASC_TEXT)
        self.SortOrderBtn.setProperty('class', 'sort-order-btn')
        # Trigger enter key press as click 
        self.SortOrderBtn.setDefault(True)
        self.SortOrderBtn.clicked.connect(self.OnSortOrderBtnClick)
        # Add btn
        self.AddAccBtn = QPushButton(parent=self, text='Add Account')
        self.AddAccBtn.setProperty('class', 'add-acc-btn')
        # Trigger enter key press as click 
        self.AddAccBtn.setDefault(True)
        self.AddAccBtn.clicked.connect(addAcc.Create)
        # Manual sync btn
        self.ManualSyncBtn = QPushButton(parent=self, text='Sync')
        self.ManualSyncBtn.setProperty('class', 'manual-sync-btn')
        # Trigger enter key press as click 
        self.ManualSyncBtn.setDefault(True)
        self.ManualSyncBtn.clicked.connect(clientSocket.SendManualSyncMsg)
        # Settings btn
        self.SettingsBtn = QPushButton(parent=self, text='Settings')
        self.SettingsBtn.setProperty('class', 'settings-btn')
        # Trigger enter key press as click 
        self.SettingsBtn.setDefault(True)
        self.SettingsBtn.clicked.connect(settings.Create)
        # Pwd visibility btn
        self.AllPwdsVisibilityBtn = QPushButton(parent=self)
        self.AllPwdsVisibilityBtn.setText(HIDE_PWDS_TEXT if GetAllPwdsVisibilityBool() else SHOW_PWDS_TEXT)
        self.AllPwdsVisibilityBtn.setProperty('class', 'pwd-visibility-btn')
        # Trigger enter key press as click 
        self.AllPwdsVisibilityBtn.setDefault(True)
        self.AllPwdsVisibilityBtn.clicked.connect(self.OnAllPwdsVisibilityClick)
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
        # Init pwd copy list
        self.UpdateAccsCopyList(Accs)
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
        ShowHidePwd = QShortcut(QKeySequence('Space'), self.Table)
        ShowHidePwd.setContext(Qt.WidgetShortcut)
        ShowHidePwd.setAutoRepeat(False)
        ShowHidePwd.activated.connect(self.OnSpaceCellPressed)
        CloseWindow = QShortcut(QKeySequence('Ctrl+W'), self)
        CloseWindow.setAutoRepeat(False)
        CloseWindow.activated.connect(self.close)

    def OnSpaceCellPressed(self):
        col = self.Table.currentColumn()
        if col < 2: 
            return
        # Show/hide password
        pwdText = self.Table.currentItem().text()
        if pwdText.__contains__(encoder.PWD_MASK_CHAR):
            rowIndex = self.Table.currentRow()
            pwdText = self.GetPwdOfRow(rowIndex)
            self.CheckUpdateAllPwdsVisibilityBtn(operationBool=True)
        else:
            pwdText = encoder.MaskPassword(pwdText)
            self.CheckUpdateAllPwdsVisibilityBtn(operationBool=False)
        self.Table.currentItem().setText(pwdText)
        # Cause a re-paint to update cell value
        self.Table.horizontalHeader().setFocus()
        self.Table.setFocus()

    def UpdateAllPwdsVisibilityBtn(self):
        curValue = GetAllPwdsVisibilityBool()
        nValue = not curValue
        # Update btn text
        self.AllPwdsVisibilityBtn.setText(HIDE_PWDS_TEXT if nValue else SHOW_PWDS_TEXT)
        # Update bool
        SetAllPwdsVisibilityBool(nValue)

    def ResetManualPwdVisCount(self):
        self.manualPwdVisCount = 0

    def CheckUpdateAllPwdsVisibilityBtn(self, operationBool):
        # Important because if the table items are low and the user manually toggles the password visibility shortcut for each item, then the global one will keep its current operation, which will be doing the same on the first click 
        curGlobalOperationBool = GetAllPwdsVisibilityBool()
        if curGlobalOperationBool ^ operationBool:
            self.manualPwdVisCount += 1
            if self.manualPwdVisCount == len(self.AccsCopy):
                # Update btn text and operation
                self.UpdateAllPwdsVisibilityBtn()
                self.ResetManualPwdVisCount()
        else:
            self.manualPwdVisCount -= 1

    def OnAllPwdsVisibilityClick(self):
        self.UpdateAllPwdsVisibilityBtn()
        # Update visibility
        nValue = GetAllPwdsVisibilityBool()
        for i in range(len(self.AccsCopy)):
            item = self.Table.item(i, 2)
            pwdValue = None
            if nValue:
                pwdValue = self.GetPwdOfRow(i)
            else:
                pwdText = item.text()
                pwdValue = encoder.MaskPassword(pwdText)
            item.setText(pwdValue)
        # Cause a re-paint to update table values
        self.Table.setFocus()
        self.AllPwdsVisibilityBtn.setFocus()
        # Reset
        self.ResetManualPwdVisCount()

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

            .sort-order-btn, .settings-btn, .add-acc-btn, .manual-sync-btn
            {
                border: 1px solid #333;
            }

            .pwd-visibility-btn
            {
                border: none;
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
        # Sort order btn
        self.SortOrderBtn.setSizePolicy(FixedSizePolicy)
        self.SortOrderBtn.setFixedHeight(30)
        self.SortOrderBtn.setStyleSheet('border: none;')
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
        # Pwd visibility btn
        self.AllPwdsVisibilityBtn.setSizePolicy(FixedSizePolicy)
        self.AllPwdsVisibilityBtn.setFixedHeight(30)
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
        # Sort layout
        SortLayout = QHBoxLayout()
        SortLayout.setAlignment(Qt.AlignLeft)
        SortLayout.setContentsMargins(12, 0, 0, 0)
        SortLayout.addWidget(self.SortResultsLbl)
        SortLayout.addWidget(self.SortResultsDropMenu)
        SortLayout.addWidget(self.SortOrderBtn)
        # Search layout
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
        FeatureLayout.addStretch()
        FeatureLayout.addWidget(self.AllPwdsVisibilityBtn)
        # Parent layout
        self.WindowLayout = QVBoxLayout()
        self.WindowLayout.setAlignment(Qt.AlignTop|Qt.AlignLeft)
        self.WindowLayout.addLayout(SearchLayout)
        self.WindowLayout.addLayout(FeatureLayout)
        self.WindowLayout.addWidget(self.Table)
        self.setLayout(self.WindowLayout)

    def StoreCurTableSelection(self):
        selRow = self.Table.currentRow()
        if selRow == -1:
            self.Table.lastSelValue = None
            self.Table.lastSelCol = -1
            return
        selCol = self.Table.currentColumn()
        selValue = self.Table.item(selRow, selCol).text()
        if selCol == 2:
            # Store password without mask to re-find it after sorting
            if selValue.__contains__(encoder.PWD_MASK_CHAR):
                selValue = self.GetPwdOfRow(selRow)
        self.Table.lastSelValue = selValue
        self.Table.lastSelCol = selCol

    def FocusOnLastTableSelection(self):
        if self.Table.lastSelValue == None:
            return
        nSelRow = None
        selCol = self.Table.lastSelCol
        selValue = self.Table.lastSelValue
        Items = self.Table.GetAllItems()
        for i in range(len(Items)):
            Item = Items[i]
            if Item[selCol] != selValue:
                continue
            nSelRow = i
            break
        # Get item
        Item = self.Table.item(nSelRow, selCol)
        # Focus on item
        self.Table.setCurrentItem(Item)
        # Select item
        self.Table.setItemSelected(Item, True)

    def UpdateAccsCopyList(self, items):
        self.AccsCopy = items
        
    def GetPwdOfRow(self, rowIndex):
        pwd = self.AccsCopy[rowIndex][2]
        return pwd

    def SortResults(self, results=None):
        # Get current items as the results
        if results == None:
            results = self.Table.GetAllItems()
        self.Table.ClearAllItems()
        optionIndex = self.selSortOptionIndex
        SortedResults = None
        # Time added
        if optionIndex == 0:
            SortedResults = self.SortByTimeAdded(results)
        # Alphabetically 
        elif optionIndex == 1:
            SortedResults = self.SortAlphabetically(results)
        # By number of filled fields
        elif optionIndex == 2:
            SortedResults = self.SortByNumberOfFilledFields(results)
        # Display the items here to get the list without the password mask
        # Display sorted results 
        for Result in SortedResults:
            self.Table.SetRowItem(Result)
        # Update pwd copy list
        self.UpdateAccsCopyList(SortedResults)
        self.ResetManualPwdVisCount()

    def OnSortDropdownOptionChange(self, optionIndex):
        # Update sort option
        self.selSortOptionIndex = optionIndex
        # Check if needed to update results
        itemCount = len(self.Table.GetAllItems())
        if itemCount <= 1:
            return
        self.StoreCurTableSelection()
        # Apply sort
        self.SortResults()
        # Focus on selected item before sort
        self.FocusOnLastTableSelection()

    def GetTimeAddedItemIndexOf(self, Accs, item):
        index = Accs.index(item)
        return index

    def SortByTimeAdded(self, results):
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
                if (self.sortOrder == ASC_ORDER and itemIndex < topItemIndex) or (self.sortOrder == DESC_ORDER and itemIndex > topItemIndex):
                    topItem = Items[j]
                    topIndex = j
                    topItemIndex = itemIndex
                j += 1
            # Transport
            if topIndex > i:
                tmpItem = Items[i]
                Items[topIndex] = tmpItem
                Items[i] = topItem
            i += 1
        return Items

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

    def SortAlphabetically(self, results):
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
                if (self.sortOrder == ASC_ORDER and res == 1) or (self.sortOrder == DESC_ORDER and res == 2):
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
            i += 1
        return Items 

    def GetCountOfFilledFields(self, Item):
        filledCount = 0
        for value in Item:
            if value == '-':
                continue
            filledCount += 1
        return filledCount

    def SortByNumberOfFilledFields(self, results):
        Items = results
        itemCount = len(Items)
        # Sort
        i = 0
        while i < itemCount-1:
            top = self.GetCountOfFilledFields(Items[i])
            topIndex = i
            j = i+1
            while j < itemCount:
                count = self.GetCountOfFilledFields(Items[j])
                if (self.sortOrder == ASC_ORDER and count < top) or (self.sortOrder == DESC_ORDER and count > top):
                    top = count
                    topIndex = j
                j += 1
            # Transport
            if topIndex > i:
                tmpItem = Items[i]
                topItem = Items[topIndex]
                Items[topIndex] = tmpItem
                Items[i] = topItem
            i += 1
        return Items

    def OnSortOrderBtnClick(self):
        self.sortOrder = DESC_ORDER if self.sortOrder == ASC_ORDER else ASC_ORDER
        self.SortOrderBtn.setText(DESC_TEXT if self.sortOrder == DESC_ORDER else ASC_TEXT)
        # Check if needed to update results
        itemCount = len(self.Table.GetAllItems())
        if itemCount <= 1:
            return
        self.StoreCurTableSelection()
        # Update sort
        self.SortResults()
        # Focus on selected item before sort
        self.FocusOnLastTableSelection()

    def CopySelectedValue(self):
        selItem = self.Table.selectedItems()[0]
        value = selItem.text()
        if value.__contains__(encoder.PWD_MASK_CHAR):
            # Get password
            rowIndex = self.Table.currentRow()
            value = self.GetPwdOfRow(rowIndex)
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
        if self.selSortOptionIndex == 0 or len(SearchResults) <= 1:
            for result in SearchResults:
                self.Table.SetRowItem(result)
            # Update pwd copy list
            self.UpdateAccsCopyList(SearchResults)
            if len(SearchResults) > 1:
                self.ResetManualPwdVisCount()
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
        DeleteEditInput.setContext(Qt.WidgetShortcut)
        DeleteEditInput.setAutoRepeat(False)
        DeleteEditInput.activated.connect(self.FocusOnTableAfterEdit)
        PreventTabChange = QShortcut(QKeySequence('Tab'), self.EditInput)
        PreventTabChange.setContext(Qt.WidgetShortcut)
        PreventTabChange.setAutoRepeat(False)
        PreventTabChange.activated.connect(None)
        PreventShiftTabChange = QShortcut(QKeySequence('Shift+Tab'), self.EditInput)
        PreventShiftTabChange.setContext(Qt.WidgetShortcut)
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
            # Already exists
            AccNames = xmlHandler.GetAccNames()
            if AccNames.__contains__(nValue):
                QMessageBox.critical(self, 'Not Changed', 'This account name already exists')
                self.FocusOnTableAfterEdit()
                return
        elif self.selCol == 2:
            # Warn user if password already exists
            Pwds = xmlHandler.GetAccPwds()
            if Pwds.__contains__(nValue):
                WarningDialog = InformationDialog(parent=self, size=(420, 150), title='Warning', text='This password already exists', details="Using the same password for multiple accounts isn't recommended.\nContinue ?")
                action = WarningDialog.exec_()
                # User selected no
                if action == 0:
                    return
        # Sync
        operator = 'U'
        selAccName = self.Table.item(self.selRow, 0).text()
        encSelAccName = encoder.Encrypt(selAccName)
        encSelCol = encoder.Encrypt(str(self.selCol))
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
        
def Init():
    global allPwdsVisibilityBool
    allPwdsVisibilityBool = xmlHandler.GetPwdVisibilityOptionIndex()

def GetAllPwdsVisibilityBool():
    return allPwdsVisibilityBool

def SetAllPwdsVisibilityBool(value):
    global allPwdsVisibilityBool
    allPwdsVisibilityBool = value

def Create():
    global Window
    Window = MainWindow()
    Window.show()
    Window.setFocus()
    return Window
