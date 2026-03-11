import instruction_info

from dataclasses import dataclass
from utils import Mask


@dataclass
class TableEntry:
    ops: List[Mask]
    result: str


section_2_table = [
    TableEntry(
        ops=[
            Mask("0", 31),
            Mask("0000", 25),
        ],
        result="Reserved",
    ),
    TableEntry(
        ops=[
            Mask("1", 31),
            Mask("0000", 25),
        ],
        result="Scalable Matrix Extension (SME)",
    ),
    TableEntry(
        ops=[
            Mask("0010", 25),
        ],
        result="Scalable Vector Extension (SVE)",
    ),
    TableEntry(
        ops=[
            Mask("00x1", 25),
        ],
        result="UNALLOCATED",
    ),
    TableEntry(
        ops=[
            Mask("100x", 25),
        ],
        result="Data Processing -- Immediate",
    ),
    TableEntry(
        ops=[
            Mask("101x", 25),
        ],
        result="Branches, Exception Generating and System instructions",
    ),
    TableEntry(
        ops=[
            Mask("x101", 25),
        ],
        result="Data Processing -- Register",
    ),
    TableEntry(
        ops=[
            Mask("x111", 25),
        ],
        result="Data Processing -- Scalar Floating-Point and Advanced SIMD",
    ),
    TableEntry(
        ops=[
            Mask("x1x0", 25),
        ],
        result="Loads and Stores",
    ),
]

section_3_tables = {
    "Data Processing -- Immediate": {
        "subsection": "3.1",
        "ops_bits": [(30, 29), (25, 22)],
        "table": [
            TableEntry(
                ops=[
                    Mask("11", 29),
                    Mask("111x", 22),
                ],
                result="Data-processing (1 source immediate)",
            ),
            TableEntry(
                ops=[
                    Mask("00xx", 22),
                ],
                result="PC-rel. addressing",
            ),
            TableEntry(
                ops=[
                    Mask("010x", 22),
                ],
                result="Add/subtract (immediate)",
            ),
            TableEntry(
                ops=[
                    Mask("0111", 22),
                ],
                result="Min/max (immediate)",
            ),
            TableEntry(
                ops=[
                    Mask("100x", 22),
                ],
                result="Logical (immediate)",
            ),
            TableEntry(
                ops=[
                    Mask("101x", 22),
                ],
                result="Move wide (immediate)",
            ),
        ],
    },
    "Branches, Exception Generating and System instructions": {
        "subsection": "3.2",
        "ops_bits": [(31, 29), (25, 12), (4, 0)],
        "table": [
            TableEntry(
                ops=[
                    Mask("010", 29),
                    Mask("00xxxxxxxxxxxx", 12),
                ],
                result="Conditional branch (immediate)",
            ),
            TableEntry(
                ops=[
                    Mask("110", 29),
                    Mask("00xxxxxxxxxxxx", 12),
                ],
                result="Exception generation",
            ),
            TableEntry(
                ops=[Mask("110", 29), Mask("01000000110010", 12), Mask("11111", 0)],
                result="Hints",
            ),
            TableEntry(
                ops=[
                    Mask("110", 29),
                    Mask("1xxxxxxxxxxxxx", 12),
                ],
                result="Unconditional branch (register)",
            ),
            TableEntry(
                ops=[Mask("x00", 29)], result="Unconditional branch (immediate)"
            ),
            TableEntry(
                ops=[
                    Mask("x01", 29),
                    Mask("0xxxxxxxxxxxxx", 12),
                ],
                result="Compare and branch (immediate)",
            ),
            TableEntry(
                ops=[
                    Mask("x01", 29),
                    Mask("1xxxxxxxxxxxxx", 12),
                ],
                result="Test and branch (immediate)",
            ),
        ],
    },
    "Data Processing -- Register": {
        "subsection": "3.3",
        "ops_bits": [(30, 30), (28, 28), (24, 21), (15, 10)],
        "table": [
            TableEntry(
                ops=[
                    Mask("0", 30),
                    Mask("1", 28),
                    Mask("0110", 21),
                ],
                result="Data-processing (2 source)",
            ),
            TableEntry(
                ops=[
                    Mask("1", 30),
                    Mask("1", 28),
                    Mask("0110", 21),
                ],
                result="Data-processing (1 source)",
            ),
            TableEntry(
                ops=[
                    Mask("0", 28),
                    Mask("0xxx", 21),
                ],
                result="Logical (shifted register)",
            ),
            TableEntry(
                ops=[
                    Mask("0", 28),
                    Mask("1xx0", 21),
                ],
                result="Add/subtract (shifted register)",
            ),
            TableEntry(
                ops=[
                    Mask("0", 28),
                    Mask("1xx1", 21),
                ],
                result="Add/subtract (extended register)",
            ),
            TableEntry(
                ops=[
                    Mask("1", 28),
                    Mask("0000", 21),
                    Mask("000000", 10),
                ],
                result="Add/subtract (with carry)",
            ),
            TableEntry(
                ops=[
                    Mask("1", 28),
                    Mask("0100", 21),
                ],
                result="Conditional select",
            ),
            TableEntry(
                ops=[
                    Mask("1", 28),
                    Mask("1xxx", 21),
                ],
                result="Data-processing (3 source)",
            ),
        ],
    },
    "Loads and Stores": {
        "subsection": "3.4",
        "ops_bits": [(31, 28), (26, 26), (24, 10)],
        "table": [
            TableEntry(
                ops=[Mask("xx00", 28), Mask("0", 26), Mask("01x1xxxxxxxxxxx", 10)],
                result="Compare and swap",
            ),
            TableEntry(
                ops=[Mask("xx01", 28), Mask("0xxxxxxxxxxxxxx", 10)],
                result="Load register (literal)",
            ),
            TableEntry(
                ops=[Mask("xx10", 28), Mask("xxxxxxxxxxxxxxx", 10)],
                result="Load/store register pair",
            ),
            TableEntry(
                ops=[Mask("xx11", 28), Mask("0xx0xxxxxxxxxx1", 10)],
                result="Load/store register (immediate pre/post-indexed)",
            ),
            TableEntry(
                ops=[Mask("xx11", 28), Mask("0xx1xxxxxxxxx10", 10)],
                result="Load/store register (register offset)",
            ),
            TableEntry(
                ops=[Mask("xx11", 28), Mask("1xxxxxxxxxxxxxx", 10)],
                result="Load/store register (unsigned immediate)",
            ),
        ],
    },
}

section_4_instructions = {
    "Add/subtract (immediate)": {
        "subsection": "4.01",
        "encoding": instruction_info.add_sub_imm,
    },
    "Move wide (immediate)": {
        "subsection": "4.02",
        "encoding": instruction_info.mov_wide,
    },
    "Unconditional branch (immediate)": {
        "subsection": "4.03",
        "encoding": instruction_info.uncond_branch_imm,
    },
    "Unconditional branch (register)": {
        "subsection": "4.04",
        "encoding": instruction_info.uncond_branch_reg,
    },
    "Conditional branch (immediate)": {
        "subsection": "4.05",
        "encoding": instruction_info.cond_branch_imm,
    },
    "Compare and branch (immediate)": {
        "subsection": "4.06",
        "encoding": instruction_info.comp_branch_imm,
    },
    "Data-processing (2 source)": {
        "subsection": "4.07",
        "encoding": instruction_info.sudiv,
    },
    "Logical (shifted register)": {
        "subsection": "4.08",
        "encoding": instruction_info.logical,
    },
    "Add/subtract (shifted register)": {
        "subsection": "4.09",
        "encoding": instruction_info.add_sub_reg,
    },
    "Data-processing (3 source)": {
        "subsection": "4.10/4.11",
        "encoding": instruction_info.muls,
    },
    "Load/store register pair": {
        "subsection": "4.12",
        "encoding": instruction_info.ldp_stp,
    },
    "Load/store register (unsigned immediate)": {
        "subsection": "4.13",
        "encoding": instruction_info.ldr_str_uimm_offset,
    },
    "Load/store register (immediate pre/post-indexed)": {
        "subsection": "4.14",
        "encoding": instruction_info.ldr_str_pre_post_idx,
    },
    "Load/store register (register offset)": {
        "subsection": "4.15",
        "encoding": instruction_info.ldr_str_reg_offset,
    },
    "Hints": {
        "subsection": "4.16",
        "encoding": instruction_info.nop,
    },
}
