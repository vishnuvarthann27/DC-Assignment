import grpc
from concurrent import futures
import ContentProvider_Server_pb2
import ContentProvider_Server_pb2_grpc
import time
import socket
import fileread
import serverConfig

NEARBY_SERVER_IP = ''
NEARBY_SERVER_PORT = ''
MY_HOSTNAME = socket.gethostname()
MY_IP = socket.gethostbyname(MY_HOSTNAME)

class FileTransmitService(ContentProvider_Server_pb2_grpc.ContentProvider_ServerServicer):
    def TransmitFile(self, request, context):
        fileread.fileWrite(request.fileName, request.fileContent)
        response = ContentProvider_Server_pb2.TransmitFileResponse(transmitStatus = 'Success')
        return response
    
    def replicateFile(self, request, context):
        fileList = fileread.getFileList()
        
    
    def GetFile(self, request, context):
        fileContent = fileread.fileRead(request.fileName, "ServerFiles")

        if(fileContent != "File Not Found"):
            response = ContentProvider_Server_pb2.GetFileResponse(fileName = request.fileName, fileContent = fileContent)
            return response
        else:
            if(NEARBY_SERVER_IP != ''):
                channel = grpc.insecure_channel(NEARBY_SERVER_IP + ':' + NEARBY_SERVER_PORT)
                stub = ContentProvider_Server_pb2_grpc.ContentProvider_ServerStub(channel)
                fileDataResponse = stub.GetFile(ContentProvider_Server_pb2.GetFileRequest(fileName = request.fileName))
                channel.close()

                if(fileDataResponse.fileContent != "File Not Found in server"):
                    fileread.fileWrite(fileDataResponse.fileName, fileDataResponse.fileContent)
                response = ContentProvider_Server_pb2.GetFileResponse(fileName = fileDataResponse.fileName, fileContent = fileDataResponse.fileContent)
                return response
            
            else:
                response = ContentProvider_Server_pb2.GetFileResponse(fileName = request.fileName, fileContent = "File Not Found in server")
                return response
            
def syncFiles():
    fileList = fileread.getFileList()
    if(len(fileList) > 0):
        for server in serverConfig.serverList:
            IP_ADDRESS = server.split(":")[0]
            if(MY_IP != IP_ADDRESS):
                print(MY_IP)
                print(IP_ADDRESS)

def serve(serverPort):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    ContentProvider_Server_pb2_grpc.add_ContentProvider_ServerServicer_to_server(FileTransmitService(), server)
    server.add_insecure_port('[::]:' + serverPort)
    server.start()
    try:
        while True:
            time.sleep(10)
            syncFiles()
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    NEARBY_SERVER_IP = input('Enter Nearby Server IP : ')
    NEARBY_SERVER_PORT = input('Enter Nearby Server Port : ')
    serverPort = input('Input Port to Host the Server : ')
    serve(serverPort)