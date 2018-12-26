import socket
import os
import os.path
import sys
import datetime
import mimetypes


#VARS
host = ''
port = 10560
DEFAULT_PORT_Min =10560
DEFAULT_PORT_Max =10579
addr= []
#filereq = ''

#check args
if(len(sys.argv) != 2):
    print('Invalid Number of Arguements', file=sys.stderr)
    sys.exit(1)

# check port
port = int(sys.argv[1])

if(int(port < DEFAULT_PORT_Min or port > DEFAULT_PORT_Max )):
    print('Port Number is Invalid', file=sys.stderr)
    sys.exit(1)

#SETUP HOST AND PORTS
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error as e:
    print('Failed to create socket. Error: ' + str(e[0]), file=sys.stderr)
    sys.exit(1)

#HOST INFO - append local ip to host
gethostname= socket.gethostname()
print(gethostname)
# host = socket.gethostbyname(gethostna
host = socket.gethostbyname('')
#BINDING
try:
    s.bind((host,port))
except socket.error as e:
    print('Bind failed. Error: ' + str(e), file=sys.stderr)
    sys.exit(1)

#METHODS
def isGetMSG(msg):
    GETmsg = b'GET'
    if(GETmsg in msg): #has a get
        return True
    else:
        return False

#checks to see if file exists
def hasFile(dir):
    if(os.path.isfile(dir) == True):
        return True
    else:
        return False

#splits message info
def splitMessage(msg):
    split_list = msg.split(b'\r\n')
    return split_list

#check path of file req
def get_path(path):
    temp = path.decode('UTF-8')
    parse1 =  temp.split('GET')
    parse2 = parse1[1].split(' HTTP/1.1') #Watch for spacing
    parse3 = parse2[0].split('/',1)
    path_parse = str(parse3[1])
    print('Path: '+path_parse,file=sys.stderr)
    return path_parse

#check mod time
def lastModified(path):
    file_path = path
    lastmod = os.stat(file_path).st_mtime
    return str(lastmod)

#Returns files size
def getFileSize(body):
    size = str(len(body))
    ret = str(size)
    return ret
def getConnectionType(header):
    if(header.count(b'Connection: ') > 0):
        parse1 = header.split(b'Connection: ')
        parse2 = parse1[1].split(b'\r\n', 1)
        ret = connection_type = parse2[0].decode('UTF-8')
        return ret
    else:
        print('Cannot find Connection', file=sys.stderr)
        sys.exit(1)


#send message and file
def sendMsgandFile(cli_socket, res, body):
    sendRes = res
    responseMsg = sendRes.encode('UTF-8')
    sizeofheader= len(responseMsg)
    responseMsg += body
    # print(str(sys.getsizeof(body))+ ' is the size of body')
    #print(responseMsg)
    totalsent = 0
    while totalsent < len(responseMsg):
        sent = cli_socket.send(responseMsg[totalsent:])
        if sent == 0:
            raise RuntimeError("socket connection broken")
        totalsent = totalsent + sent
    # print(str(totalsent) + ' - ' + str(sizeofheader) +' = ' + str(totalsent-sizeofheader))
def getBody(path):
    fileReq = open(path, 'rb')
    body = fileReq.read()
    ret = body
    fileReq.close()
    return ret
#filehandler
def sendMsg(cli_socket, res):
    sendRes = res.encode('UTF-8')
    totalsent = 0
    while totalsent < len(sendRes):
        sent = cli_socket.send(sendRes[totalsent:])
        if sent == 0:
            raise RuntimeError("socket connection broken")
        totalsent = totalsent + sent

def getMimeType(path):
    mime_type= mimetypes.guess_type(path)
    ret = str(mime_type[0])
    return ret

def getDate():
    ret= str(datetime.datetime.now())
    return ret
#LISTEN
s.listen(5)

print('Listening on Host:'+ host + ' Port: '+ str(port) )

buffer = b''
while True:
    conn, addr = s.accept()
    print(('Connected to ' + addr[0] + ':' + str(addr[1])))
    data = conn.recv(1024)
    if not data:
        break
    buffer += data
    if buffer == b'':
        raise RuntimeError('SOCKET BROKEN')
    print(data, file=sys.stderr)
    msg = splitMessage(data)
    #print(msg,file=sys.stderr)
    response = ''
    #IS a Get msg
    if(isGetMSG(data) == True):
        # print('IS a Get msg', file=sys.stderr)
        #Has File
        path = get_path(msg[0])
        if hasFile(path):
            msgbody = getBody(path)
            response = '200 OK ' + '\r\n'
            response += 'Connection: close \r\n' #fix to be close as well
            response += 'Date: ' + getDate() + '\r\n'
            response += 'Last-Modified: ' + lastModified(path) + '\r\n'
            response += 'Content-Length: ' + getFileSize(msgbody) + '\r\n'
            response += 'Content-Type: ' + getMimeType(path) + '\r\n'
            response += '\r\n\r\n'
            print(response, file=sys.stderr)
            # sendmsg plus file
            sendMsgandFile(conn, response, msgbody)
        #Doesn't have file, send error
        else:
            print('Can not find file ', file=sys.stderr)
            response = '404 Not Found'
            sendMsg(conn,response)

    else:
        print('NOT IMPLEMENT', file=sys.stderr)
        response = '501 Not Implemented'  # finish
        sendMsg(conn,response)
    buffer=b'' #clear buffer
    if(getConnectionType() == 'close'):
        conn.close()


s.close()


