Exploring Stack Overflow public dataset in BigQuery


###What is BigQuery?

BigQuery is a fully-managed, serverless data warehouse that enables scalable analysis over petabytes of data. It is a Platform as a Service (PaaS) that supports querying using ANSI SQL.

###BigQuery Architecture

BigQuery’s serverless architecture decouples storage and compute and allows them to scale independently on demand. This structure offers both immense flexibility and cost controls for customers because they don’t need to keep their expensive compute resources up and running all the time.
![](/images/markdownx/bqArchitecture.png)

We don't need to know much about BigQuery architecture. But understanding BigQuery Architecture helps us in controlling cost and optimizing query performance. Compute is Dremel, a large multi-tenant cluster that executes SQL queries. Storage is Colossus, Google’s global storage system.BigQuery leverages the columnar storage format and compression algorithm to store data in Colossus, optimized for reading large amounts of structured data.

###BigQuery public datasets
BigQuery provides high-demand public datasets, making it easy for us to access and uncover new insights in the cloud. We can query up to 1 TB of data/month at no cost and gain more value from this growing data ecosystem. There are about 100 public datasets from different industries available for us to use.

### Stack Overflow data set
Stack Overflow public dataset is hosted in Google BigQuery and is included in BigQuery's 1TB/mo of free tier processing. This BigQuery dataset includes an archive of Stack Overflow content, including posts, votes, tags, and badges. BigQuery also provides some examples of SQL queries we can run on this data. Let us explore them next.

###How to access Stack Overflow public dataset in BigQuery?
![](/images/markdownx/bq-menu.png)
We can access the public dataset by navigating into BigQuery under the Big Data section using the Cloud Console hamburger menu. In the BigQuery UI follow the below steps:

1. Click on ADD DATA - Explore public data sets
2. Type Stack Overflow and hit enter
3. Click on VIEW DATA SET. Now the project "bigquery-public-data" will be pinned under the projects section.

![](/images/markdownx/AddData.png)

![](/images/markdownx/stackoverflow.png)

![](/images/markdownx/stackoverflow_overview.png)

###Exploring sample queries provided by BigQuery
BigQuery provides some samples to experiment on the power of this service. We can get these samples by switching to the samples tab on the VIEW DATA SET page. On clicking on the Run this query link BigQuery opens the query editor with the SQL loaded by default. The below query looks at how many questions were posted on Stack Overflow from 2010 to 2015, and what percentage of them have been answered annually.
![](/images/markdownx/overview.png)

```
#standardSQL
SELECT
  EXTRACT(YEAR FROM creation_date) AS Year,
  COUNT(*) AS Number_of_Questions,
  ROUND(100 * SUM(IF(answer_count > 0, 1, 0)) / COUNT(*), 1) AS Percent_Questions_with_Answers
FROM
  `bigquery-public-data.stackoverflow.posts_questions`
GROUP BY
  Year
HAVING
  Year > 2009 AND Year < 2016 
ORDER BY
  YEAR
```
![](/images/markdownx/qqq.png)

In the above image, we can see the message "This query will process 313 MB when run" this is very helpful when we are running queries on production because BigQuery will charge based on the amount of data queried. For more information on BigQuery pricing refer to [BQ pricing](https://cloud.google.com/bigquery/pricing) .

We can check the Query execution plan by clicking on the Execution details tab under the Query results. BigQuery converts the SQL statement into a graph of execution, broken up into a series of query stages, which themselves are composed of more granular sets of execution steps. This is to take advantage of parallelism in the execution of complex SQL statements.

![](/images/markdownx/execplan.png)

BigQuery provides us the option to preview data which will help us to have a first glance look at the data without writing any SQL. It also provides some Metadata about the table we need to query by clicking on the dataset and then clicking on the Details tab. This includes

* Table size
* Number of rows
* Created
* Table expiry
* Last modified
* Data location

![](/images/markdownx/details.png)

Now, let's check what are the top 10 technologies on which the most number of questions are asked in stack overflow over some time. For us to find an answer to this question we need to analyze the columns present in the table posts_questions and we can find a column named tags having names of technologies separated by the delimiter "|". We can extract the tag by running the below query
```
SELECT
  SPLIT(tags,'|') AS TechnologyName,
  COUNT(*) AS Count
FROM
  `bigquery-public-data.stackoverflow.posts_questions`
WHERE
  EXTRACT (YEAR
  FROM
    creation_date)>2016
GROUP BY
  tags
```
![](/images/markdownx/array_data.png)

The resulting data we get after running the above query is in the form of an array. We can use UNNEST operator to Flattening the arrays. The UNNEST takes an ARRAY and returns a table with a single row for each element in the ARRAY. The above SQL can be modified as follows

```
SELECT
  splitted_tags,
  COUNT(*) AS tech_count
FROM (
  SELECT
    SPLIT(tags,'|') AS TechnologyName
  FROM
    `bigquery-public-data.stackoverflow.posts_questions`
  WHERE
    EXTRACT (YEAR
    FROM
      creation_date)>2016)
CROSS JOIN
  UNNEST(TechnologyName) splitted_tags
GROUP BY
  splitted_tags
ORDER BY
  tech_count DESC
LIMIT 10
```
In the query above we are performing a cross join on the array object as a separate table and then grouping the count with individual tag name then sorting the results in descending and limiting it to 10 records. The cross join is a cartesian join which will create a paired combination of each row of the first table with each row of the second table.
![](/images/markdownx/result_1.png)

###Saving BigQuery query results
Now we have successfully run our query and we need to store the result somewhere. BigQuery provides us the option to save the query results as CSV in Google Drive, in our local machine, as JSON, and as a BigQuery table. For saving the result as a BigQuery table we need to have a data set under a BigQuery project. We can create a dataset by clicking on the CREATE DATASET button and name the dataset something like top_10_tech and click on Create dataset button from the pop-up menu. You can also create a dataset using the bq command-line tool from terminal or cloud shell as below.

```
bq mk --dataset --data_location=US top_10_tech
```
![](/images/markdownx/save_res.png)

Click on the SAVE RESULTS button in the Query results section. Select the dataset name and provide the table name in the appropriate fields then click on save. Now you can see the table get created under the dataset top_10_tech.

Now we can query the newly created table using the below SQL

```
SELECT
  *
FROM
  `dataanalysisbq.top_10_tech.top10_results`
```
![](/images/markdownx/first_query.png)

From the above image, we can see the message "Query complete (0.4 sec elapsed, 149 B processed)". If we run the same query again we can see the message "Query complete (0.0 sec elapsed, cached)" this is because BigQuery writes all query results to a table. When we ran the same query, again BigQuery attempts to reuse cached results as the data in the table remained the same. You can read more on Query caching [here](https://cloud.google.com/bigquery/docs/cached-results) .

![](/images/markdownx/cached_query.png)

One important thing to note here is we need to avoid using "SELECT * " as this method is cost-inefficient and can also reduce performance. So we need to select only the necessary columns. The difference is noticeable for tables with a large number of columns.

```
SELECT
  splitted_tags,
  tech_count
FROM
  `dataanalysisbq.top_10_tech.top10_results`
```
One last thing all the above tasks can be performed without creating a cloud account and sharing the credit card details. Having a Gmail account is good enough to get started. So please feel free to experiment with BigQuery.
