# API config params
BIRTHDAY_START = "1900-01-01"
EXPECTED_RESPONSE = 10000
QUANTITY = 1000
API_ENDPOINT = "https://fakerapi.it/api/v2/persons"

# ingest pipeline configuration
MAX_REQUEST_RETRY = 2
MASK_ENCODER = "****"
VALID_FIELDS_API = ["address", "birthday", "email"]
PRIVATE_FIELDS = ["firstname", "lastname", "phone", "email", "address"]
LOCATION_FIELD = "country"

# Dataflow pipeline params
RUNNER_TYPE='DataflowRunner'
GCP_PROJECT_ID='steven-case-studies'
GCP_REGION='europe-west9'
TEMP_BKT_FOLDER='gs://dataflow-tmp-bucket-steven/tmp/'
SAVE_MAIN_SESSION=True
STAGGING_BKT_FOLDER='gs://dataflow-tmp-bucket-steven/stag/'

# Sink config
from datetime import datetime
folder_datime = datetime.now().strftime('%Y_%m_%d_%H_%M')
GCP_DATA_LAKE = f"gs://dataflow-data-lake-steven/{folder_datime}"
BQ_DATASET = 'simple_ingest_ds'
BQ_TABLE = 'persons'
BQ_TABLE_SCHEMA = {'fields': [
                                {"name": "uuid", "type": "STRING", "mode": "NULLABLE"},
                                {"name": "location", "type": "STRING", "mode": "NULLABLE"},
                                {"name": "age_group", "type": "STRING", "mode": "NULLABLE"},
                                {"name": "email_domain", "type": "STRING", "mode": "NULLABLE"}
                            ]
                   }