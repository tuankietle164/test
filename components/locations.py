locations = {
    'Ho Chi Minh': {'latitude': 10.8231, 'longitude': 106.6297},
    'Hanoi': {'latitude': 21.0285, 'longitude': 105.8542},
    'Da Nang': {'latitude': 16.0471, 'longitude': 108.2068},
    'Can Tho': {'latitude': 10.0452, 'longitude': 105.7469},
    'Nha Trang': {'latitude': 12.2388, 'longitude': 109.1967}
}

def get_location_coordinates(location_name):
    return locations.get(location_name, locations['Ho Chi Minh'])
