import json
from threading import Thread
import websocket

class WebSocketEventHandler:
    """
    Class for SockJS WebSocket communication

    params:
    url - URL of Printer
    on_open - callback function with 1 argument, API of WebSocketApp
            - executes on creating new connection
    on_close - callback function with 1 argument, API of WebSocketApp
             - executes on connection close
    on_message - callback function with 2 arguments, API of WebSocketApp
                 and message in dict format
               - executes on received message, if array, then it executes
                 for every value of given array
    """
    def __init__(self, url, on_open=None, on_close=None, on_message=None):
        self.url = url
        self.on_open = on_open
        self.on_close = on_close
        self.on_message = on_message
        self.socket = None
        self.thread = None

    def run(self):
        """
        Runs thread, which listens on socket.
        Executes given callbacks on events
        """
        def on_message(ws, data):
            if data.startswith('m'):
                self.on_message(ws, json.loads(data[1:]))
            elif data.startswith('a'):
                for msg in json.loads(data[1:]):
                    self.on_message(ws, msg)

        self.socket = websocket.WebSocketApp(
            self.url,
            on_open=self.on_open,
            on_close=self.on_close,
            on_message=on_message
        )
        self.thread = Thread(target=self.socket.run_forever)
        self.thread.daemon = True
        self.thread.start()

    def send(self, data):
        """
        Sends data, currently not working properly.
        OctoPrint server is unable to parse.
        """
        self.socket.send(json.dumps(data))
