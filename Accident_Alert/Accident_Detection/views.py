from django.shortcuts import render
from .models import *
from django.shortcuts import render
from django.http.response import StreamingHttpResponse
from Accident_Detection.stream import streaming
from googleplaces import GooglePlaces
from geopy.distance import geodesic
import requests
import vonage
import time
from .models import *
from django.shortcuts import redirect

global hospital_name
hospital_name ="ABCD"

def home(request):
    return render(request,'index.html')

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

def webcam_feed(request):
    return StreamingHttpResponse(gen(streaming()),content_type='multipart/x-mixed-replace; boundary=frame')

# Cam Location
def current_loc_identify():

    api_key = ''
    # Get your Google Places API Key from Google Cloud Projects Site
    url = 'https://www.googleapis.com/geolocation/v1/geolocate?key=' + api_key

    try:
        response = requests.post(url, json={})
        response.raise_for_status()  # Raise an HTTPError for bad responses
        current_location_data = response.json()['location']  # Extract only the 'location' part
        global current_location
        current_location = {'lat': float(current_location_data['lat']), 'lng': float(current_location_data['lng'])}
        print(current_location)
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"Error: {err}")

    return current_location


def maps(request):
    api_key = ''
    google_places = GooglePlaces(api_key)

    user_latitude = current_location['lat']  # Replace with the user's latitude
    user_longitude = current_location['lng']  # Replace with the user's longitude

    global nearby_hospitals
    nearby_hospitals = find_nearby_hospitals(user_latitude, user_longitude)

    global email_list
    email_list = []
    for hospitals in nearby_hospitals:
        email_list.append(hospitals['email'])


    return render(request,'index.html')

def send_mail(request):
    client = vonage.Client(key="4627a3c9", secret="KAd19Rz2sQ7HM3Tc")
    sms = vonage.Sms(client)
    
def hospital(request):
    hospitals = Hospital.objects.all()
    context = {'hospitals': hospitals}
    return render(request,'hospital.html',context)

def test(request):
    global hospital_name
    notifications = Notifications.objects.all().order_by('-n_id')
    current_location = current_loc_identify()
    result = find_nearby_hospitals(current_location['lat'],current_location['lng'])
    context = {
        'notifications': notifications,
        'hospital_name':hospital_name,
        'result': result
    }
    return render(request,"ui.html",context)

def accept(request,id):
    notification = Notifications.objects.filter(n_id=id).update(accepted = 1)
    return redirect('test')

def register(request):
    global hospital_name
    if request.method == 'POST':
        name=request.POST.get('name')
        email=request.POST.get('email')
        latitude=request.POST.get('latitude')
        longitude=request.POST.get('longitude')
        print(name,email,latitude,longitude)
        hospital=Hospital(name=name,email=email,h_lattitude=latitude,h_longitude=longitude)
        hospital.save()
        hospital_name=name
        return redirect('test')
    return render(request, 'register.html')


def calculate_distance(lat1, lon1, lat2, lon2):
    # Convert latitude and longitude to real numbers
    lat1, lat2, lon1, lon2 = map(float, [lat1, lat2, lon1, lon2])
    # Calculate the distance using Vincenty formula
    distance = geodesic((lat1, lon1), (lat2, lon2)).meters  # Convert to meters
    return distance

def find_nearby_hospitals(user_latitude, user_longitude):
    max_distance = float(50000)  # 50000 meters
    hospitals = Hospital.objects.all()
    global result
    result = []

    for h in hospitals:
        name = h.name
        lat = h.h_lattitude
        lon = h.h_longitude
        email = h.email

        distance = calculate_distance(user_latitude, user_longitude, lat, lon)
        
        if float(distance) <= max_distance:
            hospital_info = {
                'Name': name,
                'Email': email,
                'Latitude': lat,
                'Longitude': lon,
                'Distance': distance
            }
            result.append(hospital_info)
    return result