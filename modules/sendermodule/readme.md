# Direct Message Sender Module

This module is an example of direct message sender. It can be used to test the direct message receiver module.


https://learn.microsoft.com/en-us/azure/iot-hub/iot-hub-devguide-sdks#azure-iot-hub-device-sdks

https://github.com/Azure/azure-iot-sdk-python


https://github.com/Azure/azure-iot-sdk-python/blob/main/samples/async-edge-scenarios/invoke_method_on_module.py

```python	
 fake_method_params = {
        "methodName": "doSomethingInteresting",
        "payload": "foo",
        "responseTimeoutInSeconds": 5,
        "connectTimeoutInSeconds": 2,
    }
    response = await module_client.invoke_method(
        device_id="fakeDeviceId", module_id="fakeModuleId", method_params=fake_method_params
    )
    print("Method Response: {}".format(response))
```	