import xml.etree.ElementTree as et

from . import cryptor
from . import view_handler
from . import tray_handler

resources_dir = None
_save_file_name = None
_tree = None
_root = None
# Security section
_security_section_tag_name = None
_security_section_tag = None
_lock_code_tag_name = None
_pwd_vis_tag_name = None
# Password generation section
MIN_POSSIBLE_GEN_PWD_LEN = 1
MAX_POSSIBLE_GEN_PWD_LEN = 50
_gen_pwd_section_tag_name = None
_gen_pwd_section_tag = None
_gen_def_pwd_len_tag_name = None
# General section
_general_section_tag_name = None
_general_section_tag = None
_run_on_bg_tag_name = None
# (internal setting)
_last_window_state_tag_name = None
WINDOW_NORMAL_STATE = 'normal'
WINDOW_MAXIMIZED_STATE = 'maximized'
# Acc tags
_accs_tag_name = None
_accs_tag = None
_acc_tag_name = None
_acc_name_tag_name = None
_extra_info_tag_name = None
_pwd_tag_name = None

def init():
    # XML parser
    global resources_dir, _save_file_name, _tree, _root
    resources_dir = r'..\..\Resources'
    _save_file_name = f'{resources_dir}/save.xml'
    _tree = et.parse(_save_file_name)
    _root = _tree.getroot()
    # Security section
    global _security_section_tag_name, _security_section_tag, _lock_code_tag_name, _pwd_vis_tag_name
    _security_section_tag_name = 'security-section'
    _security_section_tag = _root.find(_security_section_tag_name)
    _lock_code_tag_name = 'lock-code'
    _pwd_vis_tag_name = 'pwd-visibility'
    # Password generation section
    global _gen_pwd_section_tag_name, _gen_pwd_section_tag, _gen_def_pwd_len_tag_name
    _gen_pwd_section_tag_name = 'gen-pwd-section'
    _gen_pwd_section_tag = _root.find(_gen_pwd_section_tag_name)
    _gen_def_pwd_len_tag_name = 'gen-def-pwd-len'
    # General section
    global _general_section_tag_name, _general_section_tag, _run_on_bg_tag_name, _last_window_state_tag_name
    _general_section_tag_name = 'general-section'
    _general_section_tag = _root.find(_general_section_tag_name)
    _run_on_bg_tag_name = 'run-on-bg'
    _last_window_state_tag_name = 'last-window-state'
    # Acc tags
    global _accs_tag_name, _accs_tag, _acc_tag_name, _acc_name_tag_name, _extra_info_tag_name, _pwd_tag_name
    _accs_tag_name = 'accs'
    _accs_tag = _root.find(_accs_tag_name)
    _acc_tag_name = 'acc'
    _acc_name_tag_name = 'acc-name'
    _extra_info_tag_name = 'extra-info'
    _pwd_tag_name = 'pwd'

# Security section
def get_lock_code():
    lock_tag = _security_section_tag.find(_lock_code_tag_name)
    code = lock_tag.text
    # XML parser returns None on empty text
    if code != None:
        code = cryptor.decrypt(code)
    else:
        code = ''
    return code

def is_locked():
    return get_lock_code() != ''

def update_lock_code(typed_code):
    cur_code = get_lock_code()
    if cur_code == typed_code:
        return
    lock_tag = _security_section_tag.find(_lock_code_tag_name)
    lock_tag.text = cryptor.encrypt(typed_code)
    _commit()

def get_pwd_vis_option_index():
    pwd_vis_tag = _security_section_tag.find(_pwd_vis_tag_name)
    option_index = int(pwd_vis_tag.text)
    return option_index

def update_pwd_vis_option_index(sel_index):
    cur_index = get_pwd_vis_option_index()
    if cur_index == sel_index:
        return
    pwd_vis_tag = _security_section_tag.find(_pwd_vis_tag_name)
    pwd_vis_tag.text = str(sel_index)
    _commit()

# Password generation section
def get_gen_def_pwd_len():
    gen_def_pwd_len_tag = _gen_pwd_section_tag.find(_gen_def_pwd_len_tag_name)
    enc_def_pwd_len = gen_def_pwd_len_tag.text
    def_pwd_len = int(cryptor.decrypt(enc_def_pwd_len))
    return def_pwd_len

def update_gen_def_pwd_len(sel_def_len):
    cur_def_len = get_gen_def_pwd_len()
    if cur_def_len == sel_def_len:
        return
    gen_def_pwd_len_tag = _gen_pwd_section_tag.find(_gen_def_pwd_len_tag_name)
    gen_def_pwd_len_tag.text = cryptor.encrypt(str(sel_def_len)) 
    _commit()

# General section
def get_run_on_bg():
    run_on_bg_tag = _general_section_tag.find(_run_on_bg_tag_name)
    value = run_on_bg_tag.text
    return True if value == 'enabled' else False 

def update_run_on_bg(sel_state):
    cur_state = get_run_on_bg()
    if cur_state == sel_state:
        return
    run_on_bg_tag = _general_section_tag.find(_run_on_bg_tag_name)
    run_on_bg_tag.text = 'enabled' if sel_state else 'disabled'
    _commit()
    # Apply change without need to restart app
    if sel_state:
        tray_handler.show()
    else:
        tray_handler.hide()

# Last window state (internal setting)
def get_last_window_state():
    last_window_state_tag = _root.find(_last_window_state_tag_name)
    return last_window_state_tag.text

def update_last_window_state(cur_state):
    last_state = get_last_window_state()
    if cur_state == last_state:
        return
    last_window_state_tag = _root.find(_last_window_state_tag_name)
    last_window_state_tag.text = cur_state
    _commit()

# Account operations
def save_acc(enc_acc):
    enc_acc_name, enc_extra_info, enc_pwd = enc_acc
    # Update XML
    acc_tag = et.SubElement(_accs_tag, _acc_tag_name)
    acc_name_tag = et.SubElement(acc_tag, _acc_name_tag_name)
    acc_name_tag.text = enc_acc_name
    extra_info_tag = et.SubElement(acc_tag, _extra_info_tag_name)
    extra_info_tag.text = enc_extra_info
    pwd_tag = et.SubElement(acc_tag, _pwd_tag_name)
    pwd_tag.text = enc_pwd
    _commit()
    # Update table
    acc_name = cryptor.decrypt(enc_acc_name)
    extra_info = cryptor.decrypt(enc_extra_info)
    pwd = cryptor.decrypt(enc_pwd)
    acc = [acc_name, extra_info, pwd]
    view_handler.update_acc_table('C', acc)
    print('Added account from broadcast')

def get_accs(decrypt=True):
    accs = []
    for acc_tag in _accs_tag:
        enc_acc_name = acc_tag[0].text
        enc_extra_info = acc_tag[1].text
        enc_pwd = acc_tag[2].text
        if decrypt:
            acc_name = cryptor.decrypt(enc_acc_name)
            extra_info = cryptor.decrypt(enc_extra_info)
            pwd = cryptor.decrypt(enc_pwd)
            accs.append([acc_name, extra_info, pwd])
        else:
            accs.append([enc_acc_name, enc_extra_info, enc_pwd])
    return accs

def get_acc_names():
    accs = get_accs()
    return list(map(lambda acc_details:acc_details[0], accs))    

def get_acc_pwds():
    accs = get_accs()
    return list(map(lambda acc_details:acc_details[2], accs))    

def update_acc_value(enc_details):
    # Get prev acc name
    enc_prev_acc_name = enc_details.pop(0)
    prev_acc_name = cryptor.decrypt(enc_prev_acc_name)
    # Update XML
    acc_names = get_acc_names()
    # Device does not have this account
    if not acc_names.__contains__(prev_acc_name):
        print('Device does not have this account. Replacing the msg on this device with a create msg instead')
        # Create it instead
        enc_acc = enc_details.pop(0)
        save_acc(enc_acc)
        return
    # Remove latest details arr
    # Only if its a broadcast msg, I am using it locally as well to speed up table update delay
    if len(enc_details[0]) == 3:
        enc_details.pop(0)
    acc_index = acc_names.index(prev_acc_name)
    acc_tag = _accs_tag[acc_index]
    i = 0
    for enc_detail_arr in enc_details:
        index = int(cryptor.decrypt(enc_detail_arr[0]))
        enc_detail = enc_detail_arr[1]
        acc_tag[index].text = enc_detail
    _commit()
    # Update table
    acc_details = [prev_acc_name] 
    for i in range(3):
        enc_detail = acc_tag[i].text
        detail = cryptor.decrypt(enc_detail)
        acc_details.append(detail)
    view_handler.update_acc_table('U', acc_details)
    print('Updated account from broadcast') 

def del_acc(enc_acc_name):
    # Decrypt acc name
    acc_name = cryptor.decrypt(enc_acc_name)
    # Get acc index
    acc_names = get_acc_names()
    # Device does not have this account
    if not acc_names.__contains__(acc_name):
        print('!Delete msg cannot be completed. Device does not have this account. Skipping..')
        return
    acc_index = acc_names.index(acc_name) 
    # Update XML
    acc_tag = _accs_tag[acc_index]
    _accs_tag.remove(acc_tag)
    _commit()
    # Update table
    view_handler.update_acc_table('D', acc_name)
    print('Deleted account from broadcast')

def _commit():
    _tree.write(_save_file_name)
