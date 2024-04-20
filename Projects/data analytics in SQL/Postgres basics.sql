/*markdown
# First some simple operations in Postgres 
Also see [SQL Style Guide](https://www.sqlstyle.guide/)
*/

CREATE TABLE IF NOT EXISTS test (
	name varchar,
	age INT
    );

INSERT INTO test (name, age)
VALUES ('John Doe', 30),
       ('Jane Smith', 25),
       ('Emily Johnson', 40);

/*markdown
Note that you can import csv in a query, using:

```sql
COPY your_table_name (column1, column2, column3, ...)
FROM '/path/to/your/file.csv'
DELIMITER ','
CSV HEADER;
```
Note that the table should already exist, and its schema should match the data in the CSV file.
*/

SELECT * 
FROM test

SELECT column_name, data_type, udt_name
FROM INFORMATION_SCHEMA.COLUMNS
WHERE table_name = 'test'

/*markdown
To drill deeper into (user defined) data types, use `pg_type`
*/

SELECT typname, typcategory
FROM pg_type
WHERE typname = 'varchar';

/*markdown
## Extensions
*/

SELECT *
FROM pg_available_extensions

CREATE EXTENSION IF NOT EXISTS fuzzystrmatch;

SELECT levenshtein('BOGUS', 'BORGOS');

/*markdown
## INSERT INTO // VALUES should be the first thing to learn
*/

INSERT INTO test (name, age)
    VALUES ('Johannes2', 36)
    RETURNING name, age;

/*markdown
# Alongside INSERT, use this to UPDATE 
*/

UPDATE test SET name = 'Rosy' 
    WHERE name = 'Johannes2'
    RETURNING name, age;

SELECT STRING_AGG(name, ', ')
FROM test

/*markdown
# DELETE
*/

DELETE FROM test 
WHERE age >= 40;

/*markdown
## Create a temp table

useful if you can't make a new table due to permissions.
*/

/*markdown
```sql
CREATE TEMP TABLE temporary AS
SELECT name, age
    FROM test

-- or (less common)    
SELECT name, age
INTO TEMP TABLE temporary
    FROM test

-- then to add rows
INSERT INTO temporary
SELECT name, age
FROM test
WHERE age BETWEEN 30 AND 40;
```
*/

DROP TABLE IF EXISTS temporary;

/*markdown
# Datacamp notes
*/

/*markdown
Create bins: use trunc() 
*/

SELECT trunc('125.5', -2);

-- Create bins
WITH bins AS ( 
    SELECT generate_series(30, 60, 5) AS lower, 
        generate_series(35,65,5) AS upper
        ),
-- Subset data to tag of interest
    ebs AS ( 
        SELECT unanswered_count 
        FROM stackoverflow 
        WHERE tag='amazon-ebs' 
        )
-- Count values in each bin
SELECT lower, upper, count(unanswered_count)
    -- left join keeps all bins
    FROM bins
        LEFT JOIN ebs
            ON unanswered_count >= lower
            AND unanswered_count < upper
    -- Group by bin bounds to create the groups
    GROUP BY lower, upper
    ORDER BY lower;

/*markdown
same can be done if you make 1 time-based series and then join the original table with a date_trunc.
```SQL 
LEFT JOIN sales
    ON hours=date_trunc('hour', date)
```

OR a lower and upper time-series and join `ON date >= lower AND date < upper`
*/

/*markdown
# String operations
*/

SELECT split_part('a,bc,d', ',', 2);

SELECT substring('abcdef' FROM 2 FOR 3);

SELECT 'a' || 2 || 'cc'; -- or concat()

/*markdown
## Common issue with string categories

Inputted as 'Aple', ' apple'...

|customer | fav_fruit|
|----------|-----------|
|349 | aple|
|874 | Apple|
|703 | apple|


...
## Strategy: recode > join
```SQL
-- Step 1
CREATE TEMP TABLE recode AS
SELECT DISTINCT fav_fruit AS original, -- original, messy values
fav_fruit AS standardized -- new standardized values
FROM fruit;

-- Step 2
-- All rows: lower case, remove white space on ends
UPDATE recode
SET standardized=trim(lower(original));
-- Specific rows: correct a misspelling
UPDATE recode
SET standardized='banana'
WHERE standardized LIKE '%nn%';
-- All rows: remove any s
UPDATE recode
SET standardized=rtrim(standardized, 's');

-- Step 3
SELECT standardized,
    count(*)
    FROM fruit
        LEFT JOIN recode
        ON fav_fruit=original
    GROUP BY standardized;
```


*/

SELECT date_trunc('month', now());

SELECT generate_series('2018-01-01',
                        '2018-01-15',
                        '2 days'::interval);

-- alternative to LIKE
SELECT title, description
FROM film
WHERE to_tsvector(title) @@ to_tsquery('elf');

/*markdown
## Correlation matrix

Note that the correlations are calculated/inserted by row. 
```SQL
DROP TABLE IF EXISTS correlations;

CREATE TEMP TABLE correlations AS
SELECT 'profits'::varchar AS measure,
       corr(profits, profits) AS profits,
       corr(profits, profits_change) AS profits_change,
       corr(profits, revenues_change) AS revenues_change
  FROM fortune500;

INSERT INTO correlations
SELECT 'profits_change'::varchar AS measure,
       corr(profits_change, profits) AS profits,
       corr(profits_change, profits_change) AS profits_change,
       corr(profits_change, revenues_change) AS revenues_change
  FROM fortune500;

INSERT INTO correlations
SELECT 'revenues_change'::varchar AS measure,
       corr(revenues_change, profits) AS profits,
       corr(revenues_change, profits_change) AS profits_change,
       corr(revenues_change, revenues_change) AS revenues_change
  FROM fortune500;

-- Select each column, rounding the correlations
SELECT measure, 
       round(profits::numeric, 2) AS profits,
       round(profits_change::numeric, 2) AS profits_change,
       round(revenues_change::numeric, 2) AS revenues_change
  FROM correlations;
  ```
*/

/*markdown
|measure	|profits	|profits_change	|revenues_change|
|--|--|--|--|
|profits|	1.00	|0.02	|0.02|
|profits_change	|0.02	|1.00	|-0.09|
|revenues_change	|0.02	|-0.09	|1.00|
*/