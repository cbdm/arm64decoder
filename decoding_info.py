"""Logic to decode machine code bytes into instructions for the Section 4 instructions."""

import logging

from utils import CCs, MachineCode, Mask, twos_comp

logger = logging.getLogger(__name__)


# Idea: might be able to have a generic parsing function and each
# instruction defines a set of rules to complete a string template.


def decode_add_sub_imm(mc: MachineCode) -> str:
    """Decoding logic for Section 4.01"""
    logger.debug("Action: Rd = Rn ± ((imm << 12) if sh else imm)")

    rd_bits = mc.get_bits(4, 0)
    rd = int(rd_bits, 2)
    logger.debug("\tRd (bits 4~0) = %s (%d) ", rd_bits, rd)

    rn_bits = mc.get_bits(9, 5)
    rn = int(rn_bits, 2)
    logger.debug("\tRn (bits 9~5) = %s (%d)", rn_bits, rn)

    imm_bits = mc.get_bits(21, 10)
    imm = twos_comp(imm_bits)
    logger.debug("\timm (bits 21~10) = %s (%d) ", imm_bits, imm)

    sh_bit = mc.get_bits(22)
    sh = ", LSL #12" if sh_bit == "1" else ""
    logger.debug("\tsh (bit 22) = %s", sh_bit)

    s_suffix_bit = mc.get_bits(29)
    s_suffix = "s" if s_suffix_bit == "1" else ""
    logger.debug("\tS (bit 29) = %s", s_suffix_bit)

    op_bit = mc.get_bits(30)
    op = "add" if op_bit == "0" else "sub"
    logger.debug("\top (bit 30) = %s (%s)", op_bit, op)

    reg_bit = mc.get_bits(31)
    reg = "x" if reg_bit == "1" else "w"
    logger.debug("\tsf (bit 31) = %s (using %s registers)", reg_bit, reg)

    return f"{op}{s_suffix} {reg}{rd}, {reg}{rn}, #{imm}{sh}"


def decode_mov_wide(mc: MachineCode) -> str:
    """Decoding logic for Section 4.02"""
    logger.debug("Action: Rd = imm << (16 * hw)")

    rd_bits = mc.get_bits(4, 0)
    rd = int(rd_bits, 2)
    logger.debug("\tRd (bits 4~0) = %s (%d) ", rd_bits, rd)

    imm_bits = mc.get_bits(20, 5)
    imm = twos_comp(imm_bits)
    logger.debug("\timm (bits 20~5) = %s (%d) ", imm_bits, imm)

    hw_bits = mc.get_bits(21, 22)
    hw = int(hw_bits, 2)
    imm <<= hw * 16
    logger.debug("\thw (bits 22~21) = %s (%d) ", hw_bits, hw)

    reg_bit = mc.get_bits(31)
    reg = "x" if reg_bit == "1" else "w"
    logger.debug("\tsf (bit 31) = %s (using %s registers)", reg_bit, reg)

    return f"mov {reg}{rd}, #{imm}"


def decode_uncond_branch_imm(mc: MachineCode) -> str:
    """Decoding logic for Section 4.03"""
    logger.debug("Action: PC += (imm*4) *and* X30 = PC+4 *if* op")

    imm_bits = mc.get_bits(25, 0)
    imm = twos_comp(imm_bits)
    logger.debug("\timm (bits 25~0) = %s (%d) ", imm_bits, imm)

    link_bit = mc.get_bits(31)
    link = "l" if link_bit == "1" else ""
    logger.debug("\top (bit 31) = %s", link_bit)

    return f"b{link} label // (label is {imm * 4} bytes away from PC)"


def decode_uncond_branch_reg(mc: MachineCode) -> str:
    """Decoding logic for Section 4.04"""
    logger.debug("Action: PC = Rn *and* X30 = PC+4 *if* op")

    rn_bits = mc.get_bits(9, 5)
    rn = int(rn_bits, 2)
    logger.debug("\tRn (bits 9~5) = %s (%d)", rn_bits, rn)

    link_bit = mc.get_bits(21)
    link = "l" if link_bit == "1" else ""
    logger.debug("\top (bit 21) = %s", link_bit)

    return f"b{link}r x{rn}"


def decode_cond_branch_imm(mc: MachineCode) -> str:
    """Decoding logic for Section 4.05"""
    logger.debug("Action: PC += (imm * 4) if CC else (4)")

    cc_bits = mc.get_bits(3, 0)
    cc = CCs(int(cc_bits, 2) + 1)
    logger.debug("\tCC (bits 3~0) = %s (%s) ", cc_bits, cc)

    imm_bits = mc.get_bits(23, 5)
    imm = twos_comp(imm_bits)
    logger.debug("\timm (bits 23~5) = %s (%d) ", imm_bits, imm)

    return f"b.{cc.name} label // (label is {imm * 4} bytes away from PC)"


def decode_comp_branch_imm(mc: MachineCode) -> str:
    """Decoding logic for Section 4.06"""
    logger.debug("Action: PC += (imm * 4) if (Rt op 0) else (4)")

    rt_bits = mc.get_bits(4, 0)
    rt = int(rt_bits, 2)
    logger.debug("\tRt (bits 4~0) = %s (%d)", rt_bits, rt)

    imm_bits = mc.get_bits(23, 5)
    imm = twos_comp(imm_bits)
    logger.debug("\timm (bits 23~5) = %s (%d) ", imm_bits, imm)

    op_bit = mc.get_bits(24)
    op = "n" if op_bit == "1" else ""
    logger.debug("\top (bit 24) = %s (%s= 0)", op_bit, "!" if op_bit == "1" else "=")

    reg_bit = mc.get_bits(31)
    reg = "x" if reg_bit == "1" else "w"
    logger.debug("\tsf (bit 31) = %s (using %s registers)", reg_bit, reg)

    return f"cb{op}z {reg}{rt}, label // (label is {imm * 4} bytes away from PC)"


def decode_sudiv(mc: MachineCode) -> str:
    """Decoding logic for Section 4.07"""
    logger.debug("Action: Rd = Rn / Rm")

    rd_bits = mc.get_bits(4, 0)
    rd = int(rd_bits, 2)
    logger.debug("\tRd (bits 4~0) = %s (%d) ", rd_bits, rd)

    rn_bits = mc.get_bits(9, 5)
    rn = int(rn_bits, 2)
    logger.debug("\tRn (bits 9~5) = %s (%d)", rn_bits, rn)

    su_bit = mc.get_bits(10)
    su = "s" if su_bit == "1" else "u"
    logger.debug("\tS/U (bit 10) = %s (%s)", su_bit, su)

    rm_bits = mc.get_bits(20, 16)
    rm = int(rm_bits, 2)
    logger.debug("\tRm (bits 20~16) = %s (%d)", rm_bits, rm)

    reg_bit = mc.get_bits(31)
    reg = "x" if reg_bit == "1" else "w"
    logger.debug("\tsf (bit 31) = %s (using %s registers)", reg_bit, reg)

    return f"{su}div {reg}{rd}, {reg}{rn}, {reg}{rm}"


def decode_logical(mc: MachineCode) -> str:
    """Decoding logic for Section 4.08"""
    logger.debug("Action: Rd = Rn op (N(Rm) << uimm)")

    rd_bits = mc.get_bits(4, 0)
    rd = int(rd_bits, 2)
    logger.debug("\tRd (bits 4~0) = %s (%d) ", rd_bits, rd)

    rn_bits = mc.get_bits(9, 5)
    rn = int(rn_bits, 2)
    logger.debug("\tRn (bits 9~5) = %s (%d)", rn_bits, rn)

    uimm_bits = mc.get_bits(15, 10)
    uimm = int(uimm_bits, 2)
    shift = f", LSL #{uimm}" if uimm > 0 else ""
    logger.debug("\tuimm (bits 15~10) = %s (%d)", uimm_bits, uimm)

    rm_bits = mc.get_bits(20, 16)
    rm = int(rm_bits, 2)
    logger.debug("\tRm (bits 20~16) = %s (%d)", rm_bits, rm)

    flip_bit = mc.get_bits(21)
    logger.debug("\tFlip Rm (bit 21) = %s", flip_bit)

    op_bits = mc.get_bits(30, 29)
    op = {"00": "and", "01": "orr", "10": "eor", "11": "ands"}[op_bits]
    if flip_bit == "1":
        op = {"and": "bic", "orr": "orn", "eor": "eon", "ands": "bics"}[op]
    logger.debug("\top (bits 30~29) = %s (%s)", op_bits, op)

    reg_bit = mc.get_bits(31)
    reg = "x" if reg_bit == "1" else "w"
    logger.debug("\tsf (bit 31) = %s (using %s registers)", reg_bit, reg)

    return f"{op} {reg}{rd}, {reg}{rn}, {reg}{rm}{shift}"


def decode_add_sub_reg(mc: MachineCode) -> str:
    """Decoding logic for Section 4.09"""
    logger.debug("Action: Rd = Rn ± (Rm << uimm)")

    rd_bits = mc.get_bits(4, 0)
    rd = int(rd_bits, 2)
    logger.debug("\tRd (bits 4~0) = %s (%d) ", rd_bits, rd)

    rn_bits = mc.get_bits(9, 5)
    rn = int(rn_bits, 2)
    logger.debug("\tRn (bits 9~5) = %s (%d)", rn_bits, rn)

    uimm_bits = mc.get_bits(15, 10)
    uimm = int(uimm_bits, 2)
    shift = f", LSL #{uimm}" if uimm > 0 else ""
    logger.debug("\tuimm (bits 15~10) = %s (%d)", uimm_bits, uimm)

    rm_bits = mc.get_bits(20, 16)
    rm = int(rm_bits, 2)
    logger.debug("\tRm (bits 20~16) = %s (%d)", rm_bits, rm)

    s_suffix_bit = mc.get_bits(29)
    s_suffix = "s" if s_suffix_bit == "1" else ""
    logger.debug("\tS (bit 29) = %s", s_suffix_bit)

    op_bit = mc.get_bits(30)
    op = "add" if op_bit == "0" else "sub"
    logger.debug("\top (bit 30) = %s (%s)", op_bit, op)

    reg_bit = mc.get_bits(31)
    reg = "x" if reg_bit == "1" else "w"
    logger.debug("\tsf (bit 31) = %s (using %s registers)", reg_bit, reg)

    return f"{op}{s_suffix} {reg}{rd}, {reg}{rn}, {reg}{rm}{shift}"


def decode_madd_msub(mc: MachineCode) -> str:
    """Decoding logic for Section 4.10"""
    logger.debug("Action: Rd = Ra ± Rn * Rm")

    rd_bits = mc.get_bits(4, 0)
    rd = int(rd_bits, 2)
    logger.debug("\tRd (bits 4~0) = %s (%d) ", rd_bits, rd)

    rn_bits = mc.get_bits(9, 5)
    rn = int(rn_bits, 2)
    logger.debug("\tRn (bits 9~5) = %s (%d)", rn_bits, rn)

    ra_bits = mc.get_bits(14, 10)
    ra = int(ra_bits, 2)
    logger.debug("\tRa (bits 14~10) = %s (%d)", ra_bits, ra)

    addsub_bit = mc.get_bits(15)
    addsub = "add" if addsub_bit == "0" else "sub"
    logger.debug("\t± (bit 15) = %s (%s)", addsub_bit, addsub)

    rm_bits = mc.get_bits(20, 16)
    rm = int(rm_bits, 2)
    logger.debug("\tRm (bits 20~16) = %s (%d)", rm_bits, rm)

    op_bits = mc.get_bits(23, 21)
    prefix = {"001": "s", "101": "u"}.get(op_bits, "")
    suffix = "l" if prefix else ""
    op = f"{prefix}m{addsub}{suffix}"
    logger.debug("\top (bits 23~21) = %s (%s)", op_bits, op)

    reg_bit = mc.get_bits(31)
    reg = "x" if reg_bit == "1" else "w"
    logger.debug(
        "\tsf (bit 31) = %s (%d-bit result)", reg_bit, 64 if reg == "x" else 32
    )

    reg_sizes = {
        ("", "x"): ("x", "x", "x", "x"),
        ("", "w"): ("w", "w", "w", "w"),
        ("l", "x"): ("x", "w", "w", "x"),
    }[(suffix, reg)]

    return f"{op} {reg_sizes[0]}{rd}, {reg_sizes[1]}{rn}, {reg_sizes[2]}{rm}, {reg_sizes[3]}{ra}"


def decode_mulh(mc: MachineCode) -> str:
    """Decoding logic for Section 4.11"""
    logger.debug("Action: Rd = (Rn * Rm) >> 64")

    rd_bits = mc.get_bits(4, 0)
    rd = int(rd_bits, 2)
    logger.debug("\tRd (bits 4~0) = %s (%d) ", rd_bits, rd)

    rn_bits = mc.get_bits(9, 5)
    rn = int(rn_bits, 2)
    logger.debug("\tRn (bits 9~5) = %s (%d)", rn_bits, rn)

    rm_bits = mc.get_bits(20, 16)
    rm = int(rm_bits, 2)
    logger.debug("\tRm (bits 20~16) = %s (%d)", rm_bits, rm)

    su_bit = mc.get_bits(23)
    su = "u" if su_bit == "1" else "s"
    logger.debug("\tS/U (bit 23) = %s (%s)", su_bit, su)

    return f"{su}mulh x{rd}, x{rn}, x{rm}"


def decode_muls(mc: MachineCode) -> str:
    """Find whether this is a mulh or regular mul instruction."""

    logger.debug("Checking op bits to find type of multiplication...")
    if mc.check_mask(Mask("x10", 21)):
        logger.debug("\top bits are x10; mulh instruction")
        return decode_mulh(mc)
    else:
        logger.debug("\top bits are *not* x10; regular mul/neg instruction")
        return decode_madd_msub(mc)


def decode_ldp_stp(mc: MachineCode) -> str:
    """Decoding logic for Section 4.12"""
    logger.debug("Action: Rt:Rt2 <-dir-> Mem[Rn + imm * (4 if Wt:Wt2 else 8))]")

    rt_bits = mc.get_bits(4, 0)
    rt = int(rt_bits, 2)
    logger.debug("\tRt (bits 4~0) = %s (%d)", rt_bits, rt)

    rn_bits = mc.get_bits(9, 5)
    rn = int(rn_bits, 2)
    logger.debug("\tRn (bits 9~5) = %s (%d)", rn_bits, rn)

    rt2_bits = mc.get_bits(14, 10)
    rt2 = int(rt2_bits, 2)
    logger.debug("\tRt2 (bits 14~10) = %s (%d)", rt2_bits, rt2)

    imm_bits = mc.get_bits(21, 15)
    imm = twos_comp(imm_bits)
    logger.debug("\timm (bits 21~10) = %s (%d) ", imm_bits, imm)

    dir_bit = mc.get_bits(22)
    op = "ldp" if dir_bit == "1" else "stp"
    logger.debug("\tdir (bit 22) = %s (%s)", dir_bit, op)

    mode_bits = mc.get_bits(24, 23)
    mode = {
        "01": "post-index",
        "10": "offset",
        "11": "pre-index",
    }[mode_bits]
    logger.debug("\tmode (bit 24~23) = %s (%s)", mode_bits, mode)

    reg_bit = mc.get_bits(31)
    reg = "x" if reg_bit == "1" else "w"
    logger.debug("\tsf (bit 31) = %s (using %s registers)", reg_bit, reg)

    real_imm = imm * (8 if reg == "x" else 4)

    offset = pre_index = post_index = ""
    if real_imm:
        offset = f", #{real_imm}" if mode in {"offset", "pre-index"} else ""
        pre_index = "!" if mode == "pre-index" else ""
        post_index = f", #{real_imm}" if mode == "post-index" else ""

    return f"{op} {reg}{rt}, {reg}{rt2}, [x{rn}{offset}]{pre_index}{post_index}"


def decode_ldr_str_uimm_offset(mc: MachineCode) -> str:
    """Decoding logic for Section 4.13"""
    logger.debug("Action: Rt <-(opc)-> Mem[Rn + imm]")

    rt_bits = mc.get_bits(4, 0)
    rt = int(rt_bits, 2)
    logger.debug("\tRt (bits 4~0) = %s (%d)", rt_bits, rt)

    rn_bits = mc.get_bits(9, 5)
    rn = int(rn_bits, 2)
    logger.debug("\tRn (bits 9~5) = %s (%d)", rn_bits, rn)

    uimm_bits = mc.get_bits(21, 10)
    uimm = int(uimm_bits, 2)
    logger.debug("\tuimm (bits 21~10) = %s (%d)", uimm_bits, uimm)

    opc_bits = mc.get_bits(23, 22)
    opc = {
        "00": "store",
        "01": "unsigned",
        "10": "signed into Xt",
        "11": "signed into Wt",
    }[opc_bits]
    op = "str" if opc_bits == "00" else "ldr"
    signed_suffix = "s" if opc_bits[0] == "1" else ""
    logger.debug("\topc (bits 23~22) = %s (%s)", opc_bits, opc)

    data_size_bits = mc.get_bits(31, 30)
    data_size = {
        "00": "byte",
        "01": "hword",
        "10": "word",
        "11": "xword",
    }[data_size_bits]
    size_suffix = {
        "byte": "b",
        "hword": "h",
    }.get(data_size, "")
    # Scale immediate based on data size's natural alignment
    real_uimm = uimm * {"byte": 1, "hword": 2, "word": 4, "xword": 8}[data_size]
    if signed_suffix and not size_suffix:
        # If we're doing sign extension without byte/hword, must be word into Xt.
        size_suffix = "w"
    logger.debug("\tdata size (bits 31~30) = %s (%s)", data_size_bits, data_size)

    rt_size = "x" if (data_size == "xword" or opc == "signed into Xt") else "w"

    return f"{op}{signed_suffix}{size_suffix} {rt_size}{rt}, [x{rn}, #{real_uimm}]"


def decode_ldr_str_pre_post_idx(mc: MachineCode):
    """Decoding logic for Section 4.14"""
    logger.debug("Action: Rt <-(opc)-> Mem[Rn + imm]")

    rt_bits = mc.get_bits(4, 0)
    rt = int(rt_bits, 2)
    logger.debug("\tRt (bits 4~0) = %s (%d)", rt_bits, rt)

    rn_bits = mc.get_bits(9, 5)
    rn = int(rn_bits, 2)
    logger.debug("\tRn (bits 9~5) = %s (%d)", rn_bits, rn)

    pre_post_bit = mc.get_bits(11)
    pre_post = "pre-index" if pre_post_bit == "1" else "post-index"
    logger.debug("\tpre/post-index (bit 11) = %s (%s)", pre_post_bit, pre_post)

    imm_bits = mc.get_bits(20, 12)
    imm = twos_comp(imm_bits)
    logger.debug("\timm (bits 20~12) = %s (%d)", imm_bits, imm)

    opc_bits = mc.get_bits(23, 22)
    opc = {
        "00": "store",
        "01": "unsigned",
        "10": "signed into Xt",
        "11": "signed into Wt",
    }[opc_bits]
    op = "str" if opc_bits == "00" else "ldr"
    signed_suffix = "s" if opc_bits[0] == "1" else ""
    logger.debug("\topc (bits 23~22) = %s (%s)", opc_bits, opc)

    data_size_bits = mc.get_bits(31, 30)
    data_size = {
        "00": "byte",
        "01": "hword",
        "10": "word",
        "11": "xword",
    }[data_size_bits]
    size_suffix = {
        "byte": "b",
        "hword": "h",
    }.get(data_size, "")
    if signed_suffix and not size_suffix:
        # If we're doing sign extension without byte/hword, must be word into Xt.
        size_suffix = "w"
    logger.debug("\tdata size (bits 31~30) = %s (%s)", data_size_bits, data_size)

    rt_size = "x" if (data_size == "xword" or opc == "signed into Xt") else "w"
    index_suffix = f", #{imm}]!" if pre_post == "pre-index" else f"], #{imm}"

    return f"{op}{signed_suffix}{size_suffix} {rt_size}{rt}, [x{rn}{index_suffix}"


def decode_ldr_str_reg_offset(mc: MachineCode):
    """Decoding logic for Section 4.15"""
    logger.debug("Action: Rt <-(opc)-> Mem[Rn + Rm]")

    rt_bits = mc.get_bits(4, 0)
    rt = int(rt_bits, 2)
    logger.debug("\tRt (bits 4~0) = %s (%d)", rt_bits, rt)

    rn_bits = mc.get_bits(9, 5)
    rn = int(rn_bits, 2)
    logger.debug("\tRn (bits 9~5) = %s (%d)", rn_bits, rn)

    rm_bits = mc.get_bits(20, 16)
    rm = int(rm_bits, 2)
    logger.debug("\tRm (bits 20~16) = %s (%d)", rm_bits, rm)

    opc_bits = mc.get_bits(23, 22)
    opc = {
        "00": "store",
        "01": "unsigned",
        "10": "signed into Xt",
        "11": "signed into Wt",
    }[opc_bits]
    op = "str" if opc_bits == "00" else "ldr"
    signed_suffix = "s" if opc_bits[0] == "1" else ""
    logger.debug("\topc (bits 23~22) = %s (%s)", opc_bits, opc)

    data_size_bits = mc.get_bits(31, 30)
    data_size = {
        "00": "byte",
        "01": "hword",
        "10": "word",
        "11": "xword",
    }[data_size_bits]
    size_suffix = {
        "byte": "b",
        "hword": "h",
    }.get(data_size, "")
    if signed_suffix and not size_suffix:
        # If we're doing sign extension without byte/hword, must be word into Xt.
        size_suffix = "w"
    logger.debug("\tdata size (bits 31~30) = %s (%s)", data_size_bits, data_size)

    rt_size = "x" if (data_size == "xword" or opc == "signed into Xt") else "w"

    return f"{op}{signed_suffix}{size_suffix} {rt_size}{rt}, [x{rn}, x{rm}]"


def decode_nop(unused_mc: MachineCode) -> str:
    """Decoding logic for Section 4.16"""
    logger.debug("Action: literally does nothing")
    return "nop"
