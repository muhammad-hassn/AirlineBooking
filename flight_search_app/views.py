import os
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from amadeus import Client, ResponseError
from .models import UserContact, PaymentAttempt, Airport
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from .utils import get_iata_code

# Initialize Amadeus Client
def get_amadeus_client():
    return Client(
        client_id=os.getenv("AMADEUS_CLIENT_ID"),
        client_secret=os.getenv("AMADEUS_CLIENT_SECRET")
    )

def format_duration(iso_duration):
    """Converts PT1H30M to 1 Hr 30 Min"""
    import re
    if not iso_duration:
        return ""
    
    hours = 0
    minutes = 0
    
    # Extract hours
    h_match = re.search(r'(\d+)H', iso_duration)
    if h_match:
        hours = int(h_match.group(1))
        
    # Extract minutes
    m_match = re.search(r'(\d+)M', iso_duration)
    if m_match:
        minutes = int(m_match.group(1))
        
    return f"{hours} Hrs {minutes} Min"

def home(request):
    return render(request, 'flight_search_app/search.html')

def about(request):
    return render(request, 'flight_search_app/about.html')

@login_required(login_url='login')
def search_results(request):
    if request.method == 'GET':
        raw_origin = request.GET.get('origin') or request.GET.get('origin_label')
        raw_destination = request.GET.get('destination') or request.GET.get('destination_label')
        departure_date = request.GET.get('departure_date')
        adults = int(request.GET.get('adults', 1))
        flight_class = request.GET.get('flight_class', 'Economy')
        sort_by = request.GET.get('sort_by', '')

        if not all([raw_origin, raw_destination, departure_date]):
            messages.error(request, "Please fill in all required fields.")
            return redirect('home')

        # Convert inputs to IATA codes
        origin = get_iata_code(raw_origin)
        destination = get_iata_code(raw_destination)

        if not origin:
            messages.error(request, f"Could not find an airport for '{raw_origin}'. Please try a major city name or IATA code.")
            return redirect('home')
            
        if not destination:
            messages.error(request, f"Could not find an airport for '{raw_destination}'. Please try a major city name or IATA code.")
            return redirect('home')

        # Map UI class names to Amadeus API values
        class_mapping = {
            'Economy': 'ECONOMY',
            'Business': 'BUSINESS',
            'First Class': 'FIRST'
        }
        travel_class = class_mapping.get(flight_class, 'ECONOMY')

        amadeus = get_amadeus_client()
        flights = []

        try:
            # Build API parameters
            api_params = {
                'originLocationCode': origin,
                'destinationLocationCode': destination,
                'departureDate': departure_date,
                'adults': adults,
                'travelClass': travel_class,
                'max': 10
            }
            
            response = amadeus.shopping.flight_offers_search.get(**api_params)
            
            for offer in response.data:
                # We only process the first itinerary (one-way logic for now)
                itinerary = offer['itineraries'][0]
                segments = itinerary['segments']
                
                # First Segment (Take off)
                first_segment = segments[0]
                # Last Segment (Landing)
                last_segment = segments[-1]
                
                stops_count = len(segments) - 1
                stop_info = "NON-STOP" if stops_count == 0 else f"{stops_count} STOP{'S' if stops_count > 1 else ''}"

                # Lookup airport names
                dep_code = first_segment['departure']['iataCode']
                arr_code = last_segment['arrival']['iataCode']
                
                # Simple caching or direct lookup
                dep_airport = Airport.objects.filter(iata_code=dep_code).first()
                arr_airport = Airport.objects.filter(iata_code=arr_code).first()

                # Calculate price per adult
                total_price = float(offer['price']['total'])
                price_per_adult = total_price / adults if adults > 0 else total_price

                # Convert duration to minutes for sorting
                import re
                duration_str = itinerary['duration']
                hours = 0
                minutes = 0
                h_match = re.search(r'(\d+)H', duration_str)
                if h_match:
                    hours = int(h_match.group(1))
                m_match = re.search(r'(\d+)M', duration_str)
                if m_match:
                    minutes = int(m_match.group(1))
                duration_minutes = hours * 60 + minutes

                # Build detailed segments info for "View Details"
                detailed_segments = []
                for seg in segments:
                    seg_dep_airport = Airport.objects.filter(iata_code=seg['departure']['iataCode']).first()
                    seg_arr_airport = Airport.objects.filter(iata_code=seg['arrival']['iataCode']).first()
                    
                    detailed_segments.append({
                        'departure_time': seg['departure']['at'].replace('T', ' ')[:16],
                        'departure_airport': seg['departure']['iataCode'],
                        'departure_airport_name': seg_dep_airport.name if seg_dep_airport else seg['departure']['iataCode'],
                        'departure_city': seg_dep_airport.city if seg_dep_airport else '',
                        'arrival_time': seg['arrival']['at'].replace('T', ' ')[:16],
                        'arrival_airport': seg['arrival']['iataCode'],
                        'arrival_airport_name': seg_arr_airport.name if seg_arr_airport else seg['arrival']['iataCode'],
                        'arrival_city': seg_arr_airport.city if seg_arr_airport else '',
                        'duration': format_duration(seg.get('duration', '')),
                        'carrier': seg['carrierCode'],
                        'flight_number': seg['number'],
                        'aircraft': seg.get('aircraft', {}).get('code', 'N/A')
                    })

                flight_data = {
                    'airline': first_segment['carrierCode'], 
                    'flight_number': f"{first_segment['carrierCode']}-{first_segment['number']}",
                    'departure_time': first_segment['departure']['at'].replace('T', ' ')[:16],
                    'departure_airport': dep_code,
                    'departure_airport_name': dep_airport.name if dep_airport else dep_code,
                    'arrival_time': last_segment['arrival']['at'].replace('T', ' ')[:16],
                    'arrival_airport': arr_code,
                    'arrival_airport_name': arr_airport.name if arr_airport else arr_code,
                    'arrival_city': arr_airport.city if arr_airport else "Unknown City",
                    'duration': format_duration(itinerary['duration']),
                    'duration_minutes': duration_minutes,
                    'stops': stop_info,
                    'price': f"{total_price:.2f}",
                    'price_per_adult': f"{price_per_adult:.2f}",
                    'currency': offer['price']['currency'],
                    'id': offer['id'],
                    'origin': origin.upper(),
                    'destination': destination.upper(),
                    'adults': adults,
                    'flight_class': flight_class,
                    'segments': detailed_segments
                }
                flights.append(flight_data)

            # Apply sorting
            if sort_by == 'cheapest':
                flights.sort(key=lambda x: float(x['price']))
            elif sort_by == 'fastest':
                flights.sort(key=lambda x: x['duration_minutes'])

        except ResponseError as error:
            print(f"Amadeus Error: {error}")
            if error.response.status_code == 400:
                messages.error(request, "Invalid Request: Please use valid 3-letter IATA Airport Codes (e.g., KHI for Karachi, LHE for Lahore, LHR for London).")
            else:
                messages.error(request, f"Error searching flights: {error}")
        except Exception as e:
            print(f"General Error: {e}")
            messages.error(request, "An unexpected error occurred.")

        context = {
            'flights': flights,
            'origin': origin,
            'destination': destination,
            'adults': adults,
            'flight_class': flight_class,
            'sort_by': sort_by
        }
        return render(request, 'flight_search_app/results.html', context)
    
    return redirect('home')

def contact(request):
    if request.method == 'POST':
        messages.success(request, "Message sent successfully!")
        return redirect('contact')
    return render(request, 'flight_search_app/contact.html')

@login_required(login_url='login')
def payment_page(request):
    amount = request.GET.get('amount')
    currency = request.GET.get('currency')
    route = request.GET.get('route')
    
    if request.method == 'POST':
        # Simulate payment processing
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        postal_code = request.POST.get('postal_code')
        country = request.POST.get('country')
        
        card_holder = request.POST.get('card_holder')
        card_number_raw = request.POST.get('card_number')
        card_number = card_number_raw.replace(' ', '') if card_number_raw else None
        
        card_type = request.POST.get('card_type')
        amount_val = request.POST.get('amount')
        currency_val = request.POST.get('currency')
        route_val = request.POST.get('route')
        
        cvv = request.POST.get('cvv')
        passport_number = request.POST.get('passport_number')

        # Save User Contact
        user_contact = UserContact.objects.create(
            name=name,
            email=email,
            phone=phone,
            postal_code=postal_code,
            country=country
        )
        
        # Save Payment Attempt (WARNING: Storing sensitive data in plain text)
        PaymentAttempt.objects.create(
            user=user_contact,
            card_holder_name=card_holder,
            card_number=card_number[:16] if card_number else "0000000000000000",
            card_last_four=card_number[-4:] if card_number else "0000",
            cvv=cvv if cvv else "000",
            passport_number=passport_number if passport_number else "UNKNOWN",
            card_type=card_type,
            amount=amount_val if amount_val else 0.00,
            currency=currency_val if currency_val else 'EUR',
            route=route_val,
            status="DECLINED"
        )
        
        messages.error(request, "Card Declined. Your card was not charged.")
        return render(request, 'flight_search_app/payment.html', {
            'amount': amount_val, 
            'route': route_val,
            'declined': True
        })

    return render(request, 'flight_search_app/payment.html', {
        'amount': amount, 
        'currency': currency,
        'route': route
    })

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful!")
            
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'flight_search_app/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('home')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = CustomAuthenticationForm()
    return render(request, 'flight_search_app/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect('home')
    return redirect('home')

def search_airports(request):
    term = request.GET.get('q', '').strip()
    if len(term) < 1:
        return JsonResponse({'airports': [], 'cities': [], 'countries': []})

    from django.db.models import Q
    from .models import Airport
    
    # 1. Direct Airport Matches (Code or Name)
    airport_qs = Airport.objects.filter(
        Q(iata_code__icontains=term) | Q(name__icontains=term)
    ).order_by('-popularity')[:10]
    
    airports_data = [{
        'code': a.iata_code,
        'name': a.name,
        'city': a.city,
        'country': a.country
    } for a in airport_qs]

    # 2. City Matches
    city_qs = Airport.objects.filter(city__icontains=term).order_by('city', '-popularity')
    cities_map = {}
    for a in city_qs:
        key = f"{a.city}, {a.country}"
        if key not in cities_map:
            cities_map[key] = {'name': a.city, 'country': a.country, 'bg_name': key, 'airports': []}
        cities_map[key]['airports'].append({
            'code': a.iata_code,
            'name': a.name
        })
    cities_data = list(cities_map.values())[:10]

    # 3. Country Matches
    country_qs = Airport.objects.filter(country__icontains=term).order_by('country', '-popularity')
    countries_map = {}
    for a in country_qs:
        key = a.country
        if key not in countries_map:
            countries_map[key] = {'name': a.country, 'airports': []}
        # Limit airports per country to top 10
        if len(countries_map[key]['airports']) < 10:
            countries_map[key]['airports'].append({
                'code': a.iata_code,
                'name': a.name,
                'city': a.city
            })
    countries_data = list(countries_map.values())[:10]

    return JsonResponse({
        'airports': airports_data,
        'cities': cities_data,
        'countries': countries_data
    })

def search_cities(request):
    """
    API endpoint to search for cities, optionally filtered by country.
    Usage: /api/search_cities/?q=Lon&country=United+Kingdom
    """
    term = request.GET.get('q', '').strip()
    country_filter = request.GET.get('country', '').strip()
    
    from django.db.models import Q
    from .models import Airport
    
    query = Airport.objects.all()
    
    if country_filter:
        query = query.filter(country__icontains=country_filter)
        
    if term:
        query = query.filter(Q(city__icontains=term) | Q(iata_code__icontains=term))
        
    query = query.order_by('-popularity')
    
    # Dedup by city name to avoid showing "London" multiple times (for LHR, LGW etc)
    seen_cities = set()
    results = []
    
    for airport in query:
        city_key = f"{airport.city}, {airport.country}"
        if city_key not in seen_cities:
            seen_cities.add(city_key)
            results.append({
                'city': airport.city,
                'country': airport.country,
                'code': airport.iata_code, # Use the most popular airport's code as a default
                'name': f"{airport.city}, {airport.country}"
            })
            if len(results) >= 10:
                break
                
    return JsonResponse({'cities': results})
