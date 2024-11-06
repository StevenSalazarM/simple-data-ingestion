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

In the second section, the decision of the technologies and their implementation will be presented.

In the third section, the organization of the project in terms of files, folders and how-to-use will be presented.

In the fourth section, the SQL queries that answer to the requested information will be presented (under the docs folder, there is also a BI-report pdf).

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

### Dataflow - Apache Beam

When working with Big Data technologies, it is crucial to develop a pipeline that can handle huge amount of data and can scale if needed. One of the main tools that Google proposes is Dataflow, Dataflow is an executor system that runs Apache Beam pipelines. The main advatanges of Dataflow are that it is a **serverless service**, it can easily **scale** (no needed configuration), it can **optimize the shuffle operations** by handling them in Google backend with the Shuffle service enabled, and it **works with Apache Beam**. 

Apache Beam is a programming model that unifies the development of batch an streaming pipelines by minimizing the differences in the two approaches. It written in Java, Python and Go and was developed by Google. Even though, Apache Beam supports those languanges, it is languange agnostic, which means that modules developed in Java can be easily called from a Python pipeline and vice versa. Apache Beam is completly flexible for the execution of the pipeline since it relies on something called 'Runner' that will be responsable of executing the code, providing the resources, orchestrating the workflow of the pipeline and more.

In the last years, Google has invested also on the possibility of making Dataflow low code for people that do not code or have a programming background by providing something called 'Flex Templates'. The Flex templates are allowing to develop pipelines and reusing them easily for the most common use cases (e.g. read from S3, read from GCS, read from pub sub & insert to BQ, etc.). **Flex Templates facilitates the execution of the pipeline by making it completly parametric**.

The following pipeline represents the current pipeline that is executed when the ETL process starts.

![ETL pipeline](https://github.com/StevenSalazarM/simple-data-ingestion/blob/main/docs/etl-dataflow.png)

some considerations:
- 3 and 4 steps run in parallel.
- 3.2 and 4.2 are optinal but provide the possibility of recovery on failure and expend to future use cases.
- in case of failure in the step 2, the pipeline retries to reperform the HTTP request up to a maximum configured. No failure management was added in step 3. One future possibility could be to cover all the steps and introduce a logging table that shows the most common failures message (or traceback) or the success of the run and finally an alerting system could also be implemented for that table or for a pub/sub queue.

### BigQuery

BigQuery is another **serverless** service provided by Google, it is a fully managed Datawarehouse that fits on both enterprise and non enterprise use cases thanks to its **model cost**. BigQuery can scale easily depending on the query complexity and provides multiple optimizations to store the data (and make them faster to be accessed) like **partitioning**, **clustering**, furthermore, BigQuery provides also the **possibility to set policy rules for row and column access of specific tables** that is integrated with IAM.

The main reason of BigQuery for this project are that:
1. Dataflow can easily write to BigQuery which makes development faster and reduces the gap between production and development architecture environment.
2. BigQuery integrates with Looker Studio, which allows to create easily dashboards that are updated in real time.
3. Airflow can easily interact with BigQuery through the BigQuery Operators, and if it is hosted in Cloud Composer, no configuration for the connection is required.

Once the ETL pipeline completes, a persons table is created in TRUCATE mode. From the Airflow environment, 5 views are created in BigQuery reporting dataset.

![BigQuery Reporting](https://github.com/StevenSalazarM/simple-data-ingestion/blob/main/docs/bigquery-reporting.png)

### Looker Studio

Looker Studio is a **free** tool that Google provides to create basic dashboards. It integrates with multiple data sources, and one of them is BigQuery. Looker Studio does not process data but forwards the queries to BigQuery, which makes it **completly user-friendly and fast to operate**. Furthermore, data is accessed in **real time**.

The entire report generated for the requested queries is present at [Report](https://github.com/StevenSalazarM/simple-data-ingestion/blob/main/docs/BI-report.pdf). Here is an extraction of some statistics related to the distribution of countries in the dataset of 10K people:

![Country Distribution](https://github.com/StevenSalazarM/simple-data-ingestion/blob/main/docs/country-distribution.png)

### Cloud Storage

As a good practice in the data field, it is often suggested to include a data lake in your pipelines regarless of the data warehouse architecture that you are building. The main point of having a data lake is to have a safe place were your historic data will be stored which **can turn to be useful for future ML or reporting use cases**. Furthermore, it is also recommended to save the data in multiple layers (e.g. Bronze, Silver, Gold.). Where Bronze is the point in which the data is close to how it was ingested (zero to low processing), Silver or Gold where you have already performed some processing or data quality steps.

Google Cloud Storage is the **serverless** object storage service offered by Google, it provides multiple options to cover a huge number of use cases (e.g. **IAM access, object versioning, lock prevention, retention policy, object lifecycle, different price based on access**).

As mentioned in the Dataflow subsection, two folders were created for the data lake space.


### Cloud Composer - Airflow

Airflow is one of the most famous data orchestration tool that has been getting popularity recently and Google has been investing on **optimizing its use and faciliting its deployment on GCP**. Cloud Composer is the technology of GCP that allows to create an Airflow environment, in the latest version (three at the time of this project), [a few clicks](https://cloud.google.com/composer/docs/composer-3/run-apache-airflow-dag) are needed to create an Airflow environment since the networking configuration has been optimized.

For this use case, Airflow allows to **schedule or trigger** the execution of the Dataflow job, and once the job has been completed, it will create the BigQuery views if they do not exist already. 

And the following DAG was created in Airflow. It executes the Dataflow job through a flex template operator and then creates the 5 views.

![Airflow DAG](https://github.com/StevenSalazarM/simple-data-ingestion/blob/main/docs/airflow-dag.png)

some considerations:

- Airflow is a powerful orchestration tool, more tasks could easily be added but for the simplicity of the project they were not included (e.g. verification of the dataset existance, person table existance/correct upload, bucket objects existance)