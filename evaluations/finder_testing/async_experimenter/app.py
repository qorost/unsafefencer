import argparse
import logging
import os
import re
import sqlite3
import sys
import threading
from datetime import datetime
from distutils.version import StrictVersion
from lazyme.string import color_print

import asyncio
from rust.cargo import *
from rust.config import *
from rust.database import *

sys.path.append(os.path.dirname(os.path.realpath(__file__)))

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def cprint(line):
    print('\x1b[6;30;42m' + line + '\x1b[0m')

def redprint(line):
    print('\x1b[6;30;41m' + line + '\x1b[0m')

def find_cargo_projects(directory):
    """
    Find cargo projects in the given directory,
    Return:
        an array of cargo project paths
    """
    if not os.path.exists(directory):
        return []
    directory = os.path.abspath(directory)
    return [os.path.join(directory,i) for i in os.listdir(directory) if os.path.isdir(os.path.join(directory,i)) ]

def scan_tree(directory):
    try:
        for entry in os.scandir(directory):
            if entry.is_dir(follow_symlinks=False):
                yield from scan_tree(entry.path)
            else:
                yield entry.path
    except:
        eprint("directory {} has type {}".format(directory, str(type(directory))))

def find_crates(directory):
    """
    Walk into the directory, and return an array of filepaths
    """
    print("Finding total crates...")
    crates = []
    for entry in scan_tree(directory):
        entry = str(entry)
        if entry.endswith(".crate"):
            crates.append(entry)
    print("Found {} crates in the directory".format(len(crates)))
    for i in crates:
        print("in find_crates {}".format(i))
        break
    return crates


version_regs = r'(?P<name>.*)-(?P<version>\d+\.\d+\.\d+[^.]*)\.(?P<crate>.*)'

def find_latest_crates(directory):
    print("Finding crates...")
    crates = find_crates(directory)
    rx = re.compile(version_regs)
    latest_crates = dict()
    crates_versions = dict()
    latest_versions = dict()

    for crate in crates:
        crate = os.path.abspath(crate)
        crate_base = os.path.basename(crate)
        m = rx.search(crate_base)
        if m:
            verstr = m.group("version")
            name = m.group("name")
        else:
            print("Failed to resolve {}".format(crate_base))
            continue
        try:
            version = StrictVersion(verstr)
        except:
            # Excluding unregular named version
            # print("Exception in StrictVersion for ({}), verstr is ({})".format(crate, verstr))
            continue
        if name in crates_versions:
            if version > crates_versions[name]:
                crates_versions[name] = version
                latest_crates[name] = crate
                latest_versions[name] = verstr
        else:
            crates_versions[name] = version
            latest_crates[name] = crate
            latest_versions[name] = verstr

    print("Filtered {} latest versions from total {} crates".format(len(latest_crates), len(crates)))
    return latest_crates, latest_versions


async def worker_demo(crate):
    pass
    #print(crate)

async def worker_uncompress_crate(crate):
    """
    Uncompress the crate the directory of the crate
    """
    # print("worker_uncompress_crate")
    uncompress_crate(crate)

async def worker_uncompress_crate_locally(crate):
    """
    Uncompress the crate the running directory
    """
    # utils.uncompress_crate(crate,True)
    uncompress_crate(crate,True)

async def worker_simple_cargo_build(crate):
    """
    Input, c is a Crate in the Database or directory, only build, not processing log
    """
    if type(crate) != str:
        srcdir = crate.srcdir
    else:
        srcdir = crate
    print("\nIn worker_simple_cargo_build {}".format(srcdir))
    restore_cargo(srcdir)
    backup_cargo(srcdir)
    insert_depency_to_cargo(srcdir)
    summary = build_cargo(srcdir,enable_analysis=False)
    restore_cargo(srcdir)


async def worker_cargo_build(crate):
    """
    Input, c is a Crate in the Database
    """
    print("\nIn worker_cargo_build {}".format(crate.name))
    srcdir = crate.srcdir
    if not os.path.exits(srcdir):
        print("{} not exists".format(srcdir))
        return
    logfile = os.path.join(os.path.abspath(srcdir), "build.log")
    if process_newnutlint_log(logger_load_log(logfile)) is not None:
        print("The cargo {} has been built before".format(srcdir))
        return
    backup_cargo(srcdir)
    insert_depency_to_cargo(srcdir)
    summary = build_cargo(srcdir)
    restore_cargo(srcdir)
    if type(summary) == tuple:
        save_record(crate, summary)
        print("{} Built Successfully, {}".format(crate.name, summary))
    else:
        save_failure_record(crate)
        print("Failed to build {}".format(crate.name))

async def worker_cargo_clean(crate):
    print("\nIn worker_cargo_clean {}".format(crate.name))
    srcdir = crate.srcdir
    rtn = build_cargo(srcdir, "cargo clean", False)

async def worker_delete_cargo(srcdir):
    """
    remove the source dir
    """
    if not os.path.isabs(srcdir):
        srcdir = os.path.abspath(srcdir)
    try:
        shutil.rmtree(srcdir)
    except Exception as e:
        eprint("Exception happens when deleting {}".format(srcdir))

async def worker_log_analyzer(srcdir):
    logfile = os.path.join(os.path.abspath(srcdir), "build.log")
    if os.path.exists(logfile):
        x = process_newnutlint_log(logger_load_log(logfile))
        print("Result:\t",srcdir, x)
    else:
        print("{}, logfile not exits".format(logfile))

def async_run(works, worker):
    """
    Running worker asynchrously, with data works.
    Input:
        works: the data array
        worker: the function that perform on data, should be declared with `async def`
    """
    if type(works) == dict:
        tmp = works
        works = []
        for item in tmp:
            works.append(tmp[item])
    if type(works) != list:
        print("Input is an Invalid type")
        return

    loop = asyncio.get_event_loop()
    tasks = [asyncio.ensure_future(worker(work)) for work in works]
    loop.run_until_complete(asyncio.wait(tasks))


def normal_run(directory):
    #cur = conn.cursor()
    crates = find_crates(directory)
    for i in crates:
        exp_fun(i)

"""
Functions used to test
"""
def test():
    crates, versions = find_latest_crates("/home/huang/Desktop/Rust/myworkspace/data")
    async_run(crates, worker_demo)

def test_uncompress():
    directory = "./tests/samples"
    crates, versions = find_latest_crates(directory)
    async_run(crates, worker_uncompress_crate_locally)

def test_build():
    #crates = get_crates()
    print("test_build in app.py..")
    crates = get_test_samples()
    async_run(crates, worker_cargo_build)

def test_config():
    print_configfile()
    print(get_build_line())

def build_all_crates():
    crates = get_crates()
    async_run(crates, worker_cargo_build)

def clean_all_built_crates():
    crates = get_cleaning_crates()
    async_run(crates, worker_cargo_clean)

def build_filtered_crates():
    """
    build the
    """
    return




"""
api related to user input
"""

def query_yes_no(question, default="yes"):
    """Ask a yes/no question via input() and return their answer.
    refer from http://stackoverflow.com/questions/3041986/apt-command-line-interface-like-yes-no-input
    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        redprint(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            print("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Experiments Carrier.")
    #FIXME, improve the clarity
    subparsers = parser.add_subparsers(title="subcommands", \
                                        description="valid subcommands", \
                                        help="sub-command help")

    parser_uncompress = subparsers.add_parser('uncompress', help="uncompress crate")
    parser_uncompress.add_argument("srcdirectory", type=str, help="directory that crate files in")
    parser_uncompress.add_argument("dstdirectory", type=str, default=".", help="directory to store uncompressed")

    parser_find = subparsers.add_parser("find",help="find crates as desired")
    parser_find.add_argument("-f", "--filter", type=str, choices=["all","unrun" ,"failed", "success", "targets"], help="list the crates in database Crate table")
    parser_find.add_argument("-i", "--input", type=str, help="find cargo projects in the input directory")
    parser_find.add_argument("-m", action="store_true", help="modify the cargo.toml in the project")
    parser_find.add_argument("-b", action="store_true", help="build the cargo project")
    parser_find.add_argument("-a", action="store_true", help="analyze thd build log")
    parser_find.add_argument("-d", action="store_true", help="rm the crate src directory")
    parser_find.add_argument("-o", "--output", type=str, help="output of the results")

    parser.add_argument("-c", "--configfile", type=str, help="specify config file")
    args = parser.parse_args()

    if args.configfile is not None:
        set_configfile(args.configfile)

    crates = [] # the samples to work on
    if args.filter is not None: # find crates in database, crates are an array of Crate objects
        if args.filter == "all":
            crates = get_crates()
        elif args.filter == "failed":
            crates = get_checked_crates(0)
        elif args.filter == "unrun":
            crates = get_unrun_crates()
        elif args.filter == "targets":
            crates = get_vul_crates()
        cprint("{} \"{}\" crates found in database".format(len(crates), args.filter))
        if args.b:
            async_run(crates, worker_cargo_build)

        #update crates to fit for general operations, that are not required to write database
        crates = [c.srcdir for c in crates]
    elif args.input is not None: # find crates in directory, return an array of directories
        crates = find_cargo_projects(args.input)
        cprint("{} crates found in directory: {}".format(len(crates), args.input))
        if args.b:
            async_run(crates, worker_simple_cargo_build)


    #Below is generic operations on crate src directory
    if args.a:
        # analyze the logfile
        cprint("Analyzing log for {} crates".format(len(crates)))
        async_run(crates, worker_log_analyzer)

    if args.d:
        #print("Deleting {} crates".format(len(crates)))
        is_sure = query_yes_no("Are you sure to delelte {} creates".format(len(crates)), default="no")
        if is_sure:
            is_sure = query_yes_no("Think twice before you delete, this is dangerous, you sure?", default="no")
            if not is_sure:
                cprint("Better Choice, you can do it when you made up your mind!")
            else:
                async_run(crates, worker_delete_cargo)
        else:
            cprint("Give up deleting crates!")


