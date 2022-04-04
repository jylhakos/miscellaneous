
"""The Python implementation of the GRPC helloworld.Greeter client."""

from __future__ import print_function
import logging

import grpc

import asyncio

import helloworld_pb2
import helloworld_pb2_grpc

async def run():
    # NOTE(gRPC Python Team): .close() is possible on a channel and should be
    # used in circumstances in which the with statement does not fit the needs
    # of the code.
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = helloworld_pb2_grpc.GreeterStub(channel)
        while True:
        	await asyncio.sleep(2)
        	response = stub.SayHello(helloworld_pb2.HelloRequest(name='you'))
        	print("Greeter client received: " + response.message)
        	response = stub.SayHelloAgain(helloworld_pb2.HelloRequest(name='you'))
        	print("Greeter client received: " + response.message)

if __name__ == '__main__':
	logging.basicConfig()
	#run()
	loop = asyncio.get_event_loop()
	try:
		asyncio.ensure_future(run())
		loop.run_forever()
	except KeyboardInterrupt:
		pass
	finally:
		print("Closing Loop")
		loop.close()
