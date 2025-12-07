import os
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from amadeus import Client, ResponseError
from .models import UserContact, PaymentAttempt
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

@login_required(login_url='login')
def search_results(request):
    if request.method == 'GET':
        raw_origin = request.GET.get('origin')
        raw_destination = request.GET.get('destination')
        departure_date = request.GET.get('departure_date')
        adults = request.GET.get('adults', 1)

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

        amadeus = get_amadeus_client()
        flights = []

        try:
            response = amadeus.shopping.flight_offers_search.get(
                originLocationCode=origin,
                destinationLocationCode=destination,
                departureDate=departure_date,
                adults=adults,
                max=10
            )
            
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

                flight_data = {
                    'airline': first_segment['carrierCode'], 
                    'flight_number': f"{first_segment['carrierCode']}-{first_segment['number']}",
                    'departure_time': first_segment['departure']['at'].replace('T', ' ')[:16], # YYYY-MM-DD HH:MM
                    'departure_airport': first_segment['departure']['iataCode'],
                    'arrival_time': last_segment['arrival']['at'].replace('T', ' ')[:16],
                    'arrival_airport': last_segment['arrival']['iataCode'],
                    'duration': format_duration(itinerary['duration']),
                    'stops': stop_info,
                    'price': offer['price']['total'],
                    'currency': offer['price']['currency'],
                    'id': offer['id'],
                    'origin': origin.upper(),
                    'destination': destination.upper()
                }
                flights.append(flight_data)

        except ResponseError as error:
            print(f"Amadeus Error: {error}")
            if error.response.status_code == 400:
                messages.error(request, "Invalid Request: Please use valid 3-letter IATA Airport Codes (e.g., KHI for Karachi, LHE for Lahore, LHR for London).")
            else:
                messages.error(request, f"Error searching flights: {error}")
        except Exception as e:
            print(f"General Error: {e}")
            messages.error(request, "An unexpected error occurred.")

        return render(request, 'flight_search_app/results.html', {'flights': flights, 'origin': origin, 'destination': destination})
    
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
