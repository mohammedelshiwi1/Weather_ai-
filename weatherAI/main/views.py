from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db import IntegrityError
from .analysis import analysis
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
import csv
import joblib  
import numpy as np
from django.conf import settings
import os
import requests
from .models import reading
from .moonphase_calc import get_moon_phase

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request,'login.html')
    else:
        return render(request,'login.html')
    


def register_view(request):
    if request.method == 'POST':
        firstname = request.POST.get('firstname')
        secondname = request.POST.get('secondname')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=firstname,
                last_name=secondname
            )
            login(request, user)
            messages.success(request, 'Account created successfully.')
            return redirect('login')  # غيّرها حسب صفحة البداية عندك
        except IntegrityError:
            messages.error(request, 'Username already exists.')
            return redirect('register')

    return render(request, 'sign_up.html')


def home_view(request):
    if request.method == "POST":
        start_date=request.POST.get('start_date')
        end_date=request.POST.get('end_date')
        data=analysis(start_date,end_date)
        return render(request,'home.html',{'data':data})
    else:
        return render(request,'home.html')

 
model_path=os.path.join(settings.BASE_DIR, 'main', 'data', 'model.pkl')
model = joblib.load(model_path)

@csrf_exempt
def fetch_weather_data(request):
    if request.method == "POST":
        ip_address = request.POST.get("ip_address")
        try:
            response = requests.get(f"http://{ip_address}/", timeout=5)
            response.raise_for_status()
            data = response.json()
            data["max_feel_like"] = float(data["max_feel_like"])
            if float(data['lux']) > 1000:
                cloud=0
            else:
                cloud=(1-(float(data['lux'])/1000))*100
            

            moon_phase=get_moon_phase()
            features = np.array([[ 
                float(data["max_temp"]),
                float(data["min_temp"]),
                float(data["realTempC"]),
                float(data["max_feel_like"]),
                float(data["min_feel_like"]),
                int(data["humidity"]),
                float(data['pressure']),
                cloud, 
                moon_phase,
            ]])

            prediction = model.predict(features)[0]
            prediction_text = 'it will rain' if prediction == 1 else 'it will not rain'

            read = reading.objects.create(
                user=request.user,
                max_temp=float(data["max_temp"]),
                min_temp=float(data["min_temp"]),
                real_temp=float(data["realTempC"]),
                max_feel=float(data["max_feel_like"]),
                min_feel=float(data["min_feel_like"]),
                humidity=int(data["humidity"]),
                pressure=float(data['pressure']) ,
                prediction=prediction_text
            )

            return JsonResponse({
                "success": True,
                "data": {
                    "id": read.id,
                    "real_temp": read.real_temp,
                    "max_temp": read.max_temp,
                    "min_temp": read.min_temp,
                    "max_feel": read.max_feel,
                    "min_feel": read.min_feel,
                    "humidity": read.humidity,
                    "pressure": read.pressure,
                    "prediction": read.prediction,
                    "timestamp": read.date.strftime('%Y-%m-%d %H:%M:%S')
                }
            })

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return render(request, "weather_fetch.html")

def user_readings_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="user_readings.csv"'

    writer = csv.writer(response)
    writer.writerow(['Real Temp', 'Max Temp', 'Min Temp', 'Max Feel', 'Min Feel', 'Humidity', 'Pressure', 'Prediction', 'Time'])

    for r in reading.objects.filter(user=request.user).order_by('-date'):
        writer.writerow([
            r.real_temp, r.max_temp, r.min_temp, r.max_feel, r.min_feel,
            r.humidity, r.pressure, r.prediction, r.date
        ])

    return response