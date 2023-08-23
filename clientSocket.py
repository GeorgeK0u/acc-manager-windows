# Web scraping
import requests
import socket
from threading import Thread, Lock
from time import sleep 
# My files
import xmlHandler
import encoder

conn = None
UTF8 = 'utf-8'
MANUAL_SYNC = 'manual_sync'
MANUAL_SYNC_CLIENT_END = 'manual_sync_client_end'
SYNC_BC = 'sync_broadcast'
CLOSE_CONN = 'close_conn'

def CreateConn():
    def Listen():
        try:
            Lock().acquire
            serverLocalIP = '192.168.2.7'
            publicIP = ''
            try:
                publicIP = requests.get('https://api.ipify.org').text
            except:
                print('Failed to get public IP address')
                return
            homePublicIP = socket.gethostbyname('my-ddns.ddns.net')
            insideConn = publicIP == homePublicIP
            host = ''
            if insideConn:
                host = serverLocalIP
            else:
                host = homePublicIP
            port = 56789
            global conn
            conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            conn.connect((host, port))
            print('Socket got created!')
            # Listen for server msgs
            open = True
            while open:
                try:
                    serverMsg = conn.recv(1024).decode(UTF8)
                    if serverMsg == CLOSE_CONN:
                        print('Server received the close socket message and sents it back to close the listen thread') 
                        open = False
                    elif serverMsg.__contains__(SYNC_BC) or serverMsg.__contains__(MANUAL_SYNC):
                        if serverMsg.__contains__(SYNC_BC):
                            print('Sync message received from server broadcast')
                        else:
                            # print('Manual sync message received from server')
                            print(f'Manual sync msg received from server: {serverMsg}')
                        MsgParts = serverMsg.split(', ')
                        # Remove sync keyword from msg
                        MsgParts.pop(0)
                        operation = MsgParts.pop(0)
                        EncAccDetails = MsgParts
                        Sync(operation, EncAccDetails)
                    else:
                        print(f'Server says {serverMsg}')
                except Exception as e:
                    open = False
                    print(f'Failed to receive msg from server. Exception: {e}')
            # Close connection from client side
            conn.close()
            conn = None
            print('Connection closed from client side')
        except Exception as e:
            conn = None
            print(f'Failed to connect. Exception: {e}')
    ConnThread = Thread(target=Listen)
    ConnThread.start()

def SendMsg(msgStr):
    if not conn:
        return
    try:
        msg = msgStr.encode(UTF8) 
        conn.send(msg)
    except:
        print('Failed to send msg to server')

def SendManualSyncMsg():
    if not conn:
        print('Failed to connect to server to perform manual sync')
        return
    def SendManualSyncMsgs():
        try:
            # Send all accs to the server 
            # and wait for either a keep or delete response
            EncAccs = xmlHandler.GetAccs(decrypt=False)
            for i in range(len(EncAccs)):
                EncAcc = EncAccs[i]
                msg = f'{MANUAL_SYNC}, {", ".join(EncAcc)}'
                SendMsg(msg)
                print(f'Sent manual sync msg to server: {msg}')
                Acc = []
                for field in EncAcc: 
                    decField = encoder.Decrypt(field)
                    Acc.append(decField)
                decMsg = f'{MANUAL_SYNC}, {", ".join(Acc)}'
                print(f'Decrypted => Sent manual sync msg to server: {decMsg}')
                sleep(.1)
            msg = MANUAL_SYNC_CLIENT_END
            SendMsg(msg)
            print('Signalled the client end on manual sync to start the server manual sync part')
        except Exception as e:
            print(f'Failed to send all accs for manual sync. Exception: {e}')
    SendManualSyncMsgsThread = Thread(target=SendManualSyncMsgs)
    SendManualSyncMsgsThread.start()

def SendSyncBroadcastMsg(msg):
    SendMsg(msg)
    print('Sent sync broadcast message to server')

def Sync(op, EncAccDetails):
    # Create acc
    if op == 'C':
        print('Create operation type sync message received')
        xmlHandler.SaveAcc(EncAccDetails)
    # Rename acc detail
    elif op == 'U':
        print('Update operation type sync message received')
        accName = encoder.Decrypt(EncAccDetails[0])
        colIndex = encoder.Decrypt(EncAccDetails[1])
        nValue = encoder.Decrypt(EncAccDetails[2])
        xmlHandler.ChangeAccValue(accName, colIndex, nValue)
    # Delete acc
    elif op == 'D':
        print('Delete operation type sync message received')
        accName = encoder.Decrypt(EncAccDetails[0])  
        xmlHandler.DeleteAcc(accName)

def SendCloseSocketMsg():
    SendMsg(CLOSE_CONN)
