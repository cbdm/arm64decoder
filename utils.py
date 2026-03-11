from enum import Enum
from typing import List, Callable
from dataclasses import dataclass


@dataclass
class Mask:
    mask: str
    lowest_bit_number: int


class MachineCode(object):
    def __init__(self, hex_bytes: str) -> None:
        self._value = int("".join(hex_bytes), 16)

    def getHex(self) -> str:
        """Return the machine code bytes as a hex string."""
        return f"{self._value:0x}"

    def getBits(self, start: int, end: int = None) -> str:
        """Return the requested bit(s) as a binary string."""
        if end is None:
            end = start
        high, low = max(start, end), min(start, end)
        diff = high - low + 1
        return f"{(self._value >> low) & ((2 ** diff) - 1):0{diff}b}"

    def checkMask(self, op_mask: Mask) -> bool:
        """Check whether the given op_mask matches the bits in this machine code."""
        reverse_mask = op_mask.mask[::-1]
        for i in range(len(reverse_mask)):
            if reverse_mask[i] == "x":
                continue
            if reverse_mask[i] != self.getBits(op_mask.lowest_bit_number + i):
                return False
        return True


class ARM64Instruction(object):
    def __init__(
        self, instr_bit_format: Mask, decode_fun: Callable[[MachineCode], str]
    ) -> None:
        self._format = instr_bit_format
        self._decode = decode_fun

    def decode(self, mc: MachineCode) -> str:
        assert mc.checkMask(
            self._format
        ), "Given machine code does not match this instruction's format"
        return self._decode(mc)


CCs = Enum(
    "Condition Code",
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
