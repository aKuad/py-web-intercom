# coding: UTF-8
"""Tests for ``packet_conv/audio_ndarray.py``

Test cases:
  * Can encode/decode audio packet from/to ``ndarray`` with[out] custom bytes to bytes
  * Can encode/decode silent audio packet from/to ``ndarray`` with[out] custom bytes to bytes
  * Can create silent audio packet when the audio dBFS is less than threshold
  * Raise TypeError if invalid argument is passed
  * Raise ValueError if invalid argument is passed
  * Can check an bytes is correct audio/silent-audio packet
  * Raise TypeError or ValueError if non audio/silent-audio packet is passed to decode function

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
from util.rand_ndarray_int import generate_rand_ndarray_int


class Test_packet_conv_audio_ndarray(unittest.TestCase):
  @classmethod
  def setUpClass(self):
    self.TEST_AUDIO_SHAPE = (AUDIO_PARAM.ONE_FRAME_SAMPLES, AUDIO_PARAM.CHANNELS)
    self.TEST_AUDIO_PCM = generate_rand_ndarray_int(self.TEST_AUDIO_SHAPE, AUDIO_PARAM.DTYPE)
    self.SILENT_AUDIO_PCM = np.zeros(self.TEST_AUDIO_SHAPE, AUDIO_PARAM.DTYPE)


  def test_true_enc_dec_verify_ext(self):
    audio_pcm_org = self.TEST_AUDIO_PCM
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
    audio_pcm_org = self.TEST_AUDIO_PCM
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
    audio_pcm_org = self.TEST_AUDIO_PCM
    audio_pcm_org = audio_pcm_org * 0.1 # Apply gain -20[dB] = 10 ** (-20/20) = 0.1
    audio_pcm_org = audio_pcm_org.astype(np.int16)
    lane_name_org = "ABC"
    ext_bytes_org = bytes([1, 2, 3, 4])

    raw_packet = audio_ndarray.encode(audio_pcm_org, lane_name_org, ext_bytes_org)
    audio_pcm_prc, lane_name_prc, ext_bytes_prc = audio_ndarray.decode(raw_packet)

    self.assertEqual(raw_packet[0], audio_ndarray.SILENT_AUDIO_PACKET_TYPE_ID)
    self.assertTrue(audio_ndarray.is_audio_packet(raw_packet))
    self.assertTrue((self.SILENT_AUDIO_PCM == audio_pcm_prc).all())
    self.assertEqual(lane_name_org, lane_name_prc)
    self.assertEqual(ext_bytes_org, ext_bytes_prc)#


  def test_true_enc_dec_verify_silent_noext(self):
    audio_pcm_org = self.TEST_AUDIO_PCM
    audio_pcm_org = audio_pcm_org * 0.1 # Apply gain -20[dB] = 10 ** (-20/20) = 0.1
    audio_pcm_org = audio_pcm_org.astype(np.int16)
    lane_name_org = "ABC"
    ext_bytes_org = bytes()

    raw_packet = audio_ndarray.encode(audio_pcm_org, lane_name_org, ext_bytes_org)
    audio_pcm_prc, lane_name_prc, ext_bytes_prc = audio_ndarray.decode(raw_packet)

    self.assertEqual(raw_packet[0], audio_ndarray.SILENT_AUDIO_PACKET_TYPE_ID)
    self.assertTrue(audio_ndarray.is_audio_packet(raw_packet))
    self.assertTrue((self.SILENT_AUDIO_PCM == audio_pcm_prc).all())
    self.assertEqual(lane_name_org, lane_name_prc)
    self.assertEqual(ext_bytes_org, ext_bytes_prc)#


  # def test_true_verify_ng(self):
  #   # is_audio_packet() implemented in `audio_aseg`, so this test omitted
  #   pass


  def test_err_enc_invalid_type(self):
    audio_pcm = self.TEST_AUDIO_PCM
    audio_pcm_invalid = audio_pcm.astype(np.float32)  # float32 as non int16  type
    lane_name = "ABC"
    ext_bytes = bytes([1,2,3])

    self.assertRaises(TypeError, audio_ndarray.encode, ""       , lane_name, ext_bytes) # str "" as non ndarray
    self.assertRaises(TypeError, audio_ndarray.encode, audio_pcm_invalid, lane_name, ext_bytes)
    self.assertRaises(TypeError, audio_ndarray.encode, audio_pcm, 1        , ext_bytes) # int 1 as non str
    self.assertRaises(TypeError, audio_ndarray.encode, audio_pcm, lane_name, "")        # str "" as non bytes


  def test_err_enc_invalid_value(self):
    audio_pcm = self.TEST_AUDIO_PCM
    lane_name = "ABC"
    ext_bytes = bytes([1,2,3])

    lane_name_non_ascii = "🗒"
    lane_name_over_len = "ABCD"
    ext_bytes_over_len = bytes(256)

    self.assertRaises(ValueError, audio_ndarray.encode, audio_pcm, lane_name_non_ascii, ext_bytes)
    self.assertRaises(ValueError, audio_ndarray.encode, audio_pcm, lane_name, ext_bytes_over_len)
    self.assertRaises(ValueError, audio_ndarray.encode, audio_pcm, lane_name_over_len, ext_bytes)


  # def test_err_dec_invalid_type(self):
  #   # packet verification integrated to `is_audio_packet` tests
  #   pass


  # def test_err_dec_invalid_value(self):
  #   # packet verification integrated to `is_audio_packet` tests
  #   pass


  # def test_err_verify_invalid_type(self):
  #   # no error cases of `is_audio_packet`
  #   pass


  # def test_err_verify_invalid_value(self):
  #   # no error cases of `is_audio_packet`
  #   pass


if __name__ == "__main__":
  unittest.main(verbosity=2)
