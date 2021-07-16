import tts.sapi
import uuid
import os
import shelve
from core.logger import Logger

voice = tts.sapi.Sapi()


def create_tts_file(path, text, voice_name):
    Logger.log(f"Speaking {text}")
    file_name = os.path.join(path, str(uuid.uuid4()) + ".wav")

    if not os.path.exists(path):
        os.makedirs(path)

    voice.set_voice(voice_name)
    voice.create_recording(file_name, text)
    return file_name
