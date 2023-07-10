import lxml.etree as et
# My widgets
import encoder

saveFileName = None
xmlTree = None
xmlRoot = None
accTagName = None
accNameTagName = None
ExtraInfoTagName = None
pwdTagName = None

def Init():
    global saveFileName, xmlTree, xmlRoot, accTagName, accNameTagName, extraInfoTagName, pwdTagName
    saveFileName = "Resources/save.xml"
    xmlTree = et.parse(saveFileName)
    xmlRoot = xmlTree.getroot()
    accTagName = "account"
    accNameTagName = "account-name"
    extraInfoTagName = "account-extra-info"
    pwdTagName = "account-pwd"

def Commit():
    xmlTree.write(saveFileName)

def SaveAcc(accName, extraInfo, pwd):
    encAccName = encoder.Encrypt(accName)
    encExtraInfo = encoder.Encrypt(extraInfo)
    encPwd = encoder.Encrypt(pwd)
    accTag = et.SubElement(xmlRoot, accTagName)
    accNameTag = et.SubElement(accTag, accNameTagName)
    accNameTag.text = encAccName
    extraInfoTag = et.SubElement(accTag, extraInfoTagName)
    extraInfoTag.text = encExtraInfo
    pwdTag = et.SubElement(accTag, pwdTagName)
    pwdTag.text = encPwd
    Commit()

def GetAccs():
    Accs = xmlRoot.findall(accTagName)
    return list(map(lambda AccTag:[encoder.Decrypt(AccTag[0].text), encoder.Decrypt(AccTag[1].text), encoder.Decrypt(AccTag[2].text)], Accs))

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
    # Update XML
    xmlTree.write(saveFileName)

def DeleteAcc(accName):
    AccNames = GetAccNames()
    accIndex = AccNames.index(accName) 
    xmlRoot.remove(xmlRoot.findall(accTagName)[accIndex])
    Commit()
