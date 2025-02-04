import os.path
import sys
from socket import *
import threading
import queue
import pickle
import random



def sendAck( ackNo, sock, end ):
    rand = random.randint(0,9)
    if rand > 1:
        toSend = (ackNo,)
        msg = pickle.dumps( toSend)
        sock.sendto( msg, end)

def rx_thread( s, sender, que, bSize, filesize):
    expectedBlockNo = 1
    noBytesRecv = 0
    while True:
        if expectedBlockNo * bSize > filesize + bSize:
            break
        buf, _ = s.recvfrom(bSize + 128)
        block = pickle.loads(buf)
        blockNo, data = block

        if blockNo == expectedBlockNo:
            que.put(data)
            noBytesRecv += len(data)
            sendAck(blockNo, s, sender)
            expectedBlockNo += 1
        else:
            sendAck(expectedBlockNo - 1, s, sender)
    while True:
        res, _ = s.recvfrom(256)
        result = pickle.loads(res)
        msg, msg_len = result
        if msg == "All ack":
            break
        else:
            sendAck(expectedBlockNo, s, sender)     

def receiveNextBlock( q ):
    return q.get()

def main(sIP, sPort, fNameRemote, fNameLocal, chunkSize):

    s = socket( AF_INET, SOCK_DGRAM)
    #interact with sender without losses
    request = (fNameRemote, chunkSize)
    req = pickle.dumps(request)
    sender = (sIP, sPort)
    print("sending request")
    s.sendto( req, sender)
    print("waiting for reply")
    rep, ad = s.recvfrom(128)
    reply = pickle.loads(rep)
    print(f"Received reply: code = {reply[0]} fileSize = {reply[1]}")
    if reply[0]!=0:
        print(f'file {fNameRemote} does not exist in sender')
        sys.exit(1)
    #start transfer with data and ack losses
    fileSize = reply[1]
    if os.path.exists(fNameLocal):
        print("File already exists")
        rep = "quit"
        reply = pickle.dumps(rep)
        s.sendto(reply, sender)
        s.close()
        sys.exit(1)
    else:
        rep = "continue"
        reply = pickle.dumps(rep)
        s.sendto(reply,sender)

    q = queue.Queue( )
    tid = threading.Thread( target=rx_thread, args=(s, sender, q, chunkSize, fileSize))
    tid.start()
    # falta testar se existe o ficheiro local
    f = open( fNameLocal, 'wb')
    noBytesRcv = 0
    while noBytesRcv < fileSize:
        print(f'Going to receive; noByteRcv={noBytesRcv}')
        b = receiveNextBlock( q )
        sizeOfBlockReceived = len(b)
        if sizeOfBlockReceived > 0:
            f.write(b)
            noBytesRcv += sizeOfBlockReceived
    print("File has been fully received")
    f.close()
    tid.join()
    s.close()
       

if __name__ == "__main__":
    # python receiver.py senderIP senderPort fileNameInSender fileNameInReceiver chunkSize
    if len(sys.argv) != 6:
        print("Usage: python receiver.py senderIP senderPort fileNameRemote fileNameLocal chunkSize")
        sys.exit(1)
    senderIP = sys.argv[1]
    senderPort = int(sys.argv[2])
    fileNameRemote = sys.argv[3]
    fileNameLocal = sys.argv[4]
    chunkSize = int(sys.argv[5])
    main( senderIP, senderPort, fileNameRemote, fileNameLocal, chunkSize)
    
