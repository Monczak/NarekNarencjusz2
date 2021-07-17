import tts.sapi
import uuid
import os
import shelve
import librosa
from soundfile import write
from core.logger import Logger

voice = tts.sapi.Sapi()


def create_tts_file(path, text, preferences):
    Logger.log(f"Speaking {text}")
    file_name = os.path.join(path, str(uuid.uuid4()) + ".wav")

    if not os.path.exists(path):
        os.makedirs(path)

    voice.set_voice(preferences.voice_name)
    voice.set_rate(preferences.voice_rate)
    voice.create_recording(file_name, text)

    if preferences.pitch_shift != 0:
        y, sr = librosa.load(file_name, sr=22050)
        y_shifted = librosa.effects.pitch_shift(y, sr, n_steps=preferences.pitch_shift)
        write(file_name, y_shifted, samplerate=22050)

    return file_name
