import apache_beam as beam
import requests
import logging
import uuid
import re
from configs.config import *
from utils.utils import get_age_group

class Ingest(beam.DoFn):
    """A DoFn class for fetching data from an API endpoint.

    This DoFn retrieves data from a specified API endpoint based on input elements
    and configured parameters. It includes functionality for retrying failed requests
    up to a maximum number of retries.

    Attributes:
        api_endpoint (str): The base URL of the API endpoint.
        quantity (int): The quantity parameter to be included in the API request.
        birthday_start (str): The birthday_start parameter for filtering data.
        request_max_retry (int): The maximum number of retries for failed API requests.
    """

    def __init__(self, quantity=QUANTITY):
        """Initializes the DoFn with parameters from configs/config.py

        Args:
        api_endpoint (str): The base URL of the API endpoint.
        quantity (int): The quantity parameter to be included in the API request. Max value is 1000.
        birthday_start (str): The birthday_start parameter for filtering data.
        request_max_retry (int): The maximum number of retries for failed API requests.
        """
        self.api_endpoint = API_ENDPOINT
        self.quantity = quantity
        self.birthday_start = BIRTHDAY_START
        
    def process(self, element):
        """Processes an element from the input PCollection and fetches data from the API.

        This method constructs the API URL using the configured parameters and the
        input element. It then retrieves data from the API with retry logic in case
        of failures.

        Args:
        element: The element from the input PCollection.

        Yields:
        The retrieved data from the API as dictionaries.
        """
        # fetch data from the API
        url = f"{self.api_endpoint}?_quantity={self.quantity}&_seed={element}&_birthday_start={self.birthday_start}"
        
        # each HTTP request will be run in parallel and retry count should be set to 0 for each element in the input pcollection
        self.retry = 0

        while self.retry <= MAX_REQUEST_RETRY:
            # it may be possible to introduce a sleep after retry but not needed due to the small amount of requests and retries
            logging.info(f"Requesting URL as {url}")
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    json_response = response.json()
                    if json_response["code"] == 200 and json_response["status"] == "OK": 
                        logging.info(f"Request to {url} was successful")
                        data = json_response["data"]
                        for d in data:
                            yield d
                        break
                self.retry += 1
            except:
                logging.warning(f"Retrying for {url} with retry count {self.retry} and max retry {MAX_REQUEST_RETRY}")
    
        if self.retry == MAX_REQUEST_RETRY:
            # at this point, the retry policy was not enough and it may be worth investigating.
            # Saving the error traceback or message in a status/metadata table could be useful.
            logging.error(f"Exausted retries for {url}")

class Generalize(beam.DoFn):
    """A DoFn class for generalizing and transforming input data.

    This DoFn takes raw data elements and performs the following operations:
    - Generates a unique UUID for each element.
    - Filters and extracts specific fields based on a whitelist (`valid_fields_api`).
    - Transforms specific fields:
        - Extracts the domain name from the email address using a regular expression.
        - Calculates the age group based on the birthday (if provided).
    - Copies other fields from the input data to the output element.

    Attributes:
    mask_encoder (optional): An encoder object for masking sensitive data (not used in this example).
    valid_fields_api (list): A list of valid field names to include in the output.
    location_field (str): The field name within the 'address' dictionary for extracting location data (configurable).
    """

    def __init__(self):
        """Initializes the DoFn with parameters.

        Args:
        valid_fields_api (list): A list of valid field names to include in the output.
        location_field (str, optional): The field name within the 'address' dictionary for extracting location data. Defaults to "country".
        """
        self.valid_fields_api = VALID_FIELDS_API
        self.location_field = LOCATION_FIELD

    def process(self, element):
        """Processes an element and transforms the data.

        This method generates a UUID, filters and extracts specified fields,
        performs transformations on certain fields, and yields the resulting data.

        Args:
        element: The element from the input PCollection.

        Yields:
        The transformed element as a dictionary.
        """

        new_element = {}
        new_element['uuid'] = str(uuid.uuid4())
        # we filter by location field, it is set as country but it can be easily change to city, zipcode, etc.
        for k in VALID_FIELDS_API:
            match k:
                case 'address':
                    new_element['location'] = element.get('address', {}).get(LOCATION_FIELD, None)
                case 'email':
                    match = re.search(r'@([^.]+)\.', element.get('email'))
                    new_element['email_domain'] = match.group(1) if match else None
                case 'birthday':
                    new_element['age_group'] = get_age_group(element.get('birthday', None))
                case _:
                    new_element[k] = element.get(k, None)
        yield new_element
