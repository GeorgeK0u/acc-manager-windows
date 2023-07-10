from PySide2.QtCore import Qt
from PySide2.QtWidgets import QMainWindow, QWidget, QMessageBox, QShortcut, QVBoxLayout, QHBoxLayout, QLineEdit, QTableWidget, QTableWidgetItem, QMenu as QRightClickMenu
from PySide2.QtGui import QKeySequence
# My files
import xmlHandler
import addAcc

window = None

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

class Wnd(QMainWindow):
    editInput = None

    def FocusOnTableAfterEdit(self):
        self.editInput.deleteLater()
        self.table.setFocus()

    def UpdateFieldValue(self):
        nValue = self.editInput.text()
        # If name or username/email trim white spaces
        if self.selCol < 3: 
            nValue = nValue.strip()
        # Update value
        if self.curValue != nValue:
            selRecordAccName = self.table.item(self.selRow, 0).text()
            xmlHandler.ChangeAccValue(selRecordAccName, self.selCol, nValue)
            # Update table value
            selItem = self.table.item(self.selRow, self.selCol)
            selItem.setText(nValue)
        self.FocusOnTableAfterEdit()

    def EditField(self):
        # Edit input
        self.editInput = QLineEdit(self.centralWidget)
        self.editInput.setPlaceholderText('New value')
        self.editInput.setStyleSheet('font-size: 11pt;')
        self.editInput.setMinimumWidth(150)
        self.editInput.setMaximumWidth(250)
        self.editInput.setFixedHeight(30)
        self.editInput.setFocus()
        # Get cur value
        selItem = self.table.selectedIndexes()[0]
        self.selRow = selItem.row()
        self.selCol = selItem.column()
        self.curValue = self.table.item(self.selRow, self.selCol).text()
        self.editInput.setText(self.curValue)
        # Edit input shortcuts
        self.editInput.returnPressed.connect(self.UpdateFieldValue)
        DeleteEditInput = QShortcut(QKeySequence('Esc'), self.editInput)
        DeleteEditInput.setAutoRepeat(False)
        DeleteEditInput.activated.connect(self.FocusOnTableAfterEdit)
        PreventTabChange = QShortcut(QKeySequence('Tab'), self.editInput)
        PreventTabChange.setAutoRepeat(False)
        PreventTabChange.activated.connect(None)
        PreventShiftTabChange = QShortcut(QKeySequence('Shift+Tab'), self.editInput)
        PreventShiftTabChange.setAutoRepeat(False)
        PreventShiftTabChange.activated.connect(None)
        self.centralWidgetLayout.addWidget(self.editInput)
    
    def DeleteAcc(self):
        selItem = self.table.selectedIndexes()[0]
        self.selRow = selItem.row()
        selRecordAccName = self.table.item(self.selRow, 0).text()
        xmlHandler.DeleteAcc(selRecordAccName)
        # Update table
        self.table.removeRow(self.selRow)

    def ShowRightClickTableMenu(self, pos):
        # Check if only one item is selected
        menu = QRightClickMenu()
        editAction = menu.addAction('Edit field')
        delAction = menu.addAction('Delete account')
        clickedAction = menu.exec_(self.table.viewport().mapToGlobal(pos))
        if clickedAction == editAction:
            self.EditField()
        elif clickedAction == delAction:
            self.DeleteAcc()

    def UpdateSearchResults(self):
        self.table.clearItems()
        searchQuery = self.searchInput.text().strip().lower()
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
            self.table.setRowItem(tuple(result))
        # Select and focus on the first table item
        if len(SearchResults) > 0:
            # Focus on table
            self.table.setFocus()
            firstItem = self.table.item(0, 0)
            # Focus on item
            self.table.setCurrentItem(firstItem)
            # Select item
            self.table.setItemSelected(firstItem, True)
        else:
            self.searchInput.setFocus()

    def FocusOnSearchInput(self):
        if self.searchInput.hasFocus() or self.editInput != None:
            return
        self.searchInput.setFocus()
        self.searchInput.selectAll()

    def __init__(self):
        super().__init__(parent=None)
        # Window properties 
        self.setWindowTitle('Manage Accounts')
        self.setMinimumSize(800, 600)
        self.showMaximized()
        self.setStyleSheet("""

        """)
        # Widgets
        # Central
        self.centralWidget = QWidget(self)
        # Search input
        self.searchInput = QLineEdit(self.centralWidget)
        self.searchInput.setPlaceholderText('Search')
        self.searchInput.setStyleSheet('font-size: 11pt;')
        self.searchInput.setMinimumWidth(150)
        self.searchInput.setMaximumWidth(250)
        self.searchInput.setFixedHeight(30)
        self.searchInput.returnPressed.connect(self.UpdateSearchResults)
        # Search shortcuts
        FocusOnSearchInput1 = QShortcut(QKeySequence('/'), self.centralWidget)
        FocusOnSearchInput1.setAutoRepeat(False)
        FocusOnSearchInput1.activated.connect(self.FocusOnSearchInput)
        FocusOnSearchInput2 = QShortcut(QKeySequence('Alt+D'), self.centralWidget)
        FocusOnSearchInput2.setAutoRepeat(False)
        FocusOnSearchInput2.activated.connect(self.FocusOnSearchInput)
        FocusOnSearchInput3 = QShortcut(QKeySequence('Ctrl+L'), self.centralWidget)
        FocusOnSearchInput3.setAutoRepeat(False)
        FocusOnSearchInput3.activated.connect(self.FocusOnSearchInput)
        # Table
        self.table = MyTable(parent=self.centralWidget)
        self.table.setColumnCount(3)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        scrollbarOffset = 20
        self.table.setHorizontalHeaderLabels(['Account Name', 'Username / Email', 'Password'])
        Accs = xmlHandler.GetAccs() 
        for acc in Accs:
            self.table.setRowItem(acc)
        self.table.setColumnWidth(0, 350)
        self.table.setColumnWidth(1, 350)
        self.table.setColumnWidth(2, 350)
        columnWidthSum = 350 * 3
        # An extra offset to remove the scrollbar
        lastColOffset = 40
        self.table.setMaximumWidth(columnWidthSum+lastColOffset+scrollbarOffset)
        self.table.setFixedHeight(850)
        # Specify focus
        self.UpdateSearchResults()
        # Table shortcuts
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.ShowRightClickTableMenu)
        # Place widgets
        self.centralWidgetLayout = QVBoxLayout()
        self.centralWidgetLayout.setAlignment(Qt.AlignTop)
        self.centralWidgetLayout.addWidget(self.searchInput)
        self.centralWidgetLayout.addWidget(self.table)
        self.centralWidget.setLayout(self.centralWidgetLayout)
        self.setCentralWidget(self.centralWidget)
        # Shortcuts
        CloseMainWindow = QShortcut(QKeySequence('Ctrl+W'), self)
        CloseMainWindow.setAutoRepeat(False)
        CloseMainWindow.activated.connect(self.close)

    def closeEvent(self, e):
        super().closeEvent(e)
        global window
        window = None

def ShowAccManagerWindow():
    global window
    if addAcc.window != None or window != None:
        return
    window = Wnd()
    window.show()
