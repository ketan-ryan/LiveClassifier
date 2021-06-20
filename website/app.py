from flask import Flask, render_template, Response, request
import cv2 as cv
import threading
import datetime
import requests
import time

# initialize the output frame and a lock used to ensure thread-safe
# exchanges of the output frames (useful when multiple browsers/tabs
# are viewing the stream)
outputFrame = None
lock = threading.Lock()

app = Flask(__name__)

# initialize the video stream and allow the camera sensor to
# warmup
capture = cv.VideoCapture(0)
time.sleep(2.0)


# Root URL
@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')


def get_country(ip_address):
    try:
        response = requests.get("http://ip-api.com/json/{}".format(ip_address))
        js = response.json()
        string = f"{js['lat']} {js['lon']} {js['city']}, {js['regionName']}"
        return string
    except Exception as e:
        return str(e)


@app.route('/live')
def live_feed():
    return render_template('live.html', location=get_country(request.remote_addr))


@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


def gen_frames():
    # grab global references to the video stream, output frame, and
    # lock variables
    global vs, outputFrame, lock
    total_frames = 0
    while True:
        success, frame = capture.read()
        if not success:
            break
        else:
            # frame = vsutils.resize(frame, width=400)

            timestamp = datetime.datetime.now()
            cv.putText(frame, timestamp.strftime('%b %d %Y, %I:%M:%S %p EST'), (10, frame.shape[0] - 10),
                       cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            ret, buffer = cv.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result


def generate():
    # grab global references to the output frame and lock variables
    global outputFrame, lock
    # loop over frames from the output stream
    while True:
        # wait until the lock is acquired
        with lock:
            # check if the output frame is available, otherwise skip
            # the iteration of the loop
            if outputFrame is None:
                continue
            # encode the frame in JPEG format
            (flag, encodedImage) = cv.imencode(".jpg", outputFrame)
            # ensure the frame was successfully encoded
            if not flag:
                continue
        # yield the output frame in the byte format
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
               bytearray(encodedImage) + b'\r\n')


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")

