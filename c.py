# -*- coding: utf-8 -*-
# registant.py

import paho.mqtt.client as mqtt
import base64
import json
import os
import imghdr

TOPIC='img'

def on_connect(client, userdata, flags, rc):
    client.subscribe(TOPIC)


def on_message(client, userdata, msg):
    print("",end="")
    # print(msg.topic+" "+str(msg.payload))


def get_b64str_from_file(fpath):
    with open(fpath, 'rb') as imfile:
        s=str(base64.urlsafe_b64encode(imfile.read()))
        print ("str:%s, type:%s"%(s,type(s)))
    return s[2:-1]


def validate_imgpath(path):
    if path is None:
        return False, None
    if os.path.isfile(path) and imghdr.what(path) in ['jpeg', 'png']:
        return True, imghdr.what(path)
    return False, None


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("blog.cleverize.life", 1883, 60)
client.loop_start()
while True:
    name = input("Enter name:")
    fpath=None
    ret, ext=validate_imgpath(fpath)
    while not ret:
        fpath = input("Enter file:")
        if fpath == None or len(fpath) == 0:
            break
        ret, ext=validate_imgpath(fpath)

    img_str=get_b64str_from_file(fpath)
    jsonobj=json.dumps({"name":name,"ext":ext, "img":img_str})
    client.publish(TOPIC,payload=jsonobj)
    # client.publish(TOPIC,'{"name":"%s", "img":"%s"}'%(name,'hihihihihi'))
    wannaquit=input("q for Quit:")
    if wannaquit == 'q':
        break
client.loop_stop()
