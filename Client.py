import grpc
from concurrent import futures
import ContentProvider_Server_pb2
import ContentProvider_Server_pb2_grpc

NEARBY_SERVER_IP = 'localhost'
NEARBY_SERVER_PORT = '12000'

def getFileFromServer(fileName):
    channel = grpc.insecure_channel(NEARBY_SERVER_IP + ':' + NEARBY_SERVER_PORT)
    stub = ContentProvider_Server_pb2_grpc.ContentProvider_ServerStub(channel)
    response = stub.GetFile(ContentProvider_Server_pb2.GetFileRequest(fileName = fileName))
    channel.close()
    print(response)

def serve():
    while True:
        try:
            fileName = input('Enter File Name To Retrieve From Server : ')
            getFileFromServer(fileName)
        except Exception as ex:
            print("Error Retriving File")
            continue

if __name__ == '__main__':
    #NEARBY_SERVER_IP = input('Enter Nearby Server IP : ')
    #NEARBY_SERVER_PORT = input('Enter Nearby Server Port : ')
    serve()