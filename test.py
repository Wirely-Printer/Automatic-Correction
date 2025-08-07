import json
from threading import Thread
from octorest import OctoRest
from websocket_event_handler import WebSocketEventHandler
import websocket

# OctoRest client setup
def make_client():
    try:
        client = OctoRest(url="http://localhost:5000", apikey="5D60CE27902F4486AFD8112B24449923")
        return client
    except Exception as e:
        print(e)

def get_version(client):
    try:
        return "You are using OctoPrint v" + client.version['server'] + "\n"
    except Exception as e:
        print(e)

def get_printer_info(client):
    try:
        message = ""
        message += str(client.version) + "\n"
        message += str(client.job_info()) + "\n"
        printing = client.printer()['state']['flags']['printing']
        if printing:
            message += "Currently printing!\n"
        else:
            message += "Not currently printing...\n"
        return message
    except Exception as e:
        print(e)

def move_absolute(client, x, y, z, speed):
    try:
        gcode_command = f"G1 X{x} Y{y} Z{z} F{speed}"
        client.gcode(command=gcode_command)
        print(f"Moving to absolute position X={x}, Y={y}, Z={z} at speed {speed}")
    except Exception as e:
        print("Error moving printer:", e)

# WebSocket client to listen for terminal logs
def handle_message(ws, message):
    """
    Callback to process each message from the WebSocket.
    Prints terminal log messages received from OctoPrint.
    """
    data = json.loads(message)
    if 'logs' in data:
        for log_entry in data['logs']:
            print("Terminal Log:", log_entry)

def start_websocket():
    url = "ws://localhost:5000/sockjs/websocket"  # Replace with your OctoPrint WebSocket URL
    ws_client = WebSocketEventHandler(url, on_message=handle_message)
    ws_client.run()


def main():
    client = make_client()
    ws_thread = Thread(target=start_websocket)
    ws_thread.daemon = True
    ws_thread.start()

    # Example commands
    #print(get_version(client))
    # print(get_printer_info(client))
    # move_absolute(client, 100, 100, 20, 300)
    

if __name__ == "__main__":
    main()
