import logging
from utils import MachineCode, Mask, CCs, twos_comp

logger = logging.getLogger(__name__)


# Idea: might be able to have a generic parsing function and each
# instruction defines a set of rules to complete a string template.


def decode_add_sub_imm(mc: MachineCode) -> str:
    """Decoding logic for Section 4.01"""
    logger.debug("Action: Rd = Rn ± ((imm << 12) if sh else imm)")

    Rd_bits = mc.getBits(4, 0)
    Rd = int(Rd_bits, 2)
    logger.debug(f"\tRd (bits 4~0) = {Rd_bits} ({Rd}) ")

    Rn_bits = mc.getBits(9, 5)
    Rn = int(Rn_bits, 2)
    logger.debug(f"\tRn (bits 9~5) = {Rn_bits} ({Rn})")

    imm_bits = mc.getBits(21, 10)
    imm = twos_comp(imm_bits)
    logger.debug(f"\timm (bits 21~10) = {imm_bits} ({imm}) ")

    sh_bit = mc.getBits(22)
    sh = ", LSL #12" if sh_bit == "1" else ""
    logger.debug(f"\tsh (bit 22) = {sh_bit}")

    s_suffix_bit = mc.getBits(29)
    s_suffix = "s" if s_suffix_bit == "1" else ""
    logger.debug(f"\tS (bit 29) = {s_suffix_bit}")

    op_bit = mc.getBits(30)
    op = "add" if op_bit == "0" else "sub"
    logger.debug(f"\top (bit 30) = {op_bit} ({op})")

    reg_bit = mc.getBits(31)
    reg = "x" if reg_bit == "1" else "w"
    logger.debug(f"\tsf (bit 31) = {reg_bit} (using {reg} registers)")

    return f"{op}{s_suffix} {reg}{Rd}, {reg}{Rn}, #{imm}{sh}"


def decode_mov_wide(mc: MachineCode) -> str:
    """Decoding logic for Section 4.02"""
    logger.debug("Action: Rd = imm << (16 * hw)")

    Rd_bits = mc.getBits(4, 0)
    Rd = int(Rd_bits, 2)
    logger.debug(f"\tRd (bits 4~0) = {Rd_bits} ({Rd}) ")

    imm_bits = mc.getBits(20, 5)
    imm = twos_comp(imm_bits)
    logger.debug(f"\timm (bits 20~5) = {imm_bits} ({imm}) ")

    hw_bits = mc.getBits(21, 22)
    hw = int(hw_bits, 2)
    imm <<= hw * 16
    logger.debug(f"\thw (bits 22~21) = {hw_bits} ({hw}) ")

    reg_bit = mc.getBits(31)
    reg = "x" if reg_bit == "1" else "w"
    logger.debug(f"\tsf (bit 31) = {reg_bit} (using {reg} registers)")

    return f"mov {reg}{Rd}, #{imm}"


def decode_uncond_branch_imm(mc: MachineCode) -> str:
    """Decoding logic for Section 4.03"""
    logger.debug("Action: PC += (imm*4) *and* X30 = PC+4 *if* op")

    imm_bits = mc.getBits(25, 0)
    imm = twos_comp(imm_bits)
    logger.debug(f"\timm (bits 25~0) = {imm_bits} ({imm}) ")

    link_bit = mc.getBits(31)
    link = "l" if link_bit == "1" else ""
    logger.debug(f"\top (bit 31) = {link_bit}")

    return f"b{link} label (label is {imm * 4} bytes away from PC)"


def decode_uncond_branch_reg(mc: MachineCode) -> str:
    """Decoding logic for Section 4.04"""
    logger.debug("Action: PC = Rn *and* X30 = PC+4 *if* op")

    Rn_bits = mc.getBits(9, 5)
    Rn = int(Rn_bits, 2)
    logger.debug(f"\tRn (bits 9~5) = {Rn_bits} ({Rn})")

    link_bit = mc.getBits(21)
    link = "l" if link_bit == "1" else ""
    logger.debug(f"\top (bit 21) = {link_bit}")

    return f"b{link}r x{Rn}"


def decode_cond_branch_imm(mc: MachineCode) -> str:
    """Decoding logic for Section 4.05"""
    logger.debug("Action: PC += (imm * 4) if CC else (4)")

    cc_bits = mc.getBits(3, 0)
    cc = CCs(int(cc_bits, 2) + 1)
    logger.debug(f"\tCC (bits 3~0) = {cc_bits} ({cc}) ")

    imm_bits = mc.getBits(23, 5)
    imm = twos_comp(imm_bits)
    logger.debug(f"\timm (bits 23~5) = {imm_bits} ({imm}) ")

    return f"b.{cc.name} label (label is {imm * 4} bytes away from PC)"


def decode_comp_branch_imm(mc: MachineCode) -> str:
    """Decoding logic for Section 4.06"""
    logger.debug("Action: PC += (imm * 4) if (Rt op 0) else (4)")

    Rt_bits = mc.getBits(4, 0)
    Rt = int(Rt_bits, 2)
    logger.debug(f"\tRt (bits 4~0) = {Rt_bits} ({Rt})")

    imm_bits = mc.getBits(23, 5)
    imm = twos_comp(imm_bits)
    logger.debug(f"\timm (bits 23~5) = {imm_bits} ({imm}) ")

    op_bit = mc.getBits(24)
    op = "n" if op_bit == "1" else ""
    logger.debug(f"\top (bit 24) = {op_bit} ({'!' if op_bit == '1' else '='}= 0)")

    reg_bit = mc.getBits(31)
    reg = "x" if reg_bit == "1" else "w"
    logger.debug(f"\tsf (bit 31) = {reg_bit} (using {reg} registers)")

    return f"cb{op}z {reg}{Rt}, label (label is {imm * 4} bytes away from PC)"


def decode_sudiv(mc: MachineCode) -> str:
    """Decoding logic for Section 4.07"""
    logger.debug("Action: Rd = Rn / Rm")

    Rd_bits = mc.getBits(4, 0)
    Rd = int(Rd_bits, 2)
    logger.debug(f"\tRd (bits 4~0) = {Rd_bits} ({Rd}) ")

    Rn_bits = mc.getBits(9, 5)
    Rn = int(Rn_bits, 2)
    logger.debug(f"\tRn (bits 9~5) = {Rn_bits} ({Rn})")

    su_bit = mc.getBits(10)
    su = "s" if su_bit == "1" else "u"
    logger.debug(f"\tS/U (bit 10) = {su_bit} ({su})")

    Rm_bits = mc.getBits(20, 16)
    Rm = int(Rm_bits, 2)
    logger.debug(f"\tRm (bits 20~16) = {Rm_bits} ({Rm})")

    reg_bit = mc.getBits(31)
    reg = "x" if reg_bit == "1" else "w"
    logger.debug(f"\tsf (bit 31) = {reg_bit} (using {reg} registers)")

    return f"{su}div {reg}{Rd}, {reg}{Rn}, {reg}{Rm}"


def decode_logical(mc: MachineCode) -> str:
    """Decoding logic for Section 4.08"""
    logger.debug("Action: Rd = Rn op (N(Rm) << uimm)")

    Rd_bits = mc.getBits(4, 0)
    Rd = int(Rd_bits, 2)
    logger.debug(f"\tRd (bits 4~0) = {Rd_bits} ({Rd}) ")

    Rn_bits = mc.getBits(9, 5)
    Rn = int(Rn_bits, 2)
    logger.debug(f"\tRn (bits 9~5) = {Rn_bits} ({Rn})")

    uimm_bits = mc.getBits(15, 10)
    uimm = int(uimm_bits, 2)
    shift = f", LSL #{uimm}" if uimm > 0 else ""
    logger.debug(f"\tuimm (bits 15~10) = {uimm_bits} ({uimm}) ")

    Rm_bits = mc.getBits(20, 16)
    Rm = int(Rm_bits, 2)
    logger.debug(f"\tRm (bits 20~16) = {Rm_bits} ({Rm})")

    flip_bit = mc.getBits(21)
    logger.debug(f"\tFlip Rm (bit 21) = {flip_bit}")

    op_bits = mc.getBits(30, 29)
    op = {"00": "and", "01": "orr", "10": "eor", "11": "ands"}[op_bits]
    if flip_bit == "1":
        op = {"and": "bic", "orr": "orn", "eor": "eon", "ands": "bics"}[op]
    logger.debug(f"\top (bits 30~29) = {op_bits} ({op})")

    reg_bit = mc.getBits(31)
    reg = "x" if reg_bit == "1" else "w"
    logger.debug(f"\tsf (bit 31) = {reg_bit} (using {reg} registers)")

    return f"{op} {reg}{Rd}, {reg}{Rn}, {reg}{Rm}{shift}"


def decode_add_sub_reg(mc: MachineCode) -> str:
    """Decoding logic for Section 4.09"""
    logger.debug("Action: Rd = Rn ± (Rm << uimm)")

    Rd_bits = mc.getBits(4, 0)
    Rd = int(Rd_bits, 2)
    logger.debug(f"\tRd (bits 4~0) = {Rd_bits} ({Rd}) ")

    Rn_bits = mc.getBits(9, 5)
    Rn = int(Rn_bits, 2)
    logger.debug(f"\tRn (bits 9~5) = {Rn_bits} ({Rn})")

    uimm_bits = mc.getBits(15, 10)
    uimm = int(uimm_bits, 2)
    shift = f", LSL #{uimm}" if uimm > 0 else ""
    logger.debug(f"\tuimm (bits 15~10) = {uimm_bits} ({uimm}) ")

    Rm_bits = mc.getBits(20, 16)
    Rm = int(Rm_bits, 2)
    logger.debug(f"\tRm (bits 20~16) = {Rm_bits} ({Rm})")

    s_suffix_bit = mc.getBits(29)
    s_suffix = "s" if s_suffix_bit == "1" else ""
    logger.debug(f"\tS (bit 29) = {s_suffix_bit}")

    op_bit = mc.getBits(30)
    op = "add" if op_bit == "0" else "sub"
    logger.debug(f"\top (bit 30) = {op_bit} ({op})")

    reg_bit = mc.getBits(31)
    reg = "x" if reg_bit == "1" else "w"
    logger.debug(f"\tsf (bit 31) = {reg_bit} (using {reg} registers)")

    return f"{op}{s_suffix} {reg}{Rd}, {reg}{Rn}, {reg}{Rm}{shift}"


def decode_madd_msub(mc: MachineCode) -> str:
    """Decoding logic for Section 4.10"""
    logger.debug("Action: Rd = Ra ± Rn * Rm")

    Rd_bits = mc.getBits(4, 0)
    Rd = int(Rd_bits, 2)
    logger.debug(f"\tRd (bits 4~0) = {Rd_bits} ({Rd}) ")

    Rn_bits = mc.getBits(9, 5)
    Rn = int(Rn_bits, 2)
    logger.debug(f"\tRn (bits 9~5) = {Rn_bits} ({Rn})")

    Ra_bits = mc.getBits(14, 10)
    Ra = int(Ra_bits, 2)
    logger.debug(f"\tRa (bits 14~10) = {Ra_bits} ({Ra})")

    addsub_bit = mc.getBits(15)
    addsub = "add" if addsub_bit == "0" else "sub"
    logger.debug(f"\t± (bit 15) = {addsub_bit} ({addsub})")

    Rm_bits = mc.getBits(20, 16)
    Rm = int(Rm_bits, 2)
    logger.debug(f"\tRm (bits 20~16) = {Rm_bits} ({Rm})")

    op_bits = mc.getBits(23, 21)
    prefix = {"001": "s", "101": "u"}.get(op_bits, "")
    suffix = "l" if prefix else ""
    op = f"{prefix}m{addsub}{suffix}"
    logger.debug(f"\top (bits 23~21) = {op_bits} ({op})")

    reg_bit = mc.getBits(31)
    reg = "x" if reg_bit == "1" else "w"
    logger.debug(f"\tsf (bit 31) = {reg_bit} ({64 if reg == 'x' else 32}-bit result)")

    reg_sizes = {
        ("", "x"): ("x", "x", "x", "x"),
        ("", "w"): ("w", "w", "w", "w"),
        ("l", "x"): ("x", "w", "w", "x"),
    }[(suffix, reg)]

    return f"{op} {reg_sizes[0]}{Rd}, {reg_sizes[1]}{Rn}, {reg_sizes[2]}{Rm}, {reg_sizes[3]}{Ra}"


def decode_mulh(mc: MachineCode) -> str:
    """Decoding logic for Section 4.11"""
    logger.debug("Action: Rd = (Rn * Rm) >> 64")

    Rd_bits = mc.getBits(4, 0)
    Rd = int(Rd_bits, 2)
    logger.debug(f"\tRd (bits 4~0) = {Rd_bits} ({Rd}) ")

    Rn_bits = mc.getBits(9, 5)
    Rn = int(Rn_bits, 2)
    logger.debug(f"\tRn (bits 9~5) = {Rn_bits} ({Rn})")

    Rm_bits = mc.getBits(20, 16)
    Rm = int(Rm_bits, 2)
    logger.debug(f"\tRm (bits 20~16) = {Rm_bits} ({Rm})")

    su_bit = mc.getBits(23)
    su = "u" if su_bit == "1" else "s"
    logger.debug(f"\tS/U (bit 23) = {su_bit} ({su})")

    return f"{su}mulh x{Rd}, x{Rn}, x{Rm}"


def decode_muls(mc: MachineCode) -> str:
    logger.debug("Checking op bits to find type of multiplication...")
    if mc.checkMask(Mask("x10", 21)):
        logger.debug("\top bits are x10; mulh instruction")
        return decode_mulh(mc)
    else:
        logger.debug("\top bits are *not* x10; regular mul/neg instruction")
        return decode_madd_msub(mc)


def decode_ldp_stp(mc: MachineCode) -> str:
    """Decoding logic for Section 4.12"""
    logger.debug("Action: Rt:Rt2 <-dir-> Mem[Rn + imm * (4 if Wt:Wt2 else 8))]")

    Rt_bits = mc.getBits(4, 0)
    Rt = int(Rt_bits, 2)
    logger.debug(f"\tRt (bits 4~0) = {Rt_bits} ({Rt}) ")

    Rn_bits = mc.getBits(9, 5)
    Rn = int(Rn_bits, 2)
    logger.debug(f"\tRn (bits 9~5) = {Rn_bits} ({Rn})")

    Rt2_bits = mc.getBits(14, 10)
    Rt2 = int(Rt2_bits, 2)
    logger.debug(f"\tRt2 (bits 14~10) = {Rt2_bits} ({Rt2})")

    imm_bits = mc.getBits(21, 15)
    imm = twos_comp(imm_bits)
    logger.debug(f"\timm (bits 21~10) = {imm_bits} ({imm}) ")

    dir_bit = mc.getBits(22)
    op = "ldp" if dir_bit == "1" else "stp"
    logger.debug(f"\tdir (bit 22) = {dir_bit} ({op}) ")

    mode_bits = mc.getBits(24, 23)
    mode = {
        "01": "post-index",
        "10": "offset",
        "11": "pre-index",
    }[mode_bits]
    logger.debug(f"\tmode (bit 24~23) = {mode_bits} ({mode})")

    reg_bit = mc.getBits(31)
    reg = "x" if reg_bit == "1" else "w"
    logger.debug(f"\tsf (bit 31) = {reg_bit} (using {reg} registers)")

    real_imm = imm * (8 if reg == "x" else 4)

    offset = pre_index = post_index = ""
    if real_imm:
        offset = f", #{real_imm}" if mode in {"offset", "pre-index"} else ""
        pre_index = "!" if mode == "pre-index" else ""
        post_index = f", #{real_imm}" if mode == "post-index" else ""

    return f"{op} {reg}{Rt}, {reg}{Rt2}, [x{Rn}{offset}]{pre_index}{post_index}"


def decode_ldr_str_uimm_offset(mc: MachineCode) -> str:
    """Decoding logic for Section 4.13"""
    logger.debug("Action: Rt <-(opc)-> Mem[Rn + imm]")

    Rt_bits = mc.getBits(4, 0)
    Rt = int(Rt_bits, 2)
    logger.debug(f"\tRt (bits 4~0) = {Rt_bits} ({Rt}) ")

    Rn_bits = mc.getBits(9, 5)
    Rn = int(Rn_bits, 2)
    logger.debug(f"\tRn (bits 9~5) = {Rn_bits} ({Rn})")

    uimm_bits = mc.getBits(21, 10)
    uimm = int(uimm_bits, 2)
    logger.debug(f"\tuimm (bits 21~10) = {uimm_bits} ({uimm}) ")

    opc_bits = mc.getBits(23, 22)
    opc = {
        "00": "store",
        "01": "unsigned",
        "10": "signed into Xt",
        "11": "signed into Wt",
    }[opc_bits]
    op = "str" if opc_bits == "00" else "ldr"
    signed_suffix = "s" if opc_bits[0] == "1" else ""
    logger.debug(f"\topc (bits 23~22) = {opc_bits} ({opc}) ")

    data_size_bits = mc.getBits(31, 30)
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
    logger.debug(f"\tdata size (bits 31~30) = {data_size_bits} ({data_size}) ")

    Rt_size = "x" if (data_size == "xword" or opc == "signed into Xt") else "w"

    return f"{op}{signed_suffix}{size_suffix} {Rt_size}{Rt}, [x{Rn}, #{real_uimm}]"


def decode_ldr_str_pre_post_idx(mc: MachineCode):
    """Decoding logic for Section 4.14"""
    logger.debug("Action: Rt <-(opc)-> Mem[Rn + imm]")

    Rt_bits = mc.getBits(4, 0)
    Rt = int(Rt_bits, 2)
    logger.debug(f"\tRt (bits 4~0) = {Rt_bits} ({Rt}) ")

    Rn_bits = mc.getBits(9, 5)
    Rn = int(Rn_bits, 2)
    logger.debug(f"\tRn (bits 9~5) = {Rn_bits} ({Rn})")

    pre_post_bit = mc.getBits(11)
    pre_post = "pre-index" if pre_post_bit == "1" else "post-index"
    logger.debug(f"\tpre/post-index (bit 11) = {pre_post_bit} ({pre_post}) ")

    imm_bits = mc.getBits(20, 12)
    imm = twos_comp(imm_bits)
    logger.debug(f"\timm (bits 20~12) = {imm_bits} ({imm}) ")

    opc_bits = mc.getBits(23, 22)
    opc = {
        "00": "store",
        "01": "unsigned",
        "10": "signed into Xt",
        "11": "signed into Wt",
    }[opc_bits]
    op = "str" if opc_bits == "00" else "ldr"
    signed_suffix = "s" if opc_bits[0] == "1" else ""
    logger.debug(f"\topc (bits 23~22) = {opc_bits} ({opc}) ")

    data_size_bits = mc.getBits(31, 30)
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
    logger.debug(f"\tdata size (bits 31~30) = {data_size_bits} ({data_size}) ")

    Rt_size = "x" if (data_size == "xword" or opc == "signed into Xt") else "w"
    index_suffix = f", #{imm}]!" if pre_post == "pre-index" else f"], #{imm}"

    return f"{op}{signed_suffix}{size_suffix} {Rt_size}{Rt}, [x{Rn}{index_suffix}"


def decode_ldr_str_reg_offset(mc: MachineCode):
    """Decoding logic for Section 4.15"""
    logger.debug("Action: Rt <-(opc)-> Mem[Rn + Rm]")

    Rt_bits = mc.getBits(4, 0)
    Rt = int(Rt_bits, 2)
    logger.debug(f"\tRt (bits 4~0) = {Rt_bits} ({Rt}) ")

    Rn_bits = mc.getBits(9, 5)
    Rn = int(Rn_bits, 2)
    logger.debug(f"\tRn (bits 9~5) = {Rn_bits} ({Rn})")

    Rm_bits = mc.getBits(20, 16)
    Rm = int(Rm_bits, 2)
    logger.debug(f"\tRm (bits 20~16) = {Rm_bits} ({Rm})")

    opc_bits = mc.getBits(23, 22)
    opc = {
        "00": "store",
        "01": "unsigned",
        "10": "signed into Xt",
        "11": "signed into Wt",
    }[opc_bits]
    op = "str" if opc_bits == "00" else "ldr"
    signed_suffix = "s" if opc_bits[0] == "1" else ""
    logger.debug(f"\topc (bits 23~22) = {opc_bits} ({opc}) ")

    data_size_bits = mc.getBits(31, 30)
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
    logger.debug(f"\tdata size (bits 31~30) = {data_size_bits} ({data_size}) ")

    Rt_size = "x" if (data_size == "xword" or opc == "signed into Xt") else "w"

    return f"{op}{signed_suffix}{size_suffix} {Rt_size}{Rt}, [x{Rn}, x{Rm}]"


def decode_nop(mc: MachineCode) -> str:
    """Decoding logic for Section 4.16"""
    logger.debug("Action: literally does nothing")
    return "nop"
