from PySide2.QtWidgets import QSystemTrayIcon, QMenu
from PySide2.QtGui import QIcon

from . import view_handler

_tray_icon = None
close_bg = False

def _on_show():
    view_handler.show()

def _on_exit():
    global close_bg
    close_bg = True
    view_handler.close()

def _on_icon_activation(reason):
    if reason != QSystemTrayIcon.ActivationReason.Trigger:
        return
    # Icon click
    _on_show()

def show():
    global _tray_icon
    app_icon = QIcon(r'.\Resources\Icons\app-icon.png')
    _tray_icon = QSystemTrayIcon(app_icon)
    right_click_menu = QMenu()
    show_action = right_click_menu.addAction('Show')
    show_action.triggered.connect(_on_show)
    exit_action = right_click_menu.addAction('Exit')
    exit_action.triggered.connect(_on_exit)
    _tray_icon.setContextMenu(right_click_menu)
    _tray_icon.activated.connect(_on_icon_activation)
    _tray_icon.show()

def hide():
    _tray_icon.hide()
