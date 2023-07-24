import ctypes
from PySide2.QtCore import QSize 
from PySide2.QtWidgets import QMainWindow, QWidget, QShortcut, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QMessageBox
from PySide2.QtGui import QKeySequence, QIcon
import random
# My files
import xmlHandler
import mng

window = None

def Init():
    global Characters
    

class Wnd(QMainWindow):
    pwdToggleText = 'o'

    def GeneratePass(self):
        GenCharacters = [[48, 57], [65, 90], [97, 122], ['-', '_', '.', ',', '/', ';']]
        minPwdLen = 15
        maxPwdLen = 28
        pwdLen = random.randint(minPwdLen, maxPwdLen)
        pwd = ''
        for i in range(pwdLen):
            charArrIndex = random.randrange(0, len(GenCharacters))
            CharArr = GenCharacters[charArrIndex]
            char = chr(random.randint(CharArr[0], CharArr[1])) if (len(CharArr) == 2) else CharArr[random.randint(0, len(CharArr) - 1)]
            pwd += char
        # Check if password already exists 
        Pwds = xmlHandler.GetAccPwds() 
        for p in Pwds:
            if p != pwd:
                continue
            # Re-generate pwd
            self.GeneratePass()
            return
        self.passInput.setText(pwd) 

    def AddAccount(self):
        # Trim and update empty value text
        accName = self.accNameInput.text().strip()
        if accName == '':  
            self.accNameInput.setText('-')
        else:
            self.accNameInput.setText(accName)
        # Trim and update empty value text
        extraInfo = self.extraInfoInput.text().strip()
        if self.extraInfoInput.text() == '':  
            self.extraInfoInput.setText('-')
        else:
            self.extraInfoInput.setText(extraInfo)
        # Update empty value text
        pwd = self.passInput.text()
        if pwd == '':  
            self.passInput.setText('-')
        # Update vars
        accName = self.accNameInput.text()
        extraInfo = self.extraInfoInput.text()
        pwd = self.passInput.text()
        # Check field texts
        if accName == '-' and extraInfo == '-' and pwd == '-':
            QMessageBox.information(self, 'Error', 'You need to fill at least one field')
            return
        # Encrypt & save acc
        xmlHandler.SaveAcc(accName, extraInfo, pwd)
        # Clear fields
        self.accNameInput.setText('')
        self.extraInfoInput.setText('')
        self.passInput.setText('')

    def TogglePwdVisibility(self):
        self.passInput.setEchoMode(QLineEdit.Normal) if self.passInput.echoMode() == QLineEdit.Password else self.passInput.setEchoMode(QLineEdit.Password)
        if self.passInput.echoMode() == QLineEdit.Password:
            self.pwdToggleText = 'o'
        else:
            self.pwdToggleText = '-'
        self.pwdToggleBtn.setText(self.pwdToggleText) 

    def __init__(self, mainWindow):
        super().__init__(parent=None)
        # Window properties 
        self.setWindowTitle('New Account')
        # Tell windows to use the window icon as the taskbar icon
        myappid = u'mycompany.myproduct.subproduct.version'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        # Change window icon
        iconSize = QSize(32, 32) 
        self.setIconSize(iconSize)
        mainWndIcon = QIcon('./Resources/app-icon32.png')
        self.setWindowIcon(mainWndIcon)
        self.setGeometry(50, 50, 400, 600)
        self.setStyleSheet("""

        """)
        # Widgets
        # Central
        self.centralWidget = QWidget(self)
        # Acc name
        self.accNameInput = QLineEdit(parent=self.centralWidget)
        self.accNameInput.setPlaceholderText('Account name')
        self.accNameInput.setStyleSheet('font-size: 11pt;')
        self.accNameInput.setMinimumWidth(250)
        self.accNameInput.setMaximumWidth(350)
        self.accNameInput.setFixedHeight(30)
        # Username/Email
        self.extraInfoInput = QLineEdit(parent=self.centralWidget)
        self.extraInfoInput.setPlaceholderText('Username or email')
        self.extraInfoInput.setStyleSheet('font-size: 11pt;')
        self.extraInfoInput.setMinimumWidth(250)
        self.extraInfoInput.setMaximumWidth(350)
        self.extraInfoInput.setFixedHeight(30)
        # Password
        self.passInput = QLineEdit(parent=self.centralWidget)
        self.passInput.setStyleSheet('font-size: 11pt;')
        self.passInput.setPlaceholderText('Password')
        self.passInput.setEchoMode(QLineEdit.Password)
        self.passInput.setMinimumWidth(250)
        self.passInput.setMaximumWidth(350)
        self.passInput.setFixedHeight(30)
        # Password toggle vis btn
        self.pwdToggleBtn = QPushButton(parent=self.passInput, text=self.pwdToggleText)
        self.pwdToggleBtn.setStyleSheet('border: none;')
        self.pwdToggleBtn.setDefault(True)
        self.pwdToggleBtn.clicked.connect(self.TogglePwdVisibility)
        childWidgetLayout = QHBoxLayout()
        childWidgetLayout.addStretch()
        childWidgetLayout.addWidget(self.pwdToggleBtn)
        self.passInput.setLayout(childWidgetLayout)
        # Generate btn
        self.genBtn = QPushButton(parent=self.centralWidget, text='Generate')
        self.genBtn.setStyleSheet('font-size: 11pt; border: 1px solid #353535;')
        self.genBtn.setDefault(True)
        self.genBtn.setMinimumWidth(100)
        self.genBtn.setMaximumWidth(250)
        self.genBtn.setFixedHeight(30)
        self.genBtn.clicked.connect(self.GeneratePass)
        # Add btn
        self.addBtn = QPushButton(parent=self.centralWidget, text='Add Account')
        self.addBtn.setStyleSheet('font-size: 11pt; border: 1px solid #353535;')
        self.addBtn.setDefault(True)
        self.addBtn.setMinimumWidth(100)
        self.addBtn.setMaximumWidth(250)
        self.addBtn.setFixedHeight(30)
        self.addBtn.clicked.connect(self.AddAccount)
        # Place widgets
        self.centralWidgetLayout = QVBoxLayout()
        self.centralWidgetLayout.addWidget(self.accNameInput)
        self.centralWidgetLayout.addWidget(self.extraInfoInput)
        self.subHLayout = QHBoxLayout()
        self.subHLayout.addWidget(self.passInput)
        self.subHLayout.addWidget(self.genBtn)
        self.centralWidgetLayout.addLayout(self.subHLayout)
        self.centralWidgetLayout.addWidget(self.addBtn)
        self.centralWidget.setLayout(self.centralWidgetLayout)
        self.setCentralWidget(self.centralWidget)
        # Shortcuts
        CloseMainWindow = QShortcut(QKeySequence('Ctrl+W'), self)
        CloseMainWindow.setAutoRepeat(False)
        CloseMainWindow.activated.connect(self.close)
        CloseApp = QShortcut(QKeySequence('Ctrl+Shift+W'), self)
        CloseApp.setAutoRepeat(False)
        CloseApp.activated.connect(mainWindow.close)

    def closeEvent(self, e):
        super().closeEvent(e)
        global window
        window = None

def ShowAddAccountWindow(mainWindow):
    global window
    if mng.window != None or window != None:
        return
    window = Wnd(mainWindow)
    window.show()
