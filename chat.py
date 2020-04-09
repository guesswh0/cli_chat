__version__ = '0.3.1-dev'

import asyncio
import time

import click

connections = {}


def broadcast(msg):
    data = f"({time.strftime('%X')}) {msg} + \n".encode('utf-8')
    for reader, writer in connections.values():
        writer.write(data)


async def prompt_username(reader, writer):
    while True:
        writer.write("Enter username: ".encode("utf-8"))
        data = (await reader.readline()).decode("utf-8")
        if not data:
            return
        username = data.strip()
        if username and username not in connections:
            connections[username] = (reader, writer)
            return username
        writer.write("Sorry, that username is already taken.\n".encode("utf-8"))


async def handle_connection(username, reader):
    while True:
        data = (await reader.readline()).decode("utf-8")
        if not data:
            del connections[username]
            return
        broadcast(username + ": " + data.strip())


async def accept_connection(reader, writer):
    print(f"{writer.get_extra_info('peername') !r}: is connected")
    writer.write("Welcome to tty chat \n".encode("utf-8"))
    username = await prompt_username(reader, writer)
    if username:
        broadcast("User %r has joined the room" % username)
        await handle_connection(username, reader)
        broadcast("User %r has left the room" % username)
    await writer.drain()


@click.command()
@click.option('--host', help='Server host', default='127.0.0.1')
@click.option('--port', help='Server port', type=int, default=5001)
def chat(host, port):
    loop = asyncio.get_event_loop()
    coro = asyncio.start_server(accept_connection, host, port)
    serv = loop.run_until_complete(coro)
    # Serve requests until Ctrl+C is pressed
    print('Serving chat on {}'.format(serv.sockets[0].getsockname()))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        serv.close()
    loop.run_until_complete(serv.wait_closed())
    loop.close()


if __name__ == '__main__':
    chat()
