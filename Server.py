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
MY_IP = MY_IP + ':12000'

class FileTransmitService(ContentProvider_Server_pb2_grpc.ContentProvider_ServerServicer):
    def TransmitFile(self, request, context):
        fileread.fileWrite(request.fileName, request.fileContent)
        response = ContentProvider_Server_pb2.TransmitFileResponse(transmitStatus = 'Success')
        return response
    
    def replicateFile(self, request, context):
        fileList = fileread.getFileList()
        requestList = []
        for file in request.fileNameList:
            if(file not in fileList):
                requestList.append(file)
        response = ContentProvider_Server_pb2.syncFileResponse(fileNameList = requestList)
        return response
    
    def HandleForwardRequest(self, request, context):
        fileContent = fileread.fileRead(request.fileName, "ServerFiles")

        if(fileContent != "File Not Found"):
            response = ContentProvider_Server_pb2.serverToServerResponse(fileName = request.fileName, fileContent = fileContent)
            return response
        else:
            filteredEdges = [edge for edge in serverConfig.MST if(MY_IP in edge and request.ipAddress not in edge)]
            for edge in filteredEdges:
                NEARBY_SERVER_IP = edge[(edge.index(MY_IP) + 1 ) % 2]
                try:
                    channel = grpc.insecure_channel(NEARBY_SERVER_IP)
                    stub = ContentProvider_Server_pb2_grpc.ContentProvider_ServerStub(channel)
                    response = stub.HandleForwardRequest(ContentProvider_Server_pb2.serverToServerRequest(fileName = request.fileName, ipAddress = MY_IP))
                    channel.close()
                    if(response.fileContent != "File Not Found in server"):
                        fileread.fileWrite(response.fileName, response.fileContent)
                        response = ContentProvider_Server_pb2.serverToServerResponse(fileName = request.fileName, fileContent = response.fileContent)
                        return response
                
                except Exception as ex:
                    print("Server : " + NEARBY_SERVER_IP +" Maybe Offline, Trying next server in path")
                    continue

            response = ContentProvider_Server_pb2.serverToServerResponse(fileName = request.fileName, fileContent = "File Not Found in server")
            return response
    
    def GetFile(self, request, context):
        fileContent = fileread.fileRead(request.fileName, "ServerFiles")

        if(fileContent != "File Not Found"):
            response = ContentProvider_Server_pb2.GetFileResponse(fileName = request.fileName, fileContent = fileContent)
            return response
        else:
            filteredEdges = [edge for edge in serverConfig.MST if(MY_IP in edge)]

            for edge in filteredEdges:
                NEARBY_SERVER_IP = edge[(edge.index(MY_IP) + 1 ) % 2]
                try:
                    channel = grpc.insecure_channel(NEARBY_SERVER_IP)
                    stub = ContentProvider_Server_pb2_grpc.ContentProvider_ServerStub(channel)
                    response = stub.HandleForwardRequest(ContentProvider_Server_pb2.serverToServerRequest(fileName = request.fileName, ipAddress = MY_IP))
                    channel.close()
                    if(response.fileContent != "File Not Found in server"):
                        fileread.fileWrite(response.fileName, response.fileContent)
                        response = ContentProvider_Server_pb2.GetFileResponse(fileName = request.fileName, fileContent = response.fileContent)
                        return response
                
                except Exception as ex:
                    print("Server : " + NEARBY_SERVER_IP +" Maybe Offline, Trying next server in path")
                    continue

            
            response = ContentProvider_Server_pb2.GetFileResponse(fileName = request.fileName, fileContent = "File Not Found in server")
            return response
        

            
def syncFiles():
    fileList = fileread.getFileList()
    if(len(fileList) > 0):
        for server in serverConfig.serverList:
            IP_ADDRESS = server.split(":")[0]
            if(MY_IP.split(":")[0] != IP_ADDRESS):
                try:
                    channel = grpc.insecure_channel(server)
                    stub = ContentProvider_Server_pb2_grpc.ContentProvider_ServerStub(channel)
                    response = stub.replicateFile(ContentProvider_Server_pb2.syncFileRequest(fileNameList = fileList))
                    if(len(response.fileNameList) > 0):
                        for file in response.fileNameList:
                            fileContent = fileread.fileRead(file, "ServerFiles")
                            response = stub.TransmitFile(ContentProvider_Server_pb2.TransmitFileRequest(fileName = file, fileContent = fileContent))
                            if(response.transmitStatus == 'Success'):
                                print("Successfully replicated file : " + file + " in server : " + server)
                            else:
                                print("Error in file replication will retry in 300 seconds ")
                    else:
                        print("Files are already replicated in server : " + server)

                    channel.close()
                except Exception as ex:
                    print("Server : " + server +" Maybe Offline will retry replication after sometime")
                    continue

def serve(serverPort):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    ContentProvider_Server_pb2_grpc.add_ContentProvider_ServerServicer_to_server(FileTransmitService(), server)
    server.add_insecure_port('[::]:' + serverPort)
    server.start()
    try:
        while True:
            time.sleep(300)
            syncFiles()
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serverPort = '12000'
    serve(serverPort)