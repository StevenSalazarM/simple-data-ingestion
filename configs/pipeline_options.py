from apache_beam.options.pipeline_options import PipelineOptions
from configs.config import *
import logging


pipeline_options = PipelineOptions(
    runner=runner_type,
    project=gcp_project,
    region=gcp_region,
    temp_location=temp_bucket_folder,
    save_main_session=save_main_session,
    staging_location=stagging_bucket_folder,
    setup_file="./setup.py",
    additional_experiments="use_grpc_for_gcs"
)
