import json
import os
import random as rand

from flask import Flask
from flask_socketio import SocketIO
from threading import Thread, Event
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'random_secret!'
app.config['DEBUG'] = True

# turn the flask app into a socketio app
socketio = SocketIO(app, async_mode=None, logger=True, engineio_logger=True, cors_allowed_origins='*')

thread = Thread()
thread_stop = Event()
config = None


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    return response


@app.route("/configuration/get")
def get_configuration():
    result = config
    if result is None:
        result = read_configuration()
    return result


@socketio.on('connect', namespace='/elements')
def connect():
    global thread
    print('Client connected')

    global config
    config = get_configuration()

    if not thread.isAlive():
        print("Start sending data to client")
        thread = socketio.start_background_task(output_elements)


@socketio.on('disconnect', namespace='/elements')
def disconnect():
    print('Client disconnected')


@socketio.on('stop_fetch_data', namespace='/elements')
def stop_fetch_data():
    print('Stop sending data to client')
    # stop data feed
    global thread_stop
    thread_stop.set()


@socketio.on('start_fetch_data', namespace='/elements')
def start_fetch_data():
    print('Start sending data to client')
    # re-start data feed
    global thread_stop
    thread_stop = Event()


@socketio.on('update_config', namespace='/elements')
def update_config(new_config):
    print('Updating configuration...')
    # Update config
    global config
    config = new_config


def output_elements():
    """
    The server should output the number of elements at a frequency configured for symbols.
    The price should be randomly generated.
    """
    print("Feeding new data")
    global config
    symbol_list = config["symbols"]

    while not thread_stop.isSet():
        elements = []
        create_time = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
        update_frequency = int(config["update_frequency_milliseconds"])
        elements_per_update = int(config["elements_per_update"])
        for symbol in symbol_list:
            for i in range(elements_per_update):
                price = rand.randrange(1, 1000, 2)
                elements.append({'symbol': symbol, 'price': price, 'create_time': create_time})
        socketio.emit('new_data', elements, namespace='/elements')
        socketio.sleep(update_frequency / 1000)


def read_configuration():
    filename = os.path.join(app.static_folder, 'configuration.json')
    with open(filename) as blog_file:
        data = json.load(blog_file)
        return data


if __name__ == '__main__':
    socketio.run(app)
