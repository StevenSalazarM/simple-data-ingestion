import apache_beam as beam
import logging
from configs.config import *
from configs.pipeline_options import get_pipeline_options
from transforms.dofns import Ingest, Generalize
from apache_beam.io.gcp.bigquery import WriteToBigQuery
from apache_beam.io.textio import WriteToText
from utils.utils import mask_fields
import argparse
from apache_beam.options.pipeline_options import PipelineOptions


def run(options, quantity=quantity, expected_responses=expected_responses):
    
    # Generate the seeds for the HTTP requests (e.g. [1, 1001, 2001, etc.]). Max quantity in the batch response is 1k.
    seeds = [i*quantity+1 for i in range(expected_responses//quantity)]
    with beam.Pipeline(options=options) as p:

        # Create a PCollection of seed values for 10 batches of 1000 records each
        seed_pcol = p | 'Initiate Seeds PCollection' >> beam.Create(seeds)
        
        # Fetch data for each seed in parallel and yield each element (person) into a new pcollection
        people_pcol =  (seed_pcol | 'Ingest Data and create People PCollection' >> beam.ParDo(Ingest(quantity=quantity)) 
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
    parser = argparse.ArgumentParser(description="Run mode, can be cloud or local")
    parser.add_argument(
        "--run_mode", type=str, default="cloud", help="Run type", choices=["cloud", "local"]
    )
    parser.add_argument(
        "--setup_file", type=str, default="./setup.py", help="Setup file for Dataflow"
    )
    args, pipeline_args = parser.parse_known_args()
    pipeline_options = None
    if args.run_mode == "local":
        expected_responses = 5
        quantity = 1
        bq_table = 'persons_local_test'
        runner = "DirectRunner"
        pipeline_options = get_pipeline_options(runner_type=runner)
    else:
        runner = "DataflowRunner"
        pipeline_options = get_pipeline_options(runner_type=runner, setup_file=args.setup_file)

    run(pipeline_options,quantity=quantity, expected_responses=expected_responses)