# unsafefencer

A tool to detect usnafe raw pointer dereferencing in Rust


## Overview

UnsafeFencer is made up of two components:  finder and fencer
* The finder transverses the Abstract Syntax Tree (AST) to find thief functions matching the pattern.

* The fencer applies instrumentation to AST. At every dereferencing site, it inserts codes to perform the validity checking. During execution, the inserted code will execute before dereferencing occurs. It will throw errors if unsafe behavior is detected. UnsafeFencer is flexible to deploy as compile plugin which can be turned off to the programmers' needs.


## Usage
