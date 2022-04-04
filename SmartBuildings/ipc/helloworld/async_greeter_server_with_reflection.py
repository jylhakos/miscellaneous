
"""The reflection-enabled version of gRPC AsyncIO helloworld.Greeter server."""

import asyncio
import logging

import grpc
from grpc_reflection.v1alpha import reflection

import helloworld_pb2
import helloworld_pb2_grpc


class Greeter(helloworld_pb2_grpc.GreeterServicer):

    async def SayHello(self, request: helloworld_pb2.HelloRequest,
                       context: grpc.aio.ServicerContext
                      ) -> helloworld_pb2.HelloReply:
        return helloworld_pb2.HelloReply(message='Hello, %s!' % request.name)


async def serve() -> None:
    server = grpc.aio.server()
    helloworld_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)
    SERVICE_NAMES = (
        helloworld_pb2.DESCRIPTOR.services_by_name['Greeter'].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(SERVICE_NAMES, server)
    server.add_insecure_port('[::]:50051')
    await server.start()
    await server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    asyncio.run(serve())
