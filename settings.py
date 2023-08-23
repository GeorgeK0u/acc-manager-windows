import ctypes
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QMessageBox, QShortcut, QLabel, QPushButton, QLineEdit, QCheckBox, QSpacerItem, QSizePolicy
from PySide2.QtGui import QKeySequence, QIcon
# My files
import xmlHandler
import viewHandler

Window = None

class SettingsWindow(QWidget):
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
        width = 400
        height = 300
        self.setGeometry(posX, posY, width, height)
        self.setWindowTitle('Settings')
        # Widgets
        self.setStyleSheet("""
            *
            {
                font-size: 11pt;
            }
            
            .lock-label
            {
                margin: 20px 10px 0 0;
            }

            .lock-input
            {
                margin-top: 20px;
                width: 150px;
                max-width: 150px;
                height: 25px;
                max-height: 25px;
            }

            .run-bg-checkbox
            {
                margin-top: 15px;
            }
        """)
        SizePolicy = QSizePolicy()
        # Prevent stretching to fill up all window available space
        SizePolicy.setHorizontalPolicy(QSizePolicy.Fixed)
        SizePolicy.setVerticalPolicy(QSizePolicy.Fixed)
        LockLbl = QLabel(parent=self, text='Lock code')
        LockLbl.setProperty('class', 'lock-label')
        LockLbl.setSizePolicy(SizePolicy)
        LockInput = QLineEdit(parent=self)
        LockInput.setProperty('class', 'lock-input')
        LockInput.setObjectName('lock')
        LockInput.setSizePolicy(SizePolicy)
        LockInput.setPlaceholderText('None')
        LockInput.setText(xmlHandler.GetLockCode())
        RunOnBgCheckBox = QCheckBox(parent=self, text='Run on background')
        RunOnBgCheckBox.setProperty('class', 'run-bg-checkbox')
        RunOnBgCheckBox.setObjectName('run-bg')
        RunOnBgCheckBox.setSizePolicy(SizePolicy)
        isRunOnBgEnabled = xmlHandler.GetRunOnBg()
        RunOnBgCheckBox.setChecked(isRunOnBgEnabled)
        # Layout
        LockLayout = QHBoxLayout()
        LockLayout.setSpacing(0)
        LockLayout.addWidget(LockLbl)
        LockLayout.addWidget(LockInput)
        WindowLayout = QVBoxLayout()
        WindowLayout.setAlignment(Qt.AlignTop)
        WindowLayout.setSpacing(0)
        WindowLayout.addLayout(LockLayout)
        WindowLayout.addWidget(RunOnBgCheckBox)
        self.setLayout(WindowLayout)
        # Shortcuts
        CloseWindow = QShortcut(QKeySequence('Ctrl+W'), self)
        CloseWindow.setAutoRepeat(False)
        CloseWindow.activated.connect(self.close)

    def UpdateSettings(self):
        try:
            # Lock
            LockInput = self.findChild(QLineEdit, 'lock')
            typedCode = LockInput.text()
            xmlHandler.UpdateLockCode(typedCode)
            # Run on bg
            RunOnBgCheckBox = self.findChild(QCheckBox, 'run-bg')
            state = RunOnBgCheckBox.isChecked()
            xmlHandler.UpdateRunOnBgCheckBox(state)
        except:
            pass

    def closeEvent(self, e):
        super().closeEvent(e)
        self.UpdateSettings()
        viewHandler.RemoveChildWindowRef(self)

def Create():
    global Window
    Window = SettingsWindow()
    Window.show()
    Window.setFocus()
