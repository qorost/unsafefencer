# Useful SQL 


## Basic Query


```
SELECT * FROM `crate` WHERE updated_time BETWEEN '2017-05-08 12:00:00' AND '2017-05-09 09:54:00'
SELECT * FROM `crate` WHERE updated_time = "2017-05-09 09:54:06"
SELECT * FROM `crate` WHERE srcdir like "%py_experiments/samples%"
```

```
SELECT
    name, srcdir, Count(*)
FROM
    crate
GROUP BY
    name, srcdir
Having
    Count(*) > 1

SELECT id, name, srcdir
FROM crate c, crate c2
WHERE c.name = c2.name


SELECT name, Count(*) c FROM crate GROUP BY name HAVING c >1;
```
## [How to select all records from one table that do not exist in another table](http://wiki.lessthandot.com/index.php/5_ways_to_return_rows_from_one_table_not_in_another_table)

```
SELECT * FROM crate WHERE ID not in (select crate_id from mutlintchecker)
```