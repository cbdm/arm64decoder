"""Functions and definitions used across the project."""

from dataclasses import dataclass
from enum import Enum
from typing import Callable, Optional


@dataclass
class Mask:
    """A bit-mask containing a sequence of 0/1/x and the bit this mask should be applied to."""

    mask: str
    lowest_bit_number: int


class MachineCode(object):
    """Contains bytes of a single instruction to check against masks and access individual bits."""

    def __init__(self, hex_string: str) -> None:
        self._value = int(hex_string.replace(" ", ""), 16)

    def get_hex(self) -> str:
        """Return the machine code bytes as a hex string."""
        return f"{self._value:0x}"

    def get_bits(self, start: int, end: Optional[int] = None) -> str:
        """Return the requested bit(s) as a binary string."""
        if end is None:
            end = start
        high, low = max(start, end), min(start, end)
        diff = high - low + 1
        return f"{(self._value >> low) & ((2 ** diff) - 1):0{diff}b}"

    def check_mask(self, op_mask: Mask) -> bool:
        """Check whether the given op_mask matches the bits in this machine code."""
        reverse_mask = op_mask.mask[::-1]
        for i, b in enumerate(reverse_mask):
            if b == "x":
                continue
            if b != self.get_bits(op_mask.lowest_bit_number + i):
                return False
        return True


class ARM64Instruction(object):
    """Stores machine code format and decoding function for a single instruction."""

    def __init__(
        self, instr_bit_format: Mask, decode_fun: Callable[[MachineCode], str]
    ) -> None:
        self._format = instr_bit_format
        self._decode = decode_fun

    def decode(self, mc: MachineCode) -> str:
        """Try to parse the bits from the given machine code into an asm instruction."""
        assert mc.check_mask(
            self._format
        ), "Given machine code does not match this instruction's format"
        return self._decode(mc)


CCs = Enum(
    "CCs",
    names=(
        "eq",
        "ne",
        "cs",
        "cc",
        "mi",
        "pl",
        "vs",
        "vc",
        "hi",
        "ls",
        "ge",
        "lt",
        "gt",
        "le",
        "al",
        "nv",
    ),
)


def twos_comp(binary_string: str) -> int:
    """Convert the given binary string into a signed two's complement integer."""
    # Adapted from: https://stackoverflow.com/a/9147327
    val, bits = int(binary_string, 2), len(binary_string)
    if (val & (1 << (bits - 1))) != 0:  # if sign bit is set e.g., 8bit: 128-255
        val = val - (1 << bits)  # compute negative value
    return val
