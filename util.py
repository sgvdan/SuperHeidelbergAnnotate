import os
import math
import re


def flatten_nan(nested_list):
    return [item for sublist in nested_list for item in sublist if not math.isnan(sublist[1])]


def glob_re(pattern, strings):
    return filter(re.compile(pattern).match, strings)


def find_file(name, path):
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)


def dir_path(string):
    if os.path.isdir(string):
        return string
    else:
        raise NotADirectoryError(string)


def sorted_nicely(l):
    """ Sort the given iterable in the way that humans expect."""
    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted([str(e) for e in l], key=alphanum_key)


def listdir_fullpath(d):
    return [os.path.join(d, f) for f in sorted_nicely(os.listdir(d))]
