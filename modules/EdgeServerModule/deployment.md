
# how to deploy in an edge device 


config 

```
 "edgeconfigserver": {
            "type": "docker",
            "status": "running",
            "restartPolicy": "always",
            "settings": {
              "image": "<your container registry>.azurecr.io/edge-config-server:<version>",
              "createOptions": "{\"ExposedPorts\":{\"<your port>/tcp\":{}},\"HostConfig\":{\"PortBindings\":{\"<your port>/tcp\":[{\"HostPort\":\"<your port>\"}]}}}"
            }
          }
```

deployment.json

```
     "edgeconfigserver":{
            "type": "docker",
            "status": "running",
            "restartPolicy": "always",
            "settings": {
              "image": "<your container registry>.azurecr.io/edge-config-server:<version>",
              "createOptions": {
                {
                  "ExposedPorts": {
                    "<your port>/tcp": {}
                  },
                  "HostConfig": {
                    "PortBindings": {
                      "<your port>/tcp": [
                        {
                          "HostPort": "<your port>"
                        }
                      ]
                    },
                    "Binds": [
                      "/home/configs:/app/configs"
                      ]
                    }
                  }
                }
              }
            }
          }
```