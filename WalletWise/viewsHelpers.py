from django.utils import timezone
from .models import User, Dashboard, Funds, MonthBudget, FundsChange
from django.urls import reverse
from django.shortcuts import redirect

def getFundChangeFormData(request, user):

    #Get the users dashboard
    dashboard = Dashboard.objects.get(owner=user)

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

    return {
        "dashboard" : dashboard,
        "action" : action,
        "title" : title,
        "amount": amount,
        "destination" : destination,
        "reoccuring" : reoccuring,
        "formType": formType
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
        budget = MonthBudget.objects.filter(date__month=month, date__year=year)[0]
    except IndexError:
        #Create  new budget, if there is none for the current month yet
        budget = createBudget(dashboard)
    
    return budget

def createBudget(dashboard):

    #Check wether this actually works

    #Get all reoccurring FundsChange objects belonging to the user
    reoccurringFundChanges = FundsChange.objects.filter(budget__dashboard__owner=dashboard.owner, reoccuring=True)

    #Create new budget object
    budget = MonthBudget.objects.create(dashboard=dashboard, date=timezone.now().date())
    budget.save()

    for oldfundChange in reoccurringFundChanges:
        fundChange = FundsChange.objects.create(title=oldfundChange.title, amount=oldfundChange.amount, budget=budget, destination=oldfundChange.destination, reoccuring=True)
        fundChange.save()
    
    return budget

def createFunds(formData, budget):
    funds = Funds.objects.create(title=formData["title"], amount=formData["amount"], budget=budget)
    funds.save()

def createExpense(formData, budget):
    expense = FundsChange.objects.create(title = formData["title"], amount=formData["amount"]*-1, budget=budget, destination=formData["origin"], reoccuring=formData["reoccuring"], is_expense=True)
    
    expense.save()

    #Change the amount of the fund that the expense is coming from
    formData["origin"].amount += expense.amount
    formData["origin"].save()

def createIncome(formData, budget):

    income = FundsChange.objects.create(title = formData["title"], amount=formData["amount"], budget=budget, destination=formData["destination"], reoccuring=formData["reoccuring"], is_expense=False)
        
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