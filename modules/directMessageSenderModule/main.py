# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for
# full license information.

import asyncio
import sys
import signal
import threading
import logging
import requests
import json
import os
from azure.iot.device.aio import IoTHubModuleClient
from azure.iot.device import MethodResponse
from azure.iot.device import Message

# Event indicating client stop
stop_event = threading.Event()
device_id = os.environ["IOTEDGE_DEVICEID"]

async def send_method_to_receiver(client):
    global device_id
    test_method_params = {
        "methodName": "get_data",
        "payload": "payload",
        "responseTimeoutInSeconds": 10,
        "connectTimeoutInSeconds": 10,
    }

    try:
        logging.info("{} : {} : {} : {}".format("Sending method to module from module ", os.environ["IOTEDGE_DEVICEID"], os.environ["IOTEDGE_MODULEID"], "directMessageReceiverModule"))
        response = await client.invoke_method(device_id=device_id, module_id="directMessageReceiverModule", method_params=test_method_params)
        logging.info("Response status: %s" % response.status)
    except Exception as e:
        print("Unexpected error %s " % e)

async def send_message_to_receiver(client):
    try:
        logging.info("{} : {} : {}".format("Sending message to module from module ", os.environ["IOTEDGE_DEVICEID"], os.environ["IOTEDGE_MODULEID"]))
        msg = {"data": "test"}
        payload = Message(json.dumps(msg), content_encoding="utf-8", content_type="application/json")
        await client.send_message_to_output(payload, "output1")
    except Exception as e:
        print("Unexpected error %s " % e)

def create_client():
    client = IoTHubModuleClient.create_from_edge_environment()

    # Define function for handling received messages
    async def receive_message_handler(message):
        # NOTE: This function only handles messages sent to "input1".
        # Messages sent to other inputs, or to the default, will be discarded
        if message.input_name == "input1":
            print("the data in the message received on input1 was ")
            print(message.data)
            print("custom properties are")
            print(message.custom_properties)
            print("forwarding mesage to output1")
            await client.send_message_to_output(message, "output1")
    try:
        # Set handler on the client
        client.on_message_received = receive_message_handler

    except:
        # Cleanup if failure occurs
        client.shutdown()
        raise

    return client


async def run_sample(client):
    # Customize this coroutine to do whatever tasks the module initiates
    # e.g. sending messages
    while True:
        await send_method_to_receiver(client)
        await send_message_to_receiver(client)
        await asyncio.sleep(10)


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
    logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO,datefmt='%Y-%m-%d %H:%M:%S')
    main()
