# mv_gateway
This flask app regularly polls the Meraki API to get a snapshot URL,
Download the snapshots from that URL
And displays it in a bootstrap carousel.

# To build the docker image: 
```
docker build -t azafred/mv_gateway:latest ~/docker/mv_cams
```

# To include the image in docker compose:
```
# vim: noai:ts=2:sw=2
---
version: "3"
services:
  mv_gateway:
    image: azafred/mv_gateway
    container_name: mv_gateway
    command: python main.py
    volumes:
      - /home/fred/hassio/ssl:/ssl
    ports:
      - 8088:8088
    restart: unless-stopped
```
Note: The location of the ssl certs will vary, so setup your volume accordingly
or disable SSL in main.py.

# Configuration:
You will need to create a file call secrets.py in the same directory as main.py that contains the following:
```
#!/usr/bin/env python3
API_KEY = "your API key"
NETWORK_ID = "L_XXXX"
CAM_SERIAL = {"cam1": "Q2GV-XXXX-XXXX",
              "cam2": "Q2GV-XXXX-XXXX",
              "cam3": "Q2GV-XXXX-XXXX",
              "cam4": "Q2GV-XXXX-XXXX"}
```

