"""
Created on Tue Apr 23 22:38:43 2019

@author: z5184936
"""

from socket import *
import sys
import time
import threading
import random

def form(event,time,seq,size,ack):
    return '%-30s %-30.3f %-20s %-20s %-s\n' % (event, time, seq, size, ack)



class CDHT():
    def __init__(self,peer,suc1,suc2,mss,dp,now):
       
        self.peer = peer
        self.suc1 = suc1
        self.suc2 = suc2
        self.mss = mss
        self.dp = dp
        self.now = now
        
        self.running = True
        
        self.pre1 = None
        self.pre2 = None
        
        self.base_port = 50000
        
        self.suc1ack = 0
        self.suc2ack = 0
        
   
    def tcp_client(self,data,port):#send_message to port
        addr = ('',port +
                self.base_port)
        client = socket(AF_INET, SOCK_STREAM)
        client.connect(addr)
        client.send(data)
        client.close()
        
    def udp_client(self,data,port):#send_message to port
        addr = ('',port + self.base_port)
        client = socket(AF_INET, SOCK_DGRAM)
        client.sendto(data,addr)
        client.close()
        
    def tcp_server(self): #port is self.peer
        addr = ('',self.peer + self.base_port)
        server = socket(AF_INET, SOCK_STREAM)
        server.bind(addr)
        server.listen(10)
        while self.running:
            conn,addr = server.accept()
            data = conn.recv(2048)
            self.tcp_receive(data,self.peer)
        server.close()
        
    def udp_server(self): #self.peer
        addr = ('',self.peer + self.base_port)
        server = socket(AF_INET, SOCK_DGRAM)
        server.bind(addr)
        while self.running:
            data,addr = server.recvfrom(2048)
            self.udp_receive(data,self.peer) 
        server.close()
        
    def ping_server(self):
        seq = 1
        while self.running:
            data1 = 'Ping1 '+ str(self.peer) + ' '+str(seq) #eg: ping1 1 0
            msg1 = data1.encode()
            data2 = 'Ping2 '+ str(self.peer) + ' '+str(seq) #eg: ping1 1 0
            msg2 = data2.encode()
            self.udp_client(msg1,self.suc1)
            self.udp_client(msg2,self.suc2)
            seq += 1
            time.sleep(10)
            

        '''
        send format (query) (peer) (message)
        
        receive format 
        '''
    def udp_receive(self,msg,p):
        message = msg.decode().split(' ')
        query = message[0]
        from_peer = int(message[1])
        seq = int(message[2])
        dead1 = False
        dead2 = False
        if query =='Ping1':
            print(f'A ping request message was received from Peer {from_peer}.')
            self.pre1 = from_peer
            data1 = 'Response ' + str(self.peer) + ' '+str(seq)
            data1 = data1.encode()
            self.udp_client(data1,from_peer)
        elif query == 'Ping2':
            print(f'A ping request message was received from Peer {from_peer}.')
            self.pre2 = from_peer
            data2 = 'Response ' + str(self.peer) + ' '+str(seq)
            data2 = data2.encode()
            self.udp_client(data2,from_peer)
        if query == 'Response': #suppose only one peer left at a time
            print(f'A ping response message was received from Peer {from_peer}.')            
            if from_peer == self.suc1 and seq > self.suc1ack:
                self.suc1ack = seq
                if self.suc1ack - self.suc2ack >= 4 and self.suc2ack > 0:
                    dead2 = True
            elif from_peer == self.suc2 and seq > self.suc2ack:
                self.suc2ack = seq
                if self.suc2ack - self.suc1ack >= 4 and self.suc1ack > 0:
                    dead1 = True
            if dead1:
                print(f'Peer {self.suc1} is no longer alive.')
                data = 'Update '+ str(self.peer) + ' ' + str(self.suc1)
                data = data.encode()
                self.tcp_client(data,self.suc2)
            if dead2:
                print(f'Peer {self.suc2} is no longer alive.')
                data = 'Update '+ str(self.peer) + ' ' + str(self.suc2)
                data = data.encode()
                self.tcp_client(data,self.suc1)

            
    def tcp_receive(self,msg,peer): #
        message = msg.decode().split(' ')
        query = message[0]
        from_peer = int(message[1])
        detail = int(message[2])
        if query == 'Update':
            if self.suc1 == int(detail):
                data = 'Next ' + str(self.peer) + ' ' + str(self.suc2)
            else:
                data = 'Next ' + str(self.peer) + ' ' + str(self.suc1)
            data = data.encode()
            self.tcp_client(data,from_peer)
            return
        if query == 'Next':
            if from_peer != self.suc1:
                self.suc1 = from_peer
            self.suc2 = detail
            print(f'My first successor is now peer {self.suc1}.')
            print(f'My second successor is now peer {self.suc2}.')
            return
        if len(message) == 4:
            query = message[0]
            leave_peer = int(message[1])
            l_next = int(message[2])
            l_after =int(message[3])
            if query == 'quit':
                print(f'Peer {leave_peer} will depart from the network.')
                if self.suc1 == int(leave_peer):
                    self.suc1 = l_next
                    self.suc2 = l_after
                else:
                    self.suc2 = l_next
                print(f'My first successor is now peer {self.suc1}.')
                print(f'My second successor is now peer {self.suc2}.')
                return
        if query == 'request':
            from_peer = int(message[1])
            filename = int(message[2])
            if self.file_position(filename,self.pre1,self.peer):
                print(f'File {filename} is here.')
                print(f'A response message, destined for peer {from_peer}, has been sent.')
                data = 'find '+ str(self.peer) + ' '+ str(filename)
                data = data.encode()
                self.tcp_client(data,from_peer)               
            else:
                print(f'File {filename} is not stored here.')
                print(f'File request message has been forwarded to my successor.')
                self.tcp_client(msg,self.suc1)
            return
        if query == 'find':
            from_peer = int(message[1])
            filename = int(message[2])
            print(f'Received a response message from peer {from_peer}, which has the file {filename}.')
            return
        
    def file_position(self,filename,p,suc1):
        file_hash = int(filename)%256
        if file_hash == p:
            return True
        elif p > suc1 > file_hash:
            return True
        elif file_hash > p > suc1:
            return True
        elif p < file_hash < suc1:
            return True
        else:
            return False


if __name__ == "__main__":
    
    peer = int(sys.argv[1])
    suc1 = int(sys.argv[2])
    suc2 = int(sys.argv[3])
    mss = int(sys.argv[4])
    dp = float(sys.argv[5])
    now = time.time()
    p = CDHT(peer,suc1,suc2,mss,dp,now)
    t1 = threading.Thread(target = p.udp_server)
    t2 = threading.Thread(target = p.tcp_server)
    t3 = threading.Thread(target = p.ping_server)

    t1.start()
    t2.start()
    t3.start()

    while p.running:
        cmd = input()

        if cmd == 'quit':
            p.running = False
            data = 'quit ' + str(p.peer) + ' ' +str(p.suc1) + ' ' +str(p.suc2)
            data = data.encode()
            p.tcp_client(data,p.pre1)
            p.tcp_client(data,p.pre2)
            quit()
        
        else:
            c = cmd.split(' ')
            if c[0] =='request' and len(c) == 2:
                filename = c[1]
                if not filename.isdigit():
                    print('Incorrect filename.')
                    break
                filename = int(c[1])
                print(f'File request message for {filename} has been sent to my successor.')
                data = 'request ' + str(p.peer) + ' ' + str(filename)
                data = data.encode()
                p.tcp_client(data,p.suc1) #request file and send to successor

