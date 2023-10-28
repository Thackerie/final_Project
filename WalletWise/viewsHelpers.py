from django.utils import timezone
from .models import Dashboard, Funds, MonthBudget, FundsChange
from django.urls import reverse
from django.shortcuts import redirect
from decimal import Decimal
import datetime

def getFundChangeFormData(request):

    #Get the users dashboard
    dashboard = Dashboard.objects.get(owner= request.user)

    #Get all form data
    action = request.POST.get('action')
    title = request.POST.get('title')
    amount = float(request.POST.get('amount'))
    destinationId = request.POST.get('destination')
    reoccuring = request.POST.get('reoccuring')
    formType = request.POST.get('formType')
    description = request.POST.get('description')

    #Get the the destination by its id
    destination = Funds.objects.get(id=destinationId)

    #Convert reoccuring value to boolean
    if reoccuring == "on":
        reoccuring = True
    else:
        reoccuring = False

    return {
        "dashboard" : dashboard,
        "action" : action,
        "title" : title,
        "amount": amount,
        "destination" : destination,
        "reoccuring" : reoccuring,
        "formType": formType,
        "description" : description
    }

def getFundFormData(request, user):

    #Get the users dashboard
    dashboard = Dashboard.objects.get(owner=user)

    #ENSURE THAT THERE CAN ONLY BE UNIQUE NAMES FOR EVERY MONTH BUDGET(probably make a function in the model that checks for that)

    #Get all form data
    action = request.POST.get('action')
    title = request.POST.get('title')
    amount = request.POST.get('amount')

    return {
        "dashboard": dashboard,
        "action" : action,
        "title": title,
        "amount": amount
    }

def getTransferFundsFormData(request, user):
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

    return {
        "dashboard": dashboard,
        "title": title,
        "amount": amount,
        "destination": destination,
        "origin": origin,
        "reoccuring": reoccuring
    }

def getBudget(dashboard):
    #Get current date
    date = timezone.now()
    month = date.month
    year = date.year

    #Get monthBudget
    try:
        budget = MonthBudget.objects.filter(dashboard=dashboard,date__month=month, date__year=year)[0]
    except IndexError:
        #Create  new budget, if there is none for the current month yet
        budget = createBudget(dashboard)
    
    return budget

def createBudget(dashboard):

    #Create new Budget object
    budget = MonthBudget.objects.create(dashboard=dashboard)
    budget.save()



    #try to get last months budget
    try:
        lastBudget = MonthBudget.objects.get(dashboard=dashboard,date__month=datetime.datetime.now().month-1)
    except:
        return budget

    #get all old balances of the user
    oldBalances = Funds.objects.filter(budget=lastBudget)

    #create all new budgets for this month
    for balance in oldBalances:
        newBalance = Funds.objects.create(budget=budget, title=balance.title, amount=balance.amount, defaultOwner=balance.defaultOwner)
        newBalance.save()
        balance.defaultOwner = None
        balance.save()

    #Get all reoccurring FundsChange objects belonging to the user
    reoccurringFundChanges = FundsChange.objects.filter(budget__dashboard__owner=dashboard.owner, reoccuring=True)

    #Add all reoccuring FundsChanges
    for oldfundChange in reoccurringFundChanges:

        #change the destination to same fund but new budget(e.g. same title, different budget)
        newDestination = Funds.objects.filter(title=fundChange.destination.title, budget=budget)

        fundChange = FundsChange.objects.create(title=oldfundChange.title, amount=oldfundChange.amount, budget=budget, destination=newDestination, reoccuring=True)
        fundChange.save()
    
    return budget

def createFunds(formData, budget):
    funds = Funds.objects.create(title=formData["title"], amount=Decimal(str(formData["amount"])), budget=budget)
    funds.save()

def createExpense(formData, budget):
    expense = FundsChange.objects.create(title = formData["title"], amount=Decimal(str(formData["amount"]*-1)), budget=budget, destination=formData["destination"], reoccuring=formData["reoccuring"], is_expense=True, description=formData["description"])
    
    expense.save()

    #Change the amount of the fund that the expense is coming from
    formData["destination"].amount += expense.amount
    formData["destination"].save()

def editExpense(formData, budget, id):
    #get the expense
    expense = FundsChange.objects.get(id=id)
    

    #remove previous expense from its destination
    expense.destination.amount -= expense.amount
    expense.destination.save()

    #update the expense
    expense.title = f"{formData['title']}"
    expense.amount=Decimal(str(formData["amount"]))
    expense.budget=budget
    expense.destination=formData["destination"]
    expense.reoccuring=formData["reoccuring"]
    expense.is_expense=True
    expense.description=formData["description"]

    #save the updated expense
    expense.save()

    #Change the amount of the fund that the expense is coming from
    formData["destination"].amount += expense.amount
    formData["destination"].save()

def createIncome(formData, budget):
    income = FundsChange.objects.create(title = formData["title"], amount=Decimal(str(formData["amount"])), budget=budget, destination=formData["destination"], reoccuring=formData["reoccuring"], is_expense=False, description=formData["description"])
    income.save()

    #Change the amount of the fund that the Income is going to
    formData["destination"].amount += income.amount
    formData["destination"].save()

def editIncome(formData, budget, id):
    #get the expense
    income = FundsChange.objects.get(id=id)
    
    #remove previous expense from its destination
    income.destination.amount -= income.amount
    income.destination.save()

    #update the expense
    income.title = f"{formData['title']}"
    income.amount=Decimal(str(formData["amount"]))
    income.budget=budget
    income.destination=formData["destination"]
    income.reoccuring=formData["reoccuring"]
    income.is_expense=False
    income.description=formData["description"]

    #save the updated expense
    income.save()

    #Change the amount of the fund that the expense is coming from
    formData["destination"].amount += income.amount
    formData["destination"].save()

def createTranfer(formData, budget):
    #Create an expense taking money from one balance and create an income giving the same amount to the other balance
    expense = FundsChange.objects.create(title = formData["title"], amount=Decimal(str(formData["amount"]*-1)), budget=budget, destination=formData["origin"], reoccuring=formData["reoccuring"], is_expense=True)
    expense.save()

    #Change the amount of the fund that the expense is coming from
    formData["origin"].amount += expense.amount
    formData["origin"].save()
    
    income = FundsChange.objects.create(title = formData["title"], amount=Decimal(str(formData["amount"])), budget=budget, destination=formData["destination"], reoccuring=formData["reoccuring"], is_expense=False)
        
    income.save()

    #Change the amount of the fund that the Income is going to
    formData["destination"].amount += income.amount
    formData["destination"].save()

def handleFormRedirect(formType, action,dashboard):
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
        
def getCurrentBudget(request):
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
        currentBudget = createBudget(dashboard)

    return {
        'currentBudget' : currentBudget,
        'user' : user,
        'dashboard' : dashboard
    }