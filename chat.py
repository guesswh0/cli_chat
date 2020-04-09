__version__ = '0.3.0-dev'

import asyncio
import sys
import time

import click


async def write_msg(writer, msg: str):
    data = msg.encode()
    writer.write(len(data).to_bytes(4, sys.byteorder))
    writer.write(data)
    await writer.drain()


async def read_msg(reader):
    data = await reader.readexactly(4)
    size = int.from_bytes(data, sys.byteorder)
    msg = await reader.readexactly(size)
    return msg.decode()


async def monitor(reader, writer):
    addr = writer.get_extra_info('peername')
    username = await read_msg(reader)
    print(f"({time.strftime('%X')}) {addr!r}: {username} is connected")

    try:
        while True:
            msg = await read_msg(reader)
            if msg:
                print(f"({time.strftime('%X')}) {username}: {msg}")
    except asyncio.streams.IncompleteReadError:
        print(f"({time.strftime('%X')}) {addr!r}: {username} closed connection")
    finally:
        writer.close()


async def handle_client(username, host, port):
    reader, writer = await asyncio.open_connection(host, port)
    await write_msg(writer, username)

    try:
        while True:
            message = input()
            if message == 'exit':
                break
            await write_msg(writer, message)
    finally:
        print('Closing connection')
        writer.close()


@click.group()
def chat():
    pass


@chat.command()
@click.option('--host', help='Server host', default='127.0.0.1')
@click.option('--port', help='Server port', type=int, default=5001)
def server(host, port):
    loop = asyncio.get_event_loop()
    coro = asyncio.start_server(monitor, host, port)
    serv = loop.run_until_complete(coro)
    # Serve requests until Ctrl+C is pressed
    print('Serving on {}'.format(serv.sockets[0].getsockname()))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        serv.close()
    loop.run_until_complete(serv.wait_closed())
    loop.close()


@chat.command()
@click.argument('username', default='anonymous')
@click.option('--host', help='Server host', default='127.0.0.1')
@click.option('--port', help='Server port', type=int, default=5001)
def client(username, host, port):
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(handle_client(username, host, port))
    except KeyboardInterrupt:
        loop.close()


if __name__ == '__main__':
    chat()
