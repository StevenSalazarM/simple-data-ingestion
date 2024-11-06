import datetime

from airflow import models
from airflow.operators import bash
from airflow.providers.google.cloud.operators.bigquery import BigQueryCreateEmptyTableOperator, BigQueryInsertJobOperator
from airflow.providers.google.cloud.operators.dataflow import DataflowStartFlexTemplateOperator
from config.reporting_config import *

# If you are running Airflow in more than one time zone
# see https://airflow.apache.org/docs/apache-airflow/stable/timezone.html
# for best practices
YESTERDAY = datetime.datetime.now() - datetime.timedelta(days=1)

default_args = {
    "owner": "Simple Data Ingestion Orchestration",
    "depends_on_past": False,
    "email": [""],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 3,
    "retry_delay": datetime.timedelta(minutes=5),
    "start_date": YESTERDAY,
}
df_sufix_name = datetime.datetime.now().strftime("%Y-%m-%d")

with models.DAG(
    "reporting_views",
    catchup=False,
    default_args=default_args,
    schedule_interval=datetime.timedelta(days=1),
) as dag:
    
    # Dataflow ETL job
    dataflow_etl_pipeline = DataflowStartFlexTemplateOperator(
    task_id="dataflow_etl_pipeline",
    project_id=PROJECT_ID,
    body={
         "launchParameter": {
             "jobName": f"etl-fakerapi-{df_sufix_name}",
             "containerSpecGcsPath": FLEX_TEMPLATE_PATH,
             "parameters": {
                 "batch_size": BATCH_SIZE,
                 "requested_data": REQUESTED_DATA,
             }
        }
    },
    location=DATAFLOW_REGION,
    append_job_name=False,
    wait_until_finished=True,
    )
    
    # create country stats view
    create_country_stats_view = BigQueryCreateEmptyTableOperator(
        task_id="create_country_stats_view",
        dataset_id=DATASET_OUTPUT,
        table_id=TABLE_OUTPUT_COUNTRY_STATS,
        view={
            "query": country_stats_view_sql,
            "useLegacySql": False,
        },
        if_exists="ignore"
    )
    
    # create german people that use gmail view
    create_germany_email = BigQueryCreateEmptyTableOperator(
        task_id="create_germany_email",
        dataset_id=DATASET_OUTPUT,
        table_id=TABLE_OUTPUT_QUERY1,
        view={
            "query": germany_email_distribution_sql,
            "useLegacySql": False,
        },
        if_exists="ignore"
    )

    # create top three gmail countries view
    create_top_3_gmail = BigQueryCreateEmptyTableOperator(
        task_id="create_top_3_gmail",
        dataset_id=DATASET_OUTPUT,
        table_id=TABLE_OUTPUT_QUERY2,
        view={
            "query": three_top_countries_gmail_sql,
            "useLegacySql": False,
        },
        if_exists="ignore"
    )

    # create age distribution view
    create_age_stats_view = BigQueryCreateEmptyTableOperator(
        task_id="create_age_stats_view",
        dataset_id=DATASET_OUTPUT,
        table_id=TABLE_OUTPUT_AGE_STATS,
        view={
            "query": age_distribution_sql,
            "useLegacySql": False,
        },
        if_exists="ignore"
    )

    # create people over 60 that use gmail view
    create_over_60_gmail = BigQueryCreateEmptyTableOperator(
        task_id="create_over_60_gmail",
        dataset_id=DATASET_OUTPUT,
        table_id=TABLE_OUTPUT_QUERY3,
        view={
            "query": over_60_email_preferences_sql,
            "useLegacySql": False,
        },
        if_exists="ignore"
    )

    dataflow_etl_pipeline >> [create_country_stats_view, create_germany_email, create_top_3_gmail, create_age_stats_view, create_over_60_gmail]