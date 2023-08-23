from PySide2.QtWidgets import QApplication
# My files 
import encoder
import xmlHandler
import viewHandler
import login
import mainWindow
import addAcc

if __name__ == '__main__':
    app = QApplication()
    encoder.Init()
    xmlHandler.Init()
    viewHandler.Init()
    addAcc.Init()
    if xmlHandler.IsLocked():
        login.Create()
    else:
        MainWindow = mainWindow.Create()
        viewHandler.OnLogin(windowRef=MainWindow)
    app.exec_()
