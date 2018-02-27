# unsafefencer

UnsafeFencer is a tool to detect unsafe raw pointer dereferencing in Rust. The raw pointer dereferencing takes superpower and could cause new safety problems, which would break the memory safety guarantee of Rust.


## Overview

UnsafeFencer is made up of two components:  finder and fencer
* The **finder** transverses the Abstract Syntax Tree (AST) to find thief functions matching the pattern. We define thief function to represent functions that could be used to generate illegal multiple mutable refereces.

* The **fencer** applies instrumentation to AST. At every dereferencing site, it inserts codes to perform the validity checking. During execution, the inserted code will execute before dereferencing occurs. 

## Running

The **evaluation** foler present how to test our tool. There are two folders:

* **performance_dynamic** is used to test the **fencer** component.
* **finder_testing** is used to test our **finder** component, it contains a tool named **async\_experimenter** to run all the experiments in parallel.


## Acknowledgements

This project makes use of the following libraries:

Rust Crates on [crates.io](crates.io):
* [toml]()
* [matches]()
* [serde_derive]()
* [serde]()
* [lazy_static]()

Python libraries on pip:
* [peewee]()
* [PyMySQL]()
* [lazyme]()
