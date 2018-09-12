import socket, json, time
import threading
import socketserver
import logging
'''
request, time = {
"request_type" : <"fileTransfer"/"command"/"ping">,
"request_data" : <"filename"/command"/ping"> # (valid file name, os command, ping [keyword])
}
'''
class Client(object):
    def __init__(self,targetHost, targetPort):
        self.targetHost = targetHost
        self.targetPort = targetPort
        self.bytesSize = 1024
        logging.basicConfig(level=logging.DEBUG,format='%(name)s: %(message)s',)

        #ip,port='127.0.0.1',8800

        logger = logging.getLogger('client')
        logger.info('Server on {}:{}'.format(ip, port))
        # Connect to the server
        logger.debug('creating socket')
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        logger.debug('connecting to server')
        self.server.connect((ip, port))

    def sendFile(self,fileNameWPath):
        # will send a communication as file need to be sent
        message = {'request_type' : 'file_transfer', {'fileName' : fileNameWPath, 'destPath' : '/tmp'}
        self.server.send(message)

        # lets wait for .1 second before start sending file
        time.sleep(.1)
        with open(self.fileNameWPath, 'rb') as file:
            data = file.read(self.bytesSize)
            self.server.send(data)

        self.server.shutdown(socket.SHUT_WR)
        myResponse = self.__getResponse()

        return myResponse

    def __getResponse(self):
        data = self.server.recv(self.bytesSize)
        while (data):
            response = response + data
            data = self.server.recv(self.bytesSize)

        return response

    def seldAllFiles(self,filePath, filePattern):
        if not os.path.isdir(filePath):
            logger.error('Invalid path {}'.format(filePath))
            return self.error
        
        allFiles = glob.glob(os.path.join(filePath,filePattern)

        if len(allFiles) == 0:
            logger.info('There are no matching files for [{filePathPattern}]'.format(filePathPattern = os.path.join(filePath, filePattern)))

        for file in allFiles:
            myResponse = sendFile(file)
            print(myResponse)

    # Send the data
message = {
"request_type" : "file_transfer",
"request_data" : "Screenshot.png"
}

logger.debug('sending data: "%s"', message)
if isinstance(message,dict):
    len_sent = s.send(json.dumps(message).encode('utf-8'))
    print('bytes sent {}'.format(len_sent))

#s.shutdown(socket.SHUT_WR)
time.sleep(.1)
if message['request_type'] == 'file_transfer':

    f = open(message['request_data'],'rb')
    l = f.read(1024)
    while (l):
        print('sending bytes: {}'.format(len(l)))
        s.send(l)
        l = f.read(1024)
    f.close()

# Receive a response
#s.sendall(byte(''))
#time.sleep(1)
s.shutdown(socket.SHUT_WR) # this is needed to shutdown the write and wait for receive
logger.debug('waiting for response')
response = s.recv(1024)
logger.debug('response from server: "%s"', response)

# Clean up

logger.debug('closing socket')
#s.shutdown(socket.SHUT_RD)
s.close()
logger.debug('done')
#s.close()