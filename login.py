import ctypes
from PySide2.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QMessageBox, QShortcut, QLabel, QPushButton, QLineEdit, QSpacerItem, QSizePolicy
from PySide2.QtGui import QKeySequence, QIcon
# My files 
import xmlHandler
import viewHandler
import mainWindow

Window = None

class LoginWindow(QWidget):
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
        self.setWindowTitle('Login')
        # Size
        width = 300
        height = 120
        # Prevent resizing
        self.setMinimumSize(width, height)
        self.setMaximumSize(width, height)
        # Widgets
        # Code input
        self.CodeInput = QLineEdit(parent=self)
        self.CodeInput.setProperty('class', 'code-input')
        self.CodeInput.setPlaceholderText('Code')
        self.CodeInput.returnPressed.connect(self.Validate)
        self.CodeInput.setFocus()
        # Login btn 
        self.LoginBtn = QPushButton(parent=self, text='Login')
        self.LoginBtn.setProperty('class', 'login-btn')
        # Trigger enter key press as click 
        self.LoginBtn.setDefault(True)
        self.LoginBtn.clicked.connect(self.Validate)
        # Set layout
        self.Style()
        # Shortcuts
        CloseWindow = QShortcut(QKeySequence('Ctrl+W'), self)
        CloseWindow.setAutoRepeat(False)
        CloseWindow.activated.connect(self.close)

    def Style(self):
        # Layout
        WindowLayout = QHBoxLayout()
        WindowLayout.addWidget(self.CodeInput, stretch=2)
        WindowLayout.addWidget(self.LoginBtn, stretch=1)
        self.setLayout(WindowLayout)

    def Validate(self):
        corCode = xmlHandler.GetLockCode()
        typedCode = self.CodeInput.text()
        if (typedCode != corCode):
            QMessageBox.critical(self, 'Error', 'Incorrect code')
            return
        # Code is correct 
        # Show main window
        MainWindow = mainWindow.Create()
        viewHandler.OnLogin(windowRef=MainWindow)
        # Close login window
        self.close()

def Create():
    global Window
    Window = LoginWindow()
    Window.show()
