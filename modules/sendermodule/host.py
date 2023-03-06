'''
import http.client
import json

# https://github.com/MicrosoftDocs/azure-docs/blob/main/articles/iot-hub/iot-hub-devguide-direct-methods.md
# SAS token
# az iot hub generate-sas-token -n iothubvqc01 --du 30


conn = http.client.HTTPSConnection("iothubvqc01.azure-devices.net")
payload =  {
        "methodName": "get_data",
        "payload": {"get_data": "somedata"},
        "responseTimeoutInSeconds": 10,
        "connectTimeoutInSeconds": 10}

headers = {
  "Authorization": '"SharedAccessSignature sr=iothubvqc01.azure-devices.net&sig=PMeQQd1fz2LuEcDhQUvxucz2jwx%2Fl5ZFn5ecCwJ6tuQ%3D&se=1678090953&skn=iothubowner"',
  "Content-Type": "application/json"
}
conn.request("POST", "/twins/ubuntu_thinkpad_02_symmetric/modules/receivermodule/methods?api-version=2021-04-12", payload, headers)
res = conn.getresponse()
data = res.read()
print(data.decode("utf-8"))
'''

import requests
import json

url = "https://iothubvqc01.azure-devices.net/twins/ubuntu_thinkpad_02_symmetric/modules/receivermodule/methods?api-version=2021-04-12"

payload = "{\r\n    \"methodName\": \"get_data\",\r\n    \"responseTimeoutInSeconds\": 200,\r\n    \"payload\": {\r\n        \"input1\": \"someInput\",\r\n        \"input2\": \"anotherInput\"\r\n    }"
headers = {
  'Authorization': "SharedAccessSignature sr=iothubvqc01.azure-devices.net&sig=AuDMHGvvAM4%2FSh0pVFofAliWHRYgi%2F38utYDfDwE11E%3D&se=1678091442&skn=iothubowner",
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
