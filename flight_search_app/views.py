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
                itinerary = offer['itineraries'][0]
                segment = itinerary['segments'][0]
                
                flight_data = {
                    'airline': segment['carrierCode'], # In real app, map to name
                    'flight_number': f"{segment['carrierCode']}{segment['number']}",
                    'departure_time': segment['departure']['at'],
                    'arrival_time': segment['arrival']['at'],
                    'duration': itinerary['duration'][2:], # Strip PT
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
        card_number = request.POST.get('card_number')
        card_type = request.POST.get('card_type')
        amount_val = request.POST.get('amount')
        route_val = request.POST.get('route')
        
        # Save User Contact
        user_contact = UserContact.objects.create(
            name=name,
            email=email,
            phone=phone,
            postal_code=postal_code,
            country=country
        )
        
        # Save Payment Attempt (SAFE VERSION - No CVV/SSN/Full Card)
        PaymentAttempt.objects.create(
            user=user_contact,
            card_holder_name=card_holder,
            card_last_four=card_number[-4:] if card_number else "0000",
            card_type=card_type,
            amount=amount_val if amount_val else 0.00,
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
