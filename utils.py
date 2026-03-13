"""Functions and definitions used across the project."""

import re
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Optional


@dataclass
class Mask:
    """A bit-mask containing a sequence of 0/1/x and the bit this mask should be applied to."""

    mask: str
    lowest_bit_number: int


class MachineCode:
    """Contains bytes of a single instruction to check against masks and access individual bits."""

    def __init__(self, hex_string: str) -> None:
        self._value = int(hex_string.replace(" ", ""), 16)

    @staticmethod
    def from_binary(bin_string: str) -> "MachineCode":
        """Create a MachineCode object from a binary string."""
        return MachineCode(f"{int(bin_string, 2):0x}")

    def get_value(self) -> int:
        """Return the instruction's value."""
        return self._value

    def get_hex(self) -> str:
        """Return the machine code bytes as a hex string."""
        return f"{self._value:0X}"

    def get_pretty_hex(self) -> str:
        """Return the machine code bytes as a hex string with split bytes."""
        raw_hex = self.get_hex()
        split_hex = [raw_hex[i : i + 2] for i in range(0, len(raw_hex), 2)]
        return " ".join(split_hex)

    def get_bin(self) -> str:
        """Return the machine code bytes as a binary string."""
        return f"{self._value:032b}"

    def get_pretty_bin(self) -> str:
        """Return the machine code bytes as a binary string with split hex digits."""
        raw_bin = self.get_bin()
        split_bin = [raw_bin[i : i + 4] for i in range(0, len(raw_bin), 4)]
        return " ".join(split_bin)

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


class ARM64Instruction:
    """Stores machine code format and decoding function for a single instruction."""

    def __init__(
        self,
        instr_bit_format: Mask,
        decode_fun: Callable[[MachineCode], str],
        instr_asm_regex: str,
        encode_fun: Callable[[re.Match[str]], MachineCode],
    ) -> None:
        self._bit_format = instr_bit_format
        self._decode = decode_fun
        self._asm_regex = instr_asm_regex
        self._encode = encode_fun

    def decode(self, mc: MachineCode) -> str:
        """Try to parse the bits from the given machine code into an asm instruction."""
        assert mc.check_mask(
            self._bit_format
        ), "Given machine code does not match this instruction's format"
        return self._decode(mc)

    def encode(self, asm_instr: str) -> MachineCode:
        """Try to encode the given instruction into machine code bytes."""
        matches = re.fullmatch(self._asm_regex, asm_instr)
        assert matches, "Given asm instruction doesn't match this instruction's regex"
        return self._encode(matches)


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


def from_twos_comp(binary_string: str) -> int:
    """Convert the given binary string into a signed two's complement integer."""
    # Adapted from: https://stackoverflow.com/a/9147327
    val, bits = int(binary_string, 2), len(binary_string)
    if (val & (1 << (bits - 1))) != 0:  # if sign bit is set e.g., 8bit: 128-255
        val = val - (1 << bits)  # compute negative value
    return val


def to_twos_comp(value: int, length: int) -> str:
    """Convert the given value into a two's complement string of appropriate length."""
    # Adapted from: https://stackoverflow.com/a/7823051
    twos_comp_value = (value + (1 << length)) % (1 << length)
    return f"{twos_comp_value:0{length}b}"


def equivalent_asm(instr1: str, instr2: str) -> bool:
    """Check whether two asm instructions are equivalent."""

    # Extract the opcode from both instructions while removing repeated spaces.
    opcode1, *args1 = [x for x in instr1.lower().split() if x]
    opcode2, *args2 = [x for x in instr2.lower().split() if x]

    # If different opcodes, not a match.
    if opcode1 != opcode2:
        return False

    # Split up the arguments based on commas.
    parsed_args1 = "".join(args1).split(",")
    parsed_args2 = "".join(args2).split(",")

    # If different number of arguments, not a match.
    if len(parsed_args1) != len(parsed_args2):
        return False

    # Compare each argument individually so we can account for, e.g., different bases.
    for a1, a2 in zip(parsed_args1, parsed_args2):
        # Check if they're immediates.
        if a1.startswith("#") and a2.startswith("#"):
            # If they *are* immediates, parse them into ints so we can compare their actual values.
            a1_val = int(a1[1:], 0)
            a2_val = int(a2[1:], 0)

            # If their int values are the same, these args are equivalent.
            if a1_val == a2_val:
                continue

            # Otherwise, they differ and these instructions are not equivalent.
            return False

        # If args are *not* immediates, compare their values directly.
        if a1 != a2:
            return False

    # If no differences, they're equivalent.
    return True
