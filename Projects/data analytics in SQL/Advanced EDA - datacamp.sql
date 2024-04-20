/*markdown
## coalesce

In the fortune500 data, industry contains some missing values. Use coalesce() to use the value of sector as the industry when industry is NULL. Then find the most common industry.

Use coalesce() to select the first non-NULL value from industry, sector, or 'Unknown' as a fallback value.
Find the most common value of industry2.
*/

SELECT coalesce(industry, sector, 'unknown') as industry2, count(*)
FROM fortune500
GROUP BY industry2
ORDER BY count(*) DESC
LIMIT 1;

/*markdown
## min, max, avg, stddev
Compute the min(), avg(), max(), and stddev() of profits.

Now repeat step 1, but summarize profits by sector.
Order the results by the average profits for each sector.
*/

SELECT sector,
    min(profits), round(avg(profits)) avg, max(profits), round(stddev(profits)) stddev
FROM fortune500
GROUP BY sector
ORDER BY 3 DESC
LIMIT 10;

/*markdown
## Generate series
Summarize the distribution of the number of questions with the tag "dropbox" on Stack Overflow per day by binning the data.
*/

/*markdown
## Create a temp table
Find the Fortune 500 companies that have profits in the top 20% for their sector (compared to other Fortune 500 companies).

To do this, first, find the 80th percentile of profit for each sector with

```sql
percentile_disc(fraction) 
WITHIN GROUP (ORDER BY sort_expression)
```
and save the results in a temporary table.

Then join fortune500 to the temporary table to select companies with profits greater than the 80th percentile cut-off.
*/

/*markdown
### Group and recode values
There are almost 150 distinct values of evanston311.category. But some of these categories are similar, with the form "Main Category - Details". We can get a better sense of what requests are common if we aggregate by the main category.

To do this, create a temporary table recode mapping distinct category values to new, standardized values. Make the standardized values the part of the category before a dash ('-'). Extract this value with the split_part() function:

split_part(string text, delimiter text, field int)
You'll also need to do some additional cleanup of a few cases that don't fit this pattern.

Then the evanston311 table can be joined to recode to group requests by the new standardized category values.
*/

/*markdown
## Monthly average with missing dates
Find the average number of Evanston 311 requests created per day for each month of the data.

This time, do not ignore dates with no requests.

Generate a series of dates from 2016-01-01 to 2018-06-30.
Join the series to a subquery to count the number of requests created per day.
Use date_trunc() to get months from date, which has all dates, NOT day.
Use coalesce() to replace NULL count values with 0. Compute the average of this value.
*/

/*markdown
## Longest gap

What is the longest time between Evanston 311 requests being submitted?
*/