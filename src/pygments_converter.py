import re

from pygments.token import Token, Whitespace, Comment, Keyword, Operator, Name, String, Number, Generic, Error

TERMINAL_CUSTOM_COLORS = {
    Token:              ('',            ''),

    Whitespace:         ('gray',   'brightblack'),
    Comment:            ('gray',   'brightblack'),
    Comment.Preproc:    ('cyan',        'brightcyan'),
    Keyword:            ('blue',    'brightblue'),
    Keyword.Type:       ('cyan',        'brightcyan'),
    Operator.Word:      ('magenta',      'brightmagenta'),
    Name.Builtin:       ('cyan',        'brightcyan'),
    Name.Function:      ('green',   'yellow'),
    Name.Namespace:     ('_cyan_',      '_brightcyan_'),
    Name.Class:         ('_green_', '_yellow_'),
    Name.Exception:     ('cyan',        'brightcyan'),
    Name.Decorator:     ('brightblack',    'gray'),
    Name.Variable:      ('red',     'brightred'),
    Name.Constant:      ('red',     'brightred'),
    Name.Attribute:     ('cyan',        'brightcyan'),
    Name.Tag:           ('brightblue',        'brightblue'),
    String:             ('yellow',       'brightgreen'),
    Number:             ('blue',    'brightblue'),

    Generic.Deleted:    ('brightred',        'brightred'),
    Generic.Inserted:   ('green',  'yellow'),
    Generic.Heading:    ('**',         '**'),
    Generic.Subheading: ('*magenta*',   '*brightmagenta*'),
    Generic.Prompt:     ('**',         '**'),
    Generic.Error:      ('brightred',        'brightred'),

    Error:              ('_brightred_',      '_brightred_'),
}

def format_pygments_line(line: list):
    ansi_escape1 = re.compile(r"(\x1b\[[0-9]([0-9])m)")
    ansi_escape2 = re.compile(r"(\x1b\[[0-9]{2};[0-9]{2};[0-9]([0-9])m)")

    line_copy = line[1]

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
