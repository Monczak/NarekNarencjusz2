import math


def timestamp(seconds):
    secs = math.ceil(seconds) % 60
    minutes = math.floor(seconds // 60)
    return f"{str(minutes).zfill(2)}:{str(secs).zfill(2)}"
