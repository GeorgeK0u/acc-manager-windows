from PySide2.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QShortcut, QPushButton
from PySide2.QtGui import QKeySequence
# My files 
import addAcc 

class Wnd(QMainWindow):
    def __init__(self):
        super().__init__(parent=None)
        # Window properties 
        self.setWindowTitle('Account Manager')
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
        addAccBtn.clicked.connect(addAcc.ShowAddAccountWindow)
        addAccBtn.setFocus()
        # Manage existing accounts
        accMngBtn = QPushButton(parent=centralWidget, text='Manage')
        accMngBtn.setDefault(True)
        # accMngBtn.clicked.connect(self.ShowAccManagerWindow)
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


    def closeEvent(self, e):
        super().closeEvent(e)
        # Manually close child window
        if addAcc.window != None:
            addAcc.window.close()

_app = QApplication()
window = Wnd()
window.show()
_app.exec_()
# Window closed
print('App closed')
