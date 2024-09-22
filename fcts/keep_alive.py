from flask import Flask
from threading import Thread
from gevent.pywsgi import WSGIServer
from flask_compress import Compress

app = Flask('')
compress = Compress()
compress.init_app(app)


@app.route('/')
def home():
    return "Bot is online"


def run():
    http_server = WSGIServer(('0.0.0.0', 8080), app)
    http_server.serve_forever()


def keep_alive():
    t = Thread(target=run)
    t.start()
