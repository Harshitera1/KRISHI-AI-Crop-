"""
Location Service - Handles location matching and nearby location detection
Supports both map-based and voice-based location input
"""
import math
import logging

logger = logging.getLogger(__name__)

# Comprehensive location database with coordinates
LOCATION_DATABASE = {
    "delhi": {"lat": 28.7041, "lng": 77.1025, "region": "North", "aliases": ["new delhi", "delhi ncr"]},
    "punjab": {"lat": 31.1471, "lng": 74.8550, "region": "North", "aliases": ["punjab state", "ludhiana"]},
    "haryana": {"lat": 29.0588, "lng": 77.0745, "region": "North", "aliases": ["haryana state", "gurgaon", "faridabad"]},
    "uttar pradesh": {"lat": 26.8467, "lng": 80.9462, "region": "North", "aliases": ["up", "lucknow", "meerut"]},
    "bihar": {"lat": 25.0961, "lng": 85.3131, "region": "East", "aliases": ["bihar state", "patna"]},
    "west bengal": {"lat": 24.8355, "lng": 88.2635, "region": "East", "aliases": ["wb", "kolkata"]},
    "jharkhand": {"lat": 23.6102, "lng": 85.2799, "region": "East", "aliases": ["jharkhand state", "ranchi"]},
    "maharashtra": {"lat": 19.7515, "lng": 75.7139, "region": "Central", "aliases": ["maharashtra state", "mumbai", "pune"]},
    "madhya pradesh": {"lat": 22.9375, "lng": 78.6553, "region": "Central", "aliases": ["mp", "indore", "bhopal"]},
    "karnataka": {"lat": 15.3173, "lng": 75.7139, "region": "South", "aliases": ["karnataka state", "bangalore", "bengaluru"]},
    "tamil nadu": {"lat": 11.1271, "lng": 78.6569, "region": "South", "aliases": ["tn", "tamil nadu state", "chennai"]},
    "telangana": {"lat": 18.1124, "lng": 79.0193, "region": "South", "aliases": ["telangana state", "hyderabad"]},
    "andhra pradesh": {"lat": 15.9129, "lng": 78.4855, "region": "South", "aliases": ["ap", "andhra pradesh state", "visakhapatnam"]},
    "meerut": {"lat": 28.9845, "lng": 77.7064, "region": "North", "aliases": ["meerut city", "meerut uttar pradesh"]},
}

def find_nearest_location(latitude, longitude):
    """
    Find the nearest known location from database using map coordinates
    Returns the matched location details
    """
    min_distance = float('inf')
    nearest_location = None
    nearest_key = None
    
    for location_key, location_data in LOCATION_DATABASE.items():
        lat_diff = location_data["lat"] - latitude
        lng_diff = location_data["lng"] - longitude
        distance = math.sqrt(lat_diff**2 + lng_diff**2)
        
        if distance < min_distance:
            min_distance = distance
            nearest_location = location_data
            nearest_key = location_key
    
    result = {
        "location": nearest_key.title(),
        "latitude": nearest_location["lat"],
        "longitude": nearest_location["lng"],
        "region": nearest_location["region"],
        "distance": round(min_distance, 3)
    }
    
    logger.info(
        "Nearest location found",
        extra={
            "event": "location_matched",
            "input_coords": {"lat": latitude, "lng": longitude},
            "matched_location": nearest_key,
            "distance": min_distance
        }
    )
    
    return result


def match_voice_location(location_text):
    """
    Match voice input location to database
    Handles partial matches and aliases
    Returns matched location or None
    """
    if not location_text:
        return None
    
    text_lower = location_text.lower().strip()
    
    # Exact match first
    if text_lower in LOCATION_DATABASE:
        loc_data = LOCATION_DATABASE[text_lower]
        return {
            "location": text_lower.title(),
            "latitude": loc_data["lat"],
            "longitude": loc_data["lng"],
            "region": loc_data["region"],
            "match_type": "exact"
        }
    
    # Alias/partial match
    for location_key, location_data in LOCATION_DATABASE.items():
        # Check main location name
        if location_key in text_lower or text_lower in location_key:
            return {
                "location": location_key.title(),
                "latitude": location_data["lat"],
                "longitude": location_data["lng"],
                "region": location_data["region"],
                "match_type": "partial"
            }
        
        # Check aliases
        for alias in location_data.get("aliases", []):
            if alias in text_lower or text_lower in alias:
                return {
                    "location": location_key.title(),
                    "latitude": location_data["lat"],
                    "longitude": location_data["lng"],
                    "region": location_data["region"],
                    "match_type": "alias"
                }
    
    logger.warning(
        "Location not found in database",
        extra={
            "event": "location_not_matched",
            "input": location_text
        }
    )
    
    return None


def get_all_locations():
    """Return all available locations"""
    return list(LOCATION_DATABASE.keys())


def get_region_locations(region):
    """Get all locations in a specific region"""
    region_locs = []
    for location_key, location_data in LOCATION_DATABASE.items():
        if location_data["region"] == region:
            region_locs.append(location_key)
    return region_locs
