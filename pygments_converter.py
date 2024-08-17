import re


def format_pygments_line(line):
    ansi_escape1 = re.compile(r"(\x1b\[[0-9]([0-9])m)")
    ansi_escape2 = re.compile(r"(\x1b\[[0-9]{2};[0-9]{2};[0-9]([0-9])m)")

    line_copy = line

    # line_copy = line_copy.replace('\x1b[90m', '\x1b[0m')

    for match in ansi_escape1.finditer(line_copy):
        groups = match.groups()
        if groups[1] is not None:
            line_copy = line_copy.replace(groups[0], f"\x1b[9{groups[1]}m")

    for match in ansi_escape2.finditer(line_copy):
        groups = match.groups()
        if groups[1] is not None:
            line_copy = line_copy.replace(groups[0], f"\x1b[0m")

    return line_copy


# test = "\x1b[01m# Previewer\x1b[39;49;00m"
# test2 = '\x1b[94m-\x1b[39;49;00m\x1b[90m \x1b[39;49;00mPreview non-binary files\x1b[90m\x1b[39;49;00m'
# result2 = format_pygments_line(test2)
# print(result2)
