#!/usr/bin/env python3
import os
from flask import Flask, redirect, make_response, render_template, send_from_directory
from requests import get
from PIL import Image
from secrets import *
import requests
import json
import threading


def cam_url(api_key=API_KEY, network_id=NETWORK_ID, cam_serial='na'):
    url = "https://api.meraki.com/api/v0/networks/" + network_id + "/cameras/" + cam_serial + "/snapshot"
    header = {
        'Accept': "application/json",
        'X-Cisco-Meraki-API-Key': api_key
            }
    r = requests.post(url, headers=header)
    json_return = json.loads(r.content)
    new_url = json_return['url']
    print("Received new url: " + new_url)
    return new_url

def retrieve_image(url, cam):
  path='./static/' + cam + '.jpg'
  try:
    img = Image.open(requests.get(url, stream=True).raw)
  except:
    print("Failed to download snapshot...")
    retrieve_image(url, cam)
    return path
  img.save(path)
  print("Image downloaded as {}".format(path))
  return path

app = Flask(__name__, static_url_path='', static_folder='static')

# @app.route('/assets/<path:path>')
# def send_pics(path):
#   return send_from_directory(path, path)
@app.route('/static/<path:path>')
def static_file(path):
    return app.send_static_file(path)


@app.route('/refresh')
def refresh():
    for name, serial in CAM_SERIAL.items():
      url = cam_url(cam_serial=serial)
      img = retrieve_image(url, name)
    return render_template('index.html', cam=CAM_SERIAL)

@app.route('/')
def display():
  return render_template('index.html', cam=CAM_SERIAL)

@app.route('/snap/<path:path>')
def snap(path):
  serial = CAM_SERIAL[path]
  url = cam_url(cam_serial=serial)
  img = retrieve_image(url, path)
  return render_template('snap.html', cam=path)

def auto_refresh():
  print("Refreshing Thread")
  for name, serial in CAM_SERIAL.items():
    try:
      url = cam_url(cam_serial=serial)
      img = retrieve_image(url, name)
    except:
      pass

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    t = threading.Timer(15.0, auto_refresh)
    t.setDaemon(True)
    t.start()
    port = int(os.environ.get('PORT', 8088))
    #app.run(ssl_context=('/ssl/fullchain.pem', '/ssl/privkey.pem'), host='0.0.0.0', port=port)
    app.run(host='0.0.0.0', port=port)
