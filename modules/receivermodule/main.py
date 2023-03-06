# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for
# full license information.

import asyncio
import sys
import signal
import threading
import logging
import os

from azure.iot.device.aio import IoTHubModuleClient
from azure.iot.device import MethodResponse

# Event indicating client stop
stop_event = threading.Event()

 # create client that supports module twin and direct methods
def create_client():
    client = IoTHubModuleClient.create_from_edge_environment()

    logging.info("{} : {} : {}".format("ReceiverModule --------->", os.environ["IOTEDGE_DEVICEID"], os.environ["IOTEDGE_MODULEID"]))

    # digital twin
    async def twin_patch_handler(patch):
        logging.info("the data in the desired properties patch was: {}".format(patch))

    # DIRECT METHOD handling  
    # Define behavior for receiving direct messages
    async def direct_method_handler(method_request):
        global SENDING
        logging.info ("Direct Method handler - message")
        if method_request.name == "get_data":
            logging.info("{}: {}".format("Received request for get_data", method_request.payload))
            method_response = MethodResponse.create_from_method_request(
                method_request, 200, "response data"
            )
            await client.send_method_response(method_response)

        elif method_request.name == "start_send":
            logging.info("Received request for start_send")
            SENDING = True
            method_response = MethodResponse.create_from_method_request(
                method_request, 200, "start_send"
            )
            await client.send_method_response(method_response)
        
        elif method_request.name == "stop_send":
            logging.info("Received request for stop_send")
            SENDING = False
            method_response = MethodResponse.create_from_method_request(
                method_request, 200, "stop_send"
            )
            await client.send_method_response(method_response)

        else:
            logging.info("{}: {}".format("Unknown method request received - method call ok", method_request.name))
            method_response = MethodResponse.create_from_method_request(method_request, 200, None)
            await client.send_method_response(method_response)
       
    # Define behavior for receiving a twin desired properties patch
    def twin_patch_handler(patch):
        print("the data in the desired properties patch was: {}".format(patch))

    # Define function for handling received messages
    async def receive_message_handler(message):
        # NOTE: This function only handles messages sent to "input1".
        # Messages sent to other inputs, or to the default, will be discarded
        if message.input_name == "input1":
            logging.info("{}: {}".format("the data in the message received on input1 was ", message.data))
            logging.info("{}: {}".format("custom properties are", message.custom_properties))
            logging.info("forwarding mesage to output1")
            await client.send_message_to_output(message, "output1")

    
    # Set handler on the client
    client.on_message_received = receive_message_handler
    # Set handler for direct methods
    client.on_method_request_received = direct_method_handler

    client.on_twin_desired_properties_patch_received = twin_patch_handler

    return client


async def run_sample(client):
    # Customize this coroutine to do whatever tasks the module initiates
    # e.g. sending messages
    await client.connect()
    while not stop_event.is_set():
        await asyncio.sleep(1)


def main():
    if not sys.version >= "3.5.3":
        raise Exception( "The sample requires python 3.5.3+. Current version of Python: %s" % sys.version )
    print ( "IoT Hub Client for Python" )

    # NOTE: Client is implicitly connected due to the handler being set on it
    client = create_client()

    # Define a handler to cleanup when module is is terminated by Edge
    def module_termination_handler(signal, frame):
        print ("IoTHubClient sample stopped by Edge")
        stop_event.set()

    # Set the Edge termination handler
    signal.signal(signal.SIGTERM, module_termination_handler)

    # Run the sample
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(run_sample(client))
    except Exception as e:
        print("Unexpected error %s " % e)
        raise
    finally:
        print("Shutting down IoT Hub Client...")
        loop.run_until_complete(client.shutdown())
        loop.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
