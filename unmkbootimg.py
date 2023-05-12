#!/usr/bin/env python3

import os
from argparse import ArgumentParser, RawDescriptionHelpFormatter
import ctypes


def usage():
    print("""unmkbootimg.py
        -i: boot image
        -o: output directory""")


def parse_arguments():
    parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter, epilog=usage())
    parser.add_argument("-i", required=True)
    parser.add_argument("-o", required=True)
    args = parser.parse_args()
    return args


def main():
    args = parse_arguments();
    print("unmkbootimg")

    if not os.path.isfile(args.i):
        print(args.i + " is not a file.")

    header = "ANDROID!"
    with open(args.i, 'rb') as file:
        header = file.read(0x260)

    # base = ctypes.c_byte(0)
    # run = True
    # countdown = 8
    #
    android_header = b"ANDROID!"
    # header2 = (ctypes.c_char_p * len(android_header))()
    # header2[:] = android_header
    # tmp_header = header.encode('utf-8', 'strict')
    # while run:
    #     if countdown == 0:
    #         break
    #     countdown = countdown - 1
    #     run = header == tmp_header
    #     neg_two = ctypes.c_uint(-2)
    #     one = ctypes.c_uint(1)
    #     header = header + ctypes.cast(base,ctypes.c_uint) * neg_two + one
    #     tmp_header = int(tmp_header) + base * -2 + 1

    print(android_header + 8)


if __name__ == '__main__':
    main()
