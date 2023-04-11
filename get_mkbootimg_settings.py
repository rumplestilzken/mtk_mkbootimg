#!/usr/bin/env python3
import os.path
from argparse import (ArgumentParser, ArgumentTypeError,
                      FileType, RawDescriptionHelpFormatter)
from enum import IntEnum

convert_hex = False
unmk_path = ""


class UnpackMethod(IntEnum):
    notset = 0
    unmkbootimg = 1
    unpackbootimg = 2
    unpack_bootimg = 3


class PackArgument(IntEnum):
    kernel = 1
    ramdisk = 2
    dtb = 3
    base = 4
    cmdline = 5
    kernel_offset = 6
    ramdisk_offset = 7
    second_offset = 8
    pagesize = 9
    dtb_offset = 10
    tags_offset = 11
    header_version = 12
    os_version = 13
    os_patch_level = 14
    second = 15
    hash_type = 16
    name = 17
    extra_cmdline = 18
    recovery_dtbo = 19


class CommandPacket:
    def __init__(self, command, commandlist, method, alerts):
        self.command = command
        self.commandlist = commandlist
        self.method = method
        self.alerts = alerts


def convert_to_decimal(string):
    returnvalue = ""
    global convert_hex
    if convert_hex:
        returnvalue = str(int(string, 16))
    else:
        returnvalue = string
    return returnvalue


pack_cmd_dict = {PackArgument.kernel: "--kernel", PackArgument.dtb: "--dtb", PackArgument.ramdisk: "--ramdisk",
                 PackArgument.base: "--base", PackArgument.name: "--id", PackArgument.cmdline: "--cmdline",
                 PackArgument.dtb_offset: "--dtb_offset", PackArgument.hash_type: "--hashtype",
                 PackArgument.header_version: "--header_version",
                 PackArgument.kernel_offset: "--kernel_offset", PackArgument.os_patch_level: "--os_patch_level",
                 PackArgument.os_version: "--os_version", PackArgument.pagesize: "--pagesize",
                 PackArgument.ramdisk_offset: "--ramdisk_offset", PackArgument.recovery_dtbo: "--recovery_dtbo",
                 PackArgument.second_offset: "--second_offset", PackArgument.tags_offset: "--tags_offset"}


def get_unpackbootimg_commands_from_settings(path):
    commands = {}
    line_size = 0
    line_fragments = ""
    for line in open(path).read().split("\n"):
        if line.startswith("BOARD_KERNEL_CMDLINE"):
            line_fragments = line.split("BOARD_KERNEL_CMDLINE")
            line_size = len(line_fragments)
            commands[PackArgument.cmdline] = pack_cmd_dict.get(
                PackArgument.cmdline) + " \"" + line_fragments[line_size - 1].strip() + "\""
        if line.startswith("BOARD_KERNEL_BASE"):
            line_fragments = line.split(" ")
            line_size = len(line_fragments)
            commands[PackArgument.base] = pack_cmd_dict.get(PackArgument.base) + " " + convert_to_decimal(
                line_fragments[line_size - 1].strip())
        if line.startswith("BOARD_NAME"):
            line_fragments = line.split("BOARD_NAME")
            line_size = len(line_fragments)
            commands[PackArgument.name] = pack_cmd_dict.get(
                PackArgument.name) + " " + line_fragments[line_size - 1].strip()
        if line.startswith("BOARD_PAGE_SIZE"):
            line_fragments = line.split(" ")
            line_size = len(line_fragments)
            commands[PackArgument.pagesize] = pack_cmd_dict.get(
                PackArgument.pagesize) + " " + line_fragments[line_size - 1].strip()
        if line.startswith("BOARD_KERNEL_OFFSET"):
            line_fragments = line.split(" ")
            line_size = len(line_fragments)
            commands[PackArgument.kernel_offset] = pack_cmd_dict.get(
                PackArgument.kernel_offset) + " " + convert_to_decimal(
                line_fragments[line_size - 1].strip())
        if line.startswith("BOARD_RAMDISK_OFFSET"):
            line_fragments = line.split(" ")
            line_size = len(line_fragments)
            commands[PackArgument.ramdisk_offset] = pack_cmd_dict.get(
                PackArgument.ramdisk_offset) + " " + convert_to_decimal(
                line_fragments[line_size - 1].strip())
        if line.startswith("BOARD_SECOND_OFFSET"):
            line_fragments = line.split(" ")
            line_size = len(line_fragments)
            commands[PackArgument.second_offset] = pack_cmd_dict.get(
                PackArgument.second_offset) + " " + convert_to_decimal(
                line_fragments[line_size - 1].strip())
        if line.startswith("BOARD_TAGS_OFFSET"):
            line_fragments = line.split(" ")
            line_size = len(line_fragments)
            commands[PackArgument.tags_offset] = pack_cmd_dict.get(
                PackArgument.tags_offset) + " " + convert_to_decimal(
                line_fragments[line_size - 1].strip())
        if line.startswith("BOARD_OS_VERSION"):
            line_fragments = line.split(" ")
            line_size = len(line_fragments)
            commands[PackArgument.os_version] = pack_cmd_dict.get(
                PackArgument.os_version) + " " + line_fragments[line_size - 1].strip()
        if line.startswith("BOARD_OS_PATCH_LEVEL"):
            line_fragments = line.split(" ")
            line_size = len(line_fragments)
            commands[PackArgument.os_patch_level] = pack_cmd_dict.get(
                PackArgument.os_patch_level) + " " + line_fragments[line_size - 1].strip()
        if line.startswith("BOARD_HEADER_VERSION"):
            line_fragments = line.split(" ")
            line_size = len(line_fragments)
            commands[PackArgument.header_version] = pack_cmd_dict.get(
                PackArgument.header_version) + " " + line_fragments[line_size - 1].strip()
        if line.startswith("BOARD_DTB_OFFSET"):
            line_fragments = line.split(" ")
            line_size = len(line_fragments)
            commands[PackArgument.dtb_offset] = pack_cmd_dict.get(
                PackArgument.dtb_offset) + " " + convert_to_decimal(
                line_fragments[line_size - 1].strip())
    commands[PackArgument.dtb] = pack_cmd_dict.get(PackArgument.dtb) + " <dtb.dtb>"
    commands[PackArgument.kernel] = pack_cmd_dict.get(PackArgument.kernel) + " <kernel>"
    commands[PackArgument.ramdisk] = pack_cmd_dict.get(PackArgument.ramdisk) + " <ramdisk>"

    global unmk_path
    commands = get_unmkbootimg_commands_from_settings_offsets(unmk_path, commands)

    return commands


def get_unpack_bootimg_commands_from_settings(path):
    commands = {}
    line_size = 0
    line_fragments = ""
    for line in open(path).read().split("\n"):
        if line.startswith("kernel load address"):
            line_fragments = line.split(":")
            line_size = len(line_fragments)
            commands[PackArgument.kernel_offset] = pack_cmd_dict.get(
                PackArgument.kernel_offset) + " " + convert_to_decimal(
                line_fragments[line_size - 1].strip())
        if line.startswith("ramdisk load address"):
            line_fragments = line.split(":")
            line_size = len(line_fragments)
            commands[PackArgument.ramdisk_offset] = pack_cmd_dict.get(
                PackArgument.ramdisk_offset) + " " + convert_to_decimal(
                line_fragments[line_size - 1].strip())
        if line.startswith("second bootloader load address"):
            line_fragments = line.split(":")
            line_size = len(line_fragments)
            commands[PackArgument.second_offset] = pack_cmd_dict.get(
                PackArgument.second_offset) + " " + convert_to_decimal(
                line_fragments[line_size - 1].strip())
        if line.startswith("kernel tags load address"):
            line_fragments = line.split(":")
            line_size = len(line_fragments)
            commands[PackArgument.second_offset] = pack_cmd_dict.get(
                PackArgument.tags_offset) + " " + convert_to_decimal(
                line_fragments[line_size - 1].strip())
        if line.startswith("page size"):
            line_fragments = line.split(":")
            line_size = len(line_fragments)
            commands[PackArgument.pagesize] = pack_cmd_dict.get(PackArgument.pagesize) + " " + line_fragments[line_size - 1].strip()
        if line.startswith("os version"):
            line_fragments = line.split(":")
            line_size = len(line_fragments)
            commands[PackArgument.os_version] = pack_cmd_dict.get(
                PackArgument.os_version) + " " + "\"" + line_fragments[line_size - 1].strip() + "\""
        if line.startswith("os patch level"):
            line_fragments = line.split(":")
            line_size = len(line_fragments)
            commands[PackArgument.os_patch_level] = pack_cmd_dict.get(PackArgument.os_patch_level) + " " + \
                "\"" + line_fragments[line_size - 1].strip() + "\""
        if line.startswith("boot image"):
            line_fragments = line.split(":")
            line_size = len(line_fragments)
            commands[PackArgument.header_version] = pack_cmd_dict.get(PackArgument.header_version) + " " + \
                line_fragments[line_size - 1].strip()
        if line.startswith("product"):
            line_fragments = line.split(":")
            line_size = len(line_fragments)
            commands[PackArgument.name] = pack_cmd_dict.get(PackArgument.name) + " " + line_fragments[
                line_size - 1].strip()
        if line.startswith("command"):
            line_fragments = line.split(":")
            line_size = len(line_fragments)
            commands[PackArgument.cmdline] = pack_cmd_dict.get(PackArgument.cmdline) + " " + "\"" + line_fragments[
                line_size - 1].strip() + "\""
        if line.startswith("dtb address"):
            line_fragments = line.split(":")
            line_size = len(line_fragments)
            commands[PackArgument.dtb_offset] = pack_cmd_dict.get(PackArgument.dtb_offset) + " " + convert_to_decimal(
                line_fragments[line_size - 1].strip())

        commands[PackArgument.dtb] = pack_cmd_dict.get(PackArgument.dtb) + " <dtb.dtb>"
        commands[PackArgument.kernel] = pack_cmd_dict.get(PackArgument.kernel) + " <kernel>"
        commands[PackArgument.ramdisk] = pack_cmd_dict.get(PackArgument.ramdisk) + " <ramdisk>"

        global unmk_path
        commands = get_unmkbootimg_commands_from_settings_offsets(unmk_path, commands)
    return commands


def get_unmkbootimg_commands_from_settings_offsets(path, commands):
    line_size = 0
    line_fragments = ""
    for line in open(path).read().split("\n"):
        if line.startswith("OFF_KERNEL_ADDR"):
            line_fragments = line.split(" ")
            line_size = len(line_fragments)
            commands[PackArgument.kernel_offset] = pack_cmd_dict.get(PackArgument.kernel_offset) + " " + \
                convert_to_decimal(line_fragments[line_size - 1])
        if line.startswith("OFF_RAMDISK_ADDR"):
            line_fragments = line.split(" ")
            line_size = len(line_fragments)
            commands[PackArgument.ramdisk_offset] = pack_cmd_dict.get(PackArgument.ramdisk_offset) + " " + \
                convert_to_decimal(line_fragments[line_size - 1])
        if line.startswith("OFF_SECOND_ADDR"):
            line_fragments = line.split(" ")
            line_size = len(line_fragments)
            commands[PackArgument.second_offset] = pack_cmd_dict.get(PackArgument.second_offset) + " " + \
                convert_to_decimal(line_fragments[line_size - 1])

    return commands


def get_unmkbootimg_commands_from_settings(path):
    commands = {}
    line_size = 0
    line_fragments = ""
    for line in open(path).read().split("\n"):
        if line.startswith("Kernel address"):
            line_fragments = line.split(" ")
            line_size = len(line_fragments)
            commands[PackArgument.kernel_offset] = pack_cmd_dict.get(PackArgument.kernel_offset) + " " + \
                convert_to_decimal(line_fragments[line_size - 1])
        if line.startswith("Ramdisk address"):
            line_fragments = line.split(" ")
            line_size = len(line_fragments)
            commands[PackArgument.ramdisk_offset] = pack_cmd_dict.get(PackArgument.ramdisk_offset) + " " + \
                convert_to_decimal(line_fragments[line_size - 1])
        if line.startswith("Secondary address"):
            line_fragments = line.split(" ")
            line_size = len(line_fragments)
            commands[PackArgument.second_offset] = pack_cmd_dict.get(PackArgument.second_offset) + " " + \
                convert_to_decimal(line_fragments[line_size - 1])
        if line.startswith("Kernel tags address"):
            line_fragments = line.split(" ")
            line_size = len(line_fragments)
            commands[PackArgument.tags_offset] = pack_cmd_dict.get(PackArgument.tags_offset) + " " + \
                convert_to_decimal(line_fragments[line_size - 1])
        if line.startswith("Flash page size"):
            line_fragments = line.split(" ")
            line_size = len(line_fragments)
            commands[PackArgument.pagesize] = pack_cmd_dict.get(PackArgument.pagesize) + " " + \
                line_fragments[line_size - 1]
        if line.startswith("Board name"):
            line_fragments = line.split("\"")
            line_size = len(line_fragments)
            commands[PackArgument.name] = pack_cmd_dict.get(PackArgument.name) + " " + line_fragments[line_size - 2]
        if line.startswith("Command line"):
            line_fragments = line.split("\"")
            line_size = len(line_fragments)
            commands[PackArgument.cmdline] = pack_cmd_dict.get(PackArgument.cmdline) + " \"" + \
                line_fragments[line_size - 2] + "\""
        commands[PackArgument.dtb] = pack_cmd_dict.get(PackArgument.dtb) + " <dtb.dtb>"
        commands[PackArgument.kernel] = pack_cmd_dict.get(PackArgument.kernel) + " <kernel>"
        commands[PackArgument.ramdisk] = pack_cmd_dict.get(PackArgument.ramdisk) + " <ramdisk>"
        #TODO Get base from settings file
        commands = get_unmkbootimg_commands_from_settings_offsets(path, commands)
    return commands


def get_unpack_bootimg_commands_from_path(path):
    commands = {}
    commands[PackArgument.kernel] = pack_cmd_dict.get(PackArgument.kernel) + " kernel"
    commands[PackArgument.ramdisk] = pack_cmd_dict.get(PackArgument.ramdisk) + " ramdisk"
    commands[PackArgument.dtb] = pack_cmd_dict.get(PackArgument.dtb) + " dtb"
    commands[PackArgument.recovery_dtbo] = pack_cmd_dict.get(PackArgument.recovery_dtbo) + " recovery_dtbo"
    return commands


def get_unpackbootimg_commands_from_path(path):
    commands = {}

    for file in os.listdir(path):
        if file.endswith("kernel"):
            commands[PackArgument.kernel] = pack_cmd_dict.get(PackArgument.kernel) + " " + file
        if file.endswith("dtb"):
            commands[PackArgument.dtb] = pack_cmd_dict.get(PackArgument.dtb) + " " + file
        if file.endswith("ramdisk"):
            commands[PackArgument.ramdisk] = pack_cmd_dict.get(PackArgument.ramdisk) + " " + file
        if file.endswith("recovery_dtbo"):
            commands[PackArgument.recovery_dtbo] = pack_cmd_dict.get(PackArgument.recovery_dtbo) + " " + file
        if file.endswith("base"):
            commands[PackArgument.base] = pack_cmd_dict.get(PackArgument.base) + " " + convert_to_decimal(
                open(path + file).read().strip())
        if file.endswith("board"):
            commands[PackArgument.name] = pack_cmd_dict.get(PackArgument.name) + " " + open(path + file).read().strip()
        if file.endswith("cmdline"):
            commands[PackArgument.cmdline] = pack_cmd_dict.get(PackArgument.cmdline) + " \"" + open(
                path + file).read().strip() + "\""
        if file.endswith("dtb_offset"):
            commands[PackArgument.dtb_offset] = pack_cmd_dict.get(PackArgument.dtb_offset) + " " + \
                                                convert_to_decimal(open(path + file).read().strip())
        if file.endswith("hashtype"):
            commands[PackArgument.hash_type] = pack_cmd_dict.get(PackArgument.hash_type) + " " + \
                                               open(path + file).read().strip()
        if file.endswith("header_version"):
            commands[PackArgument.header_version] = pack_cmd_dict.get(PackArgument.header_version) + " " + open(
                path + file).read().strip()
        if file.endswith("kernel_offset"):
            commands[PackArgument.kernel_offset] = pack_cmd_dict.get(
                PackArgument.kernel_offset) + " " + convert_to_decimal(open(path + file).read().strip())
        if file.endswith("os_patch_level"):
            commands[PackArgument.os_patch_level] = pack_cmd_dict.get(PackArgument.os_patch_level) + " " + open(
                path + file).read().strip()
        if file.endswith("os_version"):
            commands[PackArgument.os_version] = pack_cmd_dict.get(PackArgument.os_version) + " " + open(
                path + file).read().strip()
        if file.endswith("pagesize"):
            commands[PackArgument.pagesize] = pack_cmd_dict.get(PackArgument.pagesize) + " " + open(
                path + file).read().strip()
        if file.endswith("ramdisk_offset"):
            commands[PackArgument.ramdisk_offset] = pack_cmd_dict.get(
                PackArgument.ramdisk_offset) + " " + convert_to_decimal(open(path + file).read().strip())
        if file.endswith("second_offset"):
            commands[PackArgument.second_offset] = pack_cmd_dict.get(
                PackArgument.second_offset) + " " + convert_to_decimal(open(path + file).read().strip())
        if file.endswith("tags_offset"):
            commands[PackArgument.tags_offset] = pack_cmd_dict.get(PackArgument.tags_offset) + " " + convert_to_decimal(
                open(path + file).read().strip())
    return commands


def get_build_commands(path, method):
    commands = {}
    if os.path.isfile(path):
        match method:
            case UnpackMethod.unpack_bootimg:
                commands = get_unpack_bootimg_commands_from_settings(path)
            case UnpackMethod.unpackbootimg:
                commands = get_unpackbootimg_commands_from_settings(path)
            case UnpackMethod.unmkbootimg:
                commands = get_unmkbootimg_commands_from_settings(path)
            case _:
                print("Commands could not be parsed.")
                quit()
    if os.path.isdir(path):
        match method:
            case UnpackMethod.unpack_bootimg:
                commands = get_unpack_bootimg_commands_from_path(path)
            case UnpackMethod.unpackbootimg:
                commands = get_unpackbootimg_commands_from_path(path)
            case _:
                print("Commands could not be parsed.")
                quit()

    global unmk_path
    if unmk_path:
        commands = get_unmkbootimg_commands_from_settings_offsets(unmk_path, commands)

    return commands


def get_unpack_method_from_settings(path):
    method = UnpackMethod.notset
    with open(path, "r") as file:
        contents = file.read()
        if contents.startswith("unmkbootimg"):
            method = UnpackMethod.unmkbootimg

        if contents.startswith("boot magic: ANDROID!"):
            method = UnpackMethod.unpack_bootimg

        if contents.startswith("ANDROID! magic found at:"):
            method = UnpackMethod.unpackbootimg

    return method


def get_unpack_method(path):
    file_count = 0;
    method = UnpackMethod.notset

    if not path.endswith("settings"):
        for file in os.listdir(path):
            file_count += 1
            if file == "kernel":
                method = UnpackMethod.unpack_bootimg
                break
            if file == "initramfs.cpio.gz":
                method = UnpackMethod.unmkbootimg
                break
            if file_count > 6:
                method = UnpackMethod.unpackbootimg
                break
    if path.endswith("settings"):
        method = get_unpack_method_from_settings(path)

    return method


def generate_alerts(command):
    alerts = "\n"
    if "dtb.dtb" in command:
        alerts += "dtb need to be manually configured!!!\n"
    if "<kernel>" in command:
        alerts += "kernel need to be manually configured!!!\n"
    if "<ramdisk>" in command:
        alerts += "ramdisk need to be manually configured!!!\n"
    return alerts


def parsePath(args):
    method = get_unpack_method(args.path)
    commands = get_build_commands(args.path, method)

    global convert_hex
    if convert_hex:
        commandlist = "mkbootimg.py "
    else:
        commandlist = "mkbootimg "

    for command in sorted(list(commands)):
        commandlist += commands[command.value] + " "
    commandlist += " -o new.img"

    alerts = generate_alerts(commandlist)
    commandpacket = CommandPacket(commands, commandlist, method, alerts)
    return commandpacket;


def usage():
    print("""get_mkbootimg_settings.py
    -path: path to folder containing unpack or settings file
    -d: convert offsets to decimal
    -unmk: update offsets from unmkbootimg settings file
    Settings File can be used. Copy the output from your unpacking operation to a file called 'settings'""")


def parse_arguments():
    parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter, epilog=usage())
    parser.add_argument("-path")
    parser.add_argument("-d", required=False, default="", action="store_true")
    parser.add_argument("-unmk", required=False, default="", )
    args = parser.parse_args()
    return args


def main():
    args = parse_arguments()

    if args.path is None:
        quit()

    if args.d:
        global convert_hex
        convert_hex = True

    if args.unmk:
        global unmk_path
        unmk_path = args.unmk

    if not args.path.startswith("/"):
        args.path = "./" + args.path

    # if os.path.isfile(args.path):
    #     if args.path != "settings" and args.path.endswith("settings"):
    #         print("path must be settings file or path to unpack directory")
    #         quit()

    commandpacket = parsePath(args)
    print("You used " + commandpacket.method.name + " to unpack your image.")
    print("Your pack command is:\n" + commandpacket.commandlist)
    print(commandpacket.alerts)


if __name__ == '__main__':
    main()
