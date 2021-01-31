import utime
from machine import Pin

# Initialise all pins

PINS = [
    # First converter
    [
        Pin(0, Pin.OUT, Pin.PULL_DOWN),
        Pin(1, Pin.OUT, Pin.PULL_DOWN),
        Pin(2, Pin.OUT, Pin.PULL_DOWN),
        Pin(3, Pin.OUT, Pin.PULL_DOWN),
        Pin(4, Pin.OUT, Pin.PULL_DOWN),
        Pin(5, Pin.OUT, Pin.PULL_DOWN),
        Pin(6, Pin.OUT, Pin.PULL_DOWN),
        Pin(7, Pin.OUT, Pin.PULL_DOWN),
    ],
    # Second converter
    [
        Pin(8, Pin.OUT, Pin.PULL_DOWN),
        Pin(9, Pin.OUT, Pin.PULL_DOWN),
        Pin(10, Pin.OUT, Pin.PULL_DOWN),
        Pin(11, Pin.OUT, Pin.PULL_DOWN),
        Pin(12, Pin.OUT, Pin.PULL_DOWN),
        Pin(13, Pin.OUT, Pin.PULL_DOWN),
        Pin(14, Pin.OUT, Pin.PULL_DOWN),
        Pin(15, Pin.OUT, Pin.PULL_DOWN),
    ],
    # Third converter
    [
        Pin(16, Pin.OUT, Pin.PULL_DOWN),
        Pin(17, Pin.OUT, Pin.PULL_DOWN),
        Pin(18, Pin.OUT, Pin.PULL_DOWN),
        Pin(20, Pin.OUT, Pin.PULL_DOWN),
        Pin(21, Pin.OUT, Pin.PULL_DOWN),
        Pin(22, Pin.OUT, Pin.PULL_DOWN),
        Pin(26, Pin.OUT, Pin.PULL_DOWN),
        Pin(27, Pin.OUT, Pin.PULL_DOWN),
    ],
]

# Enable converters pin
OE = Pin(28, Pin.OUT, Pin.PULL_DOWN)

TICK_WAIT_MS = 250


def run():
    """Test writing to and reading from the register """
    ##################
    # Initialisation #
    ##################

    # Define the clock
    clock_pin = PINS[2][0]
    clear_pin = PINS[2][1]
    load_pin = PINS[2][2]
    enable_pin = PINS[2][3]

    bus = PINS[0]

    # Tying read and load as high disables them
    load_pin.value(1)
    enable_pin.value(1)

    ####################
    # Helper functions #
    ####################

    def read_bus():
        return [pin.value() for pin in bus]

    def run_actions(actions):
        # Force clock to start at 0
        clock_pin.value(0)
        utime.sleep_ms(TICK_WAIT_MS)
        for pin, value in actions:
            pin.value(value)
            utime.sleep_ms(TICK_WAIT_MS)

    def clear():
        run_actions(
            [
                (clear_pin, 1),
                (clock_pin, 1),
                (clock_pin, 0),
                (clear_pin, 0),
            ]
        )

    def load(bits):
        """Load 8 bits into the register

        Set the bus output to be the bits to load, enable reading and pulse the
        clock. We clear the bus output after reading so that we are able to
        read from the bus afterwards from the circuit
        """
        for pin, bit in zip(bus, bits):
            pin.value(bit)

        run_actions(
            [
                (load_pin, 0),  # Enabling load is tying low
                (clock_pin, 1),
                (clock_pin, 0),
                (load_pin, 1),
            ]
        )

        for pin in bus:
            pin.value(0)

    def enable():
        # Enable the enable pin
        run_actions(
            [
                (enable_pin, 0),  # Enabling read is tying low
                (clock_pin, 1),
                (clock_pin, 0),
            ]
        )
        # Get the bus value
        bits = read_bus()

        # Disable load pin again
        run_actions([(enable_pin, 1)])

        # Return the read bits
        return bits

    ####################
    # Test #
    ####################
    try:

        # Enable the output
        OE.value(1)

        # Clear the register to start with
        clear()

        # Read the bus into the register
        bits_1 = [1, 0, 1, 0, 1, 0, 1, 0]
        load(bits_1)

        # Enable the bus connection and check what's on the register
        bus_bits = enable()
        assert bus_bits == bits_1

        # Read a different value into the register
        bits_2 = [1, 1, 1, 1, 0, 0, 0, 0]
        load(bits_2)

        # Load what's on the register
        bus_bits = enable()
        assert bus_bits == bits_2

        # Clear
        clear()

        # Verify empty
        bus_bits = enable()

        assert bus_bits == [0, 0, 0, 0, 0, 0, 0, 0]
    finally:
        OE.value(0)


run()
