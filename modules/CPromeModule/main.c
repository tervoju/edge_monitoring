// Copyright (c) Microsoft. All rights reserved.
// Licensed under the MIT license. See LICENSE file in the project root for full license information.

#include <stdio.h>
#include <stdlib.h>

#include "iothub_module_client_ll.h"
#include "iothub_client_options.h"
#include "iothub_message.h"
#include "azure_c_shared_utility/threadapi.h"
#include "azure_c_shared_utility/crt_abstractions.h"
#include "azure_c_shared_utility/platform.h"
#include "azure_c_shared_utility/shared_util_options.h"
#include "iothubtransportmqtt.h"
#include "iothub.h"
#include "time.h"

#include <pthread.h>

#include <prometheus/counter.h>
#include <prometheus/exposer.h>
#include <prometheus/registry.h>

#include <array>
#include <chrono>
#include <cstdlib>
#include <memory>
#include <string>

void* prome(void *arg)
{

    // detach the current thread
    // from the calling thread
    pthread_detach(pthread_self());
    // create an http server running on port 8080
    auto exposer = Exposer{"127.0.0.1:8080"};

    // create a metrics registry with component=main labels applied to all its
    // metrics
    auto registry = std::make_shared<Registry>();

    // add a new counter family to the registry (families combine values with the
    // same name, but distinct label dimenstions)
    auto &counter_family = BuildCounter()
                               .Name("time_running_seconds")
                               .Help("How many seconds is this server running?")
                               .Labels({{"label", "value"}})
                               .Register(*registry);

    // add a counter to the metric family
    auto &second_counter = counter_family.Add(
        {{"another_label", "value"}, {"yet_another_label", "value"}});

    // ask the exposer to scrape the registry on incoming scrapes
    exposer.RegisterCollectable(registry);

    for (;;)
    {
        std::this_thread::sleep_for(std::chrono::seconds(1));
        // increment the counter by one (second)
        second_counter.Increment();
    }
    // exit the current thread
    pthread_exit(NULL);
    return 0;
}


typedef struct MESSAGE_INSTANCE_TAG
{
    IOTHUB_MESSAGE_HANDLE messageHandle;
    size_t messageTrackingId;  // For tracking the messages within the user callback.
} 
MESSAGE_INSTANCE;

size_t messagesReceivedByInput1Queue = 0;

// SendConfirmationCallback is invoked when the message that was forwarded on from 'InputQueue1Callback'
// pipeline function is confirmed.
static void SendConfirmationCallback(IOTHUB_CLIENT_CONFIRMATION_RESULT result, void* userContextCallback)
{
    // The context corresponds to which message# we were at when we sent.
    MESSAGE_INSTANCE* messageInstance = (MESSAGE_INSTANCE*)userContextCallback;
    printf("Confirmation[%zu] received for message with result = %d\r\n", messageInstance->messageTrackingId, result);
    IoTHubMessage_Destroy(messageInstance->messageHandle);
    free(messageInstance);
}

// Allocates a context for callback and clones the message
// NOTE: The message MUST be cloned at this stage.  InputQueue1Callback's caller always frees the message
// so we need to pass down a new copy.
static MESSAGE_INSTANCE* CreateMessageInstance(IOTHUB_MESSAGE_HANDLE message)
{
    MESSAGE_INSTANCE* messageInstance = (MESSAGE_INSTANCE*)malloc(sizeof(MESSAGE_INSTANCE));
    if (NULL == messageInstance)
    {
        printf("Failed allocating 'MESSAGE_INSTANCE' for pipelined message\r\n");
    }
    else
    {
        memset(messageInstance, 0, sizeof(*messageInstance));

        if ((messageInstance->messageHandle = IoTHubMessage_Clone(message)) == NULL)
        {
            free(messageInstance);
            messageInstance = NULL;
        }
        else
        {
            messageInstance->messageTrackingId = messagesReceivedByInput1Queue;
        }
    }

    return messageInstance;
}

static IOTHUBMESSAGE_DISPOSITION_RESULT InputQueue1Callback(IOTHUB_MESSAGE_HANDLE message, void* userContextCallback)
{
    IOTHUBMESSAGE_DISPOSITION_RESULT result;
    IOTHUB_CLIENT_RESULT clientResult;
    IOTHUB_MODULE_CLIENT_LL_HANDLE iotHubModuleClientHandle = (IOTHUB_MODULE_CLIENT_LL_HANDLE)userContextCallback;

    unsigned const char* messageBody;
    size_t contentSize;

    if (IoTHubMessage_GetByteArray(message, &messageBody, &contentSize) != IOTHUB_MESSAGE_OK)
    {
        messageBody = "<null>";
    }

    printf("Received Message [%zu]\r\n Data: [%s]\r\n", 
            messagesReceivedByInput1Queue, messageBody);

    // This message should be sent to next stop in the pipeline, namely "output1".  What happens at "outpu1" is determined
    // by the configuration of the Edge routing table setup.
    MESSAGE_INSTANCE *messageInstance = CreateMessageInstance(message);
    if (NULL == messageInstance)
    {
        result = IOTHUBMESSAGE_ABANDONED;
    }
    else
    {
        printf("Sending message (%zu) to the next stage in pipeline\n", messagesReceivedByInput1Queue);

        clientResult = IoTHubModuleClient_LL_SendEventToOutputAsync(iotHubModuleClientHandle, messageInstance->messageHandle, "output1", SendConfirmationCallback, (void *)messageInstance);
        if (clientResult != IOTHUB_CLIENT_OK)
        {
            IoTHubMessage_Destroy(messageInstance->messageHandle);
            free(messageInstance);
            printf("IoTHubModuleClient_LL_SendEventToOutputAsync failed on sending msg#=%zu, err=%d\n", messagesReceivedByInput1Queue, clientResult);
            result = IOTHUBMESSAGE_ABANDONED;
        }
        else
        {
            result = IOTHUBMESSAGE_ACCEPTED;
        }
    }

    messagesReceivedByInput1Queue++;
    return result;
}

static IOTHUB_MODULE_CLIENT_LL_HANDLE InitializeConnection()
{
    IOTHUB_MODULE_CLIENT_LL_HANDLE iotHubModuleClientHandle;

    if (IoTHub_Init() != 0)
    {
        printf("Failed to initialize the platform.\r\n");
        iotHubModuleClientHandle = NULL;
    }
    else if ((iotHubModuleClientHandle = IoTHubModuleClient_LL_CreateFromEnvironment(MQTT_Protocol)) == NULL)
    {
        printf("ERROR: IoTHubModuleClient_LL_CreateFromEnvironment failed\r\n");
    }
    else
    {
        // Uncomment the following lines to enable verbose logging.
        // bool traceOn = true;
        // IoTHubModuleClient_LL_SetOption(iotHubModuleClientHandle, OPTION_LOG_TRACE, &trace);
    }

    return iotHubModuleClientHandle;
}

static void DeInitializeConnection(IOTHUB_MODULE_CLIENT_LL_HANDLE iotHubModuleClientHandle)
{
    if (iotHubModuleClientHandle != NULL)
    {
        IoTHubModuleClient_LL_Destroy(iotHubModuleClientHandle);
    }
    IoTHub_Deinit();
}

static int SetupCallbacksForModule(IOTHUB_MODULE_CLIENT_LL_HANDLE iotHubModuleClientHandle)
{
    int ret;

    if (IoTHubModuleClient_LL_SetInputMessageCallback(iotHubModuleClientHandle, "input1", InputQueue1Callback, (void*)iotHubModuleClientHandle) != IOTHUB_CLIENT_OK)
    {
        printf("ERROR: IoTHubModuleClient_LL_SetInputMessageCallback(\"input1\")..........FAILED!\r\n");
        ret = 1;
    }
    else
    {
        ret = 0;
    }

    return ret;
}

void iothub_module()
{
    IOTHUB_MODULE_CLIENT_LL_HANDLE iotHubModuleClientHandle;

    srand((unsigned int)time(NULL));

    if ((iotHubModuleClientHandle = InitializeConnection()) != NULL && SetupCallbacksForModule(iotHubModuleClientHandle) == 0)
    {
        // The receiver just loops constantly waiting for messages.
        printf("Waiting for incoming messages.\r\n");
        while (true)
        {
            IoTHubModuleClient_LL_DoWork(iotHubModuleClientHandle);
            ThreadAPI_Sleep(100);
        }
    }

    DeInitializeConnection(iotHubModuleClientHandle);
}

int main(void)
{
    pthread_t ptid;
    pthread_create(&ptid, NULL, &prome, NULL);
    iothub_module();
    return 0;
}
