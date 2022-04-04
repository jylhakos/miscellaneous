
"""The Python AsyncIO implementation of the GRPC helloworld.Greeter server."""

import logging
import asyncio
import grpc

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
    listen_addr = '[::]:50051'
    server.add_insecure_port(listen_addr)
    logging.info("Starting server on %s", listen_addr)
    await server.start()
    try:
        await server.wait_for_termination()
    except KeyboardInterrupt:
        # Shuts down the server with 0 seconds of grace period. During the
        # grace period, the server won't accept new connections and allow
        # existing RPCs to continue within the grace period.
        await server.stop(0)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(serve())
