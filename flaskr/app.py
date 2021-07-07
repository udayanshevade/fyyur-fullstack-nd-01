from flask import Flask
from flask_moment import Moment

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('flaskr.config')
