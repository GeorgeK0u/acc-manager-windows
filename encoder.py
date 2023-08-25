wrongChars = None
PWD_MASK_CHAR = chr(0x25CF)

def Init():
    global wrongChars
    wrongChars = 5

def Encrypt(text):
    # No lock code
    if text == None:
        return text
    encryptedText = ''
    for ch in text:
        chAscii = ord(ch)
        eChar = chr(chAscii + wrongChars)
        encryptedText += eChar
    return encryptedText

def Decrypt(text):
    # No lock code
    if text == None:
        return text
    decryptedText = ''
    for ch in text:
        chAscii = ord(ch)
        dChar = chr(chAscii - wrongChars)
        decryptedText += dChar
    return decryptedText

def MaskPassword(text):
    maskedText = ''
    for i in range(len(text)):
        maskedText += PWD_MASK_CHAR
    return maskedText
