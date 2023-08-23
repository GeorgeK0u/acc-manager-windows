from PySide2.QtWidgets import QSystemTrayIcon, QMenu
from PySide2.QtGui import QIcon
# My files
import viewHandler

TrayIcon = None
closeBg = False

def OnShow():
    viewHandler.Show()

def OnExit():
    global closeBg
    closeBg = True
    viewHandler.Close()

def OnIconClick(reason):
    # print(f'OnIconClick {reason}')
    pass

def Show():
    global TrayIcon
    Icon = QIcon(r'Resources\app-icon32.png')
    TrayIcon = QSystemTrayIcon(Icon)
    RightClickMenu = QMenu()
    ShowAction = RightClickMenu.addAction('Show')
    ShowAction.triggered.connect(OnShow)
    ExitAction = RightClickMenu.addAction('Exit')
    ExitAction.triggered.connect(OnExit)
    TrayIcon.setContextMenu(RightClickMenu)
    TrayIcon.activated.connect(OnIconClick)
    TrayIcon.show()

def Hide():
    TrayIcon.hide()
