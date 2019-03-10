# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import sys
from socket import *
import time 
import datetime


list_rtts = []
packets_lost = 0

serverIP = str(sys.argv[1])
serverPort = int(sys.argv[2])
clientSocket = socket(AF_INET, SOCK_DGRAM)
addr = (serverIP,serverPort)
for i in range(10):
    timestamp = datetime.datetime.now().isoformat(sep = ' ')[:-7]
    pingmsg = 'PING' + str(i) + ' ' + str(timestamp) + '\r\n'
    starttime = time.time()
    clientSocket.sendto(pingmsg.encode(),addr)
    try:
        clientSocket.settimeout(1)
        modifiedSentence = clientSocket.recvfrom(1024)
        endtime = time.time()
        rtt = round((endtime - starttime)*1000)
        list_rtts.append(rtt)
        print(f"ping to {serverIP}, seq = {i}, rtt = {rtt} ms")
        clientSocket.settimeout(None)

    except timeout:
        # the client does not receive any reply from the server
        packets_lost += 1
        print(f'ping to {serverIP}, seq = {i}, rtt = time out')
print("\n")
print(f'Minimum RTT = {min(list_rtts)} ms')
print(f'Maximum RTT = {max(list_rtts)} ms')
print(f'Average RTT = {round(float(sum(list_rtts) / len(list_rtts)))} ms')
print(f'{float(packets_lost) / 10 * 100}% of packets have been lost through the network.')
clientSocket.close()
