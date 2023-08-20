from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.utils import timezone
from django.db import IntegrityError
from .models import User, Dashboard, Funds, MonthBudget, FundsChange
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

def dashboard_view(request):

    #Get the correlating user object
    user = request.user

    #Get the users dashboard
    dashboard = Dashboard.objects.get(owner=user)

    return render(request,"WalletWise/dashboard.html", {
        'user':user,
        'dashboard': dashboard
        })

def fundForm(request):

    #Get the associated user
    user = request.user

    if request.method == "POST":

        #Get the users dashboard
        dashboard = Dashboard.objects.get(owner=user)

        #ENSURE THAT THERE CAN ONLY BE UNIQUE NAMES FOR EVERY MONTH BUDGET(probably make a function in the model that checks for that)

        #Get all form data
        action = request.POST.get('action')
        title = request.POST.get('title')
        amount = request.POST.get('amount')

        #Get current date
        date = timezone.now()
        month = date.month
        year = date.year

        #Get monthBudget
        try:
            budget = MonthBudget.objects.filter(date__month=month, date__year=year)[0]
        except IndexError:
            
            #Create  new budget, if there is none for the current month yet
            budget = MonthBudget.objects.create(dashboard=dashboard, date=timezone.now().date())
            budget.save()

        funds = Funds.objects.create(title=title, amount=amount, budget=budget)
        funds.save()

        #Find out wether the page needs to be reloaded
        if action == "redo":
            return render(request, "WalletWise/fundForm.html")
        elif dashboard.openned_before:
            return redirect(reverse('dashboard_view'))
        else:
            return redirect(reverse('incomeForm'))
    else:
        return render(request, "WalletWise/fundForm.html")

def incomeForm(request):

    #Get the user
    user = request.user

    if request.method == "POST":

        #Get the users dashboard
        dashboard = Dashboard.objects.get(owner=user)

        #ENSURE THAT THERE CAN ONLY BE UNIQUE NAMES FOR EVERY MONTH INCOME(probably make a function in the model that checks for that)

        #Get all form data
        action = request.POST.get('action')
        title = request.POST.get('title')
        amount = request.POST.get('amount')

        #Get current date
        date = timezone.now()
        month = date.month
        year = date.year

        #Get monthBudget
        try:
            budget = MonthBudget.objects.filter(date__month=month, date__year=year)[0]
        except IndexError:
            
            #Create  new budget, if there is none for the current month yet
            budget = MonthBudget.objects.create(dashboard=dashboard, date=timezone.now().date())
            budget.save()

        income = FundsChange.objects.create(title=title, amount=amount, budget=budget)
        income.save()

        #Find out wether the page needs to be reloaded
        if action == "redo":
            return render(request, "WalletWise/incomeForm.html")
        elif dashboard.openned_before:
            return redirect(reverse('dashboard_view'))
        else:
            return redirect(reverse('index'))
    else:
        return render(request, "WalletWise/incomeForm.html")

def settings(request):
    #Get the correlating user object
    user = request.user
    return render(request,"WalletWise/settings.html", {
        'user':user
        })