import apache_beam as beam
import logging
from configs.config import *
from configs.pipeline_options import pipeline_options
from transforms.dofns import Ingest, Generalize
from apache_beam.io.gcp.bigquery import WriteToBigQuery
from apache_beam.io.textio import WriteToText
from utils.utils import mask_fields

def run():
    
    # Generate the seeds for the HTTP requests (e.g. [1, 1001, 2001, etc.]). Max quantity in the batch response is 1k.
    seeds = [i*quantity+1 for i in range(expected_responses//quantity)]
    with beam.Pipeline(options=pipeline_options) as p:

        # Create a PCollection of seed values for 10 batches of 1000 records each
        seed_pcol = p | 'Initiate Seeds PCollection' >> beam.Create(seeds)
        
        # Fetch data for each seed in parallel and yield each element (person) into a new pcollection
        people_pcol =  (seed_pcol | 'Ingest Data and create People PCollection' >> beam.ParDo(Ingest()) 
                        )
        
        # optinally save the data into a GCS bucket (in case other use cases may need it)
        (people_pcol | "Mask user-identicable fields" >> beam.Map(mask_fields)
                    | "Write ingested data" >> WriteToText(f"{gcp_data_lake}/ingested_data/")
        )
        # Mask, Anonymize and prepare info
        generalized_pcol =  (people_pcol | 'Mask, Anonymize and prepare' >> beam.ParDo(Generalize())
                            )
        
        generalized_pcol | "Write Prepared elements" >> WriteToText(f"{gcp_data_lake}/masked_data/")

        # Write the final data to a desired sink (e.g. BigQuery)
        generalized_pcol | 'WriteToBigQuery' >> WriteToBigQuery(
            table=gcp_project + ':' + bq_dataset + '.' + bq_table,
            create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
            write_disposition=beam.io.BigQueryDisposition.WRITE_TRUNCATE,
            schema=bq_table_schema 
        )

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    run()