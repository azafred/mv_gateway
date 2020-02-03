#!/usr/bin/env python3
import os
from flask import Flask, redirect, make_response, render_template, send_from_directory
from requests import get
from PIL import Image, ImageDraw, ImageFont
from timeloop import Timeloop
from datetime import datetime, timedelta
from secrets import *
import requests
import time
import json
import glob
import logging
import threading

tl = Timeloop()

def cam_url(api_key=API_KEY, network_id=NETWORK_ID, cam_serial='na'):
    url = "https://api.meraki.com/api/v0/networks/" + network_id + "/cameras/" + cam_serial + "/snapshot"
    header = {
        'Accept': "application/json",
        'X-Cisco-Meraki-API-Key': api_key
            }
    r = requests.post(url, headers=header)
    json_return = json.loads(r.content)
    new_url = json_return['url']
    logging.info("Received new url: " + new_url)
    return new_url

def retrieve_image(url, cam, counter=0):
  now = datetime.now()
  timestampStr = now.strftime("%d-%b-%Y (%H:%M:%S.%f)")
  timestampFile = now.strftime("%d-%b-%Y_%H-%M-%S")
  path='./static/' + cam + '_' + timestampFile + '.jpg'
  failure_counter = counter
  increment = counter / 100
  time.sleep(0.5 + increment)
  try:
    img = Image.open(requests.get(url, stream=True).raw)
  except:
    failure_counter += 1
    logging.info("Failed to retrieve {}. Try {} out of 10.".format(cam, failure_counter))
    if failure_counter < 10:
      retrieve_image(url, cam, counter=failure_counter)
    return path
  try:
    d = ImageDraw.Draw(img)
    font = ImageFont.truetype('FreeMonoBold.ttf', size=45)
    d.text((10,10), timestampStr, fill=(255,255,0), font=font)
  except Exception as e:
    logging.info("Unable to add timestamp to {}".format(cam))
    logging.info(e)
  img.save(path)
  logging.info("Image downloaded as {}".format(path))
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

# @app.route('/init')
# def start_loop():
#   try:
#     tl.start(block=True)
#   except:
#     pass
#   return render_template('index.html', cam=CAM_SERIAL)

@app.route('/snap/<path:path>')
def snap(path):
  # serial = CAM_SERIAL[path]
  # url = cam_url(cam_serial=serial)
  # img = retrieve_image(url, path)
  try:
    logging.info(path)
    list_of_files = glob.glob("static/{}*".format(path))
    logging.info(list_of_files)
    latest_file = max(list_of_files, key=os.path.getctime)
    logging.info(latest_file)
    return render_template('snap.html', cam=path, file_path=latest_file)
  except Exception as e:
    logging.info(e)
    return "Still Loading..."
def updater(name='', serial=''):
  logging.info("Updating image for the {} camera".format(name))
  try:
    url = cam_url(cam_serial=serial)
    img = retrieve_image(url, name)
    return img
  except Exception as e:
    logging.info(e)
    return None

@tl.job(interval=timedelta(seconds=20))
def auto_refresh():
  logging.info("Starting auto-refresh.")
  my_threads = {}
  for name, serial in CAM_SERIAL.items():
    logging.info("Starting thread for {}".format(name))
    my_threads[name] = threading.Thread(target=updater, args=(name, serial))
    my_threads[name].setDaemon(True)
    my_threads[name].start()

def flaskThread():
    port = int(os.environ.get('PORT', 8088))
    app.run(ssl_context=('/ssl/fullchain.pem', '/ssl/privkey.pem'), host='0.0.0.0', port=port)

if __name__ == '__main__':
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")
    # t = threading.Timer(15.0, auto_refresh)
    # # t = threading.Timer(15.0, auto_refresh)
    # t.setDaemon(True)
    # t.start()
    # app.run(ssl_context=('/ssl/fullchain.pem', '/ssl/privkey.pem'), host='0.0.0.0', port=port)
    threading.Thread(target=flaskThread).start()
    tl.start(block=True)
    #app.run(host='0.0.0.0', port=port)
