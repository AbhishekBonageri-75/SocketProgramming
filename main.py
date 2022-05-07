import threading
from check import *
from write import *
from socket import *
import asyncio
import sys
import struct
import time

ICMP_ECHO_REQUEST = 8
ICMP_ECHO_REPLY = 0
flag = 0
# Uncomment the domain which you desire to target
target_hostname = "localhost"
# target_hostname = "www.bing.com"
# target_hostname = "1.1.255.155"


# Function to build the string upto 256 char length as per the requirement of the project.
# If a user input is shorter than 256 chars in length, we will append it with '#'.
# If a user input exceeds 256 chars in length, we will truncate it to 256 chars.
def buildStr(initialStr):
    str = initialStr
    ch = '#'
    while (sys.getsizeof(str) != 256):
        str = str + ch
    return str


# The sender_ICMP function creates an IP header and the data and sends it to the server using type 8 ICMP echo request.
async def sender_ICMP(mySocket, destAddr, id=0, seq=0):
    # Header is type (8), code (8), id(16), seq(16), checksum (16)
    time.sleep(1)
    # Initially set checksum to 0.
    myChecksum = 0
    header = struct.pack("bbHHH", ICMP_ECHO_REQUEST, 0, myChecksum, id, seq)
    print("Enter the data to be sent")
    str_to_send = input()
    timestamp = time.time()
    data = struct.pack("d248s", timestamp, str_to_send.encode())
    # We calculate a checksum on the data and the dummy header with initial checksum set to 0
    myChecksum = checksum(header + data)

    # Modify the checksum as per htons requirement.
    # The 16-bit integers from host must be converted to network byte order.
    if sys.platform != 'darwin':
        myChecksum = htons(myChecksum)
    else:
        myChecksum = htons(myChecksum) & 0xffff

    header = struct.pack("bbHHH", ICMP_ECHO_REQUEST, 0, myChecksum, id, seq)
    packet = header + data

    # Send ping requests to a server separated by creating two async threads
    await sender_Thread(mySocket, packet, destAddr)
    await sender_Thread(mySocket, packet, destAddr)
    print("Data Sent")


# Helper function to start sender thread in parallel.
async def sender_Thread(mySocket, packet, destAddr):
    await asyncio.sleep(0)
    ICMP_START_TIME = time.time()
    mySocket.sendto(packet, (destAddr, 0))


# The function starts a listener to the provided socket.
# If an ICMP REQUEST is received, it will modify the header and send a reply with a same data.
# If an ICMP REPLY is received, it will print the info to the terminal also write to the "myfile.txt"
def receiver_ICMP(mySocket, timeout=0):
    i = 0
    while i < 2:
        recPacket, addr = mySocket.recvfrom(1024)
        timeReceived = time.time()
        icmpHeader = recPacket[20:28]
        icmpType, code, mychecksum, recieved_id, recieved_seq_id = struct.unpack(
            "bbHHH", icmpHeader)
        # ICMP REPLY HANDLER
        if icmpType == 0:
            # 248+8=256
            timeSent = struct.unpack("d", recPacket[28:36])[0]
            data_str = struct.unpack("248s", recPacket[36:36 + 248])[0]
            data_str = data_str.decode()
            i = i + 1
            global flag
            flag = 1
            wdata("TimeTaken:" + str(timeReceived - timeSent) + "\nData:" + data_str +
                  "\n=========================================================================")
            print("Reply Received. Time Taken:" + str(timeReceived - timeSent))
        # ICMP REQUEST HANDLER
        if icmpType == 8:
            # 248+8=256
            timeSent = struct.unpack("d", recPacket[28:36])[0]
            data_str = struct.unpack("248s", recPacket[36:36 + 248])[0]
            data_str = data_str.decode()
            myChecksum = 0
            header = struct.pack("bbHHH", ICMP_ECHO_REPLY,
                                 0, myChecksum, recieved_id, recieved_seq_id)
            data = struct.pack("d248s", timeSent, data_str.encode())
            # We calculate a checksum on the data and the dummy header with initial checksum set to 0.
            myChecksum = checksum(header + data)

            # Modify the checksum as per htons requirement.
            # The 16-bit integers from host must be converted to network byte order.
            if sys.platform != 'darwin':
                myChecksum = htons(myChecksum)
            else:
                myChecksum = htons(myChecksum) & 0xffff

            header = struct.pack("bbHHH", ICMP_ECHO_REQUEST,
                                 0, myChecksum, recieved_id, recieved_seq_id)
            packet = header + data
            mySocket.sendto(packet, (addr, 0))

# Function to start the sender and receiver threads.
def ping():
    global target_hostname
    icmp = getprotobyname("icmp")
    # Create Socket variable mySocket here
    mySocket = socket(AF_INET, SOCK_RAW, icmp)

    destAddr = gethostbyname(target_hostname)
    print("Sending 2 ICMP message of Size 256 Bytes in data to " + target_hostname)

    asyncio.run(sender_ICMP(mySocket, destAddr))
    x = threading.Thread(target=receiver_ICMP, args=(mySocket, timeout))
    x.start()
    x.join(timeout=3)
    global flag
    if flag == 0:
        print("Ping Request Timed Out")
        return


f = 1
while f != 0:
    print("-----")
    print("1 - Ping \n")
    print("2 - Exit\n")
    i = input()
    if i == "1":
        ping()
    elif i == "2":
        f = 0
    else:
        print("Invalid Input")
