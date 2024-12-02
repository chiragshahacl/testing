import colorsys
import hashlib


def get_color_from_word(word):
    m = hashlib.md5()  # nosec
    m.update(word.encode())
    byte_digest = m.digest()
    first_num = byte_digest[0]  # get int value of first character 0-255
    second_num = byte_digest[1]  # get int value of second character 0-255
    mapped_num = int(
        first_num / 255 * 360
    )  # map from 255 range to 360 range for degrees
    hue = (mapped_num % 360) / 360  # hue as percentage
    variation = (
        second_num / 255 / 2 - 0.25
    )  # add some limited randomness to saturation and brightness
    saturation = min(0.8 + variation, 1.0)  # will vary from 0.55 to 1.0
    brightness = min(0.7 + variation, 1.0)  # will vary from 0.45 to 0.95
    color = colorsys.hsv_to_rgb(hue, saturation, brightness)
    color = "#%02x%02x%02x" % tuple(int(i * 255) for i in color)
    return color
