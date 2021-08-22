from django.shortcuts import render
from customer_portal.models import *
from car_dealer_portal.models import *
def home_page(request):
    cars = Vehicles.objects.filter(is_available=True)
    return render(request, 'home/index.html',{'cars':cars})
