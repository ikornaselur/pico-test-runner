""" Based heavily on the Pyboard tool by MicroPython
https://raw.githubusercontent.com/micropython/micropython/master/tools/pyboard.py
"""
import time
from typing import Any, List, Tuple

import serial


class PicoException(Exception):
    pass


class Pico:
    serial: serial.Serial

    def __init__(self: "Pico", device: str, baudrate: int = 115200) -> None:
        self.serial = serial.Serial(device, baudrate=baudrate, interCharTimeout=1)

    def __enter__(self: "Pico") -> "Pico":
        return self

    def __exit__(self: "Pico", *_args: List[Any]) -> None:
        self.close()

    def close(self: "Pico") -> None:
        self.serial.close()

    def _read_until(
        self: "Pico",
        min_num_bytes: int,
        ending: bytes,
        timeout: int = 10,
    ) -> bytes:
        data = self.serial.read(min_num_bytes)
        timeout_count = 0
        while True:
            if data.endswith(ending):
                break
            elif self.serial.inWaiting() > 0:
                new_data = self.serial.read(1)
                data = data + new_data
                timeout_count = 0
            else:
                timeout_count += 1
                if timeout is not None and timeout_count >= 100 * timeout:
                    break
                time.sleep(0.01)
        return data

    def _enter_raw_repl(self: "Pico") -> None:
        self.serial.write(b"\r\x03\x03")
        self.serial.flushInput()
        self.serial.write(b"\r\x01")

        data = self._read_until(1, b"raw REPL; CTRL-B to exit\r\n>")
        if not data.endswith(b"raw REPL; CTRL-B to exit\r\n>"):
            print(data)
            raise PicoException("could not enter raw repl")

        self.serial.write(b"\x04")
        data = self._read_until(1, b"soft reboot\r\n")
        if not data.endswith(b"soft reboot\r\n"):
            print(data)
            raise PicoException("could not enter raw repl")

        data = self._read_until(1, b"raw REPL; CTRL-B to exit\r\n")
        if not data.endswith(b"raw REPL; CTRL-B to exit\r\n"):
            print(data)
            raise PicoException("could not enter raw repl")

    def _exit_raw_repl(self: "Pico") -> None:
        self.serial.write(b"\r\x02")

    def _raw_paste_write(self: "Pico", command_bytes: bytes) -> None:
        # Read initial header, with window size.
        data = self.serial.read(2)
        window_size = data[0] | data[1] << 8
        window_remain = window_size

        # Write out the command_bytes data.
        i = 0
        while i < len(command_bytes):
            while window_remain == 0 or self.serial.inWaiting():
                data = self.serial.read(1)
                if data == b"\x01":
                    # Device indicated that a new window of data can be sent.
                    window_remain += window_size
                elif data == b"\x04":
                    # Device indicated abrupt end.  Acknowledge it and finish.
                    self.serial.write(b"\x04")
                    return
                else:
                    # Unexpected data from device.
                    raise PicoException(f"unexpected read during raw paste: {data}")
            # Send out as much data as possible that fits within the allowed window.
            b = command_bytes[i : min(i + window_remain, len(command_bytes))]
            self.serial.write(b)
            window_remain -= len(b)
            i += len(b)

        # Indicate end of data.
        self.serial.write(b"\x04")

        # Wait for device to acknowledge end of data.
        data = self._read_until(1, b"\x04")
        if not data.endswith(b"\x04"):
            raise PicoException(f"could not complete raw paste: {data}")

    def _exec_raw(self: "Pico", command: str) -> None:
        command_bytes = bytes(command, encoding="utf8")

        # check we have a prompt
        data = self._read_until(1, b">")
        if not data.endswith(b">"):
            raise PicoException("could not enter raw repl")

        # Enter raw-paste mode
        self.serial.write(b"\x05A\x01")
        data = self.serial.read(2)

        return self._raw_paste_write(command_bytes)

    def _follow(self: "Pico", timeout: int) -> Tuple[bytes, bytes]:
        # wait for normal output
        data = self._read_until(1, b"\x04", timeout=timeout)
        if not data.endswith(b"\x04"):
            raise PicoException("timeout waiting for first EOF reception")
        data = data[:-1]

        # wait for error output
        data_err = self._read_until(1, b"\x04", timeout=timeout)
        if not data_err.endswith(b"\x04"):
            raise PicoException("timeout waiting for second EOF reception")
        data_err = data_err[:-1]

        # return normal and error output
        return data, data_err

    def execute(self: "Pico", command: str, timeout: int = 10) -> bytes:
        self._enter_raw_repl()
        self._exec_raw(command)
        ret, error = self._follow(timeout)

        if error:
            raise PicoException("exception", ret, error)

        self._exit_raw_repl()

        return ret
