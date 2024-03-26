# coding: UTF-8
"""Minimum voice client

It has only mic audio sending, receiving and playing features.
Useful for server debugging.

Author:
  aKuad

"""

from sys import argv

import sounddevice as sd
from websockets.sync.client import connect
import numpy as np

from modules.packet_conv import packet_enc_ndarray, packet_dec_ndarray
import AUDIO_PARAM


if __name__ == "__main__":
  if len(argv) >= 2:
    SERVER_URI = argv[1]
  else:
    SERVER_URI = "ws://localhost:8765"

  ws = connect(SERVER_URI)

  def callback(indata: np.ndarray, outdata: np.ndarray, frames, time, status):
    packet_send = packet_enc_ndarray(indata, bytes())
    ws.send(packet_send)
    packet_recv = ws.recv()
    outdata[:], _ = packet_dec_ndarray(packet_recv)


  try:
    with sd.Stream(channels=1,
                   samplerate=AUDIO_PARAM.SAMPLE_RATE,
                   blocksize=int(AUDIO_PARAM.SAMPLE_RATE/10),  # One sample size is 1/10 seconds
                   dtype=AUDIO_PARAM.DTYPE,
                   callback=callback):
      print("Start streaming")
      while(True):      # Infinite waiting loop
        sd.sleep(1000)  #   1000 (1 sec) has no special meaning
  except KeyboardInterrupt:
    ws.close()
    print("end")
