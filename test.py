from main import app
import unittest, json


class FlaskTest(unittest.TestCase):
    #Check if the response 200
    def test_index(self):
        tester = app.test_client(self)
        response = tester.get("http://127.0.0.1:5000/get-city/taif")
        statuscode = response.status_code
        self.assertEqual(statuscode, 200)

    #Check if content return is application/json 
    def test_index_content(self):
        tester = app.test_client(self)
        response = tester.get("http://127.0.0.1:5000/get-city/taif")
        self.assertEqual(response.content_type, "application/json")

    #Check for data returnde
    def test_index_data(self):
        tester = app.test_client(self)
        response = tester.get("http://127.0.0.1:5000/get-city/taif")
        self.assertTrue(b"temp_c" in response.data)

    


    def setUp(self):
        # Create a test client for the Flask app
        self.app = app.test_client()

    def test_post_example_endpoint(self):
        # Define test data for the POST request
        test_data = [ 
        {
        "cityName": "Makkah"
        },
        {
        "cityName": "Madina"
        },
        {
        "cityName": "Riyadh"
        } ]

        # Make a POST request to the endpoint with the test data
        response = self.app.post('/weather/bulk',
                                 data=json.dumps(test_data),
                                 content_type='application/json')

        # Check the response status code
        self.assertEqual(response.status_code, 200)

        # Parse the response JSON
        response_data = json.loads(response.get_data(as_text=True))

        # Check if the expected data is present in the response
        self.assertIn("received", response_data)
        self.assertEqual(response_data["received"], test_data["message"])



if __name__ == "__main__":
    unittest.main()


