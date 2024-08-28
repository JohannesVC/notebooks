/*markdown
# Sample Exam: Coffee Shops
Caffeine Form is a company creating coffee cups from recycled material.

Caffeine Form sells cups to coffee shops through their website. They would prefer to partner directly with the shops.

The company believes that stores with more reviews will help them to better market their product.

The company want to focus on the types of shop that get the most reviews.

They want you to investigate how types of shop and number of reviews are related.

# Task 1

Before you start your analysis, you will need to make sure the data is clean. 

The table below shows what the data should look like. 

Create a cleaned version of the dataframe. 

 - You should start with the data in the table `coffee`. 

 - All column names and values should match the table below.

| Column Name | Criteria                                                |
|-------------|---------------------------------------------------------|
| Region    | Nominal. </br> Where the store is located. One of 10 possible regions (A to J).</br> Missing values should be replaced with “Unknown”.|
| Place name | Nominal. </br>The name of the store. </br>Missing values should be replaced with “Unknown”.|
| Place type  | Nominal. </br>The type of coffee shop. One of “Coffee shop”, “Cafe”, “Espresso bar”, and “Others”. </br>Missing values should be replaced with “Unknown”. |
| Rating   | Ordinal. </br>Average rating of the store from reviews. On a 5 point scale. </br>Missing values should be replaced with 0. |
| Reviews  | Nominal. </br>The number of reviews given to the store. </br>Missing values should be replaced with the overall median number, rounded to the nearest interger value.|
| Price  | Ordinal. </br>The price range of products in the store. One of '\$', '\$\$' or '\$\$\$'. </br>Missing values should be replaced with ”Unknown”.|
| Delivery option   | Nominal. </br>If delivery is available. Either True or False. </br>Missing values should be replaced with False. |
| Dine in option | Nominal. </br>If dine in is available. Either True or False. </br>Missing values should be replaced with False. |
| Takeout option | Nominal. </br>If take away is available. Either True or False. </br>Missing values should be replaced with False.|
*/

/*markdown
# Task 2 

The team at Caffine Form believe that the number of reviews changes depending on the type of store. 

Producing a table showing the difference in the median number of reviews by rating along with the minimum and maximum number of reviews to investigate this question for the team.

 - You should start with the data in the table `coffee`.

 - It should include the three columns `Place type`, `min_review`, `max_review`. 
*/

CREATE table IF NOT EXISTS coffee (
    "Region" text,
    "Place name" text,
    "Place type" text,
    "Rating" double precision,
    "Reviews" integer,
    "Price" text,
    "Delivery option" boolean,
    "Dine in option" boolean,
    "Takeout option" boolean
);

COPY coffee (
    "Region",
    "Place name",
    "Place type",
    "Rating",
    "Reviews" ,
    "Price" ,
    "Delivery option" ,
    "Dine in option" ,
    "Takeout option" 
)
FROM 'C:\Users\johan\Downloads\coffee.csv'
DELIMITER ','
CSV HEADER;

/*markdown
> (I imported via pgadmin)
*/

SELECT *
FROM coffee
LIMIT 5;

SELECT 'reg_null' as metric, round(avg(CASE WHEN "Region" IS NOT NULL THEN 1 ELSE 0 END),2) as avg_nulls FROM coffee
UNION ALL
SELECT 'place_name_null', round(avg(CASE WHEN "Place name" IS NOT NULL THEN 1 ELSE 0 END),2) FROM coffee
UNION ALL
SELECT 'place_type_null', round(avg(CASE WHEN "Place type" IS NOT NULL THEN 1 ELSE 0 END),2) FROM coffee
UNION ALL
SELECT 'rating_null', round(avg(CASE WHEN "Rating" IS NOT NULL THEN 1 ELSE 0 END),2) FROM coffee
UNION ALL
SELECT 'rev_null', round(avg(CASE WHEN "Reviews" IS NOT NULL THEN 1 ELSE 0 END),2) FROM coffee
UNION ALL
SELECT 'price_null', round(avg(CASE WHEN "Price" IS NOT NULL THEN 1 ELSE 0 END),2) FROM coffee
UNION ALL
SELECT 'deliv_null', round(avg(CASE WHEN "Delivery option" IS NOT NULL THEN 1 ELSE 0 END),2) FROM coffee
UNION ALL
SELECT 'dine_null', round(avg(CASE WHEN "Dine in option" IS NOT NULL THEN 1 ELSE 0 END),2) FROM coffee
UNION ALL
SELECT 'takeout_null', round(avg(CASE WHEN "Takeout option" IS NOT NULL THEN 1 ELSE 0 END),2) FROM coffee

SELECT *
FROM (
  VALUES
    ('reg_null', (SELECT round(avg(CASE WHEN "Region" IS NOT NULL THEN 1 ELSE 0 END),2) FROM coffee)),
    ('place_name_null', (SELECT round(avg(CASE WHEN "Place name" IS NOT NULL THEN 1 ELSE 0 END),2) FROM coffee)),
    ('place_type_null', (SELECT round(avg(CASE WHEN "Place type" IS NOT NULL THEN 1 ELSE 0 END),2) FROM coffee)),
    ('rating_null', (SELECT round(avg(CASE WHEN "Rating" IS NOT NULL THEN 1 ELSE 0 END),2) FROM coffee)),
    ('rev_null', (SELECT round(avg(CASE WHEN "Reviews" IS NOT NULL THEN 1 ELSE 0 END),2) FROM coffee)),
    ('price_null', (SELECT round(avg(CASE WHEN "Price" IS NOT NULL THEN 1 ELSE 0 END),2) FROM coffee)),
    ('deliv_null', (SELECT round(avg(CASE WHEN "Delivery option" IS NOT NULL THEN 1 ELSE 0 END),2) FROM coffee)),
    ('dine_null', (SELECT round(avg(CASE WHEN "Dine in option" IS NOT NULL THEN 1 ELSE 0 END),2) FROM coffee)),
    ('takeout_null', (SELECT round(avg(CASE WHEN "Takeout option" IS NOT NULL THEN 1 ELSE 0 END),2) FROM coffee))
) AS ct(metric, avg_value);