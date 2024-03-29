# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for
# full license information.

import asyncio
import sys
import signal
import threading
import logging
#import requests
import json
import os
from azure.iot.device.aio import IoTHubModuleClient
#from azure.iot.device import MethodResponse
from azure.iot.device import Message
from datetime import datetime

# Event indicating client stop
stop_event = threading.Event()
DEVICEID = os.environ["IOTEDGE_DEVICEID"]

'''
send a method to the receiver module 
'''
async def send_method_to_receiver(client):
    global DEVICEID
    test_method_params = {
        "methodName": "get_data",
        "payload": {"get_data":"this data"},
        "responseTimeoutInSeconds": 5,
        "connectTimeoutInSeconds": 2,
    }
    try:
        #logging.info("Sending method to module from module %s %s %s ------------->", DEVICEID, os.environ["IOTEDGE_MODULEID"], "receivermodule")
        start_time = datetime.now()
        response = await client.invoke_method(
            device_id=DEVICEID, module_id = "receivermodule", method_params=test_method_params
        )
        end_time = datetime.now()
        #print("Method Response: {}".format(response))
        time_difference = (end_time - start_time).total_seconds() * 10**3
        logging.info("{} : {} : {}".format("direct method round trip time ", time_difference, "ms"))
    except Exception as e:
        print("Unexpected error %s " % e)


# send a message to the receiver module via edge hub
async def send_message_to_receiver(client):
    global DEVICEID
    try:
        logging.info("Sending message to module from module %s %s", DEVICEID, os.environ["IOTEDGE_MODULEID"])
        msg = {"data": "test"}
        payload = Message(json.dumps(msg), content_encoding="utf-8", content_type="application/json")
        await client.send_message_to_output(payload, "output1")
    except Exception as e:
        logging.exception("Unexpected error: %s", e)

def create_client():
    client = IoTHubModuleClient.create_from_edge_environment()

    # Define function for handling received messages
    async def receive_message_handler(message):
        # NOTE: This function only handles messages sent to "input1".
        # Messages sent to other inputs, or to the default, will be discarded
        if message.input_name == "input1":
            logging.info("".format("the data in the message received on input1 was "))
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
