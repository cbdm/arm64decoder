"""Logic to encode the Section 4 instructions into machine code bytes."""

import logging
import re

from utils import MachineCode

logger = logging.getLogger(__name__)


def encode_sudiv(matches: re.Match[str]) -> MachineCode:
    """Encoding logic for Section 4.07"""
    logger.debug("Creating machine code for a div instruction")

    binary_format = "{size}0011010110{rm}00001{sign}{rn}{rd}"
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
        sign="1" if sign == "s" else 0,
        size="1" if size_rd == "x" else 0,
        rd=f"{int(rd):05b}",
        rn=f"{int(rn):05b}",
        rm=f"{int(rm):05b}",
    )
    logger.debug("Binary result: %s", binary_result)

    mc = MachineCode.from_binary(binary_result)
    logger.debug("Hex result: %s", mc.get_pretty_hex())
    return mc
