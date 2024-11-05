import datetime

from airflow import models
from airflow.operators import bash
from airflow.providers.google.cloud.operators.bigquery import BigQueryCreateEmptyTableOperator, BigQueryInsertJobOperator
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

with models.DAG(
    "reporting_views",
    catchup=False,
    default_args=default_args,
    schedule_interval=datetime.timedelta(days=1),
) as dag:
    
    # create country stats view
    create_country_stats_view = BigQueryCreateEmptyTableOperator(
        task_id="create_country_stats_view",
        dataset_id="reporting",
        table_id=TABLE_OUTPUT_COUNTRY_STATS,
        view={
            "query": country_stats_view_sql,
            "useLegacySql": False,
        },
        if_exists="ignore"
    )
    
    create_germany_email = BigQueryCreateEmptyTableOperator(
        task_id="create_germany_email",
        dataset_id="reporting",
        table_id=TABLE_OUTPUT_QUERY1,
        view={
            "query": germany_email_distribution_sql,
            "useLegacySql": False,
        },
        if_exists="ignore"
    )

    create_top_3_gmail = BigQueryCreateEmptyTableOperator(
        task_id="create_top_3_gmail",
        dataset_id="reporting",
        table_id=TABLE_OUTPUT_QUERY2,
        view={
            "query": three_top_countries_gmail_sql,
            "useLegacySql": False,
        },
        if_exists="ignore"
    )

    create_age_stats_view = BigQueryCreateEmptyTableOperator(
        task_id="create_age_stats_view",
        dataset_id="reporting",
        table_id=TABLE_OUTPUT_AGE_STATS,
        view={
            "query": age_distribution_sql,
            "useLegacySql": False,
        },
        if_exists="ignore"
    )

    create_over_60_gmail = BigQueryCreateEmptyTableOperator(
        task_id="create_over_60_gmail",
        dataset_id="reporting",
        table_id=TABLE_OUTPUT_QUERY3,
        view={
            "query": over_60_email_preferences_sql,
            "useLegacySql": False,
        },
        if_exists="ignore"
    )

    [create_country_stats_view, create_germany_email, create_top_3_gmail, create_age_stats_view, create_over_60_gmail]