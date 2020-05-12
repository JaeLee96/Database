from __future__ import print_function
from pyspark import SparkConf, SparkContext
from pyspark.sql import SQLContext
from pyspark.sql.types import ArrayType, StringType, IntegerType, BooleanType
from pyspark.sql.functions import col, udf

import pandas as pd
import os
import cleantext


# convert files to parquet format, if the parquet files do not exist in the directory
def func():

    arr = []
    with open('./comments-minimal.json.bz2', "r+") as f:
        for line in f:
            # append each JSON object to our data variable
            arr.append(json.loads(line))

    # get results of sanitized text
    result = []
    for comment in data:
        # pass each body into sanitize and append the result to the result variable
        result.append(sanitize(comment["body"]))
    return result


def main(spark):
    """Main function takes a Spark SQL context."""
    # YOUR CODE HERE
    # YOU MAY ADD OTHER FUNCTIONS AS NEEDED
    
    # Read original data files
    # Create parquet files from the original files
    if not os.path.isdir('./labeled_data.parquet'):
        df1 = spark.read.csv('labeled_data.csv')
        df1.write.parquet('labeled_data.parquet')
    if not os.path.isdir('./submissions.parquet'):
        df2 = spark.read.json('submissions.json.bz2')
        df2.write.parquet('submissions.parquet')
    if not os.path.isdir('./comments-minimal.parquet'):
        df3 = spark.read.csv('comments-minimal.json.bz2')
        df3.write.parquet('comments-minimal.parquet')

    # Read the parquet files
    labeled_data = spark.read.parquet('./labeled_data.parquet')
    submissions = spark.read.parquet('./submissions.parquet')
    comments_minimal = spark.read.parquet('./comments-minimal.parquet')

    # Create a UDF, that takes in a comment as input and outputs the datagrams
    func_udf = udf('func', ArrayType(ArrayType(StringType())))


    # Create a dataframe that contains data from comments-minimal.json
#    schema = StructType([
#                         StructField("author", StringType(), nullable=False),
#                         StructField("body", StringType(), nullable=False),
#                         StructField("can_gild", BooleanType(), nullable=False),
#                         StructField("controversionality", IntegerType(), nullable=False),
#                         StructField("created_utc", IntegerType(), nullable=False),
#                         StructField("edited", BooleanType(), nullable=False),
#                         StructField("gilded", IntegerType(), nullable=False),
#                         StructField("id", StringType(), nullable=False),
#                         StructField("is_submitter", BooleanType(), nullable=False),
#                         StructField("link_id", StringType(), nullable=False),
#                         StructField("parent_id", StringType(), nullable=False),
#                         StructField("permalink", StringType(), nullable=False),
#                         StructField("retrieved_on", IntegerType(), nullable=False),
#                         StructField("score", IntegerType(), nullable=False),
#                         StructField("stickied", BooleanType(), nullable=False),
#                         StructField("subreddit", StringType(), nullable=False),
#                         StructField("subreddit_id", StringType(), nullable=False),
#                        ])


    # take jsonArray file, convert it into a JSON object, and then read the json file
    # https://stackoverflow.com/questions/48726208/how-do-i-read-a-large-json-array-file-in-pyspark
    SEX = spark.textFile('./comments-test/comments-minimal.json', partitions).map(lambda x: x.encode('utf-8','ignore').strip(u",\r\n[]\ufeff"))
    df = sqlContext.read.json(SEX)

#    func_udf.select('*', func_udf())

if __name__ == "__main__":
    conf = SparkConf().setAppName("CS143 Project 2B")
    conf = conf.setMaster("local[*]")
    sc   = SparkContext(conf=conf)
    sqlContext = SQLContext(sc)
    sc.addPyFile("cleantext.py")
    main(sqlContext)
