#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 huang <huang@huang-Precision-WorkStation-T3500>
#
# Distributed under terms of the MIT license.

"""
This module is used to deal with cargos
"""

import subprocess
import os
import shutil
import datetime

if not os.path.abspath('.').endswith('rust'):
    from rust.logger import *
    from rust.database import *
    from rust.config import *
else: #Test the cargo module alone
    # print("Test the cargo module", os.path.abspath('.'))
    from logger import *
    from database import *
    from config import *

import tarfile
import os


dependency_line = get_dependency_line()
command_line = get_build_line()

def update_config():
    global dependency_line
    global command_line
    dependency_line = get_dependency_line()
    command_line = get_build_line()

def uncompress_crate(cratefile, local = False):
    """
    Uncompress,
    return the compressed directory if success
    return None if fails
    """
    try:
        if local == True:
            dstpath = "."
        else:
            dstpath = os.path.abspath(os.path.dirname(cratefile))
        cratedir = os.path.basename(cratefile)[:-6]
        tar = tarfile.open(cratefile)
        tar.extractall(path=dstpath)
        tar.close()
        #print("Crate {} extracted to {}/{}".format(cratefile, dstpath, cratedir))
        return dstpath
    except Exception as e:
        print("Exception Happens on {}: {}".format(cratefile, str(e)))
        return None

def backup_cargo(src_cargo_file):
    if os.path.isdir(src_cargo_file):
        src_cargo_file = os.path.join(src_cargo_file, "Cargo.toml")
    if os.path.exists(src_cargo_file):
        dst_cargo_file = src_cargo_file+".bak"
        if os.path.exists(dst_cargo_file):
            pass
        else:
            shutil.copyfile(src_cargo_file, dst_cargo_file)
    else:
        print("{} doesn't exist".format(src_cargo_file))

def restore_cargo(src_cargo_file):
    if os.path.isdir(src_cargo_file):
        src_cargo_file = os.path.join(src_cargo_file, "Cargo.toml")
    bak_cargo_file = src_cargo_file + ".bak"
    if os.path.exists(bak_cargo_file):
        #print("Restoring cargo file {}".format(bak_cargo_file))
        shutil.copyfile(bak_cargo_file, src_cargo_file)
    else:
        print("Fail to restore {}".format(src_cargo_file))

# This function is depreciated,
# and it is replaced by adding plugin information to command line
def insert_depency_to_cargo(srcdir):
    """
    Add dependecy to the cargo.toml
    """
    #locate the cargo_file
    cargo_file_path = os.path.join(srcdir, "Cargo.toml")
    if os.path.exists(cargo_file_path) :
        try:
            fp = open(cargo_file_path, "r")
            contents = fp.readlines()
            fp.close()
            if dependency_line in contents:
                return # dependency already exisited in contents
            fp = open(cargo_file_path, "w")
            is_inserted = False
            for line in contents:
                if "[dependencies]" in line:
                    line += "\n"
                    line += dependency_line
                    line += "\n"
                    is_inserted = True
                fp.write(line)
            if not is_inserted:
                fp.write("\n[dependencies]\n" + dependency_line )
            fp.close()
        except Exception as e:
            print(str(e))
    else:
        print("cargo toml file not exist")



def build_cargo(srcdir, cmd = command_line, enable_analysis = True ):
    print("Building {}\n{}...".format(srcdir, command_line))
    cur_dir = os.path.abspath(os.getcwd())
    os.chdir(srcdir)
    logfile = os.path.join(srcdir, "build.log")
    p = subprocess.Popen(cmd, \
                        shell = True, \
                        stdout = subprocess.PIPE, \
                        stderr = subprocess.STDOUT)
    contents = p.stdout.readlines()
    decoded = [] # Python3 required decoding bytes
    for line in contents:
        decoded.append(line.decode("utf-8"))
    save_log(decoded, logfile)
    if enable_analysis is not True:
        p.wait()
        os.chdir(cur_dir)
        return None
    try:
        retval = p.wait()
        os.chdir(cur_dir)
        if is_build_success(decoded):
            summary = process_mutlint_logger(decoded, srcdir)
            return summary
        else:
            print("Failed to build crate: {}".format(srcdir))
            return None
    except Exception as e:
        print("Building {} Failed: {}".format(srcdir, str(e)))
        os.chdir(cur_dir)
        return None

"""
api for database
"""
def get_crates(results =Crate.select()):
    return [i for i in results]

def get_test_samples():
    """
    This is used to extract some samples from database
    """
    return get_crates(Crate.select().where(Crate.id < 5))


def get_unrun_crates():
    """
    get the crates that don't run
    """
    return [i for i in Crate.select() if MutLintChecker.select().join(Crate).where(Crate.id == i.id).count() == 0]

def get_joincheck_crates(results):
    return [i.crate for i in results]


def get_checked_crates(is_success = 1): #is_success 0/1
    return get_joincheck_crates(MutLintChecker.select().where(MutLintChecker.pass_build == is_success))


def get_unchecked_crates(): #is_success 0/1
    return get_checked_crates(0)

def get_cleaning_crates():
    """
    Find the crates that are built successfully
    """
    return get_checked_crates(1)

def get_vul_crates():
    """
    Get all the crates that have vulnerable crates
    """
    results = MutLintChecker.select().where(MutLintChecker.imut2mut_functions > 0)
    crates = [item.crate for item in results]
    return crates



def copyanything(src, dst):
    print("src:", src)
    print("dst:", dst)
    try:
        shutil.copytree(src, dst)
    except OSError as exc: # python >2.5
        if exc.errno == errno.ENOTDIR:
            shutil.copy(src, dst)
        else: raise



def move_vul_crates(dst):
    crates = get_vul_crates()
    for i in crates:
        copyanything(i.srcdir, dst)


"""
save row to table
"""
def save_crates_to_db(crates, versions, path="."):
    # FIXME to save to the same directory of crate
    crates_data = []
    for i in crates:
        name = i
        version = versions[i]
        cratefile = crates[i]
        srcdir = os.path.join(os.path.abspath(path)) + '/' + os.path.basename(crates[i])[:-6]
        crates_data.append({'name':name, 'version': version, 'cratefile':cratefile, 'srcdir':srcdir})

    try:
        print("Save Crates to Database")
        if db.get_tables() == []:
            init_db()
        query = Crate.insert_many(crates_data)
        retval = query.execute()
        print("Crates saved to Database {}".format(retval))
    except Exception as e:
        print("Exception in insert_many {}".format(str(e)))


def save_record(c, summary):
    """
    Save the summary to database
    Input:
        c is the Crate
        summary is the
    """
    print("###Save Record for ", c.srcdir)
    record = MutLintChecker(crate = c, \
                            total_functions = summary[0], \
                            mutrtn_functions = summary[1], \
                            imut2mut_functions = summary[2])
    try:
        if MutLintChecker.select().where(MutLintChecker.crate == c).count() == 1:
            print("\t##Update MutLintChecker")
            MutLintChecker.update(total_functions = summary[0], \
                                    mutrtn_functions = summary[1], \
                                    imut2mut_functions = summary[2], \
                                    pass_build = True, \
                                    build_time = datetime.datetime.now).where(MutLintChecker.crate == c)
        else:
            rtn = record.save()
    except Exception as e:
        print("Save Record returned: ", str(e))


def save_failure_record(c):
    print("###Save Failue record for ", c.srcdir)
    record = MutLintChecker(crate = c, \
                            total_functions = 0, \
                            mutrtn_functions = 0, \
                            imut2mut_functions = 0, \
                            pass_build = False)
    try:
        if MutLintChecker.select().where(MutLintChecker.crate == c).count() == 1:
            print("\t##Update MutLintChecker")
            MutLintChecker.update(total_functions = 0, \
                                    mutrtn_functions = 0, \
                                    imut2mut_functions = 0,\
                                    pass_build = False, \
                                    build_time = datetime.datetime.now).where(MutLintChecker.crate == c)
        else:
            print("\t##Save MutLintChecker")
            rtn = record.save() #FIXMe
    except Exception as e:
        print("Exception in Save Failue record returned: ", str(e))

"""
test api
"""
def test():
    cmd = get_build_line()
    src = "../m-0.1.0"
    backup_cargo(src)
    insert_depency_to_cargo(src)
    build_cargo(src, cmd)

def test_insert_cargo(src):
    insert_depency_to_cargo(src)


def test_get():
    #get_unrun_crates()
    get_cleaning_crates()


def test_move():
    crates = get_vul_crates()
    base = "/home/huang/Desktop/Rust/myworkspace/py_experiments/vul_samples"
    for i in crates:
        print(i.srcdir)
        name = os.path.basename(i.srcdir)
        copyanything(i.srcdir, os.path.join(base,name))



if __name__ == "__main__":
    # test_get()
    #x = get_unrun_crates()
    x = get_unchecked_crates()
    #test()
    #x = get_cleaning_crates()
    #x = get_test_samples()
    for i in x:
        print(i.srcdir)
    print("{} crates found!".format(len(x)))


