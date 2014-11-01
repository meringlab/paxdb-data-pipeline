import os


def keep_only_numbers_filter(elem):
    if not isinstance(elem, str):
        raise ValueError('accepting strings only! ' + type(elem))
    return elem.isdigit()


def get_filename_no_extension(filename):
    base = os.path.basename(filename)
    return os.path.splitext(base)[0]