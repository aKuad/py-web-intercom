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

  Args:
    raw_packet(bytes): Audio or Silent audio packet

  Return:
    tuple[pydub.AudioSegment, str, bytes]: Decoded data - Audio PCM in ``pydub.AudioSegment``, lane name and external bytes

  Raises:
    TypeError: If ``raw_packet`` is not ``bytes``
    ValueError: If ``raw_packet`` is an empty bytes
    ValueError: If ``raw_packet`` type ID bytes is not audio packet type ID
    ValueError: If ``raw_packet`` is too short (external bytes info is missing)

  """
  # Packet type verification
  if(not is_audio_packet(raw_packet)):
    raise ValueError("Invalid packet, it is not an audio packet")

  # Arguments range checking
  if(len(raw_packet) < 5):
    raise ValueError("Invalid packet, too short bytes received")

  lane_name = raw_packet[1 : 4].decode()
  ext_bytes_len = raw_packet[4]
  ext_bytes = raw_packet[5 : 5 + ext_bytes_len]

  if(raw_packet[0] == SILENT_AUDIO_PACKET_TYPE_ID):
    audio_pcm_len = int(AUDIO_PARAM.SAMPLE_RATE * AUDIO_PARAM.FRAME_DURATION_SEC * AUDIO_PARAM.ONE_SAMPLE_BYTES * AUDIO_PARAM.CHANNELS)
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


def is_audio_packet(raw_packet):
  """Verify the packet is audio packet or silent audio packet

  Note: It verify only type and packet ID. Packet structure will not be verified.

  Args:
    raw_packet(bytes): Packet to verify

  Returns:
    bool: It is an audio packet: true, otherwise: false

  Raises:
    TypeError: If ``raw_packet`` is not ``bytes``
    ValueError: If ``raw_packet`` is an empty bytes

  """
  # Arguments type checking
  if(type(raw_packet) != bytes):
    raise TypeError(f"raw_packet must be bytes, but got {type(raw_packet)}")

  # Packet content availability checking
  if(len(raw_packet) == 0):
    raise ValueError("Empty bytes passed")

  if(raw_packet[0] == AUDIO_PACKET_TYPE_ID or raw_packet[0] == SILENT_AUDIO_PACKET_TYPE_ID):
    return True
  else:
    return False
