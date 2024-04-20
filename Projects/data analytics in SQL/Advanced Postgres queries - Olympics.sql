/*markdown
# Olympics practice dataset


Using:
- pgadmin to import a csv dataset [Postgres tutorial](https://techtfq.com/blog/practice-writing-sql-queries-using-real-dataset)
- This notebook.
 
With the intention to reinforce and track learnings for later use.
*/

/*markdown
**`Questions for the dataset:`**
1. How many olympics games have been held?
2. List down all Olympics games held so far.
3. Mention the total no of nations who participated in each olympics game?
4. Which year saw the highest and lowest no of countries participating in olympics?
5. Which nation has participated in all of the olympic games?
6. Identify the sport which was played in all summer olympics.
7. Which Sports were just played only once in the olympics?
8. Fetch the total no of sports played in each olympic games.
9. Fetch details of the oldest athletes to win a gold medal.
10. Find the Ratio of male and female athletes participated in all olympic games.
11. Fetch the top 5 athletes who have won the most gold medals.
12. Fetch the top 5 athletes who have won the most medals (gold/silver/bronze).
13. Fetch the top 5 most successful countries in olympics. Success is defined by no of medals won.
14. List down total gold, silver and broze medals won by each country.
15. List down total gold, silver and broze medals won by each country corresponding to each olympic games.
16. Identify which country won the most gold, most silver and most bronze medals in each olympic games.
17. Identify which country won the most gold, most silver, most bronze medals and the most medals in each olympic games.
18. Which countries have never won gold medal but have won silver/bronze medals?
19. In which Sport/event, India has won highest medals.
20. Break down all olympic games where india won medal for Hockey and how many medals in each olympic games.
*/

SELECT STRING_AGG(DISTINCT table_name, ', ')
FROM INFORMATION_SCHEMA.COLUMNS
WHERE table_name LIKE 'olympics%'

SELECT STRING_AGG(DISTINCT column_name, ', ')
FROM INFORMATION_SCHEMA.COLUMNS
WHERE table_name = 'olympics_history'

SELECT *
FROM olympics_history
LIMIT 10;

/*markdown
## Q1
*/

SELECT COUNT(DISTINCT games)
FROM olympics_history;

/*markdown
## Q2
*/

SELECT 
    DISTINCT games, 
    year
FROM olympics_history
ORDER BY games, year
LIMIT 10;

/*markdown
## Q3
*/

/*markdown
NOC is different from team. And also from noc. 
*/

SELECT 
    DISTINCT games, year, team, noc
FROM olympics_history
ORDER BY games, year
LIMIT 10;

/*markdown
INNER JOINing it with region removes null values.
*/

with all_countries as (
    select games, nr.region
    from olympics_history oh
    left join olympics_history_noc_regions nr ON nr.noc = oh.noc
    group by games, nr.region)
    
select games, count(1) as total_countries
from all_countries
group by games
order by games
LIMIT 10;

/*markdown
## Q4
*/

-- Note that the (inner) join and left join have different counts
SELECT count(*)
FROM olympics_history hist
LEFT JOIN olympics_history_noc_regions regions 
USING (noc);

-- To see the difference, use except
SELECT hist.games,  hist.noc as hist_noc, regions.noc as regions_noc
FROM olympics_history hist
LEFT JOIN olympics_history_noc_regions regions 
USING (noc)
EXCEPT
SELECT hist.games, hist.noc as hist_noc, regions.noc as regions_noc
FROM olympics_history hist
JOIN olympics_history_noc_regions regions 
USING (noc)
LIMIT 10;

/*markdown
In other words, (inner) `JOIN` drops the rows that don't have a `NOC` column in the regions table while `LEFT JOIN` keeps those rows. 

This still doesn't explain my previous differences. 
*/

WITH countries AS (
    SELECT games, regions.region
    FROM olympics_history hist
    JOIN olympics_history_noc_regions regions 
    USING (noc)
    GROUP BY games, regions.region), -- note the comma
tot_countries AS (
    SELECT 
        games, 
        COUNT(region) as number_of_nations
    FROM countries
    GROUP BY games)

SELECT 
    DISTINCT FIRST_VALUE(games) OVER(ORDER BY number_of_nations) as Lowest, 
    FIRST_VALUE(number_of_nations) OVER(ORDER BY number_of_nations) AS Lowest_nr,
    FIRST_VALUE(games) OVER(ORDER BY number_of_nations DESC) as Highest,
    FIRST_VALUE(number_of_nations) OVER(ORDER BY number_of_nations DESC) AS Highest_nr
FROM tot_countries;

/*markdown
Alternatively, using min and max
*/

WITH countries AS (
    SELECT games, regions.region
    FROM olympics_history hist
    JOIN olympics_history_noc_regions regions 
    USING (noc)
    GROUP BY games, regions.region), -- note the comma
tot_countries AS (
    SELECT 
        games, 
        COUNT(region) as number_of_nations
    FROM countries
    GROUP BY games),
min_max AS (
    SELECT 
        MIN(number_of_nations) AS min_nations,
        MAX(number_of_nations) AS max_nations
    FROM tot_countries
)

SELECT 
    (SELECT games FROM tot_countries WHERE number_of_nations = min_max.min_nations LIMIT 1) AS Lowest,
    min_max.min_nations,
    (SELECT games FROM tot_countries WHERE number_of_nations = min_max.max_nations LIMIT 1) AS Highest,
    min_max.max_nations
FROM min_max;

/*markdown
## Q5
*/

WITH countries AS (
    SELECT games, regions.region
    FROM olympics_history hist
    JOIN olympics_history_noc_regions regions 
    USING (noc)
    GROUP BY games, regions.region),
nr_games AS (
    SELECT 
        region, COUNT(games) as number_of_games
    FROM countries
    GROUP BY region)

SELECT DISTINCT region, number_of_games
FROM nr_games
WHERE number_of_games = 51
ORDER BY number_of_games DESC;

/*markdown
## Q6 Identify the sport which was played in all summer olympics
*/

SELECT *
FROM olympics_history
LIMIT 1;

SELECT 
    DISTINCT sport, 
    count(DISTINCT games) as c_g
FROM olympics_history
GROUP BY sport
ORDER BY c_g DESC
LIMIT 10;