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

    #Try Getting the users dashboard
    try:
        dashboard = Dashboard.objects.get(owner=user)
    except:
        #Make a new dashboard if the user does not have one already
        dashboard = Dashboard.objects.create(owner=user)
    return render(request,"WalletWise/dashboard.html", {
        'user':user,
        'dashboard': dashboard
        })

def dashboard_finished_view(request):

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
            return redirect(reverse('dashboard'))
        else:
            return redirect(reverse('incomeForm'))
    else:
        return render(request, "WalletWise/fundForm.html")

def incomeForm(request):
    user = request.user
    opennedBefore = user.dashboard.openned_before
    balances = list(Funds.objects.filter(budget__dashboard__owner=user))

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

def createBudget(user, dashboard):

    #Get all reoccurring FundsChange objects belonging to the user
    reoccurringFundChanges = FundsChange.objects.filter(budget__dashboard__owner=user, reoccuring=True)

    #Create new budget object
    budget = MonthBudget.objects.create(dashboard=dashboard, date=timezone.now().date())
    budget.save()

    for oldfundChange in reoccurringFundChanges:
        fundChange = FundsChange.objects.create(title=oldfundChange.title, amount=oldfundChange.amount, budget=budget, destination=oldfundChange.destination, reoccuring=True)
        fundChange.save()

def transferFundsForm(request):
    user = request.user
    if request.method == "POST":
        #Get the users dashboard
        dashboard = Dashboard.objects.get(owner=user)

        #Get all form data
        title = request.POST.get('title')
        amount = float(request.POST.get('amount'))
        destinationId = request.POST.get('destination')
        originId = request.POST.get('origin')
        reoccuring = request.POST.get('reoccuring')

        #Convert reoccuring value to boolean
        if reoccuring == "on":
            reoccuring = True
        else:
            reoccuring = False

        #Get the the destination by its id
        destination = Funds.objects.get(id=destinationId)

        #Get the origin by its id
        origin = Funds.objects.get(id=originId)

        #Get current date
        date = timezone.now()
        month = date.month
        year = date.year

        #Get monthBudget
        try:
            budget = MonthBudget.objects.filter(date__month=month, date__year=year)[0]
        except IndexError:
            
            #Create  new budget, if there is none for the current month yet
            budget = createBudget(user, dashboard)

        #Create an expense taking money from one balance and create an income giving the same amount to the other balance
        expense = FundsChange.objects.create(title=title, amount=amount*-1, budget=budget, destination=origin, reoccuring=reoccuring, is_expense=True)
        income = FundsChange.objects.create(title=title, amount=amount, budget=budget, destination=destination, reoccuring=reoccuring, is_expense=False)
        
        expense.save()
        origin.amount += expense.amount
        origin.save()

        income.save()
        destination.amount += income.amount
        destination.save()


        return redirect(reverse('dashboard'))
    
    balances = list(Funds.objects.filter(budget__dashboard__owner=user))
    return render(request, "WalletWise/transferFundsForm.html", {
        "balances" : balances
    })

def fundsChangeForm(request):
    
    #Get the user
    user = request.user

    if request.method == "POST":

        #Get the users dashboard
        dashboard = Dashboard.objects.get(owner=user)

        #ENSURE THAT THERE CAN ONLY BE UNIQUE NAMES FOR EVERY MONTH INCOME(probably make a function in the model that checks for that)

        #Get all form data
        action = request.POST.get('action')
        title = request.POST.get('title')
        amount = float(request.POST.get('amount'))
        destinationId = request.POST.get('destination')
        reoccuring = request.POST.get('reoccuring')
        formType = request.POST.get('formType')

        #Get the the destination by its id
        destination = Funds.objects.get(id=destinationId)

        #Convert reoccuring value to boolean
        if reoccuring == "on":
            reoccuring = True
        else:
            reoccuring = False

        #Get current date
        date = timezone.now()
        month = date.month
        year = date.year

        #Get monthBudget
        try:
            budget = MonthBudget.objects.filter(date__month=month, date__year=year)[0]
        except IndexError:
            
            #Create  new budget, if there is none for the current month yet
            budget = createBudget(user, dashboard)

        if formType == "Income":
            fundsChange = FundsChange.objects.create(title=title, amount=amount, budget=budget, destination=destination, reoccuring=reoccuring, is_expense=False)
        else:
            fundsChange = FundsChange.objects.create(title=title, amount=amount*-1, budget=budget, destination=destination, reoccuring=reoccuring, is_expense=True)
        #Add/subtract the amount of the income/expense from the destination Fund
        destination.amount += fundsChange.amount
        destination.save()

        fundsChange.save()

        
        #Find out wether the page needs to be reloaded

        if formType == "Income":
            if action == "submit":
                if dashboard.openned_before:
                    return redirect(reverse('dashboard'))
                else:  
                    return redirect(reverse('expenseForm'))
            else:
                return redirect(reverse('incomeForm'))
        else:
            if action == "submit":
                if dashboard.openned_before:
                    return redirect(reverse('dashboard'))
                else:
                    dashboard.openned_before = True
                    dashboard.save()  
                    return redirect(reverse('dashboard'))
            else:
                return redirect(reverse('expenseForm'))
            

def expenseForm(request):
    user = request.user
    opennedBefore = user.dashboard.openned_before
    balances = list(Funds.objects.filter(budget__dashboard__owner=user))

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

def settings(request):
    #Get the correlating user object
    user = request.user
    balances = Funds.objects.filter(budget__dashboard__owner=user)    

    if request.method == "POST":

        #Get Form Data
 
        oldFund = Funds.objects.get(defaultOwner=user)
        oldFund.defaultOwner = None
        oldFund.save()

        defaultFundId = request.POST.get('defaultDestination')
        fund = Funds.objects.get(id=defaultFundId)
        fund.defaultOwner = user
        fund.save()

        

    return render(request,"WalletWise/settings.html", {
        'user':user,
        'balances' : balances 
        })