import sys
import os
from socket import *
import threading
import pickle
import random
import select

blocksInWindow = 0
window = []

def sendDatagram(blockNo, contents, sock, end):
    rand = random.randint(0, 9)
    if rand > 1:
        toSend = (blockNo, contents)
        msg = pickle.dumps(toSend)
        sock.sendto(msg, end)
        
def waitForAck(s, seg):
    rx, tx, er = select.select([s], [], [], seg)
    return rx != []

def tx_thread(s, receiver, windowSize, cond, timeout, is_over):
    global blocksInWindow, window

    max_retries = 10
    current_retries = 0
    while not is_over.is_set():
        with cond:
            while blocksInWindow == 0 and not is_over.is_set():
                cond.wait()
            if blocksInWindow > 0:
                if waitForAck(s, timeout):
                    current_retries = 0
                    ack_msg, _ = s.recvfrom(128)
                    ack = pickle.loads(ack_msg)
                    ack_no = ack[0]

                    while window and window[0][0] <= ack_no:
                        print(f"Block {window[0][0]} acknowledged.")
                        window.pop(0)
                        blocksInWindow -= 1

                    cond.notify_all()
                else:
                    current_retries +=1
                    for seqNo, blockData in window:
                        sendDatagram(seqNo, blockData, s, receiver)
                    cond.notify_all()
                if current_retries == max_retries:
                    print("Max retries")
                    m = "Resend ack"
                    msg = (m, len(m))
                    message = pickle.dumps(msg)
                    s.sendto(message, receiver)

def sendBlock(seqNo, fileBytes, s, receiver, windowSize, cond):
    global blocksInWindow, window
    with cond:
        while blocksInWindow >= windowSize:
            cond.wait()

        window.append((seqNo, fileBytes))
        blocksInWindow += 1
        sendDatagram(seqNo, fileBytes, s, receiver)
        cond.notify_all()

def main(hostname, senderPort, windowSize, timeOutInSec):
    s = socket(AF_INET, SOCK_DGRAM)
    s.bind((hostname, senderPort))
    
    # Interaction with receiver; no datagram loss
    buf, rem = s.recvfrom(256)
    req = pickle.loads(buf)
    fileName = req[0]
    blockSize = req[1]
    result = os.path.exists(fileName)
    
    if not result:
        print(f'File {fileName} does not exist in server')
        reply = (-1, 0)
        rep = pickle.dumps(reply)
        s.sendto(rep, rem)
        sys.exit(1)
    
    fileSize = os.path.getsize(fileName)
    reply = (0, fileSize)
    rep = pickle.dumps(reply)
    s.sendto(rep, rem)
    res , ad = s.recvfrom(256)
    result = pickle.loads(res)
    if result == "quit":
        print("File already exists in receiver")
        s.close()
        sys.exit(1)

    # File transfer; datagram loss possible
    windowCond = threading.Condition()
    is_over = threading.Event()
    tid = threading.Thread(target=tx_thread, args=(s, rem, windowSize, windowCond, timeOutInSec, is_over))
    tid.start()
    
    f = open(fileName, 'rb')
    blockNo = 1

    while True:
        b = f.read(blockSize)
        sizeOfBlockRead = len(b)
        if sizeOfBlockRead > 0:
            sendBlock(blockNo, b, s, rem, windowSize, windowCond)
        if sizeOfBlockRead == blockSize:
            blockNo += 1
        else:
            break

    with windowCond:
        while blocksInWindow > 0:
            windowCond.wait()
        is_over.set()
        windowCond.notify_all()
    m = "All ack"
    msg = (m, len(m))
    message = pickle.dumps(msg)
    s.sendto(message, ad)
    print("File has been fully sent")
    f.close()
    tid.join()
    s.close()

if __name__ == "__main__":
    # python sender.py senderPort windowSize timeOutInSec
    if len(sys.argv) != 4:
        print("Usage: python sender.py senderPort windowSize timeOutInSec")
    else:
        senderPort = int(sys.argv[1])
        windowSize = int(sys.argv[2])
        timeOutInSec = int(sys.argv[3])
        hostname = gethostbyname(gethostname())
        main(hostname, senderPort, windowSize, timeOutInSec)

