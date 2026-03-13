# arm64decoder

CLI tool to help decode and encode the subset of arm64 machine code instructions used in CSC236 at NC State.

It implements the translation of only the instructions shown in the [course materials](https://caio.link/arm64-tables).

## Usage example

### Encoding an instruction
```
$ python3 arm64decoder.py -a encode sdiv x1, x20, x3

Input asm: 'sdiv x1, x20, x3' --(encoded)-> 9A C3 0E 81
```

### Decoding machine code
```
$ python3 arm64decoder.py -a decode 9A C3 0E 81

Input bytes: 9A C3 0E 81
        Table 2 > Data Processing -- Register
        Table 3.3 > Data-processing (2 source)
        Section 4.07 > sdiv x1, x20, x3
```

### Seeing more information with `-v` flag

```
$ python3 arm64decoder.py -a decode 9A C3 0E 81 -v

Decoding '9A C3 0E 81'
Expand hex digits: 9    A    C    3    0    E    8    1
Expand to binary: 1001 1010 1100 0011 0000 1110 1000 0001
Bit count (%10):  1098 7654 3210 9876 5432 1098 7654 3210
Analyzing table in Section 2;
        op0 (bit 31) = 1
        op1 (bits 28~25) = 1101
Matched 'Data Processing -- Register' instruction type
Analyzing table in Section 3.3;
        op0 (bit 30): 0
        op1 (bit 28): 1
        op2 (bits 24 ~ 21): 0110
        op3 (bits 15 ~ 10): 000011
Matched 'Data-processing (2 source)' instruction family
Filling in placeholder bits from Section 4.07;
Action: Rd = Rn / Rm
        Rd (bits 4~0) = 00001 (1) 
        Rn (bits 9~5) = 10100 (20)
        S/U (bit 10) = 1 (s)
        Rm (bits 20~16) = 00011 (3)
        sf (bit 31) = 1 (using x registers)
Input bytes: 9A C3 0E 81
        Table 2 > Data Processing -- Register
        Table 3.3 > Data-processing (2 source)
        Section 4.07 > sdiv x1, x20, x3
```
