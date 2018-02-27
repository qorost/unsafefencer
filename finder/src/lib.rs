#![crate_type = "dylib"]


#![feature(plugin_registrar)]
#![feature(box_syntax, rustc_private)]
#![feature(i128_type)]
#![feature(conservative_impl_trait)]
#![feature(macro_vis_matcher)]

#![allow(unused_variables)]
#![allow(dead_code)]
#![allow(unused_imports)]
extern crate syntax;
//extern crate utils;

#[macro_use]
extern crate rustc;
extern crate rustc_plugin;
extern crate rustc_errors;
extern crate toml;
extern crate rustc_const_eval;
extern crate rustc_const_math;

#[macro_use]
extern crate matches as matches_macro;

#[macro_use]
extern crate serde_derive;
extern crate serde;

#[macro_use]
extern crate lazy_static;



use rustc::lint::{EarlyContext, LintContext, LintPass, EarlyLintPass, EarlyLintPassObject, LintArray};
use rustc_plugin::Registry;
use std::env;

use syntax::errors::DiagnosticBuilder;
use rustc::hir::intravisit;
use rustc::hir;
use rustc::ty;
use rustc::lint::*;
use std::collections::HashSet;
use syntax::abi::Abi;
use syntax::codemap::Span;
use syntax::visit as ast_visit;
use syntax::ast;
use syntax::ast::*;
//use syntax::ast::Unsafety;

use std::fmt;


pub struct DiagnosticWrapper<'a>(pub DiagnosticBuilder<'a>);

impl<'a> Drop for DiagnosticWrapper<'a> {
    fn drop(&mut self) {
        self.0.emit();
    }
}

impl<'a> DiagnosticWrapper<'a> {
    fn docs_link(&mut self, lint: &'static Lint) {
        if env::var("CLIPPY_DISABLE_DOCS_LINKS").is_err() {
            self.0.help(&format!(
                "for further information visit https://rust-lang-nursery.github.io/rust-clippy/v{}/index.html#{}",
                env!("CARGO_PKG_VERSION"),
                lint.name_lower()
            ));
        }
    }
}

pub fn span_lint<'a, T: LintContext<'a>>(cx: &T, lint: &'static Lint, sp: Span, msg: &str) {
    DiagnosticWrapper(cx.struct_span_lint(lint, sp, msg)).docs_link(lint);
}



mod reexport {
    pub use syntax::ast::{Name, NodeId};
}

declare_lint!(DECL_MUT, Warn, "Warn about mutting declarations");


struct Pass{
    pass_count: u32,//generic, track the function number with certain type
    func_count: u32,//functions #
    imu_mut_func_count: u32,//input imutabel, output mutable #
    pub_imu_mut_count: u32,
    pub running_item: Option<ast::Item>,
    
}

// this is used when an 
trait Counter {
    fn increment(&mut self);
    fn reset(&mut self);
}

trait Summerizer {
    fn summary(&self);
}

impl Pass {
    fn new() -> Self {
        Pass { 
            pass_count: 0,
            func_count: 0, 
            imu_mut_func_count: 0, 
            pub_imu_mut_count: 0, 
            running_item: None, 
        }
    }

    fn increment_func(&mut self){
        self.func_count += 1;
    }

    fn increment_misc(&mut self) {
        self.imu_mut_func_count += 1;
    }

    fn increment_pub_misc(&mut self) {
        self.pub_imu_mut_count += 1;
    }

}

impl Counter for Pass {
    fn increment(&mut self) {
        self.pass_count += 1;
    }

    fn reset(&mut self) {
        self.pass_count = 0;
    }
}

impl Drop for Pass {
    fn drop(&mut self) {
        println!("`mylint` finished,
                 {} functions in total,
                 {} have mut return refererance, 
                 {} are without `T` or `&mut T`,
                 after `mylint` pass.", 
                 self.func_count, 
                 self.pass_count,
                 self.imu_mut_func_count);
    }
}


impl LintPass for Pass {
    fn get_lints(&self) -> LintArray {
        lint_array!(DECL_MUT)
    }
}

fn is_arg_mutable(arg: &ast::Arg) -> bool {
    is_arg_ty_mutable(&arg.ty)
}

fn is_arg_ty_mutable(ty: &ast::Ty) -> bool{
    match ty.node {
        TyKind::Ptr(ref ptr) | TyKind::Rptr(_, ref ptr)
            => {
            if ptr.mutbl == Mutability::Mutable {
                return true;
            }
        },
        _ => {},
    }
    false
}

/// if the input is a `&mut T`
fn is_ty_mut_reference(ty: &ast::Ty) -> bool {
    match ty.node {
        TyKind::Rptr(_, ref mutty) => {
            // A reference (`&'a T` or `&'a mut T`)
            // Rptr(Option<Lifetime>, MutTy),
            mutty.mutbl == Mutability::Mutable
        },
        _ => false,
    }
}

/// if the input is a `T`
fn is_ty_variable(ty: &ast::Ty) -> bool {
    match ty.node {
        TyKind::Rptr(..) | TyKind::Ptr(..) => {
            false
        },
        _ => true,
    }

}

/// are not declared `unsafe`, and
fn is_func_unsafe(fnkind: ast_visit::FnKind) -> bool {
    match fnkind {
        //fixme FkItemFn
        //ast_visit::FnKind::ItemFn(ident, gen, unsafety, ..) => {
        ast_visit::FnKind::ItemFn(ident, unsafety, x3, x4, x5,x6) => {
            unsafety == Unsafety::Unsafe
        },
        ast_visit::FnKind::Method(ident, methodsig, ..) => {
            methodsig.unsafety == Unsafety::Unsafe
        },
        _ => false,
    }
}


/// have `&mut T` in the outpu
fn have_mut_t_in_return(decl: &ast::FnDecl) -> bool {
    match decl.output {
        ast::FunctionRetTy::Ty(ref ty) => {
            is_ty_mut_reference(ty)
        },
        _ => false,
    }
}



/// have no `T` or `&mut T` in the parameters, and
fn have_no_mut_ref_in_input(decl: &ast::FnDecl) -> bool {
    for input in &decl.inputs {
        if is_ty_mut_reference(&input.ty) {
            return false
        }
        if is_ty_variable(&input.ty) {
            return false
        }

    }
    true
}

///
fn display_fnkind_info(fnkind: ast_visit::FnKind) {
    match fnkind {
        ast_visit::FnKind::ItemFn(ident, ..) => {
            println!("FnKind::ItenFn {}", ident.name);
        },
        ast_visit::FnKind::Method(ident, ..) => {
            println!("FnKind::Method {}", ident.name);
        },
        _ => {
            println!("FnKind::Closure");
        },
    }
}

impl EarlyLintPass for Pass {
    fn check_item(&mut self, cx: &EarlyContext, it: &ast::Item) {
        self.running_item = Some(it.clone());
    }

    fn check_fn(
        &mut self, 
        cx: &EarlyContext, 
        fnkind: ast_visit::FnKind, 
        decl: &ast::FnDecl, 
        span: Span, 
        node_id: ast::NodeId) {
        self.increment_func();

        self.func_count += 1;
        //display_fnkind_info(fnkind);
        //1. check the function input, detect if
        if !is_func_unsafe(fnkind) {
            //println!("\tnot unsafe function");
            if have_mut_t_in_return(decl) {
                //println!("\tmut reference as return");
                self.pass_count += 1;
                if have_no_mut_ref_in_input(decl) {
                    span_lint(cx,
                              DECL_MUT,
                              span,
                              "This func has return reference, but the inputs are immutable");
                    self.imu_mut_func_count += 1;
                    let tmp = self.running_item.as_ref();
                    //println!("The running item {:?}", self.running_item.unwrap());
                    println!("The running item {:?}, it's visibility is {:?}",tmp, tmp.unwrap().vis);
                }
            }
        }
    }
}


#[plugin_registrar]
pub fn plugin_registrar(reg: &mut Registry) {
    reg.register_early_lint_pass(box Pass::new() as EarlyLintPassObject);
    //reg.register_late_lint_pass(box Pass as LateLintPassObject);
}
#[test]
fn it_works() {
}
