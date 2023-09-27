from PySide2.QtCore import QObject, Signal
import requests

import socket
import threading
from threading import Thread
import subprocess
from time import sleep 
import json

from . import view_handler
from . import xml_handler
from . import cryptor

_MAX_SECS_TRYING_TO_CONNECT = 2
_UTF_8 = 'utf-8'
SYNC_BC = 'sync_broadcast'
_MANUAL_SYNC = 'manual_sync'
_MANUAL_SYNC_END = 'manual_sync_end'
_CLOSE_CONN = 'close_conn'
_conn = None
_is_main_thread_alive = None
sync_instance = None

class _Sync(QObject):
    sync_msg_received = Signal(str, list)
    manual_sync_completed = Signal()

    def __init__(self):
        super().__init__()
        self.manual_sync_in_progress = False
        self.manual_sync_completed.connect(lambda:self.set_manual_sync_in_progress(False))

    def set_manual_sync_in_progress(self, value):
        if self.manual_sync_in_progress == value:
            return
        self.manual_sync_in_progress = value
    
def init():
    global sync_instance
    # Use signal/slot to call sync from main thread
    sync_instance = _Sync()

def create_conn():
    def listen():
        global _conn, _is_main_thread_alive
        try:
            server_local_ip = 'localhost'
            public_ip = ''
            try:
                public_ip = requests.get('https://api.ipify.org').text
            except:
                print('Failed to get public IP address')
                # Update connection status from main thread
                view_handler.set_conn_text('Not connected')
                return
            server_public_ip = socket.gethostbyname('my-ddns.ddns.net')
            # local_conn = public_ip == server_public_ip
            local_conn = True
            host = ''
            if local_conn:
                # Check if the server is running
                port = 56789
                command = f'nmap -p {port} {server_local_ip} | findstr "{port}/tcp"'
                output = subprocess.run(command, shell=True, encoding=_UTF_8, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout.strip()
                # Server device not connected to wifi or not listening
                if not output.__contains__('open'):
                    print('Server is not listening')
                    # Update connection status from main thread
                    view_handler.set_conn_text('Not connected')
                    return
                host = server_local_ip
            else:
                # Cannot check if the server is running before an error occurs at runtime
                host = server_public_ip
            port = 56789
            _conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Waiting X secs in between operations (only needed for before connected)
            _conn.settimeout(_MAX_SECS_TRYING_TO_CONNECT)
            _conn.connect((host, port))
            print('Socket got created!')
            # Main thread closed before socket connected handling
            _is_main_thread_alive = threading.main_thread().is_alive()
            open = None
            if not _is_main_thread_alive:
                send_close_socket_msg()
                open = False
            else:
                open = True
                # Remove timeout
                _conn.settimeout(None)
                # Update connection status from main thread
                view_handler.set_conn_text('Connected')
            # Listen for server msgs
            while open:
                server_msg = None
                try:
                    server_msg = _conn.recv(1024).decode(_UTF_8)
                    if server_msg == _CLOSE_CONN:
                        print('Server received the close socket message and sents it back to close the listen thread') 
                        open = False
                    elif server_msg.__contains__(SYNC_BC) or server_msg.__contains__(_MANUAL_SYNC):
                        if server_msg != _MANUAL_SYNC_END:
                            if server_msg.__contains__(SYNC_BC):
                                print(f'Broadcast sync msg received from server: {server_msg}')
                            else:
                                print(f'Manual sync msg received from server: {server_msg}')
                            msg_parts = json.loads(server_msg)
                            # Remove sync keyword from msg
                            msg_parts.pop(0)
                            operation = msg_parts.pop(0)
                            enc_acc_details = msg_parts
                            # Call sync from main thread
                            # If main thread has been closed, signal emitting will be skipped (no error) 
                            sync_instance.sync_msg_received.emit(operation, enc_acc_details)
                        # Server manual sync end signal
                        else:
                            print('Manual sync process completed successfully!')
                            # If main thread has been closed, signal emitting will be skipped (no error) 
                            sync_instance.manual_sync_completed.emit()
                    else:
                        print(f'Server says {server_msg}')
                except Exception as e:
                    open = False
                    print(f'Failed to receive msg from server. Exception {e}')
            # Close connection from client side
            _conn.close()
            _conn = None
            print('Connection closed from client side')
        except Exception as e:
            print(f'Failed to connect. Exception: {e}')
        finally:
            # Update connection status from main thread
            # If main thread has been closed, signal emitting will be skipped (no error) 
            view_handler.set_conn_text('Not connected')
            # Update manual sync in progress status
            sync_instance.set_manual_sync_in_progress(False)
    conn_thread = Thread(target=listen)
    conn_thread.start()

def is_connected():
    return _conn != None

def _send_msg(msg_text):
    try:
        msg = msg_text.encode(_UTF_8) 
        _conn.send(msg)
        return True
    except:
        return False

def send_manual_sync_msg():
    def send_all_accs():
        # No server connection or already started manual sync
        if not _conn or sync_instance.manual_sync_in_progress:
            if not _conn:
                print('Failed to start manual sync process')
                view_handler.show_info_msg_box(title='Cannot Sync', conn_error=True)
            else:
                print('A manual sync is already in progress')
                view_handler.show_info_msg_box(title='Cannot Sync', details='Another sync is already in progress')
            return
        # Update manual sync in progress status
        sync_instance.set_manual_sync_in_progress(True)
        # Send all accounts of this device to server
        enc_accs = xml_handler.get_accs(decrypt=False)
        for enc_acc in enc_accs:
            enc_acc.insert(0, _MANUAL_SYNC)
            # Convert list to json string
            enc_acc_json_string = cryptor.convert_to_json_string(enc_acc)
            ok = _send_msg(enc_acc_json_string)
            if not ok:
                print('Manual sync process failed. Connection with server got lost')
                break
            # Sleep for 100 ms
            sleep(.1)
        # Client part completed successfully
        else:
            # Signal end of client part
            ok = _send_msg(_MANUAL_SYNC_END)
            if not ok:
                print('Failed to send manual sync end signal to server. Connection with server got lost')
    manual_sync_thread = Thread(target=send_all_accs)
    manual_sync_thread.start()
    
def send_sync_broadcast_msg(msg):
    ok = _send_msg(msg)
    if ok:
        print('Sent sync broadcast message to server')
    else:
        print('Failed to send sync broadcast msg to server')
    return ok

def send_close_socket_msg():
    ok = _send_msg(_CLOSE_CONN)
    if ok:
        print('Sent close signal to server')
    else:
        print('Failed to send close signal to server')
