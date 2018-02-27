//
// simple.rs
// Copyright (C) 2017 huang <huang@huang-Precision-WorkStation-T3500>
// Distributed under terms of the MIT license.
//

#![feature(plugin)]
#![plugin(fencer)]

#![allow(dead_code)]
#![allow(unused_variables)]

//#[macro_use] extern crate unsafe_base;
//use unsafe_base::{check_dropped,check_readable,check_writable};
//add_headers!();


extern crate fencer_support;

#[checkderef]
#[test]
fn test_support () {
    fencer_support::say_hello();
}

#[checkderef]
#[test]
fn test_unsafe_fun () {
    unsafe fn goodbay() {
        let mut y = 10;
        let x = &mut y as *mut i32;

        // read of raw pointer
        let a = *x;

        //write of raw pointer
        *x = 1;

        *x = *x + 10;
    }
}

/*
#[derive(Debug)]
struct A {x:i32,}

#[checkderef]
#[test]
fn test_deref_typs() {
    let a:A = A{x: 12};
    let ptra = &a as *const A;
    //read of raw pointer
    let tmp = unsafe { *ptra};
}
*/

fn main () {
    //#[Readable]
    println!("Hello World, Rust Plugins!");
}
