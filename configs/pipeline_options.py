from apache_beam.options.pipeline_options import PipelineOptions
from configs.config import *
import logging


def get_pipeline_options(runner_type="DataflowRunner", setup_file="./setup.py"):
    """Creates and configures a PipelineOptions object for a Beam pipeline.

    Args:
        runner_type: The type of runner to use for the pipeline (e.g., 'DataflowRunner', 'DirectRunner').
        setup_file: The path to a Python setup file containing dependencies.

    Returns:
        A PipelineOptions object with configured options.
    """
    return PipelineOptions(
        runner=runner_type,
        project=GCP_PROJECT_ID,
        region=GCP_REGION,
        temp_location=TEMP_BKT_FOLDER,
        save_main_session=SAVE_MAIN_SESSION,
        staging_location=STAGGING_BKT_FOLDER,
        # setup file needed to interact with python files as modules in the project
        setup_file=setup_file,
        # recomended when write to GCS
        additional_experiments="use_grpc_for_gcs"
    )
