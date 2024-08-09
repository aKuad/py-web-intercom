# coding: UTF-8
"""Tests for ``packet_conv/aseg.py``

Test cases:
  * Can encode/decode audio packet from/to ``AudioSegment`` with[out] custom bytes to bytes
  * Can encode/decode silent audio packet from/to ``AudioSegment`` with[out] custom bytes to bytes
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

from modules.packet_conv import AUDIO_PARAM, audio_aseg
from util.rand_aseg import generate_random_audioseg
from util.silent_aseg import create_silent_aseg


class Test_packet_conv_audio_aseg(unittest.TestCase):
  @classmethod
  def setUpClass(self):
    self.TEST_AUDIO_PCM = generate_random_audioseg(AUDIO_PARAM.SAMPLE_RATE,
                                                   AUDIO_PARAM.ONE_SAMPLE_BYTES,
                                                   AUDIO_PARAM.CHANNELS,
                                                   AUDIO_PARAM.FRAME_DURATION_SEC)
    self.SILENT_AUDIO_PCM = create_silent_aseg(AUDIO_PARAM.SAMPLE_RATE,
                                               AUDIO_PARAM.ONE_SAMPLE_BYTES,
                                               AUDIO_PARAM.CHANNELS,
                                               AUDIO_PARAM.FRAME_DURATION_SEC)


  def test_true_enc_dec_verify_ext(self):
    audio_pcm_org = self.TEST_AUDIO_PCM
    lane_name_org = "ABC"
    ext_bytes_org = bytes([1, 2, 3, 4])

    raw_packet = audio_aseg.encode(audio_pcm_org, lane_name_org, ext_bytes_org)
    audio_pcm_prc, lane_name_prc, ext_bytes_prc = audio_aseg.decode(raw_packet)

    self.assertEqual(raw_packet[0], audio_aseg.AUDIO_PACKET_TYPE_ID)
    self.assertTrue(audio_aseg.is_audio_packet(raw_packet))
    self.assertEqual(audio_pcm_org, audio_pcm_prc)
    self.assertEqual(lane_name_org, lane_name_prc)
    self.assertEqual(ext_bytes_org, ext_bytes_prc)


  def test_true_enc_dec_verify_noext(self):
    audio_pcm_org = self.TEST_AUDIO_PCM
    lane_name_org = "ABC"
    ext_bytes_org = bytes()

    raw_packet = audio_aseg.encode(audio_pcm_org, lane_name_org, ext_bytes_org)
    audio_pcm_prc, lane_name_prc, ext_bytes_prc = audio_aseg.decode(raw_packet)

    self.assertEqual(raw_packet[0], audio_aseg.AUDIO_PACKET_TYPE_ID)
    self.assertTrue(audio_aseg.is_audio_packet(raw_packet))
    self.assertEqual(audio_pcm_org, audio_pcm_prc)
    self.assertEqual(lane_name_org, lane_name_prc)
    self.assertEqual(ext_bytes_org, ext_bytes_prc)


  def test_true_enc_dec_verify_silent_ext(self):
    audio_pcm_org = self.TEST_AUDIO_PCM
    audio_pcm_org -= 20.0 # Make audio too silent
    lane_name_org = "ABC"
    ext_bytes_org = bytes([1, 2, 3, 4])

    raw_packet = audio_aseg.encode(audio_pcm_org, lane_name_org, ext_bytes_org)
    audio_pcm_prc, lane_name_prc, ext_bytes_prc = audio_aseg.decode(raw_packet)

    self.assertEqual(raw_packet[0], audio_aseg.SILENT_AUDIO_PACKET_TYPE_ID)
    self.assertEqual(len(raw_packet), 9)  # Is short length packet
    self.assertTrue(audio_aseg.is_audio_packet(raw_packet))
    self.assertEqual(self.SILENT_AUDIO_PCM, audio_pcm_prc)
    self.assertEqual(lane_name_org, lane_name_prc)
    self.assertEqual(ext_bytes_org, ext_bytes_prc)


  def test_true_enc_dec_verify_silent_noext(self):
    audio_pcm_org = self.TEST_AUDIO_PCM
    audio_pcm_org -= 20.0 # Make audio too silent
    lane_name_org = "ABC"
    ext_bytes_org = bytes()

    raw_packet = audio_aseg.encode(audio_pcm_org, lane_name_org, ext_bytes_org)
    audio_pcm_prc, lane_name_prc, ext_bytes_prc = audio_aseg.decode(raw_packet)

    self.assertEqual(raw_packet[0], audio_aseg.SILENT_AUDIO_PACKET_TYPE_ID)
    self.assertEqual(len(raw_packet), 5)  # Is short length packet
    self.assertTrue(audio_aseg.is_audio_packet(raw_packet))
    self.assertEqual(self.SILENT_AUDIO_PCM, audio_pcm_prc)
    self.assertEqual(lane_name_org, lane_name_prc)
    self.assertEqual(ext_bytes_org, ext_bytes_prc)


  def test_true_verify_ng(self):
    lane_name_org = "ABC"
    ext_bytes_org = bytes()
    raw_packet_correct = audio_aseg.encode(self.TEST_AUDIO_PCM, lane_name_org, ext_bytes_org)
    raw_packet_silent_correct = audio_aseg.encode(self.SILENT_AUDIO_PCM, lane_name_org, ext_bytes_org)

    raw_packet_invalid_empty                  = bytes()
    raw_packet_invalid_id                     = bytes([0x20]) + raw_packet_correct[1:]  # 0x20 as non 0x10 or 0x11 byte
    raw_packet_invalid_no_extlen              = raw_packet_correct[0:4]
    raw_packet_invalid_audio_too_short        = raw_packet_correct[0:-1]
    raw_packet_invalid_audio_too_long         = raw_packet_correct + bytes([0]) # 0 as an over length byte
    raw_packet_invalid_silent_audio_too_short = raw_packet_silent_correct[0:-1]
    raw_packet_invalid_silent_audio_too_long  = raw_packet_silent_correct + bytes([0]) # 0 as an over length byte

    self.assertFalse(audio_aseg.is_audio_packet(""))  # string "" as non bytes
    self.assertFalse(audio_aseg.is_audio_packet(raw_packet_invalid_empty))
    self.assertFalse(audio_aseg.is_audio_packet(raw_packet_invalid_id))
    self.assertFalse(audio_aseg.is_audio_packet(raw_packet_invalid_no_extlen))
    self.assertFalse(audio_aseg.is_audio_packet(raw_packet_invalid_audio_too_short))
    self.assertFalse(audio_aseg.is_audio_packet(raw_packet_invalid_audio_too_long))
    self.assertFalse(audio_aseg.is_audio_packet(raw_packet_invalid_silent_audio_too_short))
    self.assertFalse(audio_aseg.is_audio_packet(raw_packet_invalid_silent_audio_too_long))

    self.assertRaises(TypeError , audio_aseg.is_audio_packet, ""                                       , True)  # string "" as non bytes
    self.assertRaises(ValueError, audio_aseg.is_audio_packet, raw_packet_invalid_empty                 , True)
    self.assertRaises(ValueError, audio_aseg.is_audio_packet, raw_packet_invalid_id                    , True)
    self.assertRaises(ValueError, audio_aseg.is_audio_packet, raw_packet_invalid_no_extlen             , True)
    self.assertRaises(ValueError, audio_aseg.is_audio_packet, raw_packet_invalid_audio_too_short       , True)
    self.assertRaises(ValueError, audio_aseg.is_audio_packet, raw_packet_invalid_audio_too_long        , True)
    self.assertRaises(ValueError, audio_aseg.is_audio_packet, raw_packet_invalid_silent_audio_too_short, True)
    self.assertRaises(ValueError, audio_aseg.is_audio_packet, raw_packet_invalid_silent_audio_too_long , True)


  def test_err_enc_invalid_type(self):
    audio_pcm = self.TEST_AUDIO_PCM
    lane_name = "ABC"
    ext_bytes = bytes([1,2,3])

    self.assertRaises(TypeError, audio_aseg.encode, ""       , lane_name, ext_bytes) # str "" as non AudioSegment
    self.assertRaises(TypeError, audio_aseg.encode, audio_pcm, 1        , ext_bytes) # int 1 as non str
    self.assertRaises(TypeError, audio_aseg.encode, audio_pcm, lane_name, "")        # str "" as non bytes


  def test_err_enc_invalid_value(self):
    audio_pcm = self.TEST_AUDIO_PCM
    lane_name = "ABC"
    ext_bytes = bytes([1,2,3])

    lane_name_non_ascii = "🗒"
    lane_name_over_len = "ABCD"
    ext_bytes_over_len = bytes(256)

    self.assertRaises(ValueError, audio_aseg.encode, audio_pcm, lane_name_non_ascii, ext_bytes)
    self.assertRaises(ValueError, audio_aseg.encode, audio_pcm, lane_name, ext_bytes_over_len)
    self.assertRaises(ValueError, audio_aseg.encode, audio_pcm, lane_name_over_len, ext_bytes)


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
