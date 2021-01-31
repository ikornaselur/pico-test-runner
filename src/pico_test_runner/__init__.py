from os import path

from pico_test_runner.pico import Pico


def run_test(test_path: str) -> None:
    with open(
        path.join(path.dirname(path.abspath(__file__)), "tests", test_path), "r"
    ) as f:
        code = f.read()

    with Pico("/dev/tty.usbmodem0000000000001") as pico:
        raw_output = pico.execute(code)

    print(raw_output.decode("utf-8"))
