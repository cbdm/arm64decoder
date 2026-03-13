"""Logic to encode the Section 4 instructions into machine code bytes."""

import logging
import re

from utils import CCs, MachineCode, to_twos_comp

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


def encode_uncond_branch_imm(matches: re.Match[str]) -> MachineCode:
    """Encoding logic for Section 4.03"""
    logger.debug("Creating machine code for a b instruction")

    binary_format = "{link}00101{imm}"
    logger.debug("Instruction format: %s", binary_format)

    link, imm = matches.groups()
    logger.debug("Parsed following information from given asm instruction:")
    logger.debug("\tlink: %s", link)
    logger.debug("\timm: %s", imm)

    int_imm = int(imm)
    assert int_imm % 4 == 0, "The immediate has to be a multiple of 4"

    binary_result = binary_format.format(
        link=1 if link is not None else 0,
        imm=to_twos_comp(int_imm // 4, 26),
    )
    logger.debug("Binary result: %s", binary_result)

    mc = MachineCode.from_binary(binary_result)
    logger.debug("Hex result: %s", mc.get_pretty_hex())
    return mc


def encode_uncond_branch_reg(matches: re.Match[str]) -> MachineCode:
    """Encoding logic for Section 4.04"""
    logger.debug("Creating machine code for a br instruction")

    binary_format = "1101011000{link}11111000000{Rn}00000"
    logger.debug("Instruction format: %s", binary_format)

    link, rn = matches.groups()
    logger.debug("Parsed following information from given asm instruction:")
    logger.debug("\tlink: %s", link)
    logger.debug("\trn: %s", rn)

    binary_result = binary_format.format(
        link=1 if link is not None else 0,
        Rn=f"{int(rn):05b}",
    )
    logger.debug("Binary result: %s", binary_result)

    mc = MachineCode.from_binary(binary_result)
    logger.debug("Hex result: %s", mc.get_pretty_hex())
    return mc


def encode_cond_branch_imm(matches: re.Match[str]) -> MachineCode:
    """Encoding logic for Section 4.05"""
    logger.debug("Creating machine code for a b.cc instruction")

    binary_format = "01010100{imm}0{CC}"
    logger.debug("Instruction format: %s", binary_format)

    cc, imm = matches.groups()
    logger.debug("Parsed following information from given asm instruction:")
    logger.debug("\tcc: %s", cc)
    logger.debug("\timm: %s", imm)

    int_imm = int(imm)
    assert int_imm % 4 == 0, "The immediate has to be a multiple of 4"

    binary_result = binary_format.format(
        imm=to_twos_comp(int_imm // 4, 19),
        CC=f"{CCs.__members__[cc].value-1:04b}",
    )
    logger.debug("Binary result: %s", binary_result)

    mc = MachineCode.from_binary(binary_result)
    logger.debug("Hex result: %s", mc.get_pretty_hex())
    return mc


def encode_comp_branch_imm(matches: re.Match[str]) -> MachineCode:
    """Encoding logic for Section 4.06"""
    logger.debug("Creating machine code for a cbz instruction")

    binary_format = "{size}011010{op}{imm}{Rt}"
    logger.debug("Instruction format: %s", binary_format)

    op, size_rt, rt, imm = matches.groups()
    logger.debug("Parsed following information from given asm instruction:")
    logger.debug("\top: %s", op)
    logger.debug("\tsize_rt: %s", size_rt)
    logger.debug("\trt: %s", rt)
    logger.debug("\timm: %s", imm)

    int_imm = int(imm)
    assert int_imm % 4 == 0, "The immediate has to be a multiple of 4"

    binary_result = binary_format.format(
        size=1 if size_rt == "x" else 0,
        op=0 if op is None else 1,
        imm=to_twos_comp(int_imm // 4, 19),
        Rt=f"{int(rt):05b}",
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


def encode_logical(matches: re.Match[str]) -> MachineCode:
    """Encoding logic for Section 4.08"""
    logger.debug("Creating machine code for a logical instruction")

    binary_format = "{size}{op}0101000{N}{Rm}{uimm}{Rn}{Rd}"
    logger.debug("Instruction format: %s", binary_format)

    ops, size_rd, rd, size_rn, rn, size_rm, rm, shift, uimm, base, value = (
        matches.groups()
    )
    logger.debug("Parsed following information from given asm instruction:")
    logger.debug("\tops: %s", ops)
    logger.debug("\tsize_rd: %s", size_rd)
    logger.debug("\trd: %s", rd)
    logger.debug("\tsize_rn: %s", size_rn)
    logger.debug("\trn: %s", rn)
    logger.debug("\tsize_rm: %s", size_rm)
    logger.debug("\trm: %s", rm)
    logger.debug("\tshift: %s", shift)
    logger.debug("\tbase: %s", base)
    logger.debug("\tvalue: %s", value)

    assert size_rd == size_rn == size_rm, "All registers must be of same size"

    op, n = {
        "and": ("00", 0),
        "orr": ("01", 0),
        "eor": ("10", 0),
        "ands": ("11", 0),
        "bic": ("00", 1),
        "orn": ("01", 1),
        "eon": ("10", 1),
        "bics": ("11", 1),
    }[ops]

    binary_result = binary_format.format(
        size=1 if size_rd == "x" else 0,
        op=op,
        N=n,
        Rm=f"{int(rm):05b}",
        uimm=f"{int(uimm, 0):06b}",
        Rn=f"{int(rn):05b}",
        Rd=f"{int(rd):05b}",
    )
    logger.debug("Binary result: %s", binary_result)

    mc = MachineCode.from_binary(binary_result)
    logger.debug("Hex result: %s", mc.get_pretty_hex())
    return mc


def encode_add_sub_reg(matches: re.Match[str]) -> MachineCode:
    """Encoding logic for Section 4.09"""
    logger.debug("Creating machine code for a add/sum immediate instruction")

    binary_format = "{size}{op}{s_suffix}01011000{Rm}{uimm}{Rn}{Rd}"
    logger.debug("Instruction format: %s", binary_format)

    (
        op,
        s_bit,
        size_rd,
        rd,
        size_rn,
        rn,
        size_rm,
        rm,
        shift,
        uimm,
        uimm_base,
        uimm_val,
    ) = matches.groups()
    logger.debug("Parsed following information from given asm instruction:")
    logger.debug("\top: %s", op)
    logger.debug("\ts_bit: %s", s_bit)
    logger.debug("\tsize_rd: %s", size_rd)
    logger.debug("\trd: %s", rd)
    logger.debug("\tsize_rn: %s", size_rn)
    logger.debug("\trn: %s", rn)
    logger.debug("\tsize_rn: %s", size_rm)
    logger.debug("\trn: %s", rm)
    logger.debug("\tshift: %s", shift)
    logger.debug("\tuimm: %s", uimm)
    logger.debug("\tuimm_base: %s", uimm_base)
    logger.debug("\tuimm_val: %s", uimm_val)

    assert size_rd == size_rm == size_rn, "All registers must be of same size"

    binary_result = binary_format.format(
        size=1 if size_rd == "x" else 0,
        op=1 if op == "sub" else 0,
        s_suffix=1 if s_bit is not None else 0,
        Rm=f"{int(rm):05b}",
        uimm=f"{int(uimm if uimm is not None else '0', 0):06b}",
        Rn=f"{int(rn):05b}",
        Rd=f"{int(rd):05b}",
    )
    logger.debug("Binary result: %s", binary_result)

    mc = MachineCode.from_binary(binary_result)
    logger.debug("Hex result: %s", mc.get_pretty_hex())
    return mc


def encode_madd_msub(matches: re.Match[str]) -> MachineCode:
    """Encoding logic for Section 4.10"""
    logger.debug("Creating machine code for a madd/msub instruction")

    binary_format = "{result_size}0011011{op}{Rm}{addsub}{Ra}{Rn}{Rd}"
    logger.debug("Instruction format: %s", binary_format)

    op, size_rd, rd, size_rn, rn, size_rm, rm, _, size_ra, ra = matches.groups()
    logger.debug("Parsed following information from given asm instruction:")
    logger.debug("\top: %s", op)
    logger.debug("\tsize_rd: %s", size_rd)
    logger.debug("\trd: %s", rd)
    logger.debug("\tsize_rn: %s", size_rn)
    logger.debug("\trn: %s", rn)
    logger.debug("\tsize_rm: %s", size_rm)
    logger.debug("\trm: %s", rm)
    logger.debug("\tsize_ra: %s", size_ra)
    logger.debug("\tra: %s", ra)

    assert size_ra == size_rd, "Ra and Rd must have the same size"
    assert size_rn == size_rm, "Rn and Rm must have the same size"

    op_bits, addsub = {
        "madd": ("000", 0),
        "msub": ("000", 1),
        "smaddl": ("001", 0),
        "smsubl": ("001", 1),
        "umaddl": ("101", 0),
        "umsubl": ("101", 1),
    }[op]

    binary_result = binary_format.format(
        result_size=1 if size_rd == "x" else 0,
        op=op_bits,
        Rm=f"{int(rm):05b}",
        addsub=addsub,
        Ra=f"{int(ra):05b}",
        Rn=f"{int(rn):05b}",
        Rd=f"{int(rd):05b}",
    )
    logger.debug("Binary result: %s", binary_result)

    mc = MachineCode.from_binary(binary_result)
    logger.debug("Hex result: %s", mc.get_pretty_hex())
    return mc


def encode_mulh(matches: re.Match[str]) -> MachineCode:
    """Encoding logic for Section 4.11"""
    logger.debug("Creating machine code for a mulh instruction")

    binary_format = "10011011{sign}10{Rm}011111{Rn}{Rd}"
    logger.debug("Instruction format: %s", binary_format)

    op, _, rd, _, rn, _, rm, *_ = matches.groups()
    logger.debug("Parsed following information from given asm instruction:")
    logger.debug("\top: %s", op)
    logger.debug("\trd: %s", rd)
    logger.debug("\trn: %s", rn)
    logger.debug("\trm: %s", rm)

    binary_result = binary_format.format(
        sign=0 if op == "smulh" else 1,
        Rm=f"{int(rm):05b}",
        Rn=f"{int(rn):05b}",
        Rd=f"{int(rd):05b}",
    )
    logger.debug("Binary result: %s", binary_result)

    mc = MachineCode.from_binary(binary_result)
    logger.debug("Hex result: %s", mc.get_pretty_hex())
    return mc


def encode_muls(matches: re.Match[str]) -> MachineCode:
    """Find whether this is a mulh or regular mul instruction."""

    op, *_ = matches.groups()
    if op in {"smulh", "umulh"}:
        return encode_mulh(matches)

    return encode_madd_msub(matches)


def encode_ldr_str_uimm_offset(matches: re.Match[str]) -> MachineCode:
    """Encoding logic for Section 4.13"""
    logger.debug("Creating machine code for a ldr/str offset instruction")

    binary_format = "{size}111001{opc}{uimm}{Rn}{Rt}"
    logger.debug("Instruction format: %s", binary_format)

    (
        op,
        signed,
        size,
        size_rt,
        rt,
        rn,
        offset,
        offset_uimm,
        offset_base,
        offset_value,
    ) = matches.groups()
    logger.debug("Parsed following information from given asm instruction:")
    logger.debug("\top: %s", op)
    logger.debug("\tsigned: %s", signed)
    logger.debug("\tsize: %s", size)
    logger.debug("\tsize_rt: %s", size_rt)
    logger.debug("\trt: %s", rt)
    logger.debug("\trn: %s", rn)
    logger.debug("\toffset: %s", offset)
    logger.debug("\toffset_uimm: %s", offset_uimm)
    logger.debug("\toffset_base: %s", offset_base)
    logger.debug("\toffset_value: %s", offset_value)

    assert signed is None or op == "ldr", "There's no sign extension for str"
    assert size is None or signed, "Need to define a size for sign extension"

    opc, result_size = {
        "str": ("00", "11" if size_rt == "x" else "10"),
        "ldr": ("01", "11" if size_rt == "x" else "10"),
        "ldrb": ("01", "00"),
        "ldrh": ("01", "01"),
        "ldrsb": ("10" if size_rt == "x" else "11", "00"),
        "ldrsh": ("10" if size_rt == "x" else "11", "01"),
        "ldrsw": ("10", "10"),
    }[f"{op}{signed}{size}"]

    align = 2 ** int(result_size, 2)
    uimm = int(offset_uimm, 0) if offset_uimm else 0
    assert uimm % align == 0, "Offset needs to be naturally aligned to the data size"

    binary_result = binary_format.format(
        size=result_size,
        opc=opc,
        uimm=f"{uimm // align:012b}",
        Rn=f"{int(rn, 0):05b}",
        Rt=f"{int(rt, 0):05b}",
    )
    logger.debug("Binary result: %s", binary_result)

    mc = MachineCode.from_binary(binary_result)
    logger.debug("Hex result: %s", mc.get_pretty_hex())
    return mc


def encode_ldr_str_pre_post_idx(matches: re.Match[str]) -> MachineCode:
    """Encoding logic for Section 4.14"""
    logger.debug("Creating machine code for a ldr/str pre/post-index instruction")

    binary_format = "{size}111000{opc}0{imm}{prepost}1{Rn}{Rt}"
    logger.debug("Instruction format: %s", binary_format)

    (
        op,
        signed,
        size,
        size_rt,
        rt,
        rn,
        offset,
        pre_offset,
        pre_offset_imm,
        pre_offset_sign,
        pre_offset_base,
        pre_offset_value,
        post_offset,
        post_offset_imm,
        post_offset_sign,
        post_offset_base,
        post_offset_value,
    ) = matches.groups()
    logger.debug("Parsed following information from given asm instruction:")
    logger.debug("\top: %s", op)
    logger.debug("\tsigned: %s", signed)
    logger.debug("\tsize: %s", size)
    logger.debug("\tsize_rt: %s", size_rt)
    logger.debug("\trt: %s", rt)
    logger.debug("\trn: %s", rn)
    logger.debug("\toffset: %s", offset)
    logger.debug("\tpre_offset: %s", pre_offset)
    logger.debug("\tpre_offset_imm: %s", pre_offset_imm)
    logger.debug("\tpre_offset_sign: %s", pre_offset_sign)
    logger.debug("\tpre_offset_base: %s", pre_offset_base)
    logger.debug("\tpre_offset_value: %s", pre_offset_value)
    logger.debug("\tpost_offset: %s", post_offset)
    logger.debug("\tpost_offset_imm: %s", post_offset_imm)
    logger.debug("\tpost_offset_sign: %s", post_offset_sign)
    logger.debug("\tpost_offset_base: %s", post_offset_base)
    logger.debug("\tpost_offset_value: %s", post_offset_value)

    assert signed is None or op == "ldr", "There's no sign extension for str"
    assert size is None or signed, "Need to define a size for sign extension"

    opc, result_size = {
        "str": ("00", "11" if size_rt == "x" else "10"),
        "ldr": ("01", "11" if size_rt == "x" else "10"),
        "ldrb": ("01", "00"),
        "ldrh": ("01", "01"),
        "ldrsb": ("10" if size_rt == "x" else "11", "00"),
        "ldrsh": ("10" if size_rt == "x" else "11", "01"),
        "ldrsw": ("10", "10"),
    }[f"{op}{signed}{size}"]
    active_imm, prepost = (
        (pre_offset_imm, 1) if pre_offset_imm else (post_offset_imm, 0)
    )

    binary_format = "{size}111000{opc}0{imm}{prepost}1{Rn}{Rt}"

    binary_result = binary_format.format(
        size=result_size,
        opc=opc,
        imm=to_twos_comp(int(active_imm, 0), 9),
        prepost=prepost,
        Rn=f"{int(rn, 0):05b}",
        Rt=f"{int(rt, 0):05b}",
    )
    logger.debug("Binary result: %s", binary_result)

    mc = MachineCode.from_binary(binary_result)
    logger.debug("Hex result: %s", mc.get_pretty_hex())
    return mc
