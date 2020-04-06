import sys


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
