"""Contains the objects for the Section 4 instructions."""

import decoding_info
import encoding_info
from utils import ARM64Instruction, MachineCode, Mask

# Turn off linting for long lines to allow long regex strings.
# pylint: disable=line-too-long

add_sub_imm = ARM64Instruction(
    instr_bit_format=Mask("xxx100010xxxxxxxxxxxxxxxxxxxxxxx", 0),
    decode_fun=decoding_info.decode_add_sub_imm,
    instr_asm_regex=r"(add|sub)(s)?\s+(x|w)(\d{1,2}),\s*(x|w)(\d{1,2}),\s*#((-)?(0x|0b)?(\d+))(,\s*lsl\s*#12)?",
    encode_fun=encoding_info.encode_add_sub_imm,
)

mov_wide = ARM64Instruction(
    instr_bit_format=Mask("x10100101xxxxxxxxxxxxxxxxxxxxxxx", 0),
    decode_fun=decoding_info.decode_mov_wide,
    instr_asm_regex=r"movz?\s+(x|w)(\d{1,2}),\s*#((-)?(0x|0b)?(\d+))",
    encode_fun=encoding_info.encode_mov,
)

uncond_branch_imm = ARM64Instruction(
    instr_bit_format=Mask("x00101xxxxxxxxxxxxxxxxxxxxxxxxxx", 0),
    decode_fun=decoding_info.decode_uncond_branch_imm,
    instr_asm_regex=r"b(l)?\s+label\s+//\s+\(label is (-?\d+) bytes away from pc\)",
    encode_fun=encoding_info.encode_uncond_branch_imm,
)

uncond_branch_reg = ARM64Instruction(
    instr_bit_format=Mask("1101011000x11111000000xxxxx00000", 0),
    decode_fun=decoding_info.decode_uncond_branch_reg,
    instr_asm_regex=r"b(l)?r\s+x(\d{1,2})",
    encode_fun=encoding_info.encode_uncond_branch_reg,
)

cond_branch_imm = ARM64Instruction(
    instr_bit_format=Mask("01010100xxxxxxxxxxxxxxxxxxx0xxxx", 0),
    decode_fun=decoding_info.decode_cond_branch_imm,
    instr_asm_regex=r"b\.(eq|ne|cs|cc|mi|pl|vs|vc|hi|ls|ge|lt|gt|le|al|nv)\s+label\s+//\s+\(label is (-?\d+) bytes away from pc\)",
    encode_fun=encoding_info.encode_cond_branch_imm,
)

comp_branch_imm = ARM64Instruction(
    instr_bit_format=Mask("x011010xxxxxxxxxxxxxxxxxxxxxxxxx", 0),
    decode_fun=decoding_info.decode_comp_branch_imm,
    instr_asm_regex=r"cb(n)?z\s+(x|w)(\d{1,2}),\s*label\s+//\s+\(label is (-?\d+) bytes away from pc\)",
    encode_fun=encoding_info.encode_comp_branch_imm,
)

sudiv = ARM64Instruction(
    instr_bit_format=Mask("x0011010110xxxxx00001xxxxxxxxxxx", 0),
    decode_fun=decoding_info.decode_sudiv,
    instr_asm_regex=r"(s|u)div\s+(x|w)(\d{1,2}),\s*(x|w)(\d{1,2}),\s*(x|w)(\d{1,2})",
    encode_fun=encoding_info.encode_sudiv,
)

logical = ARM64Instruction(
    instr_bit_format=Mask("xxx0101000xxxxxxxxxxxxxxxxxxxxxx", 0),
    decode_fun=decoding_info.decode_logical,
    instr_asm_regex=r"(and|orr|eor|ands|bic|orn|eon|bics)\s+(x|w)(\d{1,2}),\s*(x|w)(\d{1,2}),\s*(x|w)(\d{1,2})(,\s*lsl\s*#((0x|0b)?(\d+)))?",
    encode_fun=encoding_info.encode_logical,
)

add_sub_reg = ARM64Instruction(
    instr_bit_format=Mask("xxx01011000xxxxxxxxxxxxxxxxxxxxx", 0),
    decode_fun=decoding_info.decode_add_sub_reg,
    instr_asm_regex=r"(add|sub)(s)?\s+(x|w)(\d{1,2}),\s*(x|w)(\d{1,2}),\s*(x|w)(\d{1,2})(,\s*lsl\s*#((0x|0b)?(\d+)))?",
    encode_fun=encoding_info.encode_add_sub_reg,
)

muls = ARM64Instruction(
    instr_bit_format=Mask("x0011011xxxxxxxxxxxxxxxxxxxxxxxx", 0),
    decode_fun=decoding_info.decode_muls,
    instr_asm_regex=r"(madd|msub|smaddl|umaddl|smsubl|umsubl|smulh|umulh)\s+(x|w)(\d{1,2}),\s*(x|w)(\d{1,2}),\s*(x|w)(\d{1,2})(,\s*(x|w)(\d{1,2}))?",
    encode_fun=encoding_info.encode_muls,
)

ldp_stp = ARM64Instruction(
    instr_bit_format=Mask("x010100xxxxxxxxxxxxxxxxxxxxxxxxx", 0),
    decode_fun=decoding_info.decode_ldp_stp,
    instr_asm_regex=r"(stp|ldp)\s+(x|w)(\d{1,2}),\s*(x|w)(\d{1,2}),\s*\[x(\d{1,2})((\])|(,\s*#((-)?(0x|0b)?(\d+))\])|(,\s*#((-)?(0x|0b)?(\d+))\]!)|(\],\s*#((-)?(0x|0b)?(\d+))))",
    encode_fun=encoding_info.encode_ldp_stp,
)

ldr_str_uimm_offset = ARM64Instruction(
    instr_bit_format=Mask("xx111001xxxxxxxxxxxxxxxxxxxxxxxx", 0),
    decode_fun=decoding_info.decode_ldr_str_uimm_offset,
    instr_asm_regex=r"(ldr|str)(s)?(b|h|w)?\s+(x|w)(\d{1,2}),\s*\[x(\d{1,2})(,\s*#((0x|0b)?(\d+)))?\]",
    encode_fun=encoding_info.encode_ldr_str_uimm_offset,
)

ldr_str_pre_post_idx = ARM64Instruction(
    instr_bit_format=Mask("xx111000xx0xxxxxxxxxx1xxxxxxxxxx", 0),
    decode_fun=decoding_info.decode_ldr_str_pre_post_idx,
    instr_asm_regex=r"(ldr|str)(s)?(b|h|w)?\s+(x|w)(\d{1,2}),\s*\[x(\d{1,2})((,\s*#((-)?(0x|0b)?(\d+))\]!)|(\],\s*#((-)?(0x|0b)?(\d+))))",
    encode_fun=encoding_info.encode_ldr_str_pre_post_idx,
)

ldr_str_reg_offset = ARM64Instruction(
    instr_bit_format=Mask("xx111000xx1xxxxx011010xxxxxxxxxx", 0),
    decode_fun=decoding_info.decode_ldr_str_reg_offset,
    instr_asm_regex=r"(ldr|str)(s)?(b|h|w)?\s+(x|w)(\d{1,2}),\s*\[x(\d{1,2}),\s*x(\d{1,2})\]",
    encode_fun=encoding_info.encode_ldr_str_reg_offset,
)

nop = ARM64Instruction(
    instr_bit_format=Mask("11010101000000110010000000011111", 0),
    decode_fun=decoding_info.decode_nop,
    instr_asm_regex=r"nop",
    encode_fun=lambda _: MachineCode(
        f'{int("11010101000000110010000000011111", 2):0x}'
    ),
)
