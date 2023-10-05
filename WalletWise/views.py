from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.utils import timezone
import datetime
from django.db import IntegrityError
from . import viewsHelpers
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
        return dashboard_view(request)
    else:
        return render(request,"WalletWise/signup.html")

def settings(request):
    #Get the correlating user object and balances
    user = request.user
    balances = Funds.objects.filter(budget__dashboard__owner=user)    

    if request.method == "POST":

        #Remove the old defaultFund if there is any
        try:
            oldFund = Funds.objects.get(defaultOwner=user)
            oldFund.defaultOwner = None
            oldFund.save()
        except:
            ...

        #Get Form Data
        defaultFundId = request.POST.get('defaultDestination')
        fund = Funds.objects.get(id=defaultFundId)
        fund.defaultOwner = user
        fund.save()

    return render(request,"WalletWise/settings.html", {
        'user':user,
        'balances' : balances 
        })

def dashboard_view(request):

    #Get the correlating user object
    user = request.user

    #Try Getting the users dashboard
    try:
        dashboard = Dashboard.objects.get(owner=user)
    except:
        #Make a new dashboard if the user does not have one already
        dashboard = Dashboard.objects.create(owner=user)
        

    budgets = dashboard.months.all()

    currentBudget = ""

    for budget in budgets:      
        if timezone.datetime.now().month == budget.month and timezone.datetime.now().year == budget.year:
            currentBudget = budget
            break

    if currentBudget == "":
        currentBudget = viewsHelpers.createBudget(dashboard)


    return render(request,"WalletWise/dashboard.html", {
        'user':user,
        'budget': currentBudget,
        "dashboard" : dashboard
        })

def dashboard_finished(request):

    #Get the user and their dashboard
    user = request.user
    dashboard = Dashboard.objects.get(owner=user)
    #Set the dashboard to openned before and save changes
    dashboard.openned_before = True
    dashboard.save()
    #Then redirect to the dashboard page
    return redirect(reverse('dashboard'))

def fundForm(request):

    #Get the associated user
    user = request.user

    if request.method == "POST":

        #Get the form data
        formData = viewsHelpers.getFundFormData(request,user)

        #Get the month budget
        budget = viewsHelpers.getBudget(formData["dashboard"])

        #Create the funds Object
        viewsHelpers.createFunds(formData, budget)


        #Find out wether the page needs to be reloaded
        if formData["action"] == "redo":
            return render(request, "WalletWise/fundForm.html")
        elif formData["dashboard"].openned_before:
            return redirect(reverse('dashboard'))
        else:
            return redirect(reverse('incomeForm'))
        

    else:
        return render(request, "WalletWise/fundForm.html")

def incomeForm(request):
    user = request.user
    budget= MonthBudget.objects.filter(dashboard__owner=user, date__month=datetime.datetime.now().month)[0]
    opennedBefore = user.dashboard.openned_before
    balances = list(Funds.objects.filter(budget=budget))

    try:
        defaultFund = user.defaultFunds.all()[0]
        balances.remove(defaultFund)
    except IndexError:
        defaultFund = "No Default"
    return render(request, "WalletWise/fundsChangeForm.html", {
        "formType" : "Income",
        "opennedBefore" : opennedBefore,
        "balances" : balances,
        "defaultFund" : defaultFund
    })

def transferFundsForm(request):

    user = request.user

    if request.method == "POST":

        #Get the form data
        formData = viewsHelpers.getTransferFundsFormData(request, user)
        
        #Get the month budget
        budget = viewsHelpers.getBudget(formData["dashboard"])

        #Create an expense taking money from one balance and create an income giving the same amount to the other balance
        viewsHelpers.createTranfer(formData, budget)
        
        return redirect(reverse('dashboard'))
    
    balances = list(Funds.objects.filter(budget__dashboard__owner=user))
    return render(request, "WalletWise/transferFundsForm.html", {
        "balances" : balances
    })

def fundsChangeForm(request):
    
    #Get the user
    user = request.user

    if request.method == "POST":

        formData = viewsHelpers.getFundChangeFormData(request, user)

        dashboard = formData["dashboard"]

        #Get the month budget
        budget = viewsHelpers.getBudget(dashboard)

        #Get the month budget
        budget = viewsHelpers.getBudget(dashboard)

        if formData["formType"] == "Income":
            viewsHelpers.createIncome(formData, budget)
        else:
            viewsHelpers.createExpense(formData, budget)
        
        #Find out where the page needs to be redirected to
        return viewsHelpers.handleFormRedirect(formData["formType"], formData["action"], dashboard)
        
def expenseForm(request):

    user = request.user
    budget= MonthBudget.objects.filter(dashboard__owner=user, date__month=datetime.datetime.now().month)[0]
    opennedBefore = user.dashboard.openned_before
    balances = list(Funds.objects.filter(budget=budget))

    try:
        defaultFund = user.defaultFunds.all()[0]
        balances.remove(defaultFund)
    except IndexError:
        defaultFund = "No Default"

    return render(request, "WalletWise/fundsChangeForm.html", {
        "formType": "Expense",
        "opennedBefore" : opennedBefore,
        "balances" : balances,
        "defaultFund" : defaultFund
    })

def incomes(request):
    return render(request, "WalletWise/incomes.html")

def balances(request):
    #Get the correlating user object
    user = request.user

    #Try Getting the users dashboard
    try:
        dashboard = Dashboard.objects.get(owner=user)
    except:
        #Make a new dashboard if the user does not have one already
        dashboard = Dashboard.objects.create(owner=user)
        
    #DOCUMENT THIS!!
    budgets = dashboard.months.all()

    currentBudget = ""

    for budget in budgets:    

        if timezone.datetime.now().month == budget.month and timezone.datetime.now().year == budget.year:

            currentBudget = budget
            break

    if currentBudget == "":
        currentBudget = viewsHelpers.createBudget(dashboard)


    return render(request, "WalletWise/balances.html", {
        'user':user,
        'budget': currentBudget,
        'dashboard' : dashboard
    })

def changeMonth(request, date):

    user = request.user

    dashboard = Dashboard.objects.get(owner=user)

    currentBudget= MonthBudget.objects.filter(date=date, dashboard=dashboard)[0]

    return render(request, "WalletWise/balances.html", {
        'user':user,
        'budget': currentBudget,
        'dashboard' : dashboard
    })

def expenses(request):
    return render(request, "WalletWise/expenses.html")
