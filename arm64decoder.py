"""arm64decoder.py
Description: Decode and encode the subset of arm64 machine code instructions used in NCSU CSC236.
             Course Tables: https://caio.link/arm64-tables
             Based on: https://developer.arm.com/documentation/ddi0602/2025-09/Index-by-Encoding
Author: Caio Batista (@cbdm)
"""

import argparse
import logging
from typing import List

from table_info import section_2_table, section_3_tables, section_4_instructions
from utils import MachineCode, equivalent_asm

logger = logging.getLogger(__name__)


def encode_instr(instr: List[str]) -> str:
    """Encode the given instruction into bytes."""

    user_input = " ".join(instr).lower()
    logger.debug("Encoding '%s'", user_input)

    for section_name, details in section_4_instructions.items():
        logger.debug(
            "[%s] Trying to match instruction with '%s':",
            details.subsection,
            section_name,
        )

        try:
            mc = details.instruction.encode(user_input)
            logger.debug("\t-> possibly encoded as: %s", mc.get_pretty_hex())

            # TODO: can we hide debug output for the decode function call?
            decoded_mc = details.instruction.decode(mc)
            logger.debug("\t-> which would be decoded as: %s", decoded_mc)

            if not equivalent_asm(user_input, decoded_mc):
                logger.debug(
                    "\t-> '%s' and '%s' are not equivalent, so this is not a correct encoding",
                    user_input,
                    decoded_mc,
                )
                continue

            logger.debug("\t-> which is equivalent to the input!")
            return f"Input asm: '{user_input}' --(encoded)-> {mc.get_pretty_hex()}"

        except AssertionError as err:
            logger.debug("\t-> error in the process: %s", err)
            continue

    logger.error(
        "Could not find a match with the available information; is the input correct?"
    )
    return f"Unable to encode '{user_input}'"


def decode_instr(instr: List[str]) -> str:
    """Decode the given bytes into an asm instruction."""

    user_input = " ".join(instr)
    logger.debug("Decoding '%s'", user_input)

    mc = MachineCode(user_input)
    decode_result = [f"Input bytes: {mc.get_pretty_hex()}"]

    logger.debug("Expand hex digits: %s", "    ".join(mc.get_hex()))
    logger.debug("Expand to binary: %s", mc.get_pretty_bin())
    logger.debug("Bit count (%10):  1098 7654 3210 9876 5432 1098 7654 3210")

    # Decode the ops from the first table.
    op0_0 = mc.get_bits(31)
    op1_0 = mc.get_bits(28, 25)
    logger.debug("Analyzing table in Section 2;")
    logger.debug("\top0 (bit 31) = %s", op0_0)
    logger.debug("\top1 (bits 28~25) = %s", op1_0)

    instr_type = ""
    instr_type_count = 0

    for te in section_2_table:
        if all((mc.check_mask(op) for op in te.ops)):
            instr_type_count += 1
            instr_type = te.result
            logger.debug("Matched '%s' instruction type", te.result)

    if instr_type_count == 0:
        logger.error(
            "Machine code did not match any instruction type; is the input correct?"
        )
        logger.error(
            "It's possible that your assembler chose a variation of what you wrote!"
        )
        return f"Unable to decode {user_input}"

    if instr_type_count > 1:
        logger.error(
            "Machine code matched too many instruction types; is the input correct?"
        )
        return f"Unable to decode {user_input}"

    decode_result.append(f"Table 2 > {instr_type}")

    if instr_type not in section_3_tables:
        logger.debug(
            "The course tables have no further information for this instruction type..."
        )
        decode_result.append(
            "Section 3 has no further information for this instruction type."
        )
        return "\n\t-".join(decode_result)

    instr_family = ""
    instr_family_count = 0

    s3_table = section_3_tables[instr_type]
    subsection = s3_table["subsection"]
    ops_bits = s3_table["ops_bits"]

    logger.debug("Analyzing table in Section %s;", subsection)
    for i, opb in enumerate(ops_bits):
        if opb[0] == opb[1]:
            logger.debug("\top%d (bit %d): %s", i, opb[0], mc.get_bits(opb[0], opb[1]))

        else:
            logger.debug(
                "\top%d (bits %d ~ %d): %s",
                i,
                opb[0],
                opb[1],
                mc.get_bits(opb[0], opb[1]),
            )

    for te in s3_table["table"]:
        if all((mc.check_mask(op) for op in te.ops)):
            logger.debug("Matched '%s' instruction family", te.result)
            instr_family_count += 1
            instr_family = te.result

    if instr_family_count == 0:
        logger.error(
            "Machine code did not match any instruction family; is the input correct?"
        )
        logger.error(
            "It's possible that your assembler chose a variation of what you wrote!"
        )
        return f"Unable to decode {user_input}"

    if instr_family_count > 1:
        logger.error(
            "Machine code matched too many instruction families; is the input correct?"
        )
        return f"Unable to decode {user_input}"

    decode_result.append(f"Table {subsection} > {instr_family}")

    if instr_family not in section_4_instructions:
        logger.debug(
            "The course tables have no further information for this instruction family..."
        )
        decode_result.append(
            "Section 4 has no further information for this instruction family."
        )
        return "\n\t-".join(decode_result)

    s4_intr = section_4_instructions[instr_family]
    subsection = s4_intr.subsection
    instr_encoding = s4_intr.instruction

    logger.debug("Filling in placeholder bits from Section %s;", subsection)
    asm_instr = instr_encoding.decode(mc)

    decode_result.append(f"Section {subsection} > {asm_instr}")

    return "\n\t".join(decode_result)


def main(user_input: List[str], encode: bool, verbose: bool) -> str:
    """Call appropriate function based on user flags."""

    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(message)s",
    )
    return encode_instr(user_input) if encode else decode_instr(user_input)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="arm64decoder",
        description="Parses the ARM64 instructions machine code covered in NCSU's CSC236.",
    )

    parser.add_argument(
        "user_input",
        nargs="+",
        help="assembly instruction or machine code bytes to process",
    )

    parser.add_argument(
        "-a",
        "--action",
        default="decode",
        const="decode",
        nargs="?",
        choices=("decode", "encode"),
        help="what to do with your input (default: %(default)s)",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="show steps during process",
    )

    parser.add_argument(
        "-i",
        "--ignore-disclaimer",
        action="store_true",
        help="do not show the bug disclaimer before running the script",
    )

    args = parser.parse_args()

    if not args.ignore_disclaimer:
        print("----- DISCLAIMER -----")
        print("| ** There could be bugs around us! **")
        print("| If you find something that doesn't seem to work or make sense:")
        print("|\t1. double check your input and run it again")
        print(
            "|\t2. try webassembliss to double check result - https://web.assembliss.app"
        )
        print(
            "|\t3. do it manually using the translation tables - https://caio.link/arm64-tables"
        )
        print(
            "|\t4. do it again with the official documentation - "
            "https://developer.arm.com/documentation/ddi0602/2025-09/Index-by-Encoding"
        )
        print(
            "|\t5. if the problem is still there, please open an issue - "
            "https://github.com/cbdm/arm64decoder"
        )
        print("----------------------")
        print()

    print(main(args.user_input, args.action == "encode", args.verbose))
