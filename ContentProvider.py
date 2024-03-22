import grpc
from concurrent import futures
import ContentProvider_Server_pb2
import ContentProvider_Server_pb2_grpc
#import socket
import fileread

NEARBY_SERVER_IP = 'localhost'
NEARBY_SERVER_PORT = '12000'

def transmitFile(fileName, fileContent):
    channel = grpc.insecure_channel(NEARBY_SERVER_IP + ':' + NEARBY_SERVER_PORT)
    stub = ContentProvider_Server_pb2_grpc.ContentProvider_ServerStub(channel)
    response = stub.TransmitFile(ContentProvider_Server_pb2.TransmitFileRequest(fileName = fileName, fileContent = fileContent))
    channel.close()
    if(response.transmitStatus == 'Success'):
        print("Successfully transmitted file : " + fileName)
    else:
        print("Error in Transmitting file. Retry after sometime ")

def serve():
    while True:
        try:
            fileName = input('Enter File Name To Send To Server : ')
            fileContent = fileread.fileRead(fileName=fileName, folder = "ContentProvider")
            if(fileContent == "File Not Found"):
                print("File Not Found Enter a valid file name")
                continue
            else:
                transmitFile(fileName, fileContent)
        except Exception as ex:
            print("Error with file Transmission")
            continue


if __name__ == '__main__':
    #NEARBY_SERVER_IP = input('Enter Nearby Server IP : ')
    #NEARBY_SERVER_PORT = input('Enter Nearby Server Port : ')
    serve()