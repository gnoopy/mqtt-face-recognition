# -*- coding: utf-8 -*-
import paho.mqtt.client as mqtt
import json
import base64
import os
from datetime import datetime
import glob

import face_recognition
# integrate from examples/recognize_faces_in_pictures.py

TOPIC='facerecog'
BIOHOME='/home/alphago'
KNOWN=BIOHOME+'/known'
UNKNOWN=BIOHOME+'/unknown'
KNOWN_KEYS=[]
KNOWN_FACES=[]
CUTOFF_DISTANCE=0.4

def on_connect(client, userdata, flags, rc):
    client.subscribe(TOPIC)
    print("Connected with result code "+str(rc))


def on_message(client, userdata, msg):
    if msg.retain :
        return
    # print(msg.topic+" %s"%str(msg.payload))
    jsonobj=json.loads(msg.payload) #.replace("'",'"')
    if 'res' in jsonobj:
        return
    known=True
    img_person_path=None
    req=jsonobj['req']
    key=jsonobj['name']
    ext=jsonobj['ext']
    s=jsonobj['img']
#    print('ext:%s'%ext)
    if len(s)%4:
        s += '='*(4-len(s)%4)
    img_based64_bytes=base64.urlsafe_b64decode(bytes(s,'utf-8')) #.decode('base64')

    img_person_path=None
    fname = datetime.now().strftime('%f%S%M%H%d%m%Y')
    if key is None or len(key.strip()) == 0:
        known=False
        img_person_path=UNKNOWN +'/'+fname+('.jpg' if ext == 'jpeg' else '.png')
    else:
        key_dir=mkdir_if_newkey(key)
        img_person_path=key_dir +'/'+fname+('.jpg' if ext == 'jpeg' else '.png')

    print(img_person_path)
    # if os.path.exists(img_person_path):
    #     print('already %s\'s picture registered'%key)
    f = open(img_person_path,'wb') # create a writable Image
    f.write(img_based64_bytes)
    f.close()
    if not known:
        recognized_as=recognize(img_person_path)
        name='nobody' if recognized_as is None else recognized_as
        jsonobj=json.dumps({"res":req,"name":name})
        client.publish(TOPIC,payload=jsonobj)
    else:
        load_known_face_imgs()


def mkdir_if_newkey(k):
    d=KNOWN+os.sep+k
    if not os.path.exists(d):
        os.makedirs(d)
    return d

def load_known_face_imgs():
    print('Start loading face images')
    #print('Loading face images',end='')
    known_folders=glob.glob(KNOWN+'/*/')
    for folder in known_folders:
        known_key=folder.replace(KNOWN,'').replace('/','')
        flist=glob.glob(folder+'/*.[jp][pn]g')
        if len(flist) > 0:
            known_file=flist[-1] #last picture could be recent picture
            print('last file:%s'%known_file)
            a_img=face_recognition.load_image_file(known_file)
            a_face_encoding = face_recognition.face_encodings(a_img)[0]
            KNOWN_KEYS.append(known_key)
            KNOWN_FACES.append(a_face_encoding)
#        print('.',end='')
    print('End loading face images')

def recognize(unknown_file):
    unknown_image = face_recognition.load_image_file(unknown_file)
    try:
        unknown_face_encoding = face_recognition.face_encodings(unknown_image)[0]
    except IndexError:
        print("Failed to find face")
        return None #TODO:얼굴을 못찾는 것에 대한 별도 오류 처리 필요
    face_distances = face_recognition.face_distance(KNOWN_FACES, unknown_face_encoding)
    min_dstnc=100
    min_index=-1
    for i, face_distance in enumerate(face_distances):
        if min_dstnc > face_distance:
            min_dstnc=face_distance
            min_index=i
        print (KNOWN_KEYS[i]+':%s '%(face_distance))
    print('min_dstnc:%s, cutoff=%s'%(min_dstnc,CUTOFF_DISTANCE))
    if min_dstnc > CUTOFF_DISTANCE:
        return None
    return KNOWN_KEYS[min_index]

    # results = face_recognition.compare_faces(KNOWN_FACES, unknown_face_encoding)
    # for r in results:
    #     if r:
    #         return KNOWN_KEYS[results.index(r)]
    # return None

if not os.path.exists(KNOWN):
    os.makedirs(KNOWN)
if not os.path.exists(UNKNOWN):
    os.makedirs(UNKNOWN)

load_known_face_imgs()

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("blog.cleverize.life", 1883, 60)
client.loop_forever()
