__version__ = '0.3.1'

import asyncio
import time

import click


class Chat:

    def __init__(self, host, port):
        self.connections = {}
        self.server = asyncio.start_server(self.accept_connection, host, port)

    def broadcast(self, msg):
        data = f"({time.strftime('%X')}) {msg} \n".encode('utf-8')
        for reader, writer in self.connections.values():
            writer.write(data)

    async def prompt_username(self, reader, writer):
        while True:
            writer.write("Enter username: ".encode("utf-8"))
            data = (await reader.readline()).decode("utf-8")
            if not data:
                return
            username = data.strip()
            if username and username not in self.connections:
                self.connections[username] = (reader, writer)
                return username
            writer.write(
                "Sorry, that username is already taken.\n".encode("utf-8"))

    async def handle_connection(self, username, reader):
        while True:
            data = (await reader.readline()).decode("utf-8")
            if not data:
                del self.connections[username]
                return
            self.broadcast(username + ": " + data.strip())

    async def accept_connection(self, reader, writer):
        print(f"{writer.get_extra_info('peername') !r}: is connected")
        writer.write("Welcome to tty chat \n".encode("utf-8"))
        username = await self.prompt_username(reader, writer)
        if username:
            self.broadcast("User %r has joined the room" % username)
            await self.handle_connection(username, reader)
            self.broadcast("User %r has left the room" % username)
        await writer.drain()


@click.command()
@click.option('--host', help='Server host', default='127.0.0.1')
@click.option('--port', help='Server port', type=int, default=5001)
def chat(host, port):
    loop = asyncio.get_event_loop()
    chat = Chat(host, port)
    server = loop.run_until_complete(chat.server)
    # Serve requests until Ctrl+C is pressed
    print('Serving chat on {}'.format(server.sockets[0].getsockname()))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()


if __name__ == '__main__':
    chat()
