# coding: UTF-8
"""Encoding/decoding functions for audio packet - conversion for pydub ``AudioSegment``

More detail of packet protocol, see ``packet-protocol.md``

Note:
  Audio format (e.g. sample rate, channels) must be specified in ``AUDIO_PARAM.py``.
  It supports only monaural audio, not for multi channels.

Author: aKuad

"""

from pydub import AudioSegment

from . import AUDIO_PARAM


AUDIO_PACKET_TYPE_ID = 0x10
"""int: Packet type ID of audio packet
"""

SILENT_AUDIO_PACKET_TYPE_ID = 0x11
"""int: Packet type ID of silent audio packet
"""


def encode(audio_pcm: AudioSegment, lane_name: str, ext_bytes: bytes = b"", silent_threshold_dbfs: float = -20.0) -> bytes:
  """Create audio packet from ``pydub.AudioSegment``

  Args:
    audio_pcm(pydub.AudioSegment): Audio PCM in ``pydub.AudioSegment``, expects int16 type
    lane_name(str): Lane name of view in mixer-client
    ext_bytes(bytes): User's custom external bytes
    silent_threshold_dbfs(float): Under this dBFS audio_pcm passed, silent audio packet will be created

  Note:
    * ``lane_name`` can be 0~3 characters
    * ``ext_bytes`` can contain 0~255 bytes

  Return:
    bytes: Audio packet or silent audio packet

  Raises:
    TypeError: If ``audio_pcm`` is not ``pydub.AudioSegment``
    TypeError: If ``lane_name`` is not ``str``
    TypeError: If ``ext_bytes`` is not ``bytes``
    ValueError: If ``lane_name`` is non ascii
    ValueError: If ``lane_name`` has over 3 characters
    ValueError: If ``ext_bytes`` has over 255 bytes

  """
  # Arguments type checking
  if(type(audio_pcm) != AudioSegment):
    raise TypeError(f"audio_pcm must be AudioSegment, but got {type(audio_pcm)}")
  if(type(lane_name) != str):
    raise TypeError(f"lane_name must be str, but got {type(lane_name)}")
  if(type(ext_bytes) != bytes):
    raise TypeError(f"ext_bytes must be bytes, but got {type(ext_bytes)}")

  # Arguments range checking
  if(not lane_name.isascii()):
    raise ValueError("For lane_name, non ascii characters are not allowed")
  if(len(lane_name) > 3):
    raise ValueError("For lane_name, over 3 characters string is not allowed")
  if(len(ext_bytes) > 255):
    raise ValueError("For ext_bytes, over 255 bytes data is not allowed")

  lane_name = (lane_name + "   ")[:3]  # for fill spaces if under 3 characters

  if(audio_pcm.dBFS < silent_threshold_dbfs):
    return SILENT_AUDIO_PACKET_TYPE_ID.to_bytes(1, "little") + lane_name.encode() + len(ext_bytes).to_bytes(1, "little") + ext_bytes
  else:
    return AUDIO_PACKET_TYPE_ID.to_bytes(1, "little") + lane_name.encode() + len(ext_bytes).to_bytes(1, "little") + ext_bytes + audio_pcm.raw_data


def decode(raw_packet: bytes) -> tuple[AudioSegment, str, bytes]:
  """Unpack audio packet to ``pydub.AudioSegment``

  Note:
    About raises, see reference of `is_audio_packet`.

  Args:
    raw_packet(bytes): Audio or Silent audio packet

  Return:
    tuple[pydub.AudioSegment, str, bytes]: Decoded data - Audio PCM in ``pydub.AudioSegment``, lane name and external bytes

  """
  is_audio_packet(raw_packet, True)

  # Arguments range checking
  if(len(raw_packet) < 5):
    raise ValueError("Invalid packet, too short bytes received")

  lane_name = raw_packet[1 : 4].decode()
  ext_bytes_len = raw_packet[4]
  ext_bytes = raw_packet[5 : 5 + ext_bytes_len]

  if(raw_packet[0] == SILENT_AUDIO_PACKET_TYPE_ID):
    audio_pcm_len = int(AUDIO_PARAM.ONE_FRAME_SAMPLES * AUDIO_PARAM.ONE_SAMPLE_BYTES * AUDIO_PARAM.CHANNELS)
    audio_pcm = AudioSegment(bytes(audio_pcm_len),
                             sample_width=AUDIO_PARAM.ONE_SAMPLE_BYTES,
                             frame_rate=AUDIO_PARAM.SAMPLE_RATE,
                             channels=AUDIO_PARAM.CHANNELS)
  else:
    audio_pcm_raw = raw_packet[5 + ext_bytes_len :]
    audio_pcm = AudioSegment(audio_pcm_raw,
                            sample_width=AUDIO_PARAM.ONE_SAMPLE_BYTES,
                            frame_rate=AUDIO_PARAM.SAMPLE_RATE,
                            channels=AUDIO_PARAM.CHANNELS)

  return (audio_pcm, lane_name, ext_bytes)


def is_audio_packet(raw_packet: bytes, raise_on_invalid: bool = False):
  """Verify the packet is audio packet or silent audio packet

  Args:
    raw_packet(bytes): Packet to verify
    raise_on_invalid(bool): Toggle behavior if packet is invalid, true: raise exception, false: return false

  Returns:
    bool: It is an audio packet: true, otherwise: false (if throw_on_invalid === true, error will be thrown)

  Raises:
    TypeError: If ``raw_packet`` is not ``bytes``
    ValueError: If ``raw_packet`` is an empty bytes
    ValueError: If `raw_packet` is not an audio packet or silent audio packet
    ValueError: If `raw_packet` is too short bytes as audio packet
    ValueError: If `raw_packet` is too long bytes as audio packet
    ValueError: If `raw_packet` is too long bytes as silent audio packet

  """
  # Arguments type checking
  if(type(raw_packet) != bytes):
    if not raise_on_invalid:
      return False
    raise TypeError(f"raw_packet must be bytes, but got {type(raw_packet)}")

  # Packet content availability checking
  if(len(raw_packet) == 0):
    if not raise_on_invalid:
      return False
    raise ValueError("Empty bytes passed")

  # Packet type ID checking
  if(raw_packet[0] != AUDIO_PACKET_TYPE_ID and raw_packet[0] != SILENT_AUDIO_PACKET_TYPE_ID):
    if not raise_on_invalid:
      return False
    raise ValueError("It is not an audio packet or silent audio packet")

  # Packet length checking
  if(len(raw_packet) < 5):
    if not raise_on_invalid:
      return False
    raise ValueError("Too short bytes received, external bytes length missing")

  # Packet length checking (for [non]silent pattern)
  if  (raw_packet[0] == AUDIO_PACKET_TYPE_ID):
    EXPECTED_LENGTH = 5 + raw_packet[4] + AUDIO_PARAM.ONE_FRAME_SAMPLES * AUDIO_PARAM.ONE_SAMPLE_BYTES
    if  (len(raw_packet) < EXPECTED_LENGTH):
      if not raise_on_invalid:
        return False
      raise ValueError("Too short bytes as audio packet")
    elif(len(raw_packet) > EXPECTED_LENGTH):
      if not raise_on_invalid:
        return False
      raise ValueError("Too long bytes as audio packet")
  elif(raw_packet[0] == SILENT_AUDIO_PACKET_TYPE_ID):
    EXPECTED_LENGTH = 5 + raw_packet[4]
    # # Error of ValueError("Too short bytes as audio packet") will be matched as
    # #          ValueError("Too short bytes received, external bytes length missing")
    # if  (len(raw_packet) < EXPECTED_LENGTH):
    #   if not raise_on_invalid:
    #     return False
    #   raise ValueError("Too short bytes as audio packet")
    if  (len(raw_packet) > EXPECTED_LENGTH):
      if not raise_on_invalid:
        return False
      raise ValueError("Too long bytes as silent audio packet")

  return True
