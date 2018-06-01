import os, sys,socket, json, time
import threading
import socketserver

'''
request = {
    "request_type" : <"fileTransfer"/"command"/"ping">,
    "request_data" : <"filename"/command"/ping"> # (valid file name, os command, ping [keyword])
}
'''
class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):

    def handle(self):

        self.response = {"status":"","message":"","data":""}
        self.requestData = {}
        #self.requestData = {}
        self.BUFFER_SIZE=1024
        #data = str(self.request.recv(self.BUFFER_SIZE))
        data = self.request.recv(self.BUFFER_SIZE)
        print(data,type(data))
        try:
            self.requestData = json.loads(data.decode('utf-8'))
            print(self.requestData,type(self.requestData))

            cur_thread = threading.current_thread()
            myRequestType = self.requestData['request_type']
            #self.request.sendall(self.response.encode('utf-8'))

            if myRequestType == 'file_transfer':
                self.response['status'] = self.handleFileRequest(self.requestData['request_data'])

            print(self.response)
            self.request.sendall(json.dumps(self.response).encode('utf-8'))
            
        except Exception as err:
            self.response['status'] = 'error'
            self.response['message'] = err
            self.request.sendall(json.dumps(self.response).encode('utf-8'))
            self.request.shutdown()

    def validateRequest(self, request):
        # need to validate against json schema to ensure we got all the keys expectec
        print(request['request_type'])
        if request['request_type']  not in ['file_transfer','command','ping']:
            raise ValueError        

    def handleFileRequest(self, file_name):
        # check if file already exists, if its send an error or backup the file and create a new file

        print('in file transfer')
        '''
        f = open(file_name,'wb')
        print('file opened')
        while True:
            print('receiving')
            l = self.request.recv(self.BUFFER_SIZE)
            while (l):
                print('receiving')
                l = self.request.recv(self.BUFFER_SIZE)
            f.close()
            break
        '''
        try:
            print('handleFileRequest: start')
            if os.path.isfile(file_name):
                # archive the current file
                os.rename(file_name, file_name + '.arc' + str(time.strftime('%y%m%d%h%M%S%z')) )

            file = open(file_name, 'wb')
            #with open(file_name, 'wb') as f:
            print('receiving')
            data = self.request.recv(self.BUFFER_SIZE)
            while (data):
                print('receiving bytes: {}'.format(len(data)))
                file.write(data)
                data = self.request.recv(self.BUFFER_SIZE)
                if not data:
                    break                   
            file.close()                

            print('handleFileRequest: end')
            return 'success'

        except Exception as err:
            print('Error:', sys.exc_info())
            return 'error'

    def getRequestType(self, request):
        try:
            print(request)
            # need to validate against json schema to ensure we got all the keys expectec
            print(request['request_type'])
            if request['request_type']  not in ['file_transfer','command','ping']:
                self.response = 'Invalid request'
            else:
                self.response = 'ready; valid request'
                self.request_type = request['request_type']
                self.reuest_data = request['request_data']
        except Exception as err:
            print('error')
            print(err)
            self.response = 'expecting dictionary of request type, got non dict request'

    '''
    def handleFileRequest(self, file_name):
        # check if file already exists, if its send an error or backup the file and create a new file
        print('in file transfer')
        f = open(file_name,'wb')
        print('file opened')
        while True:
            l = self.request.recv(self.BUFFER_SIZE)
            while (l):
                print('receiving')
                l = self.request.recv(self.BUFFER_SIZE)
            f.close()
            break
        myResponse = 'success'
        return myResponse
    '''

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass
    '''
    def server_forever(self):
        while True:
            self.handle_request()

        return

    def handle_request(self):
        return SocketServer.TCPServer.handle_request(self)
    '''

def client(ip, port, message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    try:
        if isinstance(message,str):
            message = message.encode('utf-8')
        else:
            message = str(message).encode('utf-8')
        sock.sendall(bytes(message))
        response = str(sock.recv(1024))
        if isinstance(response,str):
            response = response.encode('utf-8')
        else:
            response = str(response).encode('utf-8')
        print("Received: {}".format(response))
    finally:
        sock.shutdown(2)
        sock.close()

if __name__ == "__main__":
    # port 0 means to select an arbitrary unused port
    #max port rang is 65535
    HOST, PORT = "localhost", 8800

    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    ip, port = server.server_address

    print('setting timeout to 60 seconds')
    server.timeout = 5
    print('{},{}'.format(ip,port))

    # start a thread with the server. 
    # the thread will then start one more thread for each request.
    server_thread = threading.Thread(target=server.serve_forever(1))
    #server_thread = threading.Thread(target=server.serve_forever)

    # exit the server thread when the main thread terminates
    server_thread.daemon = True
    server_thread.start()
    print("Server loop running in thread:", server_thread.name)

    '''
    client(ip, port, {"Message":"Hello World 1"})
    client(ip, port, {"Message":"Hello World 2"})
    client(ip, port, {"Message":"Hello World 4"})
    client(ip, port, {"Message":"Hello World 5"})
    client(ip, port, {"Message":"Hello World 6"})
    client(ip, port, {"Message":"Hello World 7"})
    client(ip, port, {"Message":"Hello World 8"})
    client(ip, port, {"Message":"Hello World 9"})
    client(ip, port, {"Message":"Hello World 10"})
    client(ip, port, {"Message":"Hello World 11"})
    client(ip, port, {"Message":"Hello World 12"})
    client(ip, port, {"Message":"Hello World 13"})
    '''

    #server_thread.join()

    server.shutdown()
    server.server_close()

    '''
    
    server.server_close()
    '''