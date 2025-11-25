from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, window, avg, sum as spark_sum, count, to_timestamp
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType
from pyspark.ml import PipelineModel

spark = SparkSession.builder.appName("SupplyChainStreaming").getOrCreate()
spark.sparkContext.setLogLevel("WARN")

schema = StructType([
    StructField("Benefit per order", DoubleType()), StructField("Sales per customer", DoubleType()),
    StructField("Order Item Quantity", IntegerType()), StructField("Order Item Product Price", DoubleType()),
    StructField("Order Item Discount", DoubleType()), StructField("Order Item Total", DoubleType()),
    StructField("Order Profit Per Order", DoubleType()), StructField("distance", DoubleType()),
    StructField("Late_delivery_risk", IntegerType()), StructField("Order Country", StringType()),
    StructField("Type", StringType()), StructField("Order Region", StringType()),
    StructField("Shipping Mode", StringType()), StructField("Department Name", StringType()),
    StructField("Category Name", StringType()), StructField("timestamp", StringType())
])

model = PipelineModel.load("/src/models/gbt_pipeline_model")

postgres_properties = {"user": "user", "password": "user", "driver": "org.postgresql.Driver"}
postgres_url = "jdbc:postgresql://postgres:5432/dataco"
mongodb_uri = "mongodb://mongodb:27017/dataco.predictions"

parsed_stream = spark.readStream.format("socket").option("host", "bridge").option("port", 9999).load() \
    .select(from_json(col("value"), schema).alias("data")).select("data.*") \
    .withColumn("event_time", to_timestamp(col("timestamp")))
def process_batch(batch_df, batch_id):
    if batch_df.count() == 0:
        return

    # ===== APPLY PIPELINE MODEL (with original column names) =====
    predictions_df = model.transform(batch_df)

    # ===== BUILD RESULTS DF (rename AFTER transformation) =====
    results_df = predictions_df.select(
        col("Benefit per order").alias("benefit_per_order"),
        col("Sales per customer").alias("sales_per_customer"),
        col("Order Item Quantity").alias("order_item_quantity"),
        col("Order Item Product Price").alias("order_item_product_price"),
        col("Order Item Discount").alias("order_item_discount"),
        col("Order Item Total").alias("order_item_total"),
        col("Order Profit Per Order").alias("order_profit_per_order"),
        col("distance"),
        col("Category Name").alias("category_name"),
        col("Order Region").alias("order_region"),
        col("Shipping Mode").alias("shipping_mode"),
        col("Department Name").alias("department_name"),
        col("Late_delivery_risk").alias("actual_late_delivery"),
        col("prediction").alias("predicted_late_delivery"),
        col("event_time")
    )

    # ===== WRITE TO POSTGRES =====
    results_df.write.jdbc(
        url=postgres_url,
        table="streaming_predictions",
        mode="append",
        properties=postgres_properties
    )

    # ===== AGGREGATE FOR MONGO =====
    aggregated_df = results_df.groupBy(
        window(col("event_time"), "1 minute"),
        col("order_region"),
        col("category_name")
    ).agg(
        count("*").alias("total_orders"),
        avg("sales_per_customer").alias("avg_sales"),
        spark_sum("sales_per_customer").alias("total_sales"),
        avg("benefit_per_order").alias("avg_profit"),
        spark_sum("benefit_per_order").alias("total_profit"),
        spark_sum("predicted_late_delivery").alias("predicted_late_deliveries"),
        avg("distance").alias("avg_distance")
    )

    # Convert to pandas to split window
    agg_pandas = aggregated_df.toPandas()
    agg_pandas['window_start'] = agg_pandas['window'].apply(lambda x: x['start'])
    agg_pandas['window_end'] = agg_pandas['window'].apply(lambda x: x['end'])

    spark.createDataFrame(agg_pandas.drop('window', axis=1)).write.format("mongodb").mode("append") \
        .option("spark.mongodb.write.connection.uri", mongodb_uri).save()

    print(f"Batch {batch_id}: {results_df.count()} predictions saved")
parsed_stream.writeStream.foreachBatch(process_batch).trigger(processingTime='10 seconds').start().awaitTermination()
