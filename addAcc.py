import ctypes
import random
from PySide2.QtCore import Signal
from PySide2.QtWidgets import QWidget, QShortcut, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QGroupBox, QSizePolicy
from PySide2.QtGui import QKeySequence, QIcon
# My files
import xmlHandler
import encoder
import clientSocket
import viewHandler

Window = None 
Characters = None

class OptionMenu(QWidget):
    clicked = Signal()
    def __init__(self, parent, text):
        super().__init__(parent=parent)
        # Create custom widget
        self.setStyleSheet("""
            .arrow-btn
            {
                border: none;
            }
        """)
        GenLbl = QLabel(parent=self, text=text)
        self.ArrowBtn = QPushButton(parent=self, text='>') 
        self.ArrowBtn.setProperty('class', 'arrow-btn')
        self.ArrowBtn.setMinimumWidth(30)
        self.ArrowBtn.setMaximumWidth(30)
        self.ArrowBtn.setDefault(True)
        self.ArrowBtn.clicked.connect(self.OnArrowClick)
        # Layout
        WidgetLayout = QHBoxLayout()
        WidgetLayout.addWidget(GenLbl)
        WidgetLayout.addWidget(self.ArrowBtn)
        self.setLayout(WidgetLayout)
        self.isMenuVisible = False

    def OnArrowClick(self):
        self.UpdateArrowText() 
        self.clicked.emit()

    def UpdateArrowText(self):
        self.isMenuVisible = not self.isMenuVisible
        self.ArrowBtn.setText('V' if self.isMenuVisible else '>')

class AddAccWindow(QWidget):
    def __init__(self):
        super().__init__(parent=None)
        viewHandler.AddChildWindowRef(self)
        self.InitUI()

    def InitUI(self):
        # Windows required to add the icon as the app taskbar icon
        myappid = u'mycompany.myproduct.subproduct.version'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        # Window properties 
        # Icon
        AppIcon = QIcon('./Resources/app-icon32.png')
        self.setWindowIcon(AppIcon)
        # Size
        posX = 100
        posY = 100
        width = 500
        height = 400
        self.setObjectName('window')
        self.setGeometry(posX, posY, width, height)
        self.setWindowTitle('Add Account')
        # Widgets
        self.setStyleSheet("""
            .gen-menu
            {
            }
        """)
        SizePolicy = QSizePolicy()
        SizePolicy.setHorizontalPolicy(QSizePolicy.Fixed)
        SizePolicy.setVerticalPolicy(QSizePolicy.Fixed)
        self.AccNameInput = QLineEdit(parent=self)
        self.AccNameInput.setPlaceholderText('Account name')
        self.AccNameInput.setStyleSheet('font-size: 11pt;')
        self.AccNameInput.setMinimumWidth(250)
        self.AccNameInput.setMaximumWidth(350)
        self.AccNameInput.setFixedHeight(30)
        self.ExtraInfoInput = QLineEdit(parent=self)
        self.ExtraInfoInput.setPlaceholderText('Extra info e.g. email')
        self.ExtraInfoInput.setStyleSheet('font-size: 11pt;')
        self.ExtraInfoInput.setMinimumWidth(250)
        self.ExtraInfoInput.setMaximumWidth(350)
        self.ExtraInfoInput.setFixedHeight(30)
        self.PwdInput = QLineEdit(parent=self)
        self.PwdInput.setStyleSheet('font-size: 11pt;')
        self.PwdInput.setPlaceholderText('Password')
        self.PwdInput.setEchoMode(QLineEdit.Password)
        self.PwdInput.setMinimumWidth(250)
        self.PwdInput.setMaximumWidth(350)
        self.PwdInput.setFixedHeight(30)
        self.pwdToggleText = 'o'
        self.PwdToggleBtn = QPushButton(parent=self.PwdInput, text=self.pwdToggleText)
        self.PwdToggleBtn.setStyleSheet('border: none;')
        self.PwdToggleBtn.setDefault(True)
        self.PwdToggleBtn.clicked.connect(self.TogglePwdVisibility)
        # Generate group menu
        self.GenOptionMenu = OptionMenu(parent=self, text='Generate')
        self.GenOptionMenu.setSizePolicy(SizePolicy)
        self.GenOptionMenu.clicked.connect(self.OnGenOptionMenuClick)
        self.GenMenu = QGroupBox(parent=self)
        self.GenMenu.setProperty('class', 'gen-menu')
        # Start hidden
        self.GenMenu.setVisible(False)
        MinPwdLenInput = QLineEdit(parent=self.GenMenu)
        MinPwdLenInput.setProperty('class', 'min-pwd-len-input')
        MinPwdLenInput.setMinimumWidth(100)
        MinPwdLenInput.setMaximumWidth(100)
        MinPwdLenInput.setFixedHeight(30)
        MinPwdLenInput.setPlaceholderText('Min length')
        # 1-99
        MinPwdLenInput.setInputMask('00')
        MaxPwdLenInput = QLineEdit(parent=self.GenMenu)
        MaxPwdLenInput.setProperty('class', 'max-pwd-len-input')
        MaxPwdLenInput.setMinimumWidth(100)
        MaxPwdLenInput.setMaximumWidth(100)
        MaxPwdLenInput.setFixedHeight(30)
        MaxPwdLenInput.setPlaceholderText('Max length')
        # 1-99
        MaxPwdLenInput.setInputMask('00')
        GenBtn = QPushButton(parent=self.GenMenu, text='Generate')
        GenBtn.setStyleSheet('font-size: 11pt; border: 1px solid #353535;')
        GenBtn.setDefault(True)
        GenBtn.setMinimumWidth(100)
        GenBtn.setMaximumWidth(250)
        GenBtn.setFixedHeight(30)
        GenBtn.clicked.connect(self.GeneratePwd)
        GenPwdLenLayout = QHBoxLayout()
        GenPwdLenLayout.addWidget(MinPwdLenInput)
        GenPwdLenLayout.addWidget(MaxPwdLenInput)
        GenMenuLayout = QVBoxLayout()
        GenMenuLayout.addLayout(GenPwdLenLayout)
        GenMenuLayout.addWidget(GenBtn)
        self.GenMenu.setLayout(GenMenuLayout)
        AddBtn = QPushButton(parent=self, text='Add Account')
        AddBtn.setStyleSheet('font-size: 11pt; border: 1px solid #353535;')
        AddBtn.setDefault(True)
        AddBtn.setMinimumWidth(100)
        AddBtn.setMaximumWidth(250)
        AddBtn.setFixedHeight(30)
        AddBtn.clicked.connect(self.AddAccount)
        # Layout
        PwdInputLayout = QHBoxLayout()
        PwdInputLayout.addStretch()
        PwdInputLayout.addWidget(self.PwdToggleBtn)
        self.PwdInput.setLayout(PwdInputLayout)
        WindowLayout = QVBoxLayout()
        WindowLayout.addWidget(self.AccNameInput)
        WindowLayout.addWidget(self.ExtraInfoInput)
        WindowLayout.addWidget(self.PwdInput)
        WindowLayout.addWidget(self.GenOptionMenu)
        WindowLayout.addWidget(self.GenMenu)
        WindowLayout.addWidget(AddBtn)
        self.setLayout(WindowLayout)
        # Shortcuts
        CloseWindow = QShortcut(QKeySequence('Ctrl+W'), self)
        CloseWindow.setAutoRepeat(False)
        CloseWindow.activated.connect(self.close)
        
    def TogglePwdVisibility(self):
        self.PwdInput.setEchoMode(QLineEdit.Normal) if self.PwdInput.echoMode() == QLineEdit.Password else self.PwdInput.setEchoMode(QLineEdit.Password)
        if self.PwdInput.echoMode() == QLineEdit.Password:
            self.pwdToggleText = 'o'
        else:
            self.pwdToggleText = '-'
        self.PwdToggleBtn.setText(self.pwdToggleText) 

    def OnGenOptionMenuClick(self):
        isVisible = self.GenMenu.isVisible()
        nValue = not isVisible
        self.GenMenu.setVisible(nValue)

    def GeneratePwd(self):
        minPwdLen = 15
        maxPwdLen = 28
        pwdLen = random.randint(minPwdLen, maxPwdLen)
        pwd = ''
        for i in range(pwdLen):
            charArrIndex = random.randrange(0, len(Characters))
            CharArr = Characters[charArrIndex]
            char = chr(random.randint(CharArr[0], CharArr[1])) if (len(CharArr) == 2) else CharArr[random.randint(0, len(CharArr) - 1)]
            pwd += char
        # Check if password already exists 
        Pwds = xmlHandler.GetAccPwds() 
        if Pwds.__contains__(pwd):
            self.GeneratePwd()
            return
        self.PwdInput.setText(pwd) 

    def AddAccount(self):
        accName = self.AccNameInput.text()
        extraInfo = self.ExtraInfoInput.text()
        pwd = self.PwdInput.text()
        AccNames = xmlHandler.GetAccNames()
        if AccNames.__contains__(accName):
            QMessageBox.critical(self, 'Not Added', 'This account name already exists')
            return
        AccDetails = [accName, extraInfo, pwd]
        ok = False
        for i in range(len(AccDetails)): 
            field = AccDetails[i]
            if field == '':
                AccDetails[i] = '-'
                continue
            if not ok:
                ok = True
        if not ok:
            QMessageBox.critical(self, 'Not Added', 'Fill at least 1 field')
            return
        accName = AccDetails[0]
        extraInfo = AccDetails[1]
        pwd = AccDetails[2]
        # Sync
        encAccName = encoder.Encrypt(accName)
        encExtraInfo = encoder.Encrypt(extraInfo)
        encPwd = encoder.Encrypt(pwd)
        op = 'C'
        msg = f'{clientSocket.SYNC_BC}, {op}, {encAccName}, {encExtraInfo}, {encPwd}'
        clientSocket.SendSyncBroadcastMsg(msg)
        # Clear fields
        self.AccNameInput.setText('')
        self.ExtraInfoInput.setText('')
        self.PwdInput.setText('')
        self.AccNameInput.setFocus()

    def closeEvent(self, e):
        super().closeEvent(e)
        viewHandler.RemoveChildWindowRef(self)

def Init():
    global Characters
    Characters = [[48, 57], [65, 90], [97, 122], ['-', '_', '.', ',', '/', ';']]

def Create():
    global Window
    Window = AddAccWindow()
    Window.show()
