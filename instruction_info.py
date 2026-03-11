import decoding_info
from utils import ARM64Instruction, Mask


add_sub_imm = ARM64Instruction(
    instr_bit_format=Mask("xxx100010xxxxxxxxxxxxxxxxxxxxxxx", 0),
    decode_fun=decoding_info.decode_add_sub_imm,
)

mov_wide = ARM64Instruction(
    instr_bit_format=Mask("x10100101xxxxxxxxxxxxxxxxxxxxxxx", 0),
    decode_fun=decoding_info.decode_mov_wide,
)

uncond_branch_imm = ARM64Instruction(
    instr_bit_format=Mask("x00101xxxxxxxxxxxxxxxxxxxxxxxxxx", 0),
    decode_fun=decoding_info.decode_uncond_branch_imm,
)

uncond_branch_reg = ARM64Instruction(
    instr_bit_format=Mask("1101011000x11111000000xxxxx00000", 0),
    decode_fun=decoding_info.decode_uncond_branch_reg,
)

cond_branch_imm = ARM64Instruction(
    instr_bit_format=Mask("01010100xxxxxxxxxxxxxxxxxxx0xxxx", 0),
    decode_fun=decoding_info.decode_cond_branch_imm,
)

comp_branch_imm = ARM64Instruction(
    instr_bit_format=Mask("x011010xxxxxxxxxxxxxxxxxxxxxxxxx", 0),
    decode_fun=decoding_info.decode_comp_branch_imm,
)

sudiv = ARM64Instruction(
    instr_bit_format=Mask("x0011010110xxxxx00001xxxxxxxxxxx", 0),
    decode_fun=decoding_info.decode_sudiv,
)

logical = ARM64Instruction(
    instr_bit_format=Mask("xxx0101000xxxxxxxxxxxxxxxxxxxxxx", 0),
    decode_fun=decoding_info.decode_logical,
)

add_sub_reg = ARM64Instruction(
    instr_bit_format=Mask("xxx01011000xxxxxxxxxxxxxxxxxxxxx", 0),
    decode_fun=decoding_info.decode_add_sub_reg,
)

muls = ARM64Instruction(
    instr_bit_format=Mask("x0011011xxxxxxxxxxxxxxxxxxxxxxxx", 0),
    decode_fun=decoding_info.decode_muls,
)

ldp_stp = ARM64Instruction(
    instr_bit_format=Mask("x010100xxxxxxxxxxxxxxxxxxxxxxxxx", 0),
    decode_fun=decoding_info.decode_ldp_stp,
)

ldr_str_uimm_offset = ARM64Instruction(
    instr_bit_format=Mask("xx111001xxxxxxxxxxxxxxxxxxxxxxxx", 0),
    decode_fun=decoding_info.decode_ldr_str_uimm_offset,
)

ldr_str_pre_post_idx = ARM64Instruction(
    instr_bit_format=Mask("xx111000xx0xxxxxxxxxx1xxxxxxxxxx", 0),
    decode_fun=decoding_info.decode_ldr_str_pre_post_idx,
)

ldr_str_reg_offset = ARM64Instruction(
    instr_bit_format=Mask("xx111000xx1xxxxx011010xxxxxxxxxx", 0),
    decode_fun=decoding_info.decode_ldr_str_reg_offset,
)

nop = ARM64Instruction(
    instr_bit_format=Mask("11010101000000110010000000011111", 0),
    decode_fun=decoding_info.decode_nop,
)
