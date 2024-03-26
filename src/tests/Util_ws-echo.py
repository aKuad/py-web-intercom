# coding: UTF-8
"""Trying utility for for ``client.py``

To try features:
  * Can send audio on websocket
  * Can receive audio from websocket and play

Author:
  aKuad

"""

import asyncio
from websockets.server import serve, WebSocketServerProtocol


async def ws_main(ws: WebSocketServerProtocol):
  print(f"Connected: {ws.id}, {ws.host}")
  try:
    async for mes in ws:
      await ws.send(mes)
    await ws.close()
    print(f"Disconnected in success: {ws.id}, {ws.host}")
  except Exception as e:
    print(f"Disconnected in error: {ws.id}, {ws.host}")
    print(e)

async def main():
  async with serve(ws_main, port=8765):
    await asyncio.Future()


if __name__ == "__main__":
  try:
    print("Server start")
    asyncio.run(main())
  except KeyboardInterrupt:
    print("Server end")
