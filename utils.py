import os
import errno


def check_folder(folder):
    try:
        if not(os.path.isdir(folder)):
            os.makedirs(os.path.join(folder))
    except OSError as e:
        if e.errno != errno.EEXIST:
            print(folder + ' is not created.')
            raise
        return False
    return True


def readlines(filename):
    """Read all the lines in a text file and return as a list
    """
    with open(filename, 'r') as f:
        lines = f.read().splitlines()
    return lines


def read_folder_list(path):
    folder_list = os.listdir(path)
    return folder_list


def check_exist(path):
    return os.path.exists(path)


def make_folder(path):
    return os.makedirs(path)


def check_folder(path):
    if not check_exist(path):
        make_folder(path)
    return True


def remove_xa0(list):
    temp_list = []
    for i in list:
        temp = i.replace(u'\xa0', u' ')
        temp_list.append(temp)
    return temp_list


def remove_slash_nt(str):
    temp_str = str.replace("\n", "")
    str = temp_str.replace("\t", "")
    str = str.split("(")[0]
    return str