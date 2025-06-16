import requests

def get_coordinates_from_address(zipcode):
    if not zipcode:
        print("ZIP code is required.")
        return None, None

    print("Geocoding ZIP:", zipcode)  # Debug print

    api_key = '7d0673dae55743a2a07cf563a99401d1'
    url = f'https://api.opencagedata.com/geocode/v1/json?q={zipcode}&key={api_key}'

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data['results']:
            geometry = data['results'][0]['geometry']
            print("Coordinates:", geometry)
            return geometry['lat'], geometry['lng']
        else:
            print("No results found for:", zipcode)
    except Exception as e:
        print(f"Geocoding error: {e}")
    return None, None
