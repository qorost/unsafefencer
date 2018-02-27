use std::any::TypeId;
use std::mem::size_of;
//use std::ops::*;



#[macro_export]
macro_rules! add_headers {
    () => {
    use myplugin_support::{Readable,Writable,Dropped};
    //use myplugin_support::DerefWrap;
    use myplugin_support::{check_dropped,check_readable,check_writable};
    use myplugin_support::{check_dropped_extend, check_readable_extend, check_writable_extend};
    use std::any::TypeId;
    use std::mem::size_of;
    }
}


/// definition of 
pub struct Readable {}
pub struct Writable {}
pub struct Dropped {}



pub fn check_dropped_extend<T>(x: *const T) -> *const T {
    check_dropped(x);
    x
}

pub fn say_hello() {
    //println!("Hello World from support module!");
}

pub fn check_readable_extend<T:std::fmt::Debug>(x:*const T) -> *const T {
    //println!("In function check_readable_extend");
    check_dropped(x);
    check_readable(x);
    x
}

pub fn check_writable_extend<T>(x:*mut T) -> *mut T {
    //println!("In function check_write_extend");
    check_dropped(x);
    check_writable(x);
    x
}

/// Check if `*const T` may be deferenced in unsafe code
pub fn check_dropped<T>(x: *const T) {
    // Computes the address of the `_type_id` field in `T`
    // Fix me: `repr()` may cause issues
    let ptr = ((x as usize) + size_of::<T>() - size_of::<TypeId>()) as *const TypeId;
    let type_id = unsafe{ *ptr };
    let type_id_dropped = TypeId::of::<Dropped>();
    if type_id == type_id_dropped {
        panic!("CheckDopped Failed, TypeId is incorrect. Expect {:?} found {:?}", type_id_dropped,
               type_id);
    }
}


/// Check if `*const T` may be deferenced in unsafe code
pub fn check_readable<T>(x: *const T) where T:std::fmt::Debug {
    // Computes the address of the `_type_id` field in `T`
    // Fix me: `repr()` may cause issues
    //println!("In check_readable, readable has an Id of {:?}",TypeId::of::<Readable>());
    let ptr = ((x as usize) + size_of::<T>() - size_of::<TypeId>()) as *const TypeId;
    let type_id = unsafe{ *ptr };
    let type_id_readable = TypeId::of::<Readable>();
    let type_id_writable = TypeId::of::<Writable>();

    if type_id == type_id_writable {
    
    }
    else if type_id != type_id_readable {
        panic!("Checkreadable Failed, TypeId is incorrect. Expect {:?} found {:?}", type_id_readable,
               type_id);
    }
}

/// Check if `*mut T` may be deferenced in unsafe code
pub fn check_writable<T>(x: *mut T) {
    // Computes the address of the `_type_id` field in `T`
    // Fix me: `repr()` may cause issues
    let ptr = ((x as usize) + size_of::<T>() - size_of::<TypeId>()) as *const TypeId;
    let type_id = unsafe{ *ptr };
    let type_id_writable = TypeId::of::<Writable>();
    if type_id != type_id_writable {
        panic!("Checkwritable Failed, TypeId is incorrect. Expect {:?} found {:?}", type_id_writable,
               type_id);
    }
}

#[macro_export]
macro_rules! extend_readable {
    ($(#[derive($tt:ident)])* struct $name:ident {
        $($x:ident : $t:ty,)*
    }) => {
        $(#[derive($tt)])*
        struct $name {
            $($x: $t,)*
            _type_id: std::any::TypeId,
        }
        impl Drop for $name {
            fn drop(&mut self) {
                self._type_id = TypeId::of::<Dropped>();
                //println!("New Drop DEBUG is dropped");
            }
        }
    } 
}

#[macro_export]
macro_rules! extend_writable {
    ($(#[derive($tt:ident)])* struct $name:ident {
        $($x:ident : $t:ty,)*
    }) => {
        $(#[derive($tt)])*
        struct $name {
            $($x: $t,)*
            _type_id: std::any::TypeId,
        }
        impl Drop for $name {
            fn drop(&mut self) {
                self._type_id = TypeId::of::<Dropped>();
                //println!("New Drop DEBUG is dropped");
            }
        }
    } 
}

#[macro_export]
macro_rules! extend_readable {
    ($(#[derive($tt:ident)])* struct $name:ident {
        $($x:ident : $t:ty,)*
    }) => {
        $(#[derive($tt)])*
        struct $name {
            $($x: $t,)*
            _type_id: std::any::TypeId,
        }
        impl Drop for $name {
            fn drop(&mut self) {
                self._type_id = TypeId::of::<Dropped>();
                //println!("New Drop DEBUG is dropped");
            }
        }
        impl UnsafeShare for $name {
            //FIXME readable is not useful to tell if this structure is read/write;
            fn readable(&self) -> bool {true}
            fn writable(&self) -> bool {false}
        }
    } 
}

#[macro_export]
macro_rules! extend_writable {
    ($(#[derive($tt:ident)])* struct $name:ident {
        $($x:ident : $t:ty,)*
    }) => {
        $(#[derive($tt)])*
        struct $name {
            $($x: $t,)*
            _type_id: std::any::TypeId,
        }
        impl Drop for $name {
            fn drop(&mut self) {
                self._type_id = TypeId::of::<Dropped>();
                //println!("New Drop DEBUG is dropped");
            }
        }
        impl UnsafeShare for $name {
            fn readable(&self) -> bool {true}
            fn writable(&self) -> bool {true}
        }
    } 
}

#[macro_export]
macro_rules! extend_struct {
    ($(#[derive($tt:ident)])* struct $name:ident {
        $($x:ident : $t:ty,)*
    }) => {
        $(#[derive($tt)])*
        struct $name {
            $($x: $t,)*
            _type_id: std::any::TypeId,
        }
        impl Drop for $name {
            fn drop(&mut self) {
                self._type_id = TypeId::of::<Dropped>();
                //println!("New Drop DEBUG is dropped");
            }
        }
    } 
}

#[macro_export]
macro_rules! onlyreadable {
    ($name: ident {
        $($x:ident : $exp:expr,)*
    }) => {
        $name{
            $($x: $exp,)*
            _type_id: TypeId::of::<Readable>()
        }
    }
}


#[macro_export]
macro_rules! allowwritable {
    ($name: ident {
        $($x:ident : $exp:expr,)*
    }) => {
        $name{
            $($x: $exp,)*
            _type_id: TypeId::of::<Writable>()
        }
    }
}




#[test]
fn it_works() {
    extend_struct!(#[derive(Debug)] struct A {x:i32,});
    let x:A =  onlyreadable!(A{x:32,});
    println!("x = {:?}",x);
    println!("readable has an Id of {:?}",TypeId::of::<Readable>());
    assert_eq!(x._type_id,TypeId::of::<Readable>());
    let raw = &x as *const A;
    check_dropped(raw);
    check_readable(raw);


    let x = check_dropped_extend(raw);
}


#[test]
fn it_works_new() {

    extend_readable!(struct A{x:i32,});

    let x:A = onlyreadable!(A{x:32,});

    assert_eq!(x.readable(),true);
    assert_eq!(x.writable(),false);

    extend_writable!(struct B{x:i32,});

    let y:B = allowwritable!(B{x:32,});

    assert_eq!(y.writable(),true);
}
