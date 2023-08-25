import ctypes
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QMessageBox, QShortcut, QLabel, QPushButton, QLineEdit, QCheckBox, QComboBox, QSpacerItem, QSizePolicy
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

            .header
            {
                font-size: 14pt;
            }
        """)
        FixedSizePolicy = QSizePolicy()
        FixedSizePolicy.setHorizontalPolicy(QSizePolicy.Fixed)
        FixedSizePolicy.setVerticalPolicy(QSizePolicy.Fixed)
        # Security header
        SecurityHeader = QLabel(parent=self, text='Security')
        SecurityHeader.setProperty('class', 'header')
        SecurityHeader.setSizePolicy(FixedSizePolicy)
        # Lock app
        LockLbl = QLabel(parent=self, text='Lock code')
        LockLbl.setSizePolicy(FixedSizePolicy)
        self.LockInput = QLineEdit(parent=self)
        self.LockInput.setSizePolicy(FixedSizePolicy)
        self.LockInput.setPlaceholderText('None')
        lockCode = xmlHandler.GetLockCode()
        self.LockInput.setText(lockCode)
        # Default visibility for passwords
        PwdVisibilityLbl = QLabel(parent=self, text='Passwords visibility')
        PwdVisibilityLbl.setSizePolicy(FixedSizePolicy)
        self.PwdVisibilityDropdown = QComboBox(parent=self)
        self.PwdVisibilityDropdown.addItems(['Hide', 'Show'])
        self.PwdVisibilityDropdown.setSizePolicy(FixedSizePolicy)
        pwdVisibilityOptionIndex = xmlHandler.GetPwdVisibilityOptionIndex()
        self.PwdVisibilityDropdown.setCurrentIndex(pwdVisibilityOptionIndex)
        # Continue running on background
        self.RunOnBgCheckBox = QCheckBox(parent=self, text='Run on background')
        self.RunOnBgCheckBox.setSizePolicy(FixedSizePolicy)
        isRunOnBgEnabled = xmlHandler.GetRunOnBg()
        self.RunOnBgCheckBox.setChecked(isRunOnBgEnabled)
        # Layout
        # Lock layout
        LockLayout = QHBoxLayout()
        LockLayout.setAlignment(Qt.AlignLeft)
        LockLayout.addWidget(LockLbl)
        LockLayout.addWidget(self.LockInput)
        # Pwd visibility layout
        PwdVisibilityLayout = QHBoxLayout()
        PwdVisibilityLayout.setAlignment(Qt.AlignLeft)
        PwdVisibilityLayout.addWidget(PwdVisibilityLbl)
        PwdVisibilityLayout.addWidget(self.PwdVisibilityDropdown)
        # Security layout
        SecurityLayout = QVBoxLayout()
        SecurityLayout.setAlignment(Qt.AlignLeft)
        SecurityLayout.addWidget(SecurityHeader)
        SecurityLayout.addSpacing(10)
        SecurityLayout.addLayout(LockLayout)
        SecurityLayout.addSpacing(6)
        SecurityLayout.addLayout(PwdVisibilityLayout)
        # Window layout
        WindowLayout = QVBoxLayout()
        WindowLayout.setAlignment(Qt.AlignTop|Qt.AlignLeft)
        WindowLayout.addLayout(SecurityLayout)
        WindowLayout.addSpacing(20)
        WindowLayout.addWidget(self.RunOnBgCheckBox)
        self.setLayout(WindowLayout)
        # Shortcuts
        CloseWindow = QShortcut(QKeySequence('Ctrl+W'), self)
        CloseWindow.setAutoRepeat(False)
        CloseWindow.activated.connect(self.close)

    def UpdateSettings(self):
        # Lock
        typedCode = self.LockInput.text()
        xmlHandler.UpdateLockCode(typedCode)
        # Pwd visibility
        selIndex = self.PwdVisibilityDropdown.currentIndex()
        xmlHandler.UpdatePwdVisibilityOptionIndex(selIndex)
        # Run on bg
        state = self.RunOnBgCheckBox.isChecked()
        xmlHandler.UpdateRunOnBgCheckBox(state)

    def closeEvent(self, e):
        super().closeEvent(e)
        self.UpdateSettings()
        viewHandler.RemoveChildWindowRef(self)

def Create():
    global Window
    Window = SettingsWindow()
    Window.show()
    Window.setFocus()
