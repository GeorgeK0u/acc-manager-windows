import json

_wrong_chars = None
PWD_MASK_CHAR = chr(0x25CF)

def init():
    global _wrong_chars
    _wrong_chars = 5

def encrypt(text):
    enc_text = ''
    for ch in text:
        ascii = ord(ch)
        enc_ch = chr(ascii + _wrong_chars)
        enc_text += enc_ch
    return enc_text

def decrypt(text):
    dec_text = ''
    for ch in text:
        ascii = ord(ch)
        dec_ch = chr(ascii - _wrong_chars)
        dec_text += dec_ch
    return dec_text

def mask_pwd(text):
    masked_text = ''
    for _ in range(len(text)):
        masked_text += PWD_MASK_CHAR
    return masked_text

def convert_to_json_string(list):
    json_string = json.dumps(list)
    return json_string

def convert_to_list(json_string):
    list_obj = json.loads(json_string)
    return list_obj
