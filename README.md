# simple-data-ingestion

This project performs a simple ETL pipeline that:
1. Extract data from Faker API.
2. Transforms the data (masks sensitive fields defined in config.py).
3. Loads the data into BigQuer that will later be accesed by Looker Studio.

and creates BigQuery views from Airflow that answer to the following queries:

1. Which percentage of users live in Germany and use Gmail as an email
provider?
2. Which are the top three countries in our database that use Gmail as an email
provider?
3. How many people over 60 years use Gmail as an email provider?

In the [first section](https://github.com/StevenSalazarM/simple-data-ingestion?tab=readme-ov-file#1-etl-and-infrastructure), the decision of the technologies and their implementation will be presented.

In the [second section](https://github.com/StevenSalazarM/simple-data-ingestion?tab=readme-ov-file#1-etl-and-infrastructure), the organization of the project in terms of files, folders and how-to-use will be presented.

In the third section, the SQL queries that answer to the requested information will be presented (under the docs folder, there is also a BI-report pdf).

And in the final section, some additional considerations will be discussed (data quality, third party retry policy, scalability, testing, flex template).

## 1. ETL and infrastructure

The ETL is a simple extract, transform, load workload. The technological stack choosen for this use case contains Dataflow as a processing tool that can easily scale and BigQuery as a sink for our processed data. Furthermore, Cloud Storage was used to store raw information that may be used in future use cases.

### 1.1 ETL - The Architecture

The following architect is the one that was implemented, since this a simple project, the tools were deployed in the public configuration and no private comunicaion (or VPC - SC) was enabled.

![Architecture ETL](https://github.com/StevenSalazarM/simple-data-ingestion/blob/main/docs/simple-data-ingestion-architecture.png)

The components that appeared disabled are still under development and will be completed in the next weeks/months. For the first basic ingestion pipeline, only the basic tools were implemented:

1. Dataflow ETL that extracts data from a public API
2. Datamarts creation through Airflow Operators
3. Reporting on Looker Studio
4. BigQuery and Cloud Storage for the saving of the processed data
5. Dataflow Flex template creation to allow an easy execution of the pipeline from Airflow

Furthermore, it is also under development the creation of the infrastructure through **Terraform**.

In the following subsections, the reasoning behind each choice will be explained.

### 1.2 Dataflow - Apache Beam

When working with Big Data technologies, it is crucial to develop a pipeline that can handle huge amount of data and can scale if needed. One of the main tools that Google proposes is Dataflow, Dataflow is an executor system that runs Apache Beam pipelines. The main advatanges of Dataflow are that it is a **serverless service**, it can easily **scale** (no needed configuration), it can **optimize the shuffle operations** by handling them in Google backend with the Shuffle service enabled, and it **works with Apache Beam**. 

Apache Beam is a programming model that unifies the development of batch an streaming pipelines by minimizing the differences in the two approaches. It written in Java, Python and Go and was developed by Google. Even though, Apache Beam supports those languanges, it is languange agnostic, which means that modules developed in Java can be easily called from a Python pipeline and vice versa. Apache Beam is completly flexible for the execution of the pipeline since it relies on something called 'Runner' that will be responsable of executing the code, providing the resources, orchestrating the workflow of the pipeline and more.

In the last years, Google has invested also on the possibility of making Dataflow low code for people that do not code or have a programming background by providing something called 'Flex Templates'. The Flex templates are allowing to develop pipelines and reusing them easily for the most common use cases (e.g. read from S3, read from GCS, read from pub sub & insert to BQ, etc.). **Flex Templates facilitates the execution of the pipeline by making it completly parametric**.

The following pipeline represents the current pipeline that is executed when the ETL process starts.

![ETL pipeline](https://github.com/StevenSalazarM/simple-data-ingestion/blob/main/docs/etl-dataflow.png)

some considerations:
- 3 and 4 steps run in parallel.
- 3.2 and 4.2 are optinal but provide the possibility of recovery on failure and expend to future use cases.
- in case of failure in the step 2, the pipeline retries to reperform the HTTP request up to a maximum configured. No failure management was added in step 3. One future possibility could be to cover all the steps and introduce a logging table that shows the most common failures message (or traceback) or the success of the run and finally an alerting system could also be implemented for that table or for a pub/sub queue.
- Basic unit test was included for the DoFn classes, ideally the unit test should be insolated but for the purpose of this project no mock state was considered and the unit test interact with FakerAPI.

### 1.3 BigQuery

BigQuery is another **serverless** service provided by Google, it is a fully managed Datawarehouse that fits on both enterprise and non enterprise use cases thanks to its **model cost**. BigQuery can scale easily depending on the query complexity and provides multiple optimizations to store the data (and make them faster to be accessed) like **partitioning**, **clustering**, furthermore, BigQuery provides also the **possibility to set policy rules for row and column access of specific tables** that is integrated with IAM.

The main reason of BigQuery for this project are that:
1. Dataflow can easily write to BigQuery which makes development faster and reduces the gap between production and development architecture environment.
2. BigQuery integrates with Looker Studio, which allows to create easily dashboards that are updated in real time.
3. Airflow can easily interact with BigQuery through the BigQuery Operators, and if it is hosted in Cloud Composer, no configuration for the connection is required.

Once the ETL pipeline completes, a persons table is created in TRUCATE mode. From the Airflow environment, 5 views are created in BigQuery reporting dataset.

![BigQuery Reporting](https://github.com/StevenSalazarM/simple-data-ingestion/blob/main/docs/bigquery-reporting.png)

### 1.4 Looker Studio

Looker Studio is a **free** tool that Google provides to create basic dashboards. It integrates with multiple data sources, and one of them is BigQuery. Looker Studio does not process data but forwards the queries to BigQuery, which makes it **completly user-friendly and fast to operate**. Furthermore, data is accessed in **real time**.

The entire report generated for the requested queries is present at [Report](https://github.com/StevenSalazarM/simple-data-ingestion/blob/main/docs/BI-report.pdf). Here is an extraction of some statistics related to the distribution of countries in the dataset of 10K people:

![Country Distribution](https://github.com/StevenSalazarM/simple-data-ingestion/blob/main/docs/country-distribution.png)

### 1.5 Cloud Storage

As a good practice in the data field, it is often suggested to include a data lake in your pipelines regarless of the data warehouse architecture that you are building. The main point of having a data lake is to have a safe place were your historic data will be stored which **can turn to be useful for future ML or reporting use cases**. Furthermore, it is also recommended to save the data in multiple layers (e.g. Bronze, Silver, Gold.). Where Bronze is the point in which the data is close to how it was ingested (zero to low processing), Silver or Gold where you have already performed some processing or data quality steps.

Google Cloud Storage is the **serverless** object storage service offered by Google, it provides multiple options to cover a huge number of use cases (e.g. **IAM access, object versioning, lock prevention, retention policy, object lifecycle, different price based on access**).

As mentioned in the Dataflow subsection, two folders were created for the data lake space.


### 1.6 Cloud Composer - Airflow

Airflow is one of the most famous data orchestration tool that has been getting popularity recently and Google has been investing on **optimizing its use and faciliting its deployment on GCP**. Cloud Composer is the technology of GCP that allows to create an Airflow environment, in the latest version (three at the time of this project), [a few clicks](https://cloud.google.com/composer/docs/composer-3/run-apache-airflow-dag) are needed to create an Airflow environment since the networking configuration has been optimized.

For this use case, Airflow allows to **schedule or trigger** the execution of the Dataflow job, and once the job has been completed, it will create the BigQuery views if they do not exist already. 

And the following DAG was created in Airflow. It executes the Dataflow job through a flex template operator and then creates the 5 views.

![Airflow DAG](https://github.com/StevenSalazarM/simple-data-ingestion/blob/main/docs/airflow-dag.png)

some considerations:

- Airflow is a powerful orchestration tool, more tasks could easily be added but for the simplicity of the project they were not included (e.g. verification of the dataset existance, person table existance/correct upload, bucket objects existance)
- It would be interesting to create a CI/CD workflow for the deployment of the DAGs
- No test was included for Airflow, hopefully, in future some testing section will be added

## 2. Organization of the project

- [DAGs/](https://github.com/StevenSalazarM/simple-data-ingestion/tree/main/DAGs): this directory contains a config folder useful for the DAGs and python file with the DAT presented above.

- [configs/](https://github.com/StevenSalazarM/simple-data-ingestion/tree/main/configs): contains a config.py file (ideally it could be migrated to a tml file), pipeline_options.py for the specific configuration of the Dataflow pipeline.

- [docs/](https://github.com/StevenSalazarM/simple-data-ingestion/tree/main/docs): folder with all the images and a report pdf produced from Looker Studio.

- [tests/](https://github.com/StevenSalazarM/simple-data-ingestion/tree/main/tests): directory holding the testing (unit and in future also integration).

- [transforms/](https://github.com/StevenSalazarM/simple-data-ingestion/tree/main/transforms): directory that includes the DoFns files that will be called from main.py (Ingest and Generalize data)

- [utils/](https://github.com/StevenSalazarM/simple-data-ingestion/tree/main/utils): folder that will include eventual functions that are generic and not depending on this specific project.

- [Dockerfile](https://github.com/StevenSalazarM/simple-data-ingestion/blob/main/Dockerfile): docker file useful for the creation of the Dataflow Flex template.

- [main.py](https://github.com/StevenSalazarM/simple-data-ingestion/blob/main/main.py): main file containing the run call for the Pipeline in Dataflow.

- [metada.json](https://github.com/StevenSalazarM/simple-data-ingestion/blob/main/metadata.json): metadata used for the generation of the flex template for dataflow (inclues possible parameters to pass to the job).

- [requirements.txt](https://github.com/StevenSalazarM/simple-data-ingestion/blob/main/requirements.txt): requirements file to install from a python virtual environemnt (tested with python 3.11).

- [setup.py](https://github.com/StevenSalazarM/simple-data-ingestion/blob/main/setup.py): setup file for the datflow job, whevener python files are referred as modules, the setup file must be passed or a custom container should be used for the workers.

### 2.1 How to use:

To use the code, you will need a clean python environment (e.g. a virtual environment) with at least python 3.10 (this was tested with python 3.11).

Since BigQuery is used also gcloud must be installed and configured in the path.

```

python -m venv /path/to/new/virtual/environment

# if Windows
source  /path/to/new/virtual/environment/Scripts/activate

# if MacOS or Linux
source /path/to/new/virtual/environment/bin/activate

pip install -r requirements.txt # make sure that you are in the root directory of the project

gcloud auth application-default login

# local execution performs only 5 HTTP requests of 1 length, however gcloud must have access to a BigQuery Project with the required permissions to run jobs and create tables.
python main.py --run_mode=local 

# cloud execution is the default but if needed, you can specificy it in the params. Launches a dataflow job that performs 10 requests of 1K length data size.
python main.py --run_mode=cloud 
```

in case of any trouble please feel free to open an issue.

## 3. SQL queries and assumptions

This section will answer to the following questions 

1. Which percentage of users live in Germany and use Gmail as an email
provider?
2. Which are the top three countries in our database that use Gmail as an email
provider?
3. How many people over 60 years use Gmail as an email provider?

but to answer, some assumptions/considerations had to be done before.

For the query 1), apart from the people that live in germany, it may be interesting to find also the distribution of the people in terms of country. Therefore an extra view was created.

For the query 2), some countries have the same rank position since they have the same number of gmail users, therefore a **dense rank** method was used and all the ranks <=3 were selected. Once grouped by rank, the values are appended in an Array.

For the query 3), again, it may be interesting to retreive first the distribution of the age in the data and from them use only the ones that are over 60 years old

### Query 1:
```
    WITH german_people AS (
        SELECT email_domain
        FROM `steven-case-studies.simple_ingest_ds.persons`
        WHERE LOWER(location) = 'germany'
    )

    SELECT  email_domain, 
            count(email_domain) as email_counter,
            ROUND((count(email_domain)* 100.0) / (SELECT COUNT(*) FROM german_people),2) AS email_percentage
    FROM german_people
    GROUP bY email_domain
    ORDER BY email_percentage DESC
```

### Additional Query for country distribution
```
    SELECT  LOWER(location) as location,
            COUNT(*) as people_in_location
    FROM `steven-case-studies.simple_ingest_ds.persons`
    GROUP BY location
    ORDER BY people_in_location DESC
```
### Query 2:
```
    WITH gmail_countries AS (
    SELECT
        location,
        COUNT(1) AS gmail_users,
        DENSE_RANK() OVER (ORDER BY COUNT(1) DESC) AS rank,
    FROM `steven-case-studies.simple_ingest_ds.persons`
    WHERE email_domain = 'gmail'
    GROUP BY location
    )

    SELECT  ARRAY_AGG(location) as locations,
            gmail_users AS gmail_users_counter
    FROM gmail_countries 
    WHERE rank <= 3
    GROUP BY gmail_users
    ORDER BY gmail_users_counter DESC
```

### Query 3:
```
    WITH people_over_60 AS (
        SELECT 
            email_domain,
            age_group,
            CAST(SUBSTR(SPLIT(age_group, '-')[OFFSET(0)], 2) AS INT64) AS age
        FROM `steven-case-studies.simple_ingest_ds.persons`
        WHERE CAST(SUBSTR(SPLIT(age_group, '-')[OFFSET(0)], 2) AS INT64) >= 60
    )

    SELECT  email_domain,
            COUNT(*) as n_people
    FROM people_over_60 
    GROUP BY email_domain 
    ORDER BY n_people DESC

```

### Additional query for age distribution
```
    WITH people_start_age_group AS (
        SELECT 
            email_domain,
            SUBSTR(SPLIT(age_group, '-')[OFFSET(0)],2) AS age
        FROM `steven-case-studies.simple_ingest_ds.persons`
    )

    SELECT CAST(age AS INT64) AS starting_age,
            COUNT(*) as n_people 
    FROM people_start_age_group 
    GROUP BY age 
    ORDER BY starting_age DESC
```

In the third section, the SQL queries that answer to the requested information will be presented (under the docs folder, there is also a BI-report pdf).

And in the final section, some additional considerations will be discussed (data quality, third party retry policy, scalability, testing, flex template).