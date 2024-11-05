import unittest
import requests
from transforms.dofns import Ingest, Generalize

class TestIngest(unittest.TestCase):

    def test_successful_request(self):
        
        # Create an Ingest instance with mock parameters
        ingest = Ingest()
        ingest.quantity = 1
        ingest.birthday_start = '1900-01-01'
        # Process an input element
        results = list(ingest.process(1))

        # Assert the output
        expected_output = {'id': 1, 'firstname': 'Harmony', 'lastname': 'Erdman', 'email': 'hkonopelski@rogahn.org', 'phone': '+12836210242', 'birthday': '2015-03-09', 'gender': 'female', 'address': {'id': 1, 'street': '704 Lourdes Squares Apt. 018', 'streetName': 'Ashly Street', 'buildingNumber': '77303', 'city': 'New Claudiemouth', 'zipcode': '34614-6623', 'country': 'Bahamas', 'country_code': 'BS', 'latitude': -73.295854, 'longitude': 69.236142}, 'website': 'http://mcglynn.com', 'image': 'http://placeimg.com/640/480/people'}
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], expected_output)

class TestGeneralize(unittest.TestCase):

    def test_generalize_data(self):
        input_data = {'id': 1, 'firstname': 'Harmony', 'lastname': 'Erdman', 'email': 'hkonopelski@rogahn.org', 'phone': '+12836210242', 'birthday': '2015-03-09', 'gender': 'female', 'address': {'id': 1, 'street': '704 Lourdes Squares Apt. 018', 'streetName': 'Ashly Street', 'buildingNumber': '77303', 'city': 'New Claudiemouth', 'zipcode': '34614-6623', 'country': 'Bahamas', 'country_code': 'BS', 'latitude': -73.295854, 'longitude': 69.236142}, 'website': 'http://mcglynn.com', 'image': 'http://placeimg.com/640/480/people'}
        generalize = Generalize()

        output_data = list(generalize.process(input_data))[0]

        # Assert the output
        self.assertIn('uuid', output_data)
        self.assertEqual(output_data['email_domain'], 'rogahn')
        self.assertEqual(output_data['age_group'], '[0-10]')
        self.assertEqual(output_data['location'], 'Bahamas')
