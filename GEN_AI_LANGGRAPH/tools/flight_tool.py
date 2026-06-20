import os
import requests
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.getenv("AVIATIONSTATCK_API_KEY")


def search_flights(query):
    url ="http://api.aviationstack.com/v1/flights"
    params = {
        "access_key": API_KEY,
        "limit": 5
    }
    response = requests.get(url,params = params)
    data = response.json()

    flights =[]

    if  'data' in data :
        for flight in data['data'][:2]:
            airline = flight.get("airline",{}).get("name","unknown")
            departure = flight.get("departure",{}).get("airport","unknown")
            arrival = flight.get("airport",{}).get("airport","unknown")
            status = flight.get("flight_status","unknown")

            flights.append(f"""
                           Airline : {airline},
                           Departure: {departure},
                           Arrival : {arrival},
                           Status : {status}
                           """)
        return "\n".join(flights)