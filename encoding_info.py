"""Logic to encode the Section 4 instructions into machine code bytes."""

import logging
import re

from utils import MachineCode, to_twos_comp

logger = logging.getLogger(__name__)


def encode_add_sub_imm(matches: re.Match[str]) -> MachineCode:
    """Encoding logic for Section 4.01"""
    logger.debug("Creating machine code for a add/sum immediate instruction")

    binary_format = "{size}{op}{s_suffix}100010{shift}{imm}{Rn}{Rd}"
    logger.debug("Instruction format: %s", binary_format)

    op, s_bit, size_rd, rd, size_rn, rn, imm, imm_sign, imm_base, imm_val, shift = (
        matches.groups()
    )
    logger.debug("Parsed following information from given asm instruction:")
    logger.debug("\top: %s", op)
    logger.debug("\ts_bit: %s", s_bit)
    logger.debug("\tsize_rd: %s", size_rd)
    logger.debug("\trd: %s", rd)
    logger.debug("\tsize_rn: %s", size_rn)
    logger.debug("\trn: %s", rn)
    logger.debug("\timm: %s", imm)
    logger.debug("\timm_sign: %s", imm_sign)
    logger.debug("\timm_base: %s", imm_base)
    logger.debug("\timm_val: %s", imm_val)
    logger.debug("\tshift: %s", shift)

    assert size_rd == size_rn, "All registers must be of same size"

    binary_result = binary_format.format(
        size=1 if size_rd == "x" else 0,
        op=1 if op == "sub" else 0,
        s_suffix=1 if s_bit is not None else 0,
        shift=1 if shift is not None else 0,
        imm=to_twos_comp(int(imm, 0), 12),
        Rd=f"{int(rd):05b}",
        Rn=f"{int(rn):05b}",
    )
    logger.debug("Binary result: %s", binary_result)

    mc = MachineCode.from_binary(binary_result)
    logger.debug("Hex result: %s", mc.get_pretty_hex())
    return mc


def encode_mov(matches: re.Match[str]) -> MachineCode:
    """Encoding logic for Section 4.02"""
    logger.debug("Creating machine code for a mov instruction")

    binary_format = "{size}10100101{hw}{imm}{Rd}"
    logger.debug("Instruction format: %s", binary_format)

    size_rd, rd, imm, imm_sign, imm_base, imm_val = matches.groups()
    logger.debug("Parsed following information from given asm instruction:")
    logger.debug("\tsize_rd: %s", size_rd)
    logger.debug("\trd: %s", rd)
    logger.debug("\timm: %s", imm)
    logger.debug("\timm_sign: %s", imm_sign)
    logger.debug("\timm_base: %s", imm_base)
    logger.debug("\timm_val: %s", imm_val)

    logger.debug("Parsing immediate into mov's format (16-bit data and hw*16 shift)")
    num_bits = 64 if size_rd == "x" else 32
    logger.debug("\tmaximum bits for this register: %d", num_bits)
    imm_bits = to_twos_comp(int(imm, 0), num_bits)
    logger.debug("\timm in %d bits: %s", num_bits, imm_bits)
    hw = "00"
    quadrant = ""
    num_quadrants = num_bits // 16
    for i in range(num_quadrants):
        quadrant = imm_bits[i * 16 : 16 * (i + 1)]
        unique_bits = "".join(set(quadrant))
        logger.debug("\tquadrant #%d: %s (unique bits: %s)", i, quadrant, unique_bits)

        # Check if current quadrant has the information we need to encode.
        if len(unique_bits) > 1:
            hw = f"{num_quadrants-i-1:02b}"
            logger.debug("\t\tmixed bits; will encode it and use hw=%s", hw)
            break

    binary_result = binary_format.format(
        size=1 if size_rd == "x" else 0,
        hw=hw,
        imm=quadrant,
        Rd=f"{int(rd):05b}",
    )
    logger.debug("Binary result: %s", binary_result)

    mc = MachineCode.from_binary(binary_result)
    logger.debug("Hex result: %s", mc.get_pretty_hex())
    return mc


def encode_sudiv(matches: re.Match[str]) -> MachineCode:
    """Encoding logic for Section 4.07"""
    logger.debug("Creating machine code for a div instruction")

    binary_format = "{size}0011010110{Rm}00001{sign}{Rn}{Rd}"
    logger.debug("Instruction format: %s", binary_format)

    sign, size_rd, rd, size_rn, rn, size_rm, rm = matches.groups()
    logger.debug("Parsed following information from given asm instruction:")
    logger.debug("\tsign: %s", sign)
    logger.debug("\tsize_rd: %s", size_rd)
    logger.debug("\trd: %s", rd)
    logger.debug("\tsize_rn: %s", size_rn)
    logger.debug("\trn: %s", rn)
    logger.debug("\tsize_rm: %s", size_rm)
    logger.debug("\trm: %s", rm)

    assert size_rd == size_rn == size_rm, "All registers must be of same size"

    binary_result = binary_format.format(
        sign=1 if sign == "s" else 0,
        size=1 if size_rd == "x" else 0,
        Rd=f"{int(rd):05b}",
        Rn=f"{int(rn):05b}",
        Rm=f"{int(rm):05b}",
    )
    logger.debug("Binary result: %s", binary_result)

    mc = MachineCode.from_binary(binary_result)
    logger.debug("Hex result: %s", mc.get_pretty_hex())
    return mc
