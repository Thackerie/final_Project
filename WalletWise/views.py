from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.db import IntegrityError
from .models import User, Dashboard
# Create your views here.


def index(request):
    return render(request, "WalletWise/index.html") 

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "WalletWise/login.html", {
                "message": "Invalid username and/or password."
            })
    else:   
        return render(request,"WalletWise/login.html")

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

def signup(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "WalletWise/signup.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "WalletWise/signup.html", {
                "message": "Username already taken."
            })
        
        #Attempt to create new dashboard
        try:
            dashboard = Dashboard.objects.create(owner=user)
            dashboard.save()
        except IntegrityError:
            return render(request, "WalletWise/signup.html", {
                "message": "Internal Issue."
            })

        login(request, user)
        return dashboard_view(request, user.username)
    else:
        return render(request,"WalletWise/signup.html")

def dashboard_view(request, username):

    #Get the correlating user object
    user = User.objects.get(username=username)

    #Get the users dashboard
    dashboard = Dashboard.objects.get(owner=user)

    return render(request,"WalletWise/dashboard.html", {
        'user':user,
        'dashboard': dashboard
        })

def settings(request, username):
    #Get the correlating user object
    user = User.objects.get(username=username)
    return render(request,"WalletWise/settings.html", {
        'user':user
        })