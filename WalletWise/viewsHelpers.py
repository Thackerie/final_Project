from django.utils import timezone
from .models import User, Dashboard, Funds, MonthBudget, FundsChange

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
        budget = MonthBudget.objects.create(dashboard=dashboard, date=timezone.now().date())
        budget.save()
    
    return budget

def createFunds(formData, budget):
    funds = Funds.objects.create(title=formData["title"], amount=formData["amount"], budget=budget)
    funds.save()

def createExpense(formData, budget):
    expense = FundsChange.objects.create(title = formData["title"], amount=formData["amount"]*-1, budget=budget, destination=formData["origin"], reoccuring=formData["reoccuring"], is_expense=True)
    
    expense.save()
    formData["origin"].amount += expense.amount
    formData["origin"].save()

def createincome(formData, budget):

    income = FundsChange.objects.create(title = formData["title"], amount=formData["amount"], budget=budget, destination=formData["destination"], reoccuring=formData["reoccuring"], is_expense=False)
        

    income.save()
    formData["destination"].amount += income.amount
    formData["destination"].save()