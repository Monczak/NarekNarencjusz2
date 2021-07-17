class Preferences:
    voice_name = None
    voice_rate = 0
    pitch_shift = 0

    def __init__(self, voice_name, voice_rate, pitch_shift):
        self.voice_name = voice_name
        self.voice_rate = voice_rate
        self.pitch_shift = pitch_shift
