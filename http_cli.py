import socket
import os
import sys


#vars
path = "/"
DEFAULT_PORT_Min =10560
DEFAULT_PORT_Max =10579

#create SOCKET
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error as e:
    print('Failed to create socket. Error: ' + str(e[0]), file=sys.stderr)
    sys.exit(1)
if(len(sys.argv) != 2):
    print('Invalid Number of Arguements', file=sys.stderr)
    sys.exit(1)

#get argument
args = str(sys.argv[1])

#PARSE STRING INTO COMPONENTS(HOST,PORT,PATH)

parse_arr= []
if(args.count('http://') > 0):
    parse_arr = args.split('://', 1)
    addr_arr= parse_arr[1]
else:
    addr_arr = args

urlinfo = addr_arr.split('/',1)
# print('url'+ str(urlinfo))
#HOSTNAME
hostname = urlinfo[0]
port = 10650 #default port now
if(hostname.count(':') > 0):
    has_port = hostname.split((':'), 1)
    port = int(has_port[1])
    if (int(port < DEFAULT_PORT_Min or port > DEFAULT_PORT_Max)):
        print('Port Number is Invalid', file=sys.stderr)
        sys.exit(1)
    hostname = has_port[0]

#PATH default: empty path
if(len(urlinfo) > 1):
    path = '/'+ urlinfo[1]

#GET HOST INFO
try:
    host = socket.getaddrinfo(hostname,port,socket.AF_INET, socket.SOCK_STREAM)
except os.error as e:
    print('Error: '+ str(e[0]) +'Could not find IP Address:'+ hostname+ ':' + str(port),file=sys.stderr)
    sys.exit(1)

#IPv4
IP = (host[0][4][0])
# print(IP)
#CONNECT
try:
    s.connect((IP,port))
except:
    print('Could not establish connection to server' , file=sys.stderr)
    sys.exit(1)

#FUNCTIONS
def getContentLength(header):
    if(header.count(b'Content-Length: ') > 0):
        parse1 = headers.split(b'Content-Length: ')
        parse2 = parse1[1].split(b'\r\n', 1)
        ret = content_len = parse2[0]
        return ret
    else:
        print('Cannot find content length', file=sys.stderr)
        sys.exit(1)

def checksumFunc(length_content, length_body):
    if (int(length_content) != int(length_body)):
        print('Not all body:bytes received, Content Bytes: ' + str(length_body), file=sys.stderr)
        sys.exit(1)
        return False
    else:
        return True

#CHECKSUM FUNCTION
def messageHandler(buffer, headers):
    if len(buffer) > 1:
        sizeofHeaders = str(len(headers))
        bodymsg = buffer[1]
        body_len = len(bodymsg)
        content_len = getContentLength(headers)
        checkSum = checksumFunc(content_len,body_len)
        print(headers.decode('UTF-8'), file=sys.stderr)
        #WRITE OUT
        try:
            bf = sys.stdout.buffer.write(bodymsg)
        except BufferError as error:
            print('Could not write file', file=sys.stderr)
            sys.exit(1)
    else:
        # IF not redirect just print headers
        print(headers.decode('UTF-8'), file=sys.stderr)
#SEND MESSAGE
def sendMsg(message):
    msg = message.encode('UTF-8')
    totalsent = 0
    while totalsent < len(msg):
        sent = s.send(msg[totalsent:])
        if sent == 0:
            raise RuntimeError("socket connection broken")
        totalsent = totalsent + sent

def createMsg(host, path):
    message = 'GET ' + path + ' HTTP/1.1\r\n'
    message += 'Host: ' + hostname + '\r\n'
    message += 'Connection: close \r\n'
    message += '\r\n\r\n'
    return message
    # print(message, file=sys.stderr)

#RECEIVE DATA
def receiveResponse():
    buffer = b''
    while True:
        data = s.recv(1024)
        if not data:
            break
        buffer += data
        if buffer == b'':
            print('Empty Buffer, not getting data', file=sys.stderr)
            raise RuntimeError('SOCKET BROKEN')
    return buffer

def getHeaders(buffer):
    bf= buffer.split(b'\r\n\r\n\r\n')
    headers = bf[0]
    return headers

#MAIN
message = createMsg(hostname, path)
#SEND MESSAGES
sendMsg(message)
msgBuffer = receiveResponse()
headers = getHeaders(msgBuffer)
body= b''
buffer_list= msgBuffer.split(b'\r\n\r\n\r\n')
#Checksum
messageHandler(buffer_list, headers)
#Closes
s.close()


