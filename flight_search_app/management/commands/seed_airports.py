from django.core.management.base import BaseCommand
from flight_search_app.models import Airport

class Command(BaseCommand):
    help = 'Seeds database with airports'

    def handle(self, *args, **kwargs):
        airports = [
            # --- PAKISTAN (Detailed Coverage) ---
            {"code": "KHI", "name": "Jinnah International", "city": "Karachi", "country": "Pakistan", "pop": 90},
            {"code": "LHE", "name": "Allama Iqbal International", "city": "Lahore", "country": "Pakistan", "pop": 85},
            {"code": "ISB", "name": "Islamabad International", "city": "Islamabad", "country": "Pakistan", "pop": 85},
            {"code": "PEW", "name": "Bacha Khan International", "city": "Peshawar", "country": "Pakistan", "pop": 70},
            {"code": "MUX", "name": "Multan International", "city": "Multan", "country": "Pakistan", "pop": 65},
            {"code": "UET", "name": "Quetta International", "city": "Quetta", "country": "Pakistan", "pop": 60},
            {"code": "SKT", "name": "Sialkot International", "city": "Sialkot", "country": "Pakistan", "pop": 60},
            {"code": "LYP", "name": "Faisalabad International", "city": "Faisalabad", "country": "Pakistan", "pop": 55},
            {"code": "GWD", "name": "Gwadar International", "city": "Gwadar", "country": "Pakistan", "pop": 50},

            # --- CANADA (Detailed Coverage) ---
            {"code": "YYZ", "name": "Toronto Pearson", "city": "Toronto", "country": "Canada", "pop": 90},
            {"code": "YVR", "name": "Vancouver International", "city": "Vancouver", "country": "Canada", "pop": 85},
            {"code": "YUL", "name": "Montréal-Trudeau", "city": "Montreal", "country": "Canada", "pop": 80},
            {"code": "YYC", "name": "Calgary International", "city": "Calgary", "country": "Canada", "pop": 75},
            {"code": "YEG", "name": "Edmonton International", "city": "Edmonton", "country": "Canada", "pop": 70},
            {"code": "YOW", "name": "Ottawa Macdonald-Cartier", "city": "Ottawa", "country": "Canada", "pop": 70},
            {"code": "YWG", "name": "Winnipeg Richardson", "city": "Winnipeg", "country": "Canada", "pop": 65},
            {"code": "YHZ", "name": "Halifax Stanfield", "city": "Halifax", "country": "Canada", "pop": 65},

            # --- USA (Major Hubs) ---
            {"code": "ATL", "name": "Hartsfield-Jackson Atlanta", "city": "Atlanta", "country": "USA", "pop": 100},
            {"code": "LAX", "name": "Los Angeles International", "city": "Los Angeles", "country": "USA", "pop": 95},
            {"code": "ORD", "name": "O'Hare International", "city": "Chicago", "country": "USA", "pop": 90},
            {"code": "DFW", "name": "Dallas/Fort Worth", "city": "Dallas", "country": "USA", "pop": 90},
            {"code": "JFK", "name": "John F. Kennedy", "city": "New York", "country": "USA", "pop": 95},
            {"code": "EWR", "name": "Newark Liberty", "city": "New York", "country": "USA", "pop": 85},
            {"code": "SFO", "name": "San Francisco International", "city": "San Francisco", "country": "USA", "pop": 90},
            {"code": "MIA", "name": "Miami International", "city": "Miami", "country": "USA", "pop": 85},
            {"code": "SEA", "name": "Seattle-Tacoma", "city": "Seattle", "country": "USA", "pop": 80},
            {"code": "LAS", "name": "Harry Reid International", "city": "Las Vegas", "country": "USA", "pop": 85},

            # --- EUROPE (Major Hubs) ---
            {"code": "LHR", "name": "Heathrow", "city": "London", "country": "UK", "pop": 100},
            {"code": "LGW", "name": "Gatwick", "city": "London", "country": "UK", "pop": 85},
            {"code": "MAN", "name": "Manchester Airport", "city": "Manchester", "country": "UK", "pop": 80},
            {"code": "CDG", "name": "Charles de Gaulle", "city": "Paris", "country": "France", "pop": 95},
            {"code": "ORY", "name": "Orly", "city": "Paris", "country": "France", "pop": 80},
            {"code": "AMS", "name": "Schiphol", "city": "Amsterdam", "country": "Netherlands", "pop": 90},
            {"code": "FRA", "name": "Frankfurt Airport", "city": "Frankfurt", "country": "Germany", "pop": 90},
            {"code": "MUC", "name": "Munich Airport", "city": "Munich", "country": "Germany", "pop": 85},
            {"code": "BER", "name": "Berlin Brandenburg", "city": "Berlin", "country": "Germany", "pop": 80},
            {"code": "MAD", "name": "Adolfo Suárez Madrid–Barajas", "city": "Madrid", "country": "Spain", "pop": 85},
            {"code": "BCN", "name": "Barcelona–El Prat", "city": "Barcelona", "country": "Spain", "pop": 85},
            {"code": "FCO", "name": "Leonardo da Vinci–Fiumicino", "city": "Rome", "country": "Italy", "pop": 85},
            {"code": "MXP", "name": "Malpensa", "city": "Milan", "country": "Italy", "pop": 80},
            {"code": "IST", "name": "Istanbul Airport", "city": "Istanbul", "country": "Turkey", "pop": 95},
            {"code": "ZRH", "name": "Zurich Airport", "city": "Zurich", "country": "Switzerland", "pop": 80},

            # --- MIDDLE EAST (Major Hubs) ---
            {"code": "DXB", "name": "Dubai International", "city": "Dubai", "country": "UAE", "pop": 100},
            {"code": "AUH", "name": "Zayed International", "city": "Abu Dhabi", "country": "UAE", "pop": 90},
            {"code": "DOH", "name": "Hamad International", "city": "Doha", "country": "Qatar", "pop": 95},
            {"code": "JED", "name": "King Abdulaziz", "city": "Jeddah", "country": "Saudi Arabia", "pop": 85},
            {"code": "RUH", "name": "King Khalid", "city": "Riyadh", "country": "Saudi Arabia", "pop": 85},

            # --- ASIA PACIFIC (Major Hubs) ---
            {"code": "HND", "name": "Haneda", "city": "Tokyo", "country": "Japan", "pop": 95},
            {"code": "NRT", "name": "Narita", "city": "Tokyo", "country": "Japan", "pop": 85},
            {"code": "SIN", "name": "Changi", "city": "Singapore", "country": "Singapore", "pop": 100},
            {"code": "BKK", "name": "Suvarnabhumi", "city": "Bangkok", "country": "Thailand", "pop": 90},
            {"code": "HKG", "name": "Hong Kong International", "city": "Hong Kong", "country": "Hong Kong", "pop": 90},
            {"code": "ICN", "name": "Incheon", "city": "Seoul", "country": "South Korea", "pop": 90},
            {"code": "DEL", "name": "Indira Gandhi", "city": "Delhi", "country": "India", "pop": 90},
            {"code": "BOM", "name": "Chhatrapati Shivaji", "city": "Mumbai", "country": "India", "pop": 85},
            {"code": "MAA", "name": "Chennai International", "city": "Chennai", "country": "India", "pop": 80},
            {"code": "SYD", "name": "Kingsford Smith", "city": "Sydney", "country": "Australia", "pop": 85},
            {"code": "MEL", "name": "Melbourne Airport", "city": "Melbourne", "country": "Australia", "pop": 80},

            # --- OTHERS ---
            {"code": "GRU", "name": "Guarulhos", "city": "São Paulo", "country": "Brazil", "pop": 85},
            {"code": "GIG", "name": "Galeão", "city": "Rio de Janeiro", "country": "Brazil", "pop": 75},
            {"code": "EZE", "name": "Ezeiza", "city": "Buenos Aires", "country": "Argentina", "pop": 80},
            {"code": "JNB", "name": "O.R. Tambo", "city": "Johannesburg", "country": "South Africa", "pop": 80},
            {"code": "CPT", "name": "Cape Town International", "city": "Cape Town", "country": "South Africa", "pop": 75},
        ]

        count = 0
        for data in airports:
            obj, created = Airport.objects.get_or_create(
                iata_code=data["code"],
                defaults={
                    "name": data["name"],
                    "city": data["city"],
                    "country": data["country"],
                    "popularity": data["pop"]
                }
            )
            if created:
                count += 1
                self.stdout.write(self.style.SUCCESS(f'Added {data["code"]}'))
            else:
                # Update just in case
                obj.name = data["name"]
                obj.city = data["city"]
                obj.country = data["country"]
                obj.popularity = data["pop"]
                obj.save()
        
        self.stdout.write(self.style.SUCCESS(f'Successfully seeded {count} new airports (Updated others)'))
