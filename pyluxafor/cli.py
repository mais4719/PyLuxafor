#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple command line interface to pyluxafor.
"""
from __future__ import division, print_function, absolute_import

import argparse
import sys
import logging

from pyluxafor import Devices
from pyluxafor import Wave, Pattern, Leds
from pyluxafor import __version__

__author__ = 'Magnus Isaksson'
__copyright__ = 'Magnus Isaksson'
__license__ = 'gpl3'

_logger = logging.getLogger(__name__)


def add_jump2color_parser(subparsers):

    parser = subparsers.add_parser('jump2color',
                                   description='Switches color on your Luxafor device.',
                                   help='Switches color on your Luxafor device.')
    parser.set_defaults(runner=jump2color)
    parser.add_argument('-c',
                        '--color',
                        required=True,
                        help='Color in 3 hex codes (e.g. #00FF00 for green).')


def jump2color(args):

    with Devices().first as d:
        d.jump2color(args.color, leds=Leds.all)

    return 'Jumping to color: {}'.format(args.color)


def add_fade2color_parser(subparsers):

    parser = subparsers.add_parser('fade2color',
                                   description='Fade to color on your Luxafor device.',
                                   help='Fade to color on your Luxafor device.')
    parser.set_defaults(runner=fade2color)
    parser.add_argument('-c',
                        '--color',
                        required=True,
                        help='Color in 3 hex codes (e.g. #00FF00 for green).')
    parser.add_argument('-s',
                        '--speed',
                        required=False,
                        default=100,
                        type=int,
                        help='Fading speed [0-255], low value equals higher speed.')


def fade2color(args):

    if args.speed < 0 or args.speed > 255:
        return 'Error: Speed needs to be an integer between 0 and 255.'

    with Devices().first as d:
        d.fade2color(args.color, leds=Leds.all, speed=args.speed)

    return 'Fading to color: {} with speed: {}'.format(args.color, args.speed)


def add_blink_parser(subparsers):

    parser = subparsers.add_parser('blink',
                                   description='Blink color on your Luxafor device.',
                                   help='Blink color on your Luxafor device.')
    parser.set_defaults(runner=blink)
    parser.add_argument('-c',
                        '--color',
                        required=True,
                        help='Color in 3 hex codes (e.g. #00FF00 for green).')
    parser.add_argument('-s',
                        '--speed',
                        required=False,
                        default=100,
                        type=int,
                        help='Blink speed [0-255], low value equals higher speed.')
    parser.add_argument('-r',
                        '--repeats',
                        required=False,
                        default=2,
                        type=int,
                        help='Repeats [1-255].')


def blink(args):

    if args.speed < 0 or args.speed > 255:
        return 'Error: Speed needs to both be an integer between 0 and 255.'
    if args.repeats < 1 or args.repeats > 255:
        return 'Error: Repeats needs to be an integer between 1 and 255.'

    with Devices().first as d:
        d.blink(args.color, leds=Leds.all, speed=args.speed, repeats=args.repeats)

    return 'Blinking color: {}, {} times with speed: {}'.format(args.color, args.repeats, args.speed)


def add_pattern_parser(subparsers):

    parser = subparsers.add_parser('pattern',
                                   description='Run pattern on your Luxafor device.',
                                   help='Run pattern on your Luxafor device.')
    parser.set_defaults(runner=pattern)
    parser.add_argument('-p',
                        '--pattern',
                        required=True,
                        help=', '.join([p for p in Pattern._fields]))
    parser.add_argument('-r',
                        '--repeats',
                        type=int,
                        default=2,
                        required=False,
                        help='Repeats [1-255].')


def pattern(args):

    args.pattern = args.pattern.lower()
    if args.pattern not in Pattern._fields:
        return 'Error: {} is not a valid pattern.'.format(args.pattern)
    if args.repeats < 1 or args.repeats > 255:
        return 'Error: Repeats needs to be a integer between 1 and 255.'

    with Devices().first as d:
        d.pattern(pattern_type=getattr(Pattern, args.pattern), repeats=args.repeats)

    return 'Running pattern {} {} times.'.format(args.pattern, args.repeats)


def add_wave_parser(subparsers):

    parser = subparsers.add_parser('wave',
                                   description='Run wave on your Luxafor device.',
                                   help='Run wave on your Luxafor device.')
    parser.set_defaults(runner=wave)
    parser.add_argument('-c',
                        '--color',
                        required=True,
                        help='Color in 3 hex codes (e.g. #00FF00 for green).')
    parser.add_argument('-w',
                        '--wave',
                        required=True,
                        help=', '.join([p for p in Wave._fields]))
    parser.add_argument('-s',
                        '--speed',
                        required=False,
                        default=100,
                        type=int,
                        help='Blink speed [0-255], low value equals higher speed.')
    parser.add_argument('-r',
                        '--repeats',
                        required=False,
                        default=2,
                        type=int,
                        help='Repeats [1-255].')


def wave(args):

    args.pattern = args.wave.lower()
    if args.pattern not in Wave._fields:
        return 'Error: {} is not a valid wave type.'.format(args.pattern)
    if args.speed < 0 or args.speed > 255:
        return 'Error: Speed needs to be an integer between 0 and 255.'
    if args.repeats < 1 or args.repeats > 255:
        return 'Error: Repeats needs to be a integer between 1 and 255.'

    with Devices().first as d:
        d.wave(color=args.color, wave_type=getattr(Wave, args.wave), speed=args.speed, repeats=args.repeats)

    return 'Running a {} wave with color {} and speed {}, {} times.'.format(args.wave, args.color,
                                                                            args.speed, args.repeats)


def add_off_parser(subparsers):

    parser = subparsers.add_parser('off',
                                   description='Turn all LEDs of on your Luxafor device.',
                                   help='Turn all LEDs of on your Luxafor device.')
    parser.set_defaults(runner=off)


def off(args):

    with Devices().first as d:
        d.off()

    return 'Turning of all LEDs on your device.'


def add_list_devices_parser(subparsers):

    parser = subparsers.add_parser('devices',
                                   description='List all Luxafor devices found on your system.',
                                   help='List all Luxafor devices found on your system.')
    parser.set_defaults(runner=list_devices)


def list_devices(args):

    ans_str = 'Sorry, no Luxafor device found in the system.'
    devices = ['Product: {}, Manufacturer: {}, Serial #: {}'.format(d.conn.product,
                                                                    d.conn.manufacturer,
                                                                    d.conn.serial_number.encode('utf-8')) for d in Devices().list]

    if devices:
        ans_str = '\n'.join(devices)

    return '\nFound {} devices connected to your system.\n{}'.format(len(devices), ans_str)


def parse_args(args):
    """
    Parse command line parameters

    :param args: command line parameters as list of strings
    :return: command line parameters as :obj:`argparse.Namespace`
    """

    parser = argparse.ArgumentParser(
        description="Simple command line interface using pyluxafor.")

    # Global arguments
    parser.add_argument('-v',
                        '--version',
                        action='version',
                        version='pyluxafor {ver}'.format(ver=__version__))

    # Sub parsers
    subparsers = parser.add_subparsers(title='subcommands')
    add_list_devices_parser(subparsers)
    add_jump2color_parser(subparsers)
    add_fade2color_parser(subparsers)
    add_blink_parser(subparsers)
    add_pattern_parser(subparsers)
    add_wave_parser(subparsers)
    add_off_parser(subparsers)

    return parser


def main(args):

    parser = parse_args(args)
    args = parser.parse_args(args)

    # Do we know what to run?
    if 'runner' not in args:
        parser.print_help()
    else:
        ans = args.runner(args)
        print(ans)


def run():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    main(sys.argv[1:])


if __name__ == "__main__":
    run()
