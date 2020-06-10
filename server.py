from rich.panel import Panel
import sys
import signal
import os
import asyncio
import websockets
import json
from websockets.exceptions import ConnectionClosedOK
from rich import print
from rich.traceback import install
from rich.console import Console


console = Console(color_system='truecolor')
install()
SOCKET_PORT = 5679
clients = {}  # client pools


# Handle sigterm to quit server
def signal_handler(sig, frame):
    os.system('clear')
    console.print('[red]Socket Server is terminated.[/red]')
    sys.exit(0)


@asyncio.coroutine
def socket_download(websocket, path):
    data = yield from websocket.recv()

    if not isinstance(data, str):
        data = data.decode('utf-8')
        data = json.loads(data.replace("'", "\""))
    else:
        data = json.loads(data)

    console.print(
        '[blue]{} current clients[/blue]. [green]New client[/green]: [bold]{}[/bold]'.format(len(clients)+1, data['name']))
    clients[websocket] = data['name']

    try:
        for client, _ in clients.items():
            if 'target' in data:
                if _ == data['target']:
                    yield from client.send(json.dumps(data))

        # Handle messages from this client
        while True:
            message = yield from websocket.recv()

    except ConnectionClosedOK:
        clients.pop(websocket)
        console.print('[green]Connection from [bold]' +
                      data['name'] + '[/bold] closed.[/green]')


def start_server():
    signal.signal(signal.SIGINT, signal_handler)
    start_server = websockets.serve(socket_download, port=SOCKET_PORT)
    os.system('clear')
    console.print(
        Panel('[bold magenta]Socket Server is running at port {}... [/bold magenta]'.format(SOCKET_PORT)))
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()


if __name__ == '__main__':
    start_server()
