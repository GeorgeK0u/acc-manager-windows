import ctypes
from PySide2.QtCore import QSize
from PySide2.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QMessageBox, QShortcut, QLabel, QPushButton, QLineEdit, QSpacerItem, QSizePolicy
from PySide2.QtGui import QKeySequence, QIcon
# My files 
import encoder
import xmlHandler
import addAcc 
import mng

class Wnd(QMainWindow):
    def CheckSaveLock(self):
        try:
            lockInputWidget = self.settCentralWidget.findChild(QLineEdit)
            typedCode = lockInputWidget.text().strip()
            xmlHandler.UpdateLockCode(typedCode)
        except:
            pass
        
    def ShowSettings(self):
        # Remove main window widgets
        for widget in self.centralWidget.children():
            widget.deleteLater()
        self.centralWidget.deleteLater()
        self.centralWidget = None
        # Settings
        self.settCentralWidget = QWidget(self)
        self.settCentralWidget.setStyleSheet('''
            QLabel
            {
                font-size: 14pt;
            }
            
            QLineEdit
            {
                font-size: 12pt;
                width: 150px;
                max-width: 150px;
            }
        ''')
        settCentralWidgetLayout = QVBoxLayout()
        self.setWindowTitle('Settings')
        spacePolicy = QSizePolicy()
        spacePolicy.setVerticalStretch(2)
        spacePolicy.setVerticalPolicy(QSizePolicy.Preferred)
        # Lock app option
        lockLbl = QLabel('Lock App', self.settCentralWidget)
        lockInput = QLineEdit(self.settCentralWidget)
        lockInput.setPlaceholderText('Not locked')
        lockInput.setText(xmlHandler.GetLockCode())
        space = QWidget()
        space.setFixedHeight(200)
        space.setSizePolicy(spacePolicy)
        # Layout
        settCentralWidgetLayout.addWidget(lockLbl)
        settCentralWidgetLayout.addWidget(lockInput)
        settCentralWidgetLayout.addWidget(space)
        self.settCentralWidget.setLayout(settCentralWidgetLayout)
        self.setCentralWidget(self.settCentralWidget)
        # Settings shortcuts
        HideSettings = QShortcut(QKeySequence('Esc'), self.settCentralWidget)
        HideSettings.setAutoRepeat(False)
        HideSettings.activated.connect(lambda:self.ShowMainWindow(reset=True))

    def ShowMainWindow(self, reset=False):
        if reset:
            self.CheckSaveLock()
            for widget in self.settCentralWidget.children():
                widget.deleteLater()
            self.settCentralWidget.deleteLater()
            self.settCentralWidget = None
        # Main window
        self.setWindowTitle('Account Manager')
        self.centralWidget = QWidget(self)
        # Add accounts
        addAccBtn = QPushButton(parent=self.centralWidget, text='Add')
        addAccBtn.setDefault(True)
        addAccBtn.clicked.connect(lambda:addAcc.ShowAddAccountWindow(self))
        addAccBtn.setFocus()
        # Manage existing accounts
        accMngBtn = QPushButton(parent=self.centralWidget, text='Manage')
        accMngBtn.setDefault(True)
        accMngBtn.clicked.connect(lambda:mng.ShowAccManagerWindow(self))
        # Place widgets
        centralWidgetLayout = QHBoxLayout()
        centralWidgetLayout.addWidget(addAccBtn)
        centralWidgetLayout.addWidget(accMngBtn)
        self.centralWidget.setLayout(centralWidgetLayout)
        self.setCentralWidget(self.centralWidget)
        # Main window shortcuts
        OpenSettings = QShortcut(QKeySequence('Alt+S'), self.centralWidget)
        OpenSettings.setAutoRepeat(False)
        OpenSettings.activated.connect(self.ShowSettings)

    def ShowLockScreen(self):
        def CheckCode():
            code = xmlHandler.GetLockCode()
            typedCode = codeInput.text().strip()
            if (code != typedCode):
                QMessageBox.critical(lockCentralWidget, 'Error', 'Code is not correct')
                return
            # Close lock screen
            for widget in lockCentralWidget.children():
                widget.deleteLater()
            lockCentralWidget.deleteLater()
            # Show main window
            self.entered = True
            self.ShowMainWindow()
        lockCentralWidget = QWidget()
        codeInput = QLineEdit(lockCentralWidget)
        codeInput.setPlaceholderText('Code')
        codeInput.returnPressed.connect(CheckCode)
        enterBtn = QPushButton('Enter', lockCentralWidget)
        enterBtn.setDefault(True)
        enterBtn.clicked.connect(CheckCode)
        # Layout
        lockCentralWidgetLayout = QHBoxLayout()
        lockCentralWidgetLayout.addWidget(codeInput)
        lockCentralWidgetLayout.addWidget(enterBtn)
        lockCentralWidget.setLayout(lockCentralWidgetLayout)
        self.setCentralWidget(lockCentralWidget)

    def __init__(self):
        super().__init__(parent=None)
        self.InitUI()
        if xmlHandler.IsLocked():
            self.entered = False
            self.ShowLockScreen()
            return
        self.entered = True
        self.ShowMainWindow()

    def InitUI(self):
        # Window properties 
        # Tell windows to use the window icon as the taskbar icon
        myappid = u'mycompany.myproduct.subproduct.version'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        # Change window icon
        iconSize = QSize(32, 32) 
        self.setIconSize(iconSize)
        mainWndIcon = QIcon('./Resources/app-icon32.png')
        self.setWindowIcon(mainWndIcon)
        self.setGeometry(100, 100, 400, 300)
        self.setStyleSheet("""
            QPushButton
            {
                font-size: 11pt;
                padding: 2px 4px;
                border: 1px solid #353535;
            }
        """)
        # Shortcuts
        CloseMainWindow = QShortcut(QKeySequence('Ctrl+W'), self)
        CloseMainWindow.setAutoRepeat(False)
        CloseMainWindow.activated.connect(self.OnWindowClose)
        CloseApp = QShortcut(QKeySequence('Ctrl+Shift+W'), self)
        CloseApp.setAutoRepeat(False)
        CloseApp.activated.connect(self.OnWindowClose)

    def OnWindowClose(self):
        if self.entered:
            self.CheckSaveLock()
        self.close()

    def closeEvent(self, e):
        super().closeEvent(e)
        # Manually close children windows
        if addAcc.window != None:
            addAcc.window.close()
        if mng.window != None:
            mng.window.close()

_app = QApplication()
encoder.Init()
xmlHandler.Init()
window = Wnd()
window.show()
window.setFocus()
_app.exec_()
