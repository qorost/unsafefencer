#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 huang <huang@huang-Precision-WorkStation-T3500>
#
# Distributed under terms of the MIT license.

"""
This module is used to load config file
"""

from configparser import ConfigParser, RawConfigParser
import io
import os

# print("in config.py:", os.path.abspath(__file__))
# if not os.path.abspath('.').endswith('rust'):
#     configfile = "rust/experiments/demo.ini"
# else:
#     configfile = "experiments/demo.ini"


configfile = os.path.join(os.path.dirname(os.path.abspath(__file__)), "experiments/demo.ini")

def set_configfile(newcfgfile):
    global configfile #Must add to write the global value
    configfile = os.path.abspath(newcfgfile)

def load_config(configfile = configfile):
    # print(help(ConfigParser))
    cfg = ConfigParser()
    cfg.read(configfile)
    return cfg

def load_cmd():
    """
    """
    cfg = load_config()
    return cfg.get('Build','cmd_line')

def load_cmd_template():
    """
    """
    cfg = load_config()
    return cfg.get('Build','template')

def load_plugin_name():
    cfg = load_config()
    return cfg.get('Basics', 'name')

def load_plugin_path():
    cfg = load_config()
    return cfg.get('Basics', 'path')

def load_plugin_info():
    cfg = load_config()
    return (cfg.get('Basics', 'name'), cfg.get('Basics', 'path'))

def get_dependency_line():
    template = "{} = {{ path = \"{}\"}}"
    info = load_plugin_info()
    print
    return template.format(info[0], info[1])

def get_build_line():
    template = load_cmd_template()
    info = load_plugin_info()
    return template.format(path=info[1], lint=info[0])

# Functions for debugging
def print_configfile():
    print("##configfile: ", configfile)

if __name__ == "__main__":
    print(load_cmd())
    print(load_plugin_name())
    print(load_plugin_path())
    print(get_dependency_line())
    print(get_build_line())