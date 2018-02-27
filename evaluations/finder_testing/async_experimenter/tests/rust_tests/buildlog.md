# MyLintLog

The summary of the mylint results: 

	266 functions.

	13 mut returns.

	**9 imut input and mut returns.**

## List of the imu_to_mut functions


* FnKind::Method ptr

```
src/client.rs:75:5
  --> src/client.rs:75:5
   |
75 |       pub fn ptr(&self) -> *mut RDKafka {
   |  _____^ starting here...
76 | |         self.ptr
77 | |     }
   | |_____^ ...ending here
   |
```

* FnKind::Method native_ptr

```
src/client.rs:116:5
   --> src/client.rs:116:5
    |
116 |       pub fn native_ptr(&self) -> *mut RDKafka {
    |  _____^ starting here...
117 | |         self.native.ptr
118 | |     }
    | |_____^ ...ending here
    |
```

* FnKind::Method ptr

```
src/config.rs:65:5
  --> src/config.rs:65:5
   |
65 |       pub fn ptr(&self) -> *mut RDKafkaConf {
   |  _____^ starting here...
66 | |         self.ptr.expect("Pointer to native Kafka client config used after free")
67 | |     }
   | |_____^ ...ending here
   |
```

* FnKind::Method ptr_mut

```
src/config.rs:70:5
  --> src/config.rs:70:5
   |
70 |       pub fn ptr_mut(mut self) -> *mut RDKafkaConf {
   |  _____^ starting here...
71 | |         self.ptr.take().expect("Pointer to native Kafka client config used after free")
72 | |     }
   | |_____^ ...ending here
   |
```

* FnKind::Method ptr

```
src/message.rs:23:5
  --> src/message.rs:23:5
   |
23 |       pub fn ptr(&self) -> *mut RDKafkaMessage {
   |  _____^ starting here...
24 | |         self.ptr
25 | |     }
   | |_____^ ...ending here
   |
```

* FnKind::Method ptr

```
src/producer.rs:52:5
  --> src/producer.rs:52:5
   |
52 |       fn ptr(&self) -> *mut RDKafkaTopic {
   |  _____^ starting here...
53 | |         self.ptr
54 | |     }
   | |_____^ ...ending here
   |
```

* FnKind::Method native_ptr

```
src/producer.rs:251:5
   --> src/producer.rs:251:5
    |
251 |       fn native_ptr(&self) -> *mut RDKafka {
    |  _____^ starting here...
252 | |         self.inner.client.native_ptr()
253 | |     }
    | |_____^ ...ending here
    |
```

* FnKind::Method native_ptr

```
src/producer.rs:444:5
   --> src/producer.rs:444:5
    |
444 |       fn native_ptr(&self) -> *mut RDKafka {
    |  _____^ starting here...
445 | |         self.inner.producer.native_ptr()
446 | |     }
    | |_____^ ...ending here
    |
```

* FnKind::Method create_native_topic_partition_list

```
src/topic_partition_list.rs:100:5
   --> src/topic_partition_list.rs:100:5
    |
100 |     pub fn create_native_topic_partition_list(&self) -> *mut RDKafkaTopicPartitionList {
    |     ^
    |
    = note: #[warn(test_lint)] on by default
    = help: for further information visit https://github.com/Manishearth/rust-clippy/wiki#test_lint

```
