# API config params
birthday_start = "1900-01-01"
expected_responses = 10000
quantity = 1000
api_endpoint = "https://fakerapi.it/api/v2/persons"

# ingest pipeline configuration
request_max_retry = 2
mask_encoder = "****"
valid_fields_api = ["address", "birthday", "email"]
private_fiels = ["firstname", "lastname", "phone", "email", "address"]
location_field = "country"

# Dataflow pipeline params
runner_type='DataflowRunner'
gcp_project='steven-case-studies'
gcp_region='europe-west9'
temp_bucket_folder='gs://dataflow-tmp-bucket-steven/tmp/'
save_main_session=True
stagging_bucket_folder='gs://dataflow-tmp-bucket-steven/stag/'

# Sink config
from datetime import datetime
folder_datime = datetime.now().strftime('%Y_%m_%d_%H_%M')
gcp_data_lake = f"gs://dataflow-data-lake-steven/{folder_datime}"
bq_dataset = 'simple_ingest_ds'
bq_table = 'persons'
bq_table_schema = {'fields': [
                                {"name": "uuid", "type": "STRING", "mode": "NULLABLE"},
                                {"name": "location", "type": "STRING", "mode": "NULLABLE"},
                                {"name": "age_group", "type": "STRING", "mode": "NULLABLE"},
                                {"name": "email_domain", "type": "STRING", "mode": "NULLABLE"}
                            ]
                   }