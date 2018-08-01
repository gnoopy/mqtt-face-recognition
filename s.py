# -*- coding: utf-8 -*-
# registrar.py

import paho.mqtt.client as mqtt
import json
import base64
import os
import time


TOPIC='img'
BIOHOME='/home/bio/imgs'
KNOWN=BIOHOME+'/known'
UNKNOWN=BIOHOME+'/unknown'
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe(TOPIC)


def on_message(client, userdata, msg):
    if msg.retain:
        return
    print("--------------------------\n %s"%str(msg.payload))
    known=True
    img_person_path=None
    jsonobj=json.loads(msg.payload) #.replace("'",'"')
    key=jsonobj['name']
    ext=jsonobj['ext']
    s=jsonobj['img']
    # print('len of base64 str:%s'%len(s))
    # print('bytes : %s'%bytes(s[2:-1],'utf-8'))
    if len(s)%4:
        s += '='*(4-len(s)%4)
    img_based64_bytes=base64.urlsafe_b64decode(bytes(s,'utf-8')) #.decode('base64')
    if key is None or len(key.strip()) == 0:
        known=False
        key = time.strftime('%m%d%H%M%S%f')
        img_person_path=(KNOWN if known else UNKNOWN)+os.sep+key+('.jpg' if ext == 'jpeg' else '.png')
    else:
        img_person_path=(KNOWN if known else UNKNOWN)+os.sep+key+('.jpg' if ext == 'jpeg' else '.png')

    print(img_person_path)
    if os.path.exists(img_person_path):
        print('already %s\'s picture registered'%key)
    f = open(img_person_path,'wb') # create a writable Image
    f.write(img_based64_bytes)
    f.close()


if not os.path.exists(KNOWN):
    os.makedirs(KNOWN)
if not os.path.exists(UNKNOWN):
    os.makedirs(UNKNOWN)
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("blog.cleverize.life", 1883, 60)
client.loop_forever()
