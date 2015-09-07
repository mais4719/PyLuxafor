PyLuxafor
=========

PyLuxafor is a simple Python module for interacting with your Luxafor device. For more information regarding Luxafor
please visit [http://luxafor.com/](http://luxafor.com/).

Install
-------

```
# pip install git+https://github.com/mais4719/PyLuxafor.git
```

Requirements
------------

Besides the obvious, a Luxafor device, is pyluxafor using [PyUSB](https://github.com/walac/pyusb). The PyUSB module is
100 % written in Python and provides an easy access to the host machine's Universal 
Serial Bus (USB) system.

Client
------

Pyluxafor comes with a simple command line client. Pip will automatically install this client on your system as 
luxafor_cli.

```
usage: luxafor_cli [-h] [-v]
                   {devices,jump2color,fade2color,blink,pattern,wave,off} ...

Simple command line interface using pyluxafor.

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit

subcommands:
  {devices,jump2color,fade2color,blink,pattern,wave,off}
    devices             List all Luxafor devices found on your system.
    jump2color          Switches color on your Luxafor device.
    fade2color          Fade to color on your Luxafor device.
    blink               Blink color on your Luxafor device.
    pattern             Run pattern on your Luxafor device.
    wave                Run wave on your Luxafor device.
    off                 Turn all LEDs of on your Luxafor device.
```

Get your Luxafor to show blue:

```
# luxafor_cli jump2color -c '#0000ff'
```

Get your Luxafor to blink like a police car:

```
# luxafor_cli pattern -p police -r 5
```

Turn the light off:

```
# luxafor_cli off
```

Module Use
----------

The following example shows some of the features available.

```python
from time import sleep
from pyluxafor import Devices
from pyluxafor import Wave, Pattern, Leds

with Devices().first as d:

    # Testing jump2color (blue followed by red).
    d.jump2color(color='#0000ff', leds=Leds.all)
    sleep(2)
    d.jump2color(color='#00ff00', leds=Leds.all)
    sleep(2)
    d.off()
    sleep(2)

    # Test diffrent LEDs.
    leds_list = list(Leds.front_list)
    leds_list.extend(Leds.back_list)

    for i, f in enumerate(leds_list):
        if i % 2 == 0:
            d.jump2color(color='#ff0000', leds=f)
        else:
            d.jump2color(color='#0000ff', leds=f)
        sleep(1)
    sleep(2)

    # Test fade2color
    d.fade2color(color='#0000ff', leds=Leds.all, speed=50)
    sleep(6)

    # Testing a pattern
    d.pattern(pattern_type=Pattern.police, repeats=5)
    sleep(6)
    d.off()
```