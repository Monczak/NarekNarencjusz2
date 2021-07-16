import math


def timestamp(seconds):
    secs = math.ceil(seconds) % 60
    minutes = math.floor(seconds // 60)
    return f"{str(minutes).zfill(2)}:{str(secs).zfill(2)}"


def truncate_with_ellipsis(text, max_length):
    return f"{text[:max_length - 3]}{'...' if len(text) > max_length else ''}"
