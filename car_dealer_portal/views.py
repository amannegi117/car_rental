from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib import auth
from car_dealer_portal.models import *
from customer_portal.models import *
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect


def index(request):
    if not request.user.is_authenticated:
        return render(request, 'car_dealer/login.html')
    else:
        return render(request, 'car_dealer/home_page.html')

def login(request):
    return render(request, 'car_dealer/login.html')


def auth_view(request):
    if request.user.is_authenticated:
        return render(request, 'car_dealer/home_page.html')
    else:
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        try:
            car_dealer = CarDealer.objects.get(car_dealer = user)
        except:
            car_dealer = None
        if car_dealer is not None:
            auth.login(request, user)
            return render(request, 'car_dealer/home_page.html')
        else:
            return render(request, 'car_dealer/login_failed.html')

def logout_view(request):
    auth.logout(request)
    return render(request, 'car_dealer/login.html')

def register(request):
    return render(request, 'car_dealer/register.html')

def registration(request):
    username = request.POST['username']
    password = request.POST['password']
    mobile = request.POST['mobile']
    firstname = request.POST['firstname']
    lastname = request.POST['lastname']
    email = request.POST['email']
    city = request.POST['city']
    city = city.lower()
    pincode = request.POST['pincode']

    try:
        user = User.objects.create_user(username = username, password = password, email = email)
        user.first_name = firstname
        user.last_name = lastname
        user.save()
    except:
        return render(request, 'car_dealer/registration_error.html')
    try:
        area = Area.objects.get(city = city, pincode = pincode)
    except:
        area = None
    if area is not None:
        car_dealer = CarDealer(car_dealer = user, mobile = mobile, area=area)
    else:
        area = Area(city = city, pincode = pincode)
        area.save()
        area = Area.objects.get(city = city, pincode = pincode)
        car_dealer = CarDealer(car_dealer = user, mobile = mobile, area=area)
    car_dealer.save()
    return render(request, 'car_dealer/registered.html')

@login_required
def add_vehicle(request):
    car_name = request.POST['car_name']
    vehichle_number = request.POST['vehichle_number']
    cd = CarDealer.objects.get(car_dealer=request.user)
    city = request.POST['city']
    city = city.lower()
    pincode = request.POST['pincode']
    rent = request.POST['rent']
    capacity = request.POST['capacity']
    try:
        area = Area.objects.get(city = city, pincode = pincode)
    except:
        area = None
    if area is not None:
        car = Vehicles(car_name=car_name, vehichle_number=vehichle_number, dealer=cd, area = area, rent=rent, capacity=capacity)
    else:
        area = Area(city = city, pincode = pincode)
        area.save()
        area = Area.objects.get(city = city, pincode = pincode)
        car = Vehicles(car_name=car_name, vehichle_number=vehichle_number, dealer=cd, area = area,rent=rent, capacity=capacity)
    car.save()
    return render(request, 'car_dealer/vehicle_added.html')

@login_required
def manage_vehicles(request):
    username = request.user
    user = User.objects.get(username = username)
    car_dealer = CarDealer.objects.get(car_dealer = user)
    vehicle_list = []
    vehicles = Vehicles.objects.filter(dealer = car_dealer)
    for v in vehicles:
        vehicle_list.append(v)
        
    return render(request, 'car_dealer/manage.html', {'vehicle_list':vehicle_list})

@login_required
def order_list(request):
    username = request.user
    user = User.objects.get(username = username)
    car_dealer = CarDealer.objects.get(car_dealer = user)
    orders = Orders.objects.filter(car_dealer = car_dealer)
    order_list = []
    for o in orders:
        if o.is_complete == False:
            order_list.append(o)
    return render(request, 'car_dealer/order_list.html', {'order_list':order_list})

@login_required
def complete(request):
    order_id = request.POST['id']
    order = Orders.objects.get(id = order_id)
    vehicle = order.vehicle
    order.is_complete = True
    order.save()
    vehicle.is_available = True
    vehicle.save()
    return HttpResponseRedirect('/car_dealer_portal/order_list/')


@login_required
def history(request):
    user = User.objects.get(username = request.user)
    car_dealer = CarDealer.objects.get(car_dealer = user)
    orders = Orders.objects.filter(car_dealer = car_dealer)
    order_list = []
    for o in orders:
        order_list.append(o)
    return render(request, 'car_dealer/history.html', {'wallet':car_dealer.wallet, 'order_list':order_list})

@login_required
def delete(request):
    veh_id = request.POST['id']
    vehicle = Vehicles.objects.get(id = veh_id)
    vehicle.delete()
    return HttpResponseRedirect('/car_dealer_portal/manage_vehicles/')

@login_required
def edit_vehicle(request,pk):

    car=Vehicles.objects.get(id = pk)
    

    if request.method=='POST':
        car=Vehicles.objects.get(id = pk)
        car.car_name = request.POST['car_name']
        car.vehichle_number = request.POST['vehichle_number']
        cd = CarDealer.objects.get(car_dealer=request.user)
        city = request.POST['city']
        car.area.city = city.lower()
        car.area.pincode = request.POST['pincode']
        car.rent = request.POST['rent']
        car.capacity = request.POST['capacity']
        try:
            area = Area.objects.get(city = car.area.city, pincode = car.area.pincode)
        except:
            area = None
        if area is not None:pass
            # car = Vehicles(car_name= car.car_name, vehichle_number= car.vehichle_number, dealer= cd, area = car.area, rent=car.rent, capacity= car.capacity)
        else:
            area = Area(city = car.area.city, pincode = car.area.pincode)
            area.save()
            # area = Area.objects.get(city = car.area.city, pincode = car.pincode)
            # car = Vehicles(car_name= car.car_name, vehichle_number= car.vehichle_number, dealer=cd, area = car.area,rent= car.rent, capacity= car.capacity)
        
        car.save()
        return render(request, 'car_dealer/vehicle_added.html')

    return render(request,'car_dealer/edit_vehicle.html',{'car': car})
