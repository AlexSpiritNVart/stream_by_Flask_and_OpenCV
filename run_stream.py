from flask import Flask, render_template, request, Response
from Camera import Cam

app = Flask(__name__, template_folder='templates')
camera = Cam()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/res', methods=['POST'])
def res():
    if request.method == 'POST':
        result = request.form.to_dict()
        camera.set_new_conf(result)
        return render_template("results.html")


@app.route('/video_feed')
def video_feed():
    camera.pyshine_process()
    return Response(camera.pyshine_process(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/results', methods=['POST', 'GET'])
def tasks():
    if request.method == 'POST':
        if request.form.get('click'):
            camera.make_capture()
        elif request.form.get('grey'):
            camera.grey = not camera.grey
        elif request.form.get('neg'):
            camera.neg = not camera.neg
        elif request.form.get('rec'):
            camera.rec = not camera.rec
            if camera.rec:
                camera.record()

            else:
                camera.stop_recording()
    return render_template('results.html')


if __name__ == '__main__':
    app.run(host='127.0.0.1', port='5000', debug=True)