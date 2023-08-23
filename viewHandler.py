# My files
import clientSocket
import systemTray as sysTray
import xmlHandler

ChildWindows = None
MainWindow = None

def Init():
    global ChildWindows
    ChildWindows = []

def OnLogin(windowRef):
    global MainWindow
    MainWindow = windowRef
    clientSocket.CreateConn()
    # Run on background
    if xmlHandler.GetRunOnBg():
        sysTray.Show()

def Show():
    if MainWindow.isVisible():
        return
    # If I don't set initial pos and try to auto-show as maximized, 
    # it fails to render besides the minimum size
    MainWindow.show()

def AddChildWindowRef(window):
    ChildWindows.append(window)

def CloseChildWindows():
    # Closing a child window, automatically removes it from my list  
    i = len(ChildWindows)-1
    while i >= 0:
        child = ChildWindows[i]
        child.close()
        i -= 1

def Close():
    MainWindow.close()

def RemoveChildWindowRef(window):
    ChildWindows.remove(window)

def OnExit():
    clientSocket.SendCloseSocketMsg()
