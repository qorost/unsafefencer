#!/usr/bin/env python

import configparser
import io

# Load the configuration file
with open("demo.ini") as f:
    sample_config = f.read()
config = configparser.RawConfigParser(allow_no_value=True)
config.readfp(io.BytesIO(sample_config))

# List all contents
print("List all contents")
for section in config.sections():
    print("Section: %s" % section)
    for options in config.options(section):
        print("x %s:::%s:::%s" % (options,
                                  config.get(section, options),
                                  str(type(options))))

# Print some contents
# print("\nPrint some contents")
# print(config.get('other', 'use_anonymous'))  # Just get the value
# print(config.getboolean('other', 'use_anonymous'))  # You know the datatype?
