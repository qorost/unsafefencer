#![crate_type = "dylib"]
#![feature(plugin_registrar, quote, rustc_private)]
#![allow(dead_code)]
#![allow(unused_imports)]

extern crate syntax;
extern crate rustc;
extern crate rustc_plugin;
extern crate syntax_pos;

//use syntax::ast::{self, StructField, Unsafety, Ident};
use syntax::ast::*;
use syntax::ast;
use syntax_pos::Span;
use syntax::codemap::{BytePos, Spanned};
use syntax::codemap::DUMMY_SP;
use syntax::ext::base::*;
use syntax::ext::quote::rt::ToTokens;
use syntax::parse::{self, token};
use syntax::ptr::P;
use syntax::symbol::Symbol;
use syntax::tokenstream::TokenTree;
use rustc_plugin::Registry;


//for fold
use std::fmt::{self, Display, Formatter};
use syntax::fold::{self, Folder};
use syntax::ext::build::AstBuilder;
/*use syntax::ast::{BinOpKind, Block, Expr, ExprKind, Item, ItemKind, Lit, Mod, 
                  LitKind, Mac, MetaItem, MetaItemKind, NestedMetaItemKind,
                  Path, PathSegment, Stmt, StmtKind, UnOp,FnDecl};
*/
//use syntax::ast::*;
use syntax::util::small_vector::SmallVector;
use syntax::print::pprust;
use std::collections::HashSet;




/// The trait is used to get/set information for 
trait Refinfo {
    // used to mark/set DEREF expr instrument mark, 
    // default false => only check readability
    fn isleft(&self) -> bool; 
    fn setleft(&mut self, value: bool);

} 

impl<'a, 'cx> Refinfo for Refchecker<'a, 'cx> {
    fn isleft(&self) -> bool {
        self.left
    }

    fn setleft(&mut self, value: bool) {
        self.left = value;
    }

}

struct Refchecker<'a, 'cx: 'a> {
    cx: &'a mut ExtCtxt<'cx>,
    left: bool, //tell if the expr is in the left of the statement
}

impl<'a, 'cx> Drop for Refchecker<'a, 'cx> {
    fn drop(&mut self) {

    }
}

impl<'a,'cx> Folder for Refchecker<'a, 'cx> {
    fn fold_expr(&mut self, e: P<Expr>) -> P<Expr> {
        #[cfg(feature = "debugmyplugin")]
        println!("in Expr, node is {:?}", e); 
        match e.clone().unwrap() {
            Expr {node: ExprKind::Unary(UnOp::Deref,arg),span, ..} => {
                let tmp = tag_method(self, vec![arg], span, Span { hi:span.lo + BytePos(1), ..span});
                //let tmp = e.clone();
                //println!("tmp = {:?}", tmp);
                tmp
            }
            _ => e.map(|e| my_noop_fold_expr(e, self)),
        }
    }

    fn fold_mac(&mut self, _mac: Mac) -> Mac {
        fold::noop_fold_mac(_mac, self)
    }

    fn fold_stmt(&mut self, s: Stmt) -> SmallVector<Stmt> {
        fold::noop_fold_stmt(s,self)
    }

    ///modify this to instrument code
    fn fold_item(&mut self, i: P<Item>) -> SmallVector<P<Item>> {
        #[cfg(feature = "debugmyplugin")]
        println!("\nIn function fold_item, {:?}", i.ident);
        my_noop_fold_item(i,self)
    }

    fn fold_item_simple(&mut self, i: Item) -> Item {
        my_noop_fold_item_simple(i,self)
    }

    fn fold_item_kind(&mut self, i: ItemKind) -> ItemKind {
        my_noop_fold_item_kind(i,self)
    }

    /// 
    fn fold_block(&mut self, b: P<Block>) -> P<Block> {
        //match 
        fold::noop_fold_block(b,self)
    }


    fn fold_fn_decl(&mut self, d: P<FnDecl>) -> P<FnDecl> {
        fold::noop_fold_fn_decl(d,self)
    }

    fn fold_mod(&mut self, m: Mod) -> Mod {
        #[cfg(feature = "debugmyplugin")]
        println!("In function fold_mod");
        fold::noop_fold_mod(m, self)
    }

    fn fold_foreign_item(&mut self, ni: ForeignItem) -> ForeignItem {
        #[cfg(feature = "debugmyplugin")]
        println!("This is in fold_foreign_item");
        fold::noop_fold_foreign_item(ni, self)
    }
}


fn my_noop_fold_item<T: Folder> (i: P<Item>, folder: &mut T) -> SmallVector<P<Item>> {
    SmallVector::one(i.map(|i| folder.fold_item_simple(i)))
}


fn my_noop_fold_item_simple<T: Folder>(Item {id, ident, attrs, node, vis, span}: Item,
                                       folder: &mut T) -> Item {

    Item {
        id: folder.new_id(id),
        vis: folder.fold_vis(vis),
        ident: folder.fold_ident(ident),
        attrs: fold::fold_attrs(attrs, folder),
        node: folder.fold_item_kind(node),//
        span: folder.new_span(span)
    }
}


fn my_noop_fold_item_kind<T: Folder> (i: ItemKind, folder: &mut T) -> ItemKind {
    match i {
       
        ItemKind::Fn(decl, unsafety, constness, abi, generics, body) => {
     
            let generics = folder.fold_generics(generics);
            let decl = folder.fold_fn_decl(decl);
            let body = folder.fold_block(body);
            if unsafety == Unsafety::Unsafe {

                #[cfg(feature = "debugmyplugin")]
                println!("unsafe function detected!");
            }
            ItemKind::Fn(decl, unsafety, constness, abi, generics, body)
        }
        _ => fold::noop_fold_item_kind(i, folder)
    }
}

/// modify the original fold_expr to mark read/write
fn my_noop_fold_expr<T:Folder + Refinfo > (e: Expr, folder: &mut T) -> Expr {
    /// rules to make match expressions
    macro_rules! make_expr {
        ( $opkind:expr, ($($op:expr),*), $el:expr, $er:expr ) => {
            {
                folder.setleft(true);
                let ltmp = folder.fold_expr($el);
                folder.setleft(false);
                let rtmp = folder.fold_expr($er);
                Expr { 
                    node: $opkind($($op,)*ltmp, rtmp), 
                    id: folder.new_id(e.id),
                    span: folder.new_span(e.span),
                    attrs: fold::fold_attrs(e.attrs.into(), folder).into(),
                }
            }    
        }
    }
    match e.node.clone() {
        // mark left and write here
        ExprKind::Assign(el,er) => {
            make_expr!(ExprKind::Assign, (), el, er)
        },
        ExprKind::AssignOp(op,el,er) => {
            make_expr!(ExprKind::AssignOp, (op), el, er)
        },
        _ => fold::noop_fold_expr(e, folder),
    }
}


fn tag_method(checker: &mut Refchecker, args:Vec<P<Expr>>, outer: Span, op:Span) -> P<Expr> {
    let crate_name = checker.cx.ident_of("myplugin_support");
    //decide this is a read/write
    let mut fn_name = checker.cx.ident_of("check_readable_extend");
    if checker.isleft() == true {
        fn_name = checker.cx.ident_of("check_writable_extend");
    }
    let path = checker.cx.path(op, vec![crate_name, fn_name]);
    let epath = checker.cx.expr_path(path);
    let args_expanded = checker.fold_exprs(args);
    checker.cx.expr_deref(outer, checker.cx.expr_call(outer, epath, args_expanded))
}




#[plugin_registrar]
pub fn plugin_registrar(reg: &mut Registry) {
    #[cfg(feature = "debugmyplugin")]
    println!("DEBUG: IN the plugin_registrar expand_checkderef");
    reg.register_syntax_extension(
        Symbol::intern("checkderef"),
        //MultiModifier(Box::new(expand_newcheckderef)));
        MultiModifier(Box::new(|cx: &mut ExtCtxt, _span: Span, mi: &MetaItem, a: Annotatable| {
            let mut checker = &mut Refchecker {
                cx: cx,
                left: false,
            };
            match a {
                Annotatable::Item(i) => Annotatable::Item (
                    checker.fold_item(i).expect_one("expected exactly one item")),
                Annotatable::TraitItem(i) => Annotatable::TraitItem (
                    i.map(|i| checker.fold_trait_item(i).expect_one("expected exactly one item"))),
                Annotatable::ImplItem(i) => Annotatable::ImplItem(
                    i.map(|i| checker.fold_impl_item(i).expect_one("expected exactly one item"))),
            }
        })));
}
