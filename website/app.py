from flask import Flask
from flask import render_template, Response
from datetime import datetime
from flask_moment import Moment

app = Flask(__name__)
moment = Moment(app)

# Root URL
@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')


@app.route('/live')
def live_feed():
    return render_template('live.html', location='In the woods')

