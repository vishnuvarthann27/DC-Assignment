import grpc
from concurrent import futures
import ContentProvider_Server_pb2
import ContentProvider_Server_pb2_grpc
import time
import fileread

NEARBY_SERVER_IP = ''
NEARBY_SERVER_PORT = ''

class FileTransmitService(ContentProvider_Server_pb2_grpc.ContentProvider_ServerServicer):
    def TransmitFile(self, request, context):
        fileread.fileRead(context.fileName, context.fileContent)
        response = ContentProvider_Server_pb2.TransmitFileResponse(transmitStatus = 'Success')
        return response


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    ContentProvider_Server_pb2_grpc.add_ContentProvider_ServerServicer_to_server(FileTransmitService(), server)
    server.add_insecure_port('[::]:' + '12000')
    server.start()
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    NEARBY_SERVER_IP = input('Enter Nearby Server IP')
    NEARBY_SERVER_PORT = input('Enter Nearby Server Port')
    serve()