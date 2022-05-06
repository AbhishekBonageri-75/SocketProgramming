import threading
from check import *
from write import *
from socket import *
import asyncio
import os
import sys
import struct
import time
import select
ICMP_ECHO_REQUEST = 8

def receiveOnePing(mySocket,timeout=0):
    i=0
    while i<2:
        recPacket, addr = mySocket.recvfrom(1024)
        # print(recPacket)
        timeReceived = time.time()
        icmpHeader = recPacket[20:24]
        icmpType, code, mychecksum = struct.unpack(
            "bbH", icmpHeader)

        if icmpType == 0:
            # 248+8=256
            timeSent = struct.unpack("d", recPacket[24:32])[0]
            data_str = struct.unpack("248s", recPacket[32:32 + 248])[0]
            data_str=data_str.decode()
            i=i+1
            wdata("TimeTaken:"+ str(timeReceived - timeSent)+"\nData:"+data_str+"\n=========================================================================")
            print("Reply Received. Time Taken:"+str(timeReceived - timeSent))
            # return

def buildStr(initialStr):
    str = initialStr
    ch = '#'
    while(sys.getsizeof(str)!= 256):
        str = str+ch
    return str


async def sendOnePing(mySocket, destAddr):
    # Header is type (8), code (8), checksum (16)
    time.sleep(1)
    myChecksum = 0
    # Make a dummy header with a 0 checksum.
    # struct -- Interpret strings as packed binary data
    header = struct.pack("bbH", ICMP_ECHO_REQUEST, 0, myChecksum)
    print("Enter the data to be sent")
    str_to_send=input()
    timestamp=time.time()
    data = struct.pack("d248s", timestamp,str_to_send.encode())
    # Calculate the checksum on the data and the dummy header.
    myChecksum = checksum(header + data)

    # Get the right checksum, and put in the header
    if sys.platform == 'darwin':
        myChecksum = htons(myChecksum) & 0xffff
    # Convert 16-bit integers from host to network byte order.
    else:
        myChecksum = htons(myChecksum)

    header = struct.pack("bbH", ICMP_ECHO_REQUEST, 0, myChecksum)
    packet = header + data
    # AF_INET address must be tuple, not str
    await fn(mySocket,packet, destAddr)
    await fn(mySocket, packet, destAddr)
    print("Data Sent")

async def fn(mySocket,packet , destAddr):
    await asyncio.sleep(0)
    mySocket.sendto(packet, (destAddr, 0))

def ping():
    icmp = getprotobyname("icmp")
    # Create Socket here
    mySocket = socket(AF_INET, SOCK_RAW, icmp)
    # Send ping requests to a server separated by approximately one second
    print("Enter the destination to ping. Press 1 to exit")
    # user_input_IP = input()
    user_input_IP = "localhost"
    if (user_input_IP == "1"):
        exit()

    destAddr = gethostbyname(user_input_IP)
    # mySocket.bind((destAddr,0))
    print("Sending 2 ICMP message of Size 256Bytes in data to "+user_input_IP)

    # receiveOnePing(mySocket, timeout)

    asyncio.run(sendOnePing(mySocket, destAddr))
    x = threading.Thread(target=receiveOnePing, args=(mySocket, timeout))
    x.start()



ping()
