import cv2
import datetime
import os


class Cam:

    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.frame = []
        self.rec = False
        self.grey = False
        self.neg = False
        self.rec_frame = []

    def __del__(self):
        cap.release()
        cv2.destroyAllWindows

    def set_new_conf(self, params):
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, int(params['width']))
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, int(params['height']))
        self.cap.set(cv2.CAP_PROP_BRIGHTNESS, int(params['brightness']))
        self.cap.set(cv2.CAP_PROP_CONTRAST, int(params['contrast']))
        self.cap.set(cv2.CAP_PROP_SATURATION, int(params['saturation']))
        self.cap.set(cv2.CAP_PROP_HUE, int(params['hue']))
        self.cap.set(cv2.CAP_PROP_GAIN, int(params['gain']))
        self.cap.set(cv2.CAP_PROP_EXPOSURE, int(params['exposure']))
        self.cap.set(cv2.CAP_PROP_SHARPNESS, int(params['sharpness']))
        self.correct_corner = int(params['rotate'])

    def record(self):
        now = datetime.datetime.now()
        pres_time = str(now.strftime("%d-%m-%Y-%H:%M:%S"))
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        width = 640
        height = 480
        fps = 20
        out = cv2.VideoWriter('vid_{}.mp4'.format(pres_time.replace(":", '')), fourcc, fps,
                              (width, height))
        while self.rec:
            out.write(self.rec_frame)
        out.release()

    def stop_recording(self):
        self.rec = False

    def correct_rotate(self):
        if self.correct_corner == 0:
            correct_corner = False
        elif self.correct_corner == 90:
            correct_corner = cv2.ROTATE_90_CLOCKWISE
        elif self.correct_corner == 180:
            correct_corner = cv2.ROTATE_180
        elif self.correct_corner == 270:
            correct_corner = cv2.ROTATE_90_COUNTERCLOCKWISE
        return correct_corner

    def make_capture(self):
        now = datetime.datetime.now()
        pres_time = str(now.strftime("%d-%m-%Y %H:%M:%S"))
        p = os.path.sep.join(['shots', "shot_{}.png".format(pres_time.replace(":", ''))])
        cv2.imwrite(p, self.frame)

    def pyshine_process(self):
        correct_corner = self.correct_rotate()

        while self.cap.isOpened():
            ret, frame = self.cap.read()

            if correct_corner:
                frame = cv2.rotate(frame, correct_corner)
            if ret:
                if self.grey:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                if self.neg:
                    frame = cv2.bitwise_not(frame)
                if self.rec:
                    self.rec_frame = cv2.putText(cv2.flip(frame, 1), "Recording...", (0, 25), cv2.FONT_HERSHEY_SIMPLEX,
                                                 1,
                                                 (0, 0, 255), 4)
                self.frame = frame
                frame = cv2.imencode('.JPEG', frame, [cv2.IMWRITE_JPEG_QUALITY, 20])[1].tobytes()
                yield b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n'
            else:
                break