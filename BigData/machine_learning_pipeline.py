# Pre-requisities to be installed on virtual environemnt for Python:
# Use Spark machine learning library mllib's Binomial Logistic Regression algorithm.
# https://spark.apache.org/docs/latest/ml-classification-regression.html#binomial-logistic-regression
# pip install pyspark
# pip install matplotlib
# pip install pandas
# pip install numpy

from pyspark.sql import SparkSession, Row
import pyspark.sql.functions as f
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
from pyspark import SparkContext
from pyspark.sql.types import StructType, StructField, StringType, DoubleType
from pyspark.ml.feature import StringIndexer, VectorAssembler, StandardScaler
from pyspark.ml.classification import LogisticRegression
from pyspark.ml import Pipeline
from pyspark.ml.linalg import Vectors
sc = SparkContext()
sc.setLogLevel("ERROR")
spark = SparkSession.builder\
    .master("local")\
    .appName("main")\
    .config("spark.dynamicAllocation.enabled", "true")\
    .config("spark.shuffle.service.enabled", "true")\
    .getOrCreate()\

sampleDataPath = "testData.data"

#Generate random sample
import random

randomData = "randomsample.data"

with open(sampleDataPath) as sampleFile:
    lines = random.sample(sampleFile.readlines(), 4000)

outF = open(randomData, "w")
outF.writelines(lines)
outF.close()

def convert(path):
    originalCols = StructType([\
    StructField("session_id", StringType(),False),\
    StructField("cname", StringType(),False),\
    StructField("email",StringType(),False),\
    StructField("gender",StringType(),False),\
    StructField("age",DoubleType(),False),\
    StructField("address",StringType(),False),\
    StructField("country",StringType(),True),\
    StructField("register_date",StringType(),False),\
    StructField("friend_count",DoubleType(),False),\
    StructField("lifetime",DoubleType(),False),\
    StructField("game1",DoubleType(),False),\
    StructField("game2",DoubleType(),False),\
    StructField("game3",DoubleType(),False),\
    StructField("game4",DoubleType(),False),\
    StructField("revenue",DoubleType(),False),\
    StructField("paid_customer",StringType(),False)])
    data = spark.read.option("header","false").schema(originalCols).csv(path)
    data.createOrReplaceTempView("gaming")
    # YOUR CODE HERE
    sql_str = "SELECT CASE WHEN gender='male' THEN CAST(1 AS DOUBLE) ELSE CAST(0 AS DOUBLE) END AS gender, age, country, CAST(friend_count AS DOUBLE), CAST(lifetime AS DOUBLE), CAST(game1 AS DOUBLE), CAST(game2 AS DOUBLE), CAST(game3 AS DOUBLE), CAST(game4 AS DOUBLE), CASE WHEN paid_customer='yes' THEN CAST(1 AS DOUBLE) ELSE CAST(0 AS DOUBLE) END AS paid_customer FROM gaming"
    df_t = spark.sql(sql_str)
    df_t.show(5)
    return df_t

data = convert(sampleDataPath)
data.cache()
data.show()

'''convert tests'''
correctCols = StructType([\
StructField("gender",DoubleType(),False),\
StructField("age",DoubleType(),True),\
StructField("country",StringType(),True),\
StructField("friend_count",DoubleType(),True),\
StructField("lifetime",DoubleType(),True),\
StructField("game1",DoubleType(),True),\
StructField("game2",DoubleType(),True),\
StructField("game3",DoubleType(),True),\
StructField("game4",DoubleType(),True),\
StructField("paid_customer",DoubleType(),False)])

fakeData = [(0.0,1.0,"A",1.0,1.0,1.0,1.0,1.0,1.0,0.0)]

fakeDf = spark.createDataFrame(fakeData, correctCols)

assert data.dtypes == fakeDf.dtypes, "the schema was expected to be %s but it was %s" % (fakeDf.dtypes, data.dtypes)

test1 = str(data.sample(False, 0.01, seed=12345).limit(1).first())
correct1 = "Row(gender=1.0, age=20.0, country='UK', friend_count=2.0, lifetime=4.0, game1=0.0, game2=0.0, game3=0.0, game4=4.0, paid_customer=0.0)"
assert test1 == correct1, "the row was expected to be %s but it was %s" % (correct1, test1)

def indexer(df):
    # YOUR CODE HERE
    indexer = StringIndexer(inputCol="country", outputCol="country_index")
    df_i = indexer.fit(df).transform(df)
    df_i.show(5)
    return df_i

indexed = indexer(data)
indexed.show()

'''indexer tests'''
correctCols = StructType([\
StructField("gender",DoubleType(),False),\
StructField("age",DoubleType(),False),\
StructField("country",StringType(),True),\
StructField("friend_count",DoubleType(),False),\
StructField("lifetime",DoubleType(),False),\
StructField("game1",DoubleType(),False),\
StructField("game2",DoubleType(),False),\
StructField("game3",DoubleType(),False),\
StructField("game4",DoubleType(),False),\
StructField("paid_customer",DoubleType(),False),\
StructField("country_index",DoubleType(),False)])

fakeData = [(0.0,1.0,"A",1.0,1.0,1.0,1.0,1.0,1.0,0.0,0.0)]

fakeDf = spark.createDataFrame(fakeData, correctCols)

assert indexed.dtypes == fakeDf.dtypes, "the schema was expected to be %s but it was %s" % (fakeDf.dtypes, indexed.dtypes)

test2 = str(indexed.sample(False, 0.01, seed=12345).limit(1).first())
correct2 = "Row(gender=1.0, age=20.0, country='UK', friend_count=2.0, lifetime=4.0, game1=0.0, game2=0.0, game3=0.0, game4=4.0, paid_customer=0.0, country_index=1.0)"
assert test2 == correct2, "the row was expected to be %s but it was %s" % (correct2, test2)

def featureAssembler(df):
    # YOUR CODE HERE
    assembler = VectorAssembler(inputCols=["gender", "age","friend_count","lifetime","game1","game2","game3","game4","country_index"], outputCol="features")
    df_d = assembler.transform(df)
    df_d.show(5)
    return df_d

assembled = featureAssembler(indexed)
assembled.show()

'''assembler schema test'''
from pyspark.ml.linalg import *
from pyspark.ml.linalg import VectorUDT

correctCols = StructType([\
StructField("gender",DoubleType(),False),\
StructField("age",DoubleType(),False),\
StructField("country",StringType(),True),\
StructField("friend_count",DoubleType(),False),\
StructField("lifetime",DoubleType(),False),\
StructField("game1",DoubleType(),False),\
StructField("game2",DoubleType(),False),\
StructField("game3",DoubleType(),False),\
StructField("game4",DoubleType(),False),\
StructField("paid_customer",DoubleType(),False),\
StructField("country_index",DoubleType(),False),\
StructField("features", VectorUDT(),True)])

fakeData = [(0.0,1.0,"A",1.0,1.0,1.0,1.0,1.0,1.0,0.0,0.0,(Vectors.dense([1.0, 2.0])))]

fakeDf = spark.createDataFrame(fakeData, correctCols)

assert assembled.dtypes == fakeDf.dtypes, "the schema was expected to be %s but it was %s" % (fakeDf.dtypes, assembled.dtypes)

test3 = str(assembled.sample(False, 0.01, seed=12345).limit(1).first())
correct3 = "Row(gender=1.0, age=20.0, country='UK', friend_count=2.0, lifetime=4.0, game1=0.0, game2=0.0, game3=0.0, game4=4.0, paid_customer=0.0, country_index=1.0, features=DenseVector([1.0, 20.0, 2.0, 4.0, 0.0, 0.0, 0.0, 4.0, 1.0]))"
assert test3 == correct3, "the row was expected to be %s but it was %s" % (correct3, test3)

def scaler(df, outputColName):
    # YOUR CODE HERE

    scaler = StandardScaler(inputCol = 'features', outputCol = 'scaledFeatures', withMean = True, withStd = True).fit(df)
    df_s = scaler.transform(df)
    df_s.show(6)
    return df_s

scaled = scaler(assembled, "scaledFeatures")
scaled.show()

'''scaler schema test'''
correctCols = StructType([\
StructField("gender",DoubleType(),False),\
StructField("age",DoubleType(),False),\
StructField("country",StringType(),True),\
StructField("friend_count",DoubleType(),False),\
StructField("lifetime",DoubleType(),False),\
StructField("game1",DoubleType(),False),\
StructField("game2",DoubleType(),False),\
StructField("game3",DoubleType(),False),\
StructField("game4",DoubleType(),False),\
StructField("paid_customer",DoubleType(),False),\
StructField("country_index",DoubleType(),False),\
StructField("features", VectorUDT(),True),\
StructField("scaledFeatures", VectorUDT(),True)])

fakeData = [(0.0,1.0,"A",1.0,1.0,1.0,1.0,1.0,1.0,0.0,0.0,(Vectors.dense([1.0, 2.0])),(Vectors.dense([2.0, 0.0])))]

fakeDf = spark.createDataFrame(fakeData, correctCols)

assert scaled.dtypes == fakeDf.dtypes, "the schema was expected to be %s but it was %s" % (fakeDf.dtypes, scaled.dtypes)

test4 = str(scaled.sample(False, 0.01, seed=12345).limit(1).first())
correct4 = "Row(gender=1.0, age=20.0, country='UK', friend_count=2.0, lifetime=4.0, game1=0.0, game2=0.0, game3=0.0, game4=4.0, paid_customer=0.0, country_index=1.0, features=DenseVector([1.0, 20.0, 2.0, 4.0, 0.0, 0.0, 0.0, 4.0, 1.0]), scaledFeatures=DenseVector([0.9008, -0.6236, -0.5183, -0.6848, -0.5844, -0.6369, -0.7638, -0.3154, -0.1343]))"
assert test4 == correct4, "the row was expected to be %s but it was %s" % (correct4, test4)

def createModel(training, featuresCol, labelCol, predCol):
    """
    Create Model
    createModel creates a Logistic Regression model. When training, 5 iterations should be enough.
    """
    # YOUR CODE HERE
    
    # Ensure labelCol is DoubleType (MLlib requires this for classification)
    from pyspark.sql.functions import col
    if dict(training.dtypes)[labelCol] != 'double':
        training = training.withColumn(labelCol, col(labelCol).cast('double'))

    # Check for class balance to understand data distribution
    class_counts = training.groupBy(labelCol).count().collect()
    print(f"Training set class distribution:")
    unique_classes = set()
    class_count_dict = {}
    for row in class_counts:
        print(f"  Class {row[labelCol]}: {row['count']} samples")
        unique_classes.add(row[labelCol])
        class_count_dict[row[labelCol]] = row['count']
    
    # Handle edge case where training has severe class imbalance or single class
    if len(unique_classes) == 1:
        print("❌ ERROR: Training set contains only ONE class - cannot train a classifier!")
        print("   This typically happens with random splits that exclude minority class.")
        print("   Attempting to create a model anyway but expect poor accuracy!")
        fit_intercept = False  # Use False to avoid the fitIntercept warning
    else:
        # Check for severe class imbalance (less than 5% minority class)
        total_samples = sum(class_count_dict.values())
        min_class_ratio = min(class_count_dict.values()) / total_samples
        
        if min_class_ratio < 0.05:  # Less than 5% minority class
            print(f"⚠️  WARNING: Severe class imbalance detected (minority class: {min_class_ratio:.1%})")
            print("   This may lead to poor accuracy. Consider using stratified sampling.")
        
        fit_intercept = True  # Normal case with multiple classes
    
    # Create Logistic Regression with enhanced parameters for better handling of imbalanced data
    # Using maxIter=5 as specified in requirements
    # Enhanced regularization and threshold adjustment for imbalanced data
    lr = LogisticRegression(
        featuresCol=featuresCol,
        labelCol=labelCol,
        predictionCol=predCol,
        maxIter=5,
        regParam=0.1,  # Increased regularization to handle imbalance better
        elasticNetParam=0.0,  # L2 regularization only
        fitIntercept=fit_intercept,  # Dynamic based on class distribution
        threshold=0.5  # Standard threshold, but model will be more robust with regularization
    )

    # Fit the model
    model = lr.fit(training)

    return model

# Do not change or edit below Python lines.

# Split the dataset into training(70%) and prediction(30%) sets
splitted = scaled.randomSplit([0.7,0.3])

model = createModel(splitted[0],"scaledFeatures","paid_customer","prediction")

def predict(model, dataToPredict):
    # YOUR CODE HERE
    df_p = model.transform(dataToPredict)
    df_p.show(5)
    return df_p

# Do not edit or change below script.
predictions = predict(model, splitted[1])
correct = predictions.where("prediction == paid_customer").count()
total = predictions.count()
print((correct / total) * 100, "% predicted correctly")
predictions.show()

'''prediction correctness test'''
data = convert(randomData)
data.cache()
indexed = indexer(data)
assembled = featureAssembler(indexed)
scaled = scaler(assembled, "scaledFeatures")
splitted = scaled.randomSplit([0.7,0.3])
model = createModel(splitted[0],"scaledFeatures","paid_customer","prediction")
predictions = predict(model, splitted[1])
correct = predictions.where("prediction == paid_customer").count()
total = predictions.count()
answer = (correct / total) * 100
print(answer, "% predicted correctly")
assert answer >= 50.0, "Error less than 50% predicted correctly."
assert answer >= 70.0, "Error less than 70% predicted correctly."
assert answer >= 85.0, "Error less than 85% predicted correctly."