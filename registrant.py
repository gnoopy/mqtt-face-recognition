# -*- coding: utf-8 -*-
import paho.mqtt.client as mqtt
import base64
import json
import os
import imghdr
import threading
from datetime import datetime

TOPIC='facerecog'
wait_res=None
evt_wait_res=None
def on_connect(client, userdata, flags, rc):
    client.subscribe(TOPIC)


def on_message(client, userdata, msg):
    global wait_res
    # print(".")
    # print(msg.topic+" "+str(msg.payload))
    if wait_res:
        jsonobj=json.loads(msg.payload) #.replace("'",'"')
        if 'res' in jsonobj:
            req_key=jsonobj['res'] #TODO: wait_resㅇ와 req_key가 같은 지 비교해서 요청시의 이미지랑 응답이 한 Tx인것을 확인할 필요 있다.
            name=jsonobj['name']
            print('>> Recognized as %s <<'%name)
            wait_res=None
            evt_wait_res.set()


def get_b64str_from_file(fpath):
    with open(fpath, 'rb') as imfile:
        s=str(base64.b64encode(imfile.read()))
        # print ("str:%s, type:%s"%(s,type(s)))
    return s


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
        print('fpath:%s'%fpath)
        if fpath == None or len(fpath) == 0:
            break
        ret, ext=validate_imgpath(fpath)
    img_str=get_b64str_from_file(fpath)
    req_key=datetime.now().strftime('%f%S%M%H%d%m%Y')
    jsonobj=json.dumps({"req":req_key, "name":name,"ext":ext, "img":img_str})
    if not name:
        wait_res=req_key
        evt_wait_res=threading.Event()
    client.publish(TOPIC,payload=jsonobj)
    if not name:
        evt_wait_res.wait(2)
    # client.publish(TOPIC,'{"name":"%s", "img":"%s"}'%(name,'hihihihihi'))
    wannaquit=input("Continue? [Y/n]:")
    if wannaquit == 'n':
        break
client.loop_stop()

