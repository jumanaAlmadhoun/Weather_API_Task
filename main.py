from flask import Flask,request, jsonify
import requests, json
from flask_caching import Cache

app = Flask(__name__)
cache = Cache()



app.config["CACHE_TYPE"] = 'simple'
cache.init_app(app)

#endpoint1
"""
#Request: 
http://api.weatherapi.com/v1/current.json?key=b4878c84201e41708a693727231612&q=<CITY NAME>

#Response:
{
  "city_name": "Jeddah",
  "lat": 21.52,
  "lon": 39.22,
  "status": "Partly cloudy",
  "temp_c": 27.0
}
"""

@app.route('/get-city/<city_name>')
@cache.cached(timeout=7200)
def get_city(city_name):
    try:
        # Make the request to the weather API
        url = "http://api.weatherapi.com/v1/current.json?key=b4878c84201e41708a693727231612&q=" + city_name
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses

        # Parse the API response
        data = response.json()

        # Extract neded weather information from the response
        weather = {
            "city_name": data['location']['name'],
            "temp_c": data['current']['temp_c'],
            "status": data['current']['condition']['text'],
            "lat": data['location']['lat'],
            "lon": data['location']['lon']
        }

        return jsonify(weather), 200

    except requests.RequestException as e:
        return jsonify({"error": f"There is no city with this name"}), 500
    
#endpoint2
"""
#Request:
curl --location --request POST 'http://127.0.0.1:5000/weather/bulk' 
--data "[
    {
        "cityName": "Makkah"
    },
    {
        "cityName": "Madina"
    }
]"


#Response:
[
     {
        "city_name": "Makkah",
        "lat": 21.43,
        "lon": 39.83,
        "status": "Clear",
        "temperature_c": 24.3
    },
    {
        "city_name": "Madina",
        "lat": 5.68,
        "lon": -0.17,
        "status": "Mist",
        "temperature_c": 29.0
    }
]
"""
@app.route("/weather/bulk", methods = ["POST"])
@cache.cached(timeout=7200)
def bulk():
    try:
      # Get weather data from the request
       weather_data = request.get_json()
      # Prepare the payload for the bulk request
       city_list = []
       for i, data in enumerate(weather_data):
          city_list.append({
          "q": data["cityName"],
           "custom_id": i+1
          })
      # Make the bulk request to the weather API
       url = "http://api.weatherapi.com/v1/current.json?key=b4878c84201e41708a693727231612&q=bulk"
       payload = json.dumps({"locations": city_list})
       headers = {'Content-Type': 'application/json'}
       response = requests.request("POST", url, headers=headers, data=payload)
       
       #to cach the response with dict type to use it on statistics() endpoint
       cache.set('bulk_data', response.json(), timeout=7200)

      # Parse the API response
       data = response.json()
      
      # Extract neded weather information from the response
       weather = []
       for i, item in enumerate(data['bulk']):        
           weather.append({
       "city_name" : item['query']['location']['name'],
       "temperature_c" : item['query']['current']['temp_c'],
       "status" : item['query']['current']['condition']['text'],
       "lat": item['query']['location']['lat'],
       "lon": item['query']['location']['lon'],
    })
   
       return jsonify(weather), 200
    except Exception as e:
        # Handle exceptions and return an error response
        error_message = f"Error: {str(e)}"
        return jsonify({"error": error_message}), 500

#endpoint3
"""
note: must call endpoint 2 first
#Request: 
http://127.0.0.1:5000/weather/statistics
#Response:
[
  {
    "average_temperature": 17.3,
    "highest_temperature": 29.0,
    "lowest_temperature": 0.6
  }
]
"""
@app.route('/weather/statistics')
@cache.cached(timeout=7200)
def statistics():
    try:
        statistics = []
        average_temperature = 0
        highest_temperature = -100
        lowest_temperature = 100
        data_bulk = cache.get('bulk_data')

        # Check if 'bulk_data' is present in the cache
        if data_bulk is None:
            raise ValueError("No 'bulk_data' found in cache")

        # Loop through the "bulk" list
        for entry in data_bulk["bulk"]:
            query_data = entry["query"]
            current_data = query_data["current"]
            location_data = query_data["location"]

            # Access the relevant data within the nested dictionaries
            city = location_data["country"]
            temperature_celsius = current_data["temp_c"]
            average_temperature += temperature_celsius

            # Check for highest temperature and corresponding city
            if temperature_celsius > highest_temperature:
                highest_temperature = temperature_celsius

            # Check for lowest temperature and corresponding city
            if temperature_celsius < lowest_temperature:
                lowest_temperature = temperature_celsius

        # Calculate average temperature
        if len(data_bulk['bulk']) > 0:
            average_temperature = average_temperature / len(data_bulk['bulk'])

        # Append statistics to the list
        statistics.append({
            "highest_temperature": highest_temperature,
            "lowest_temperature": lowest_temperature,
            "average_temperature": average_temperature
        })

        return jsonify(statistics), 200

    except Exception as e:
        # Handle the exception and return an error response
        error_message = f"An error occurred: {str(e)}"
        return jsonify({"error : must call endpoint 2 first"}), 500


if __name__ == "__main__":
    app.run(debug=True)