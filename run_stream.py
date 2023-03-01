# -*- coding: utf-8 -*-

import cv2
from flask import Flask, render_template, request, Response
import datetime, time
from cv2 import rotate
from threading import Thread
import os

app = Flask(__name__, template_folder='templates')
cap = cv2.VideoCapture(0)

global capture,rec_frame, grey, switch, neg, rec, out 
capture=0
grey=0
neg=0
switch=1
rec=0

def record(out):
    global rec_frame
    while(rec):
        time.sleep(0.05)
        out.write(rec_frame)

def correct_rotate(param):
    if param == 0:
        correct_corner=42
    elif param == 90:
        correct_corner = cv2.ROTATE_90_CLOCKWISE
    elif param == 180:
        correct_corner = cv2.ROTATE_180
    elif param == 270:
        correct_corner = cv2.ROTATE_90_COUNTERCLOCKWISE
    return correct_corner



def pyshine_process(params, cap):
    print("Parameters:", params)
    """Video streaming generator function."""


    cap.set(cv2.CAP_PROP_FRAME_WIDTH, int(params['width']))
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, int(params['height']))
    cap.set(cv2.CAP_PROP_BRIGHTNESS, int(params['brightness']))
    cap.set(cv2.CAP_PROP_CONTRAST, int(params['contrast']))
    cap.set(cv2.CAP_PROP_SATURATION, int(params['saturation']))
    cap.set(cv2.CAP_PROP_HUE, int(params['hue']))
    cap.set(cv2.CAP_PROP_GAIN, int(params['gain']))
    cap.set(cv2.CAP_PROP_EXPOSURE, int(params['exposure']))
    cap.set(cv2.CAP_PROP_SHARPNESS, int(params['sharpness']))
    correct_corner = correct_rotate(int(params['rotate']))


    print('FUNCTION DONE')
    global out, capture,rec_frame

    while (cap.isOpened()):

        ret, frame= cap.read()
        if correct_corner != 42:
            frame = rotate(frame, correct_corner)
        if ret:
            if(grey):
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            if(neg):
                frame=cv2.bitwise_not(frame)    
            if(capture):
                capture=0
                now = datetime.datetime.now()
                pres_time = str(now.strftime("%d-%m-%Y %H:%M:%S"))
                p = os.path.sep.join(['shots', "shot_{}.png".format(pres_time.replace(":",''))])
                cv2.imwrite(p, frame)
            
            if(rec):
                rec_frame=frame
                frame= cv2.putText(cv2.flip(frame,1),"Recording...", (0,25), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255),4)
            frame = cv2.imencode('.JPEG', frame, [cv2.IMWRITE_JPEG_QUALITY, 20])[1].tobytes()
            yield b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n'
        else:
            break

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/res', methods=['POST', 'GET'])
def res():
    if request.method == 'POST':
        global result
        result = request.form.to_dict()
        return render_template("results.html", result=result)


@app.route('/video_feed')
def video_feed():
    params = result
    return Response(pyshine_process(params, cap), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/results',methods=['POST','GET'])
def tasks():
    global switch,camera
    if request.method == 'POST':
        if request.form.get('click') == 'Capture':
            global capture
            capture=1
        elif  request.form.get('grey') == 'Grey':
            global grey
            grey=not grey
        elif  request.form.get('neg') == 'Negative':
            global neg
            neg=not neg
       
        elif  request.form.get('rec') == 'Start/Stop Recording':
            global rec, out
            rec= not rec
            if(rec):
                
                now = datetime.datetime.now()
                pres_time = str(now.strftime("%d-%m-%Y-%H:%M:%S")) 
                fourcc =  cv2.VideoWriter_fourcc(* 'XVID')
                # width= int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                # height= int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                # fps = int(cap.get(cv2.CAP_PROP_FPS))
                width = 640
                height = 480
                fps = 20
                out = cv2.VideoWriter('vid_{}.mp4'.format(pres_time.replace(":",'')), fourcc, fps, (width, height))
                #Start new thread for recording the video
                print(out)
                thread = Thread(target = record, args=[out,])
                thread.start()
            elif(rec==False):
                out.release()
                          
                 
    elif request.method=='GET':
        return render_template('results.html')
    return render_template('results.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000', debug=False)

cap.release()
cv2.destroyAllWindows
