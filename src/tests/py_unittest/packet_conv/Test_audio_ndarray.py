# coding: UTF-8
"""Tests for ``packet_conv/audio_ndarray.py``

Test cases:
  * Can encode/decode audio packet from/to ``ndarray`` with[out] custom bytes to bytes
  * Can encode/decode silent audio packet from/to ``ndarray`` with[out] custom bytes to bytes
  * Can create silent audio packet when the audio dBFS is less than threshold
  * Raise TypeError if invalid argument is passed
  * Raise ValueError if invalid argument is passed

Test steps:
  * Run this script by unittest - ``python3 -m unittest discover "Test_*.py"``

Author:
  aKuad

"""

# For import top layer module
import sys
from pathlib import Path
sys.path.append(Path(__file__).absolute().parent.parent.parent.parent.__str__())


import unittest

import numpy as np

from modules.packet_conv import AUDIO_PARAM, audio_ndarray


class Test_packet_conv_audio_ndarray(unittest.TestCase):
  def test_true_enc_dec_verify_ext(self):
    audio_pcm_org = part_create_random_ndarray()
    lane_name_org = "ABC"
    ext_bytes_org = bytes([1, 2, 3, 4])

    raw_packet = audio_ndarray.encode(audio_pcm_org, lane_name_org, ext_bytes_org)
    audio_pcm_prc, lane_name_prc, ext_bytes_prc = audio_ndarray.decode(raw_packet)

    self.assertEqual(raw_packet[0], audio_ndarray.AUDIO_PACKET_TYPE_ID)
    self.assertTrue(audio_ndarray.is_audio_packet(raw_packet))
    self.assertTrue((audio_pcm_org == audio_pcm_prc).all())
    self.assertEqual(lane_name_org, lane_name_prc)
    self.assertEqual(ext_bytes_org, ext_bytes_prc)


  def test_true_enc_dec_verify_noext(self):
    audio_pcm_org = part_create_random_ndarray()
    lane_name_org = "ABC"
    ext_bytes_org = bytes()

    raw_packet = audio_ndarray.encode(audio_pcm_org, lane_name_org, ext_bytes_org)
    audio_pcm_prc, lane_name_prc, ext_bytes_prc = audio_ndarray.decode(raw_packet)

    self.assertEqual(raw_packet[0], audio_ndarray.AUDIO_PACKET_TYPE_ID)
    self.assertTrue(audio_ndarray.is_audio_packet(raw_packet))
    self.assertTrue((audio_pcm_org == audio_pcm_prc).all())
    self.assertEqual(lane_name_org, lane_name_prc)
    self.assertEqual(ext_bytes_org, ext_bytes_prc)


  def test_true_enc_dec_verify_silent_ext(self):
    audio_pcm_org = part_create_random_ndarray()
    audio_pcm_org = audio_pcm_org * 0.1 # Apply gain -20[dB] = 10 ** (-20/20) = 0.1
    audio_pcm_org = audio_pcm_org.astype(np.int16)
    lane_name_org = "ABC"
    ext_bytes_org = bytes([1, 2, 3, 4])

    raw_packet = audio_ndarray.encode(audio_pcm_org, lane_name_org, ext_bytes_org)
    audio_pcm_prc, lane_name_prc, ext_bytes_prc = audio_ndarray.decode(raw_packet)

    self.assertEqual(raw_packet[0], audio_ndarray.SILENT_AUDIO_PACKET_TYPE_ID)
    self.assertTrue(audio_ndarray.is_audio_packet(raw_packet))
    self.assertTrue((part_create_silent_ndarray() == audio_pcm_prc).all())
    self.assertEqual(lane_name_org, lane_name_prc)
    self.assertEqual(ext_bytes_org, ext_bytes_prc)#


  def test_true_enc_dec_verify_silent_noext(self):
    audio_pcm_org = part_create_random_ndarray()
    audio_pcm_org = audio_pcm_org * 0.1 # Apply gain -20[dB] = 10 ** (-20/20) = 0.1
    audio_pcm_org = audio_pcm_org.astype(np.int16)
    lane_name_org = "ABC"
    ext_bytes_org = bytes()

    raw_packet = audio_ndarray.encode(audio_pcm_org, lane_name_org, ext_bytes_org)
    audio_pcm_prc, lane_name_prc, ext_bytes_prc = audio_ndarray.decode(raw_packet)

    self.assertEqual(raw_packet[0], audio_ndarray.SILENT_AUDIO_PACKET_TYPE_ID)
    self.assertTrue(audio_ndarray.is_audio_packet(raw_packet))
    self.assertTrue((part_create_silent_ndarray() == audio_pcm_prc).all())
    self.assertEqual(lane_name_org, lane_name_prc)
    self.assertEqual(ext_bytes_org, ext_bytes_prc)#


  def test_err_enc_invalid_type(self):
    audio_pcm = part_create_random_ndarray()
    audio_pcm_invalid = audio_pcm.astype(np.float32)  # float32 as non int16  type
    lane_name = "ABC"
    ext_bytes = bytes([1,2,3])

    self.assertRaises(TypeError, audio_ndarray.encode, ""       , lane_name, ext_bytes) # str "" as non ndarray
    self.assertRaises(TypeError, audio_ndarray.encode, audio_pcm_invalid, lane_name, ext_bytes)
    self.assertRaises(TypeError, audio_ndarray.encode, audio_pcm, 1        , ext_bytes) # int 1 as non str
    self.assertRaises(TypeError, audio_ndarray.encode, audio_pcm, lane_name, "")        # str "" as non bytes


  def test_err_enc_invalid_value(self):
    audio_pcm = part_create_random_ndarray()
    lane_name = "ABC"
    ext_bytes = bytes([1,2,3])

    lane_name_non_ascii = "🗒"
    lane_name_over_len = "ABCD"
    ext_bytes_over_len = bytes(256)

    self.assertRaises(ValueError, audio_ndarray.encode, audio_pcm, lane_name_non_ascii, ext_bytes)
    self.assertRaises(ValueError, audio_ndarray.encode, audio_pcm, lane_name, ext_bytes_over_len)
    self.assertRaises(ValueError, audio_ndarray.encode, audio_pcm, lane_name_over_len, ext_bytes)


  # def test_err_dec_invalid_type(self):
    # type checking will be tested in test_err_verify_invalid_type


  def test_err_dec_invalid_value(self):
    raw_packet_invalid_id = b"A" + b"ABC" + bytes([0]) + part_create_random_ndarray().tobytes()
    #                       ~~~~ as non 0x10 byte
    raw_packet_invalid_len = audio_ndarray.AUDIO_PACKET_TYPE_ID.to_bytes(1, "little") + b"ABC"
    # ext_bytes data missing packet

    self.assertRaises(ValueError, audio_ndarray.decode, raw_packet_invalid_id)
    self.assertRaises(ValueError, audio_ndarray.decode, raw_packet_invalid_len)


  def test_err_verify_invalid_type(self):
    self.assertRaises(TypeError, audio_ndarray.decode, "")  # str "" as non bytes


  def test_err_verify_invalid_value(self):
    raw_packet_invalid_empty = bytes()

    self.assertRaises(ValueError, audio_ndarray.is_audio_packet, raw_packet_invalid_empty)


def part_create_random_ndarray() -> np.ndarray:
  # Random bytes as random audio data
  return np.random.randint(-(2**15), (2**15)-1,
                           size=(int(AUDIO_PARAM.SAMPLE_RATE * AUDIO_PARAM.FRAME_DURATION_SEC), AUDIO_PARAM.CHANNELS),
                           dtype=AUDIO_PARAM.DTYPE)


def part_create_silent_ndarray() -> np.ndarray:
  return np.zeros(int(AUDIO_PARAM.SAMPLE_RATE * AUDIO_PARAM.FRAME_DURATION_SEC * AUDIO_PARAM.CHANNELS), dtype=AUDIO_PARAM.DTYPE)


if __name__ == "__main__":
  unittest.main(verbosity=2)
