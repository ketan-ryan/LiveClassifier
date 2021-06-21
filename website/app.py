from flask import Flask, render_template, Response
from video_handler import gen_frame
import requests

app = Flask(__name__)


# Root URL
@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')


def get_loc():
    try:
        ip = requests.get('https://ipinfo.io/')
        ip = ip.json()
        string = f"{ip['loc']} {ip['city']}, {ip['region']}"
        return string

    except Exception as e:
        return str(e)


@app.route('/live')
def live_feed():
    return render_template('live.html', location=get_loc())


@app.route('/video_feed')
def video_feed():
    return Response(gen_frame(), mimetype='multipart/x-mixed-replace; boundary=frame')


# DEBUG NEEDS TO BE FALSE FOR MULTITHREADING
if __name__ == '__main__':
    app.run(debug=False, threaded=True
            # , host="0.0.0.0"
            )
