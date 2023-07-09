from PySide2.QtCore import Qt
from PySide2.QtWidgets import QMainWindow, QWidget, QShortcut, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QCheckBox
from PySide2.QtGui import QKeySequence

window = None

class Wnd(QMainWindow):
    def GeneratePass(self):
        pass

    def AddAccount(self):
        pass

    def __init__(self):
        super().__init__(parent=None)
        # Window properties 
        self.setWindowTitle('New Account')
        self.setGeometry(50, 50, 400, 600)
        self.setStyleSheet("""

        """)
        # Widgets
        # Central
        centralWidget = QWidget(self)
        # Acc name
        accNameInput = QLineEdit(parent=centralWidget)
        accNameInput.setPlaceholderText('Account name')
        accNameInput.setStyleSheet('font-size: 11pt;')
        accNameInput.setMinimumWidth(250)
        accNameInput.setMaximumWidth(350)
        accNameInput.setFixedHeight(30)
        # Username/Email
        extraInfoInput = QLineEdit(parent=centralWidget)
        extraInfoInput.setPlaceholderText('Username or email')
        extraInfoInput.setStyleSheet('font-size: 11pt;')
        extraInfoInput.setMinimumWidth(250)
        extraInfoInput.setMaximumWidth(350)
        extraInfoInput.setFixedHeight(30)
        # Password
        passInput = QLineEdit(parent=centralWidget)
        passInput.setPlaceholderText('Password')
        passInput.setStyleSheet('font-size: 11pt;')
        passInput.setMinimumWidth(250)
        passInput.setMaximumWidth(350)
        passInput.setFixedHeight(30)
        # Generate btn
        genBtn = QPushButton(parent=centralWidget, text='Generate')
        genBtn.setStyleSheet('font-size: 11pt; border: 1px solid #353535;')
        genBtn.setDefault(True)
        genBtn.setMinimumWidth(100)
        genBtn.setMaximumWidth(250)
        genBtn.setFixedHeight(30)
        genBtn.clicked.connect(self.GeneratePass)
        # Add btn
        addBtn = QPushButton(parent=centralWidget, text='Add Account')
        addBtn.setStyleSheet('font-size: 11pt; border: 1px solid #353535;')
        addBtn.setDefault(True)
        addBtn.setMinimumWidth(100)
        addBtn.setMaximumWidth(250)
        addBtn.setFixedHeight(30)
        addBtn.clicked.connect(self.AddAccount)
        # Place widgets
        centralWidgetLayout = QVBoxLayout()
        centralWidgetLayout.addWidget(accNameInput)
        centralWidgetLayout.addWidget(extraInfoInput)
        subHLayout = QHBoxLayout()
        subHLayout.addWidget(passInput)
        subHLayout.addWidget(genBtn)
        centralWidgetLayout.addLayout(subHLayout)
        centralWidgetLayout.addWidget(addBtn)
        centralWidget.setLayout(centralWidgetLayout)
        self.setCentralWidget(centralWidget)
        # Shortcuts
        CloseMainWindow = QShortcut(QKeySequence('Ctrl+W'), self)
        CloseMainWindow.setAutoRepeat(False)
        CloseMainWindow.activated.connect(self.close)

    def closeEvent(self, e):
        super().closeEvent(e)
        global window
        window = None

def ShowAddAccountWindow():
    global window
    if window != None:
        return
    window = Wnd()
    window.show()
