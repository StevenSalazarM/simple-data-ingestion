PROJECT_ID = "steven-case-studies"
DATASET_INPUT = "simple_ingest_ds"
TABLE_INPUT = "persons"

DATASET_OUTPUT = "reporting"
TABLE_OUTPUT_COUNTRY_STATS = "country_stats"
TABLE_OUTPUT_QUERY1 = "german_email_distribution"
TABLE_OUTPUT_QUERY2 = "three_top_gmail_countries"
TABLE_OUTPUT_AGE_STATS = "age_stats"
TABLE_OUTPUT_QUERY3 = "over_60_email_distribution"

# Dataflow configs
FLEX_TEMPLATE_PATH = "gs://dataflow-flex-template-steven/simple-etl-dataflow.json"
DATAFLOW_REGION = "europe-west9"
BATCH_SIZE="1000"
REQUESTED_DATA="10000"

country_stats_view_sql = f"""
                    SELECT LOWER(location) as location, COUNT(*) as people_in_location

                    FROM `{PROJECT_ID}.{DATASET_INPUT}.{TABLE_INPUT}`

                    GROUP BY location

                    ORDER BY people_in_location DESC
                    """

germany_email_distribution_sql = f"""
                    WITH german_people AS (
                    SELECT email_domain
                    FROM `{PROJECT_ID}.{DATASET_INPUT}.{TABLE_INPUT}`
                    WHERE LOWER(location) = 'germany'
                    )

                    SELECT email_domain, count(email_domain) as email_counter, ROUND((count(email_domain)* 100.0) / (SELECT COUNT(*) FROM german_people),2) AS email_percentage
                    FROM german_people
                    group by email_domain
                    ORDER BY email_percentage DESC
                    """

three_top_countries_gmail_sql = f"""
                    WITH gmail_countries AS (
                    SELECT
                        location,
                        COUNT(1) AS gmail_users,
                        DENSE_RANK() OVER (ORDER BY COUNT(1) DESC) AS rank,
                    FROM `{PROJECT_ID}.{DATASET_INPUT}.{TABLE_INPUT}`
                    WHERE
                        email_domain = 'gmail'
                    GROUP BY
                        location
                    )

                    SELECT ARRAY_AGG(location) as locations,
                        gmail_users AS gmail_users_counter,
                        ARRAY_AGG(distinct rank) as rank
                    FROM gmail_countries 
                    WHERE rank <= 3
                    GROUP BY gmail_users
                    ORDER BY gmail_users_counter DESC
                    """

age_distribution_sql = f"""
                    WITH people_start_age_group AS (
                        SELECT 
                            email_domain,
                            SUBSTR(SPLIT(age_group, '-')[OFFSET(0)],2) AS age
                        FROM `{PROJECT_ID}.{DATASET_INPUT}.{TABLE_INPUT}`
                    )

                    SELECT CAST(age AS INT64) AS starting_age,
                            COUNT(*) as n_people 
                    FROM people_start_age_group 
                    GROUP BY age 
                    ORDER BY starting_age DESC
                    """

over_60_email_preferences_sql = f"""
                    WITH people_over_60 AS (
                        SELECT 
                            email_domain,
                            age_group,
                            CAST(SUBSTR(SPLIT(age_group, '-')[OFFSET(0)], 2) AS INT64) AS age
                        FROM `{PROJECT_ID}.{DATASET_INPUT}.{TABLE_INPUT}`
                        WHERE CAST(SUBSTR(SPLIT(age_group, '-')[OFFSET(0)], 2) AS INT64) >= 60
                    )

                    SELECT email_domain,
                            COUNT(*) as n_people
                    FROM people_over_60 
                    GROUP BY email_domain 
                    ORDER BY n_people DESC
                    """