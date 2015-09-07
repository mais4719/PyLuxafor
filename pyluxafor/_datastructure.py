from __future__ import division, print_function, absolute_import
import binascii
import usb.core
import usb.util
from collections import namedtuple


Leds = namedtuple('Leds', 'all, all_front, all_back, front_list, back_list')
Leds.all = 255
Leds.all_front = 41
Leds.all_back = 42
Leds.front_list = (1, 2, 3)
Leds.back_list = (4, 5, 6)

Pattern = namedtuple('Pattern', 'luxafor, police, random1, random2, random3, random4, random5, rainbow_wave')
Pattern.luxafor = 1
Pattern.police = 5
Pattern.random1 = 2
Pattern.random2 = 3
Pattern.random3 = 4
Pattern.random4 = 6
Pattern.random5 = 7
Pattern.rainbow_wave = 8

Wave = namedtuple('Wave', 'short, long, overlapping_short, overlapping_long')
Wave.short = 1
Wave.long = 2
Wave.overlapping_short = 3
Wave.overlapping_long = 4


class Color(object):

    def __init__(self, hex_color='#000000'):

        hex_color = hex_color.lstrip('#')
        if len(hex_color) != 6:
            raise ValueError('hex_color must have 3 hex codes, e.g. #00ff00 for green.')

        self.bytes = bytearray.fromhex(hex_color)

    @property
    def rgb(self):
        return tuple(c for c in self.bytes)

    @property
    def hex_str(self):
        return '#{}'.format(binascii.hexlify(self.bytes).decode('ascii'))


class Device(object):
    """
    Contextmanager class for a device.
    """

    def __init__(self, conn):
        self.conn = conn

    def __enter__(self):
        self.conn.detach_kernel_driver(0)
        self.conn.set_configuration()
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        usb.util.dispose_resources(self.conn)
        self.conn.attach_kernel_driver(0)
        return False

    def connect(self):
        self.__enter__()

    def close(self):
        self.__exit__(None, None, None)

    def jump2color(self, color, leds=Leds.all):
        p = Package(command_code=1, leds=leds, color=Color(color))
        return self.conn.write(endpoint=1, data=p.data, timeout=None)

    def fade2color(self, color, leds=Leds.all, speed=50):
        if speed < 0 or speed > 255:
            raise ValueError('Fade speed out of range [0-255].')
        p = Package(command_code=2, leds=leds, color=Color(color), optional_bytes=(speed, 0, 0))
        return self.conn.write(endpoint=1, data=p.data, timeout=None)

    def blink(self, color, leds=Leds.all, speed=50, repeats=3):
        if speed < 0 or speed > 255:
            raise ValueError('Blink speed out of range [0-255].')
        if repeats < 0 or repeats > 255:
            raise ValueError('Blink repeats out of range [0-255].')
        p = Package(command_code=3, leds=leds, color=Color(color), optional_bytes=(speed, 0, repeats))
        return self.conn.write(endpoint=1, data=p.data, timeout=None)

    def pattern(self, pattern_type=Pattern.rainbow_wave, repeats=5):
        if repeats < 0 or repeats > 255:
            raise ValueError('Pattern repeats out of range [0-255].')
        pseudo_color = Color('#000000')
        pseudo_color.bytes[0] = repeats
        p = Package(command_code=6, leds=pattern_type, color=pseudo_color)
        return self.conn.write(endpoint=1, data=p.data, timeout=None)

    def wave(self, color='#00ff00', wave_type=Wave.overlapping_short, speed=100, repeats=5):
        if speed < 0 or speed > 255:
            raise ValueError('Wave speed out of range [0-255].')
        if repeats < 0 or repeats > 255:
            raise ValueError('Wave repeats out of range [0-255].')
        p = Package(command_code=4, leds=wave_type, color=Color(color), optional_bytes=(0, repeats, speed))
        return self.conn.write(endpoint=1, data=p.data, timeout=None)

    def off(self, leds=Leds.all):
        p = Package(command_code=1, leds=leds, color=Color())
        return self.conn.write(endpoint=1, data=p.data, timeout=None)


class Devices(object):

    __vendor_id = 0x04D8
    __product_id = 0xF372

    def __init__(self):
        self.__devices = tuple(Device(d) for d in usb.core.find(find_all=True,
                                                                idVendor=self.__vendor_id,
                                                                idProduct=self.__product_id) if d)

    def __len__(self):
        return len(self.__devices)

    @property
    def list(self):
        return self.__devices

    @property
    def first(self):
        if not self.__devices[0]:
            raise ValueError('Sorry, no Luxafor device found in the system.')
        return self.__devices[0]


class Package(object):
    """
    (1) Command Code
    (2) Leds
    (3) Red
    (4) Green
    (5) Blue
    (6) Optional Byte 1
    (7) Optional Byte 2
    (8) Optional Byte 3
    """

    def __init__(self, command_code, leds, color, optional_bytes=(0, 0, 0)):
        self.__data = []
        self.__data.append(command_code)
        self.__data.append(leds)
        self.__data.extend(color.rgb)
        self.__data.extend(optional_bytes)

    @property
    def data(self):
        return self.__data
