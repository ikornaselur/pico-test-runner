# Pico Test Runner

A tool to run hardware tests with a specially built Raspberry Pico circuit.

The current iteration of this circuit lives on a breadboard, with a Raspberry
Pico connected to three TXS0108E Logic Level Converters (LLC), to convert between
3.3V, which the Pico works with, and 5V to be able to run tests on 5V circuits.

*To test circuits that run on 3.3V, there's no need for the TXS0108E LLCs*

The circuit is built to have 8 output lanes and 16 input lanes, where the most
common setup will be to read 8 bits from a bus and output a clock and some
control signals, to drive the circuit being tested. In this case, it's the
8-Bit CPU, built by following along with [Ben Eater](https://eater.net/)

![tester](.tester.jpg)

## Running code on the Pico

The tool uses a simplified version of the Pyboard tool from MicroPython. It can run code by simply creating a `Pico` object and running `.execute(code)` on it, like this:

```python
from pico_test_runner.pico import Pico

code = """
from machine import Pin
import utime

onboard_led = Pin(25, Pin.OUT)

onboard_led.value(1)
utime.sleep_ms(500)
onboard.led_value(0)

print("Done!")
""".strip()

with Pico("/dev/tty.usbmodem0000000000001") as pico: # Path to the serial port
    output = pico.execute(code)
    print(output)  # b"Done!\r\n"
```
