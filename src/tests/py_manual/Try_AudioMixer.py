# coding: UTF-8
"""Try for ``AudioMixer.py``

Other of some features can test by unittest: ``Test_AudioMixer.py``

To try features:
  * Can mix multiple audio inputs
  * Can mute no recent audio input

Author:
  aKuad

"""

# For import top layer module
import sys
from pathlib import Path
sys.path.append(Path(__file__).absolute().parent.parent.parent.__str__())

from time import sleep

from numpy import frombuffer
from pydub import AudioSegment
import sounddevice

from modules.AudioMixer import AudioMixer


# Global variables (for callback function)
in_continuous_as: AudioSegment
in_unstable_as: AudioSegment
in_silent_as: AudioSegment
i: int

audio_mixer: AudioMixer
lane_1: int
lane_2: int
lane_3: int


def part_callback(indata, outdata, frames, time, status):
  global i

  audio_mixer.lane_io(lane_1, in_continuous_as)

  if i >= 10:
    audio_mixer.lane_io(lane_2, in_unstable_as)

  lane_out_aseg = audio_mixer.lane_io(lane_3, in_silent_as)
  outdata[:] = frombuffer(lane_out_aseg.raw_data, dtype="int16").reshape(-1, 1)

  i += 1
  if i >= 20:
    i = 0


if __name__ == "__main__":
  # Test data preparation
  print("Continuous input data recording...")
  sleep(1)
  in_continuous_nd = sounddevice.rec(4410, 44100, 1, "int16", blocking=True)
  in_continuous_as = AudioSegment(in_continuous_nd.tobytes(), sample_width=2, frame_rate=44100, channels=1)
  print(f"{in_continuous_as.dBFS} dBFS")

  print("Unstable input data recording...")
  sleep(1)
  in_unstable_nd = sounddevice.rec(4410, 44100, 1, "int16", blocking=True)
  in_unstable_as = AudioSegment(in_unstable_nd.tobytes(), sample_width=2, frame_rate=44100, channels=1)
  print(f"{in_unstable_as.dBFS} dBFS")

  in_silent_as = AudioSegment.silent(100, 44100)


  # AudioMixer preparation
  audio_mixer = AudioMixer()
  lane_1 = audio_mixer.create_lane()
  lane_2 = audio_mixer.create_lane()
  lane_3 = audio_mixer.create_lane()


  # Start streaming
  i = 0

  try:
    with sounddevice.Stream(44100, 4410, channels=1, dtype="int16", callback=part_callback):
      while True:
        sounddevice.sleep(1)
  except KeyboardInterrupt:
    print("End")
