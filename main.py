import ctypes
from PySide2.QtCore import QSize
from PySide2.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QShortcut, QPushButton
from PySide2.QtGui import QKeySequence, QIcon
# My files 
import encoder
import xmlHandler
import addAcc 
import mng

class Wnd(QMainWindow):
    def __init__(self):
        super().__init__(parent=None)
        # Window properties 
        self.setWindowTitle('Account Manager')
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
        # Widgets
        # Central
        centralWidget = QWidget(self)
        # Add accounts
        addAccBtn = QPushButton(parent=centralWidget, text='Add')
        addAccBtn.setDefault(True)
        addAccBtn.clicked.connect(lambda:addAcc.ShowAddAccountWindow(self))
        addAccBtn.setFocus()
        # Manage existing accounts
        accMngBtn = QPushButton(parent=centralWidget, text='Manage')
        accMngBtn.setDefault(True)
        accMngBtn.clicked.connect(lambda:mng.ShowAccManagerWindow(self))
        # Place widgets
        centralWidgetLayout = QHBoxLayout()
        centralWidgetLayout.addWidget(addAccBtn)
        centralWidgetLayout.addWidget(accMngBtn)
        centralWidget.setLayout(centralWidgetLayout)
        self.setCentralWidget(centralWidget)
        # Shortcuts
        CloseMainWindow = QShortcut(QKeySequence('Ctrl+W'), self)
        CloseMainWindow.setAutoRepeat(False)
        CloseMainWindow.activated.connect(self.close)
        CloseApp = QShortcut(QKeySequence('Ctrl+Shift+W'), self)
        CloseApp.setAutoRepeat(False)
        CloseApp.activated.connect(self.close)


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
