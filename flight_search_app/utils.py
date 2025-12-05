
# Comprehensive list of major cities and their IATA codes
IATA_CODES = {
    # North America
    "new york": "JFK", "nyc": "JFK", "new york city": "JFK",
    "los angeles": "LAX", "la": "LAX",
    "chicago": "ORD",
    "houston": "IAH",
    "toronto": "YYZ",
    "vancouver": "YVR",
    "mexico city": "MEX",
    "miami": "MIA",
    "san francisco": "SFO",
    "las vegas": "LAS",
    "orlando": "MCO",
    "washington": "IAD",
    "boston": "BOS",
    
    # Europe
    "london": "LHR", "uk": "LHR", "united kingdom": "LHR",
    "paris": "CDG", "france": "CDG",
    "frankfurt": "FRA", "germany": "FRA",
    "amsterdam": "AMS", "netherlands": "AMS",
    "madrid": "MAD", "spain": "MAD",
    "rome": "FCO", "italy": "FCO",
    "istanbul": "IST", "turkey": "IST",
    "dublin": "DUB", "ireland": "DUB",
    "zurich": "ZRH", "switzerland": "ZRH",
    "munich": "MUC",
    "barcelona": "BCN",
    "manchester": "MAN",
    
    # Middle East
    "dubai": "DXB", "uae": "DXB",
    "doha": "DOH", "qatar": "DOH",
    "abu dhabi": "AUH",
    "riyadh": "RUH", "saudi arabia": "RUH",
    "jeddah": "JED",
    "tel aviv": "TLV", "israel": "TLV",
    "cairo": "CAI", "egypt": "CAI",
    
    # Asia
    "tokyo": "HND", "japan": "HND",
    "singapore": "SIN",
    "hong kong": "HKG",
    "seoul": "ICN", "south korea": "ICN",
    "bangkok": "BKK", "thailand": "BKK",
    "delhi": "DEL", "india": "DEL",
    "mumbai": "BOM",
    "beijing": "PEK", "china": "PEK",
    "shanghai": "PVG",
    "karachi": "KHI", "pakistan": "KHI",
    "lahore": "LHE",
    "islamabad": "ISB",
    "kuala lumpur": "KUL", "malaysia": "KUL",
    "jakarta": "CGK", "indonesia": "CGK",
    "manila": "MNL", "philippines": "MNL",
    "vietnam": "SGN", "ho chi minh": "SGN",
    
    # Oceania
    "sydney": "SYD", "australia": "SYD",
    "melbourne": "MEL",
    "auckland": "AKL", "new zealand": "AKL",
    
    # South America
    "sao paulo": "GRU", "brazil": "GRU",
    "bogota": "BOG", "colombia": "BOG",
    "lima": "LIM", "peru": "LIM",
    "santiago": "SCL", "chile": "SCL",
    "buenos aires": "EZE", "argentina": "EZE",
    
    # Africa
    "johannesburg": "JNB", "south africa": "JNB",
    "cape town": "CPT",
    "nairobi": "NBO", "kenya": "NBO",
    "lagos": "LOS", "nigeria": "LOS",
    "casablanca": "CMN", "morocco": "CMN",
}

def get_iata_code(location):
    """
    Converts a city or country name to an IATA code.
    Returns the IATA code if found, or the original input (upper case) if it looks like an IATA code.
    """
    if not location:
        return None
        
    clean_location = location.strip().lower()
    
    # Check if it's already a 3-letter code
    if len(clean_location) == 3:
        return clean_location.upper()
        
    # Lookup in dictionary
    return IATA_CODES.get(clean_location)
