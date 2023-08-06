wrongChars = None

def Init():
    global wrongChars
    wrongChars = 5

def Encrypt(text):
    if text == None:
        return text
    encryptedText = ''
    for ch in text:
        chAscii = ord(ch)
        eChar = chr(chAscii + wrongChars)
        encryptedText += eChar
    return encryptedText

def Decrypt(text):
    if text == None:
        return text
    decryptedText = ''
    for ch in text:
        chAscii = ord(ch)
        dChar = chr(chAscii - wrongChars)
        decryptedText += dChar
    return decryptedText
