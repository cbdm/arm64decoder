"""arm64decoder.py
Description: Decode and encode the subset of arm64 machine code instructions used in NCSU CSC236.
             Course Materials: https://www.caiobatista.com/courses/ncsu/s26/csc236/extra-resources/arm64-machine-code-tables
             Based on official documentation: https://developer.arm.com/documentation/ddi0602/2025-09/Index-by-Encoding
Author: Caio Batista (@cbdm)
"""

import argparse
import logging
from table_info import section_2_table, section_3_tables, section_4_instructions
from typing import List
from utils import MachineCode

logger = logging.getLogger(__name__)


def encode_instr(instr: List[str]) -> str:
    logging.debug(f"Encoding '{' '.join(instr)}'")
    raise NotImplementedError()


def decode_instr(instr: List[str]) -> str:
    user_input = " ".join(instr)
    logging.debug(f"Decoding '{user_input}'")

    mc = MachineCode(user_input)
    decode_result = [f"Input bytes: {mc.getHex().upper()}"]

    logging.debug("Expand hex digits: " + "    ".join(mc.getHex()))
    logging.debug(
        "Expand to binary: " + " ".join(f"{int(x, 16):04b}" for x in mc.getHex())
    )
    logging.debug("Bit count (%10):  1098 7654 3210 9876 5432 1098 7654 3210")

    # Decode the ops from the first table.
    op0_0 = mc.getBits(31)
    op1_0 = mc.getBits(28, 25)
    logging.debug("Analyzing table in Section 2;")
    logging.debug(f"\top0 (bit 31) = {op0_0}")
    logging.debug(f"\top1 (bits 28~25) = {op1_0}")

    instr_type = ""
    instr_type_count = 0

    for te in section_2_table:
        if all((mc.checkMask(op) for op in te.ops)):
            instr_type_count += 1
            instr_type = te.result
            logging.debug(f"Matched '{te.result}' instruction type")

    if instr_type_count == 0:
        logging.error(
            "Machine code did not match any instruction type; is the input correct?"
        )
        logging.error(
            "It's possible that your assembler chose a variation of what you wrote!"
        )
        return f"Unable to decode {user_input}"

    if instr_type_count > 1:
        logging.error(
            "Machine code matched too many instruction types; is the input correct?"
        )
        return f"Unable to decode {user_input}"

    decode_result.append(f"Table 2 > {instr_type}")

    if instr_type not in section_3_tables:
        logging.debug(
            f"The course tables have no further information for this instruction type..."
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

    logging.debug(f"Analyzing table in Section {subsection};")
    for i, opb in enumerate(ops_bits):
        if opb[0] == opb[1]:
            logging.debug(f"\top{i} (bit {opb[0]}): {mc.getBits(opb[0], opb[1])}")

        else:
            logging.debug(
                f"\top{i} (bits {opb[0]} ~ {opb[1]}): {mc.getBits(opb[0], opb[1])}"
            )

    for te in s3_table["table"]:
        if all((mc.checkMask(op) for op in te.ops)):
            logging.debug(f"Matched '{te.result}' instruction family")
            instr_family_count += 1
            instr_family = te.result

    if instr_family_count == 0:
        logging.error(
            "Machine code did not match any instruction family; is the input correct?"
        )
        logging.error(
            "It's possible that your assembler chose a variation of what you wrote!"
        )
        return f"Unable to decode {user_input}"

    if instr_family_count > 1:
        logging.error(
            "Machine code matched too many instruction families; is the input correct?"
        )
        return f"Unable to decode {user_input}"

    decode_result.append(f"Table {subsection} > {instr_family}")

    if instr_family not in section_4_instructions:
        logging.debug(
            f"The course tables have no further information for this instruction family..."
        )
        decode_result.append(
            "Section 4 has no further information for this instruction family."
        )
        return "\n\t-".join(decode_result)

    s4_intr = section_4_instructions[instr_family]
    subsection = s4_intr.subsection
    instr_encoding = s4_intr.instruction

    logging.debug(f"Filling in placeholder bits from Section {subsection};")
    asm_instr = instr_encoding.decode(mc)

    decode_result.append(f"Section {subsection} > {asm_instr}")

    return "\n\t".join(decode_result)


def main(user_input: List[str], encode: bool, verbose: bool) -> str:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(message)s",
    )
    return encode_instr(user_input) if encode else decode_instr(user_input)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="arm64decoder",
        description="This program helps decode/encode the subset of ARM64 instructions machine code covered in NCSU's CSC236.",
    )

    parser.add_argument(
        "user_input",
        nargs="+",
        help="instruction or bytes to process",
    )

    parser.add_argument(
        "-a",
        "--action",
        default="encode",
        const="encode",
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

    args = parser.parse_args()
    print(main(args.user_input, args.action == "encode", args.verbose))
