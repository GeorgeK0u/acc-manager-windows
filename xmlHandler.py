import lxml.etree as et
# My widgets
import encoder
import systemTray

saveFileName = None
xmlTree = None
xmlRoot = None
lockTagName = None
pwdVisibilityTagName = None
runOnBgTagName = None
accTagName = None
accNameTagName = None
extraInfoTagName = None
pwdTagName = None

def Init():
    global saveFileName, xmlTree, xmlRoot, lockTagName, pwdVisibilityTagName, runOnBgTagName, accTagName, accNameTagName, extraInfoTagName, pwdTagName
    saveFileName = 'Resources/save.xml'
    xmlTree = et.parse(saveFileName)
    xmlRoot = xmlTree.getroot()
    lockTagName = 'lock'
    pwdVisibilityTagName = 'pwd-visibility'
    runOnBgTagName = 'run-on-bg'
    accTagName = 'account'
    accNameTagName = 'account-name'
    extraInfoTagName = 'account-extra-info'
    pwdTagName = 'account-pwd'

def Commit():
    xmlTree.write(saveFileName)

def GetLockCode():
    lockTag = xmlRoot.find(lockTagName)
    curCode = encoder.Decrypt(lockTag.text)
    return curCode

def UpdateLockCode(nCode):
    curCode = GetLockCode()
    if curCode == nCode:
        return
    lockTag = xmlRoot.find(lockTagName)
    lockTag.text = encoder.Encrypt(nCode)
    Commit()

def IsLocked():
    return GetLockCode() != None

def GetPwdVisibilityOptionIndex():
    pwdVisibilityTag = xmlRoot.find(pwdVisibilityTagName)
    optionIndex = int(pwdVisibilityTag.text)
    return optionIndex

def UpdatePwdVisibilityOptionIndex(selIndex):
    curIndex = GetPwdVisibilityOptionIndex()
    if curIndex == selIndex:
        return
    pwdVisibilityTag = xmlRoot.find(pwdVisibilityTagName)
    pwdVisibilityTag.text = str(selIndex)
    Commit()

def GetRunOnBg():
    runOnBgTag = xmlRoot.find(runOnBgTagName)
    value = runOnBgTag.text
    return True if value == 'enabled' else False 

def UpdateRunOnBgCheckBox(nState):
    curState = GetRunOnBg()
    if curState == nState:
        return
    runOnBgTag = xmlRoot.find(runOnBgTagName)
    runOnBgTag.text = 'enabled' if nState else 'disabled'
    Commit()
    # Apply change without need to restart app
    if nState:
        systemTray.Show()
    else:
        systemTray.Hide()

def SaveAcc(EncAccDetails):
    encAccName = EncAccDetails[0]
    encExtraInfo = EncAccDetails[1]
    encPwd = EncAccDetails[2]
    accTag = et.SubElement(xmlRoot, accTagName)
    accNameTag = et.SubElement(accTag, accNameTagName)
    accNameTag.text = encAccName
    extraInfoTag = et.SubElement(accTag, extraInfoTagName)
    extraInfoTag.text = encExtraInfo
    pwdTag = et.SubElement(accTag, pwdTagName)
    pwdTag.text = encPwd
    Commit()
    print('Added the new account from broadcast')

def GetAccs(decrypt=True):
    Accs = xmlRoot.findall(accTagName)
    return list(map(lambda AccTag:[encoder.Decrypt(AccTag[0].text) if decrypt else AccTag[0].text, encoder.Decrypt(AccTag[1].text) if decrypt else AccTag[1].text, encoder.Decrypt(AccTag[2].text) if decrypt else AccTag[2].text], Accs))

def GetAccNames():
    Accs = GetAccs()
    return list(map(lambda accParts:accParts[0], Accs))    

def GetAccPwds():
    Accs = GetAccs()
    return list(map(lambda accParts:accParts[-1], Accs))    

def ChangeAccValue(accName, colIndex, nValue): 
    AccNames = GetAccNames()
    accIndex = AccNames.index(accName)
    Acc = xmlRoot.findall(accTagName)[accIndex]
    AccDetail = Acc[colIndex]
    AccDetail.text = encoder.Encrypt(nValue)
    Commit()

def DeleteAcc(accName):
    AccNames = GetAccNames()
    accIndex = AccNames.index(accName) 
    xmlRoot.remove(xmlRoot.findall(accTagName)[accIndex])
    Commit()
