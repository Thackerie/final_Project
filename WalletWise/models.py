from django.db import models
from django.contrib.auth.models import AbstractUser
from decimal import Decimal, ROUND_DOWN

# Create your models here.

class User(AbstractUser):
   pass

class Dashboard(models.Model):
    owner = models.OneToOneField("User", related_name="dashboard", on_delete=models.CASCADE)
    openned_before = models.BooleanField(default=False)
    
    def month_dates_unique(self):
        dates = self.months.values_list('date', flat=True)
        return len(dates) == len(set(dates))
    
    def isValid(self):
        if self.months != None:
            return self.month_dates_unique()
        else:
            return True

    def __str__(self) -> str:
        return f"{self.owner.username}'s Dashboard"

class MonthBudget(models.Model):
    dashboard = models.ForeignKey("Dashboard", on_delete=models.CASCADE, related_name="months")
    date = models.DateField(auto_now_add=True)

    @property
    def all_funds(self):
        total_amount = Decimal(0)
        if self.funds.aggregate(amount_sum=models.Sum('amount'))['amount_sum']:
            total_amount = self.funds.aggregate(amount_sum=models.Sum('amount'))['amount_sum']
        return Decimal(total_amount).quantize(Decimal('0.00'), rounding=ROUND_DOWN) or 0  # Return 0 if no funds are associated

    @property
    def total_Income(self):
        if self.isValid():
            total_amount = Decimal(0)
            if self.fundsChanges.filter(is_expense=False).aggregate(amount_sum=models.Sum('amount'))['amount_sum']:
                total_amount = self.fundsChanges.filter(is_expense=False).aggregate(amount_sum=models.Sum('amount'))['amount_sum']
            return Decimal(total_amount).quantize(Decimal('0.00'), rounding=ROUND_DOWN) or 0  # Return 0 if no incomes are associated
        else:
            return "Invalid funds changes detected"

    @property
    def total_Expenses(self):
        if self.isValid():  
            total_amount = Decimal(0)
            if self.fundsChanges.filter(is_expense=True).aggregate(amount_sum=models.Sum('amount'))['amount_sum']:
                total_amount = self.fundsChanges.filter(is_expense=True).aggregate(amount_sum=models.Sum('amount'))['amount_sum']
            return total_amount.quantize(Decimal('0.00'), rounding=ROUND_DOWN) or 0  # Return 0 if no expenses are associated
        else:
            return "Invalid funds changes detected"

    @property
    def month(self):
        return self.date.month

    @property 
    def year(self):
        return self.date.year
    
    def isValid(self):
        valid = True
        for fundsChange in self.fundsChanges.all():
            #set valid to False if fundsChange is not valid 
            #and then keep it at False, regardless of validity of any other fundsChanges
            valid = valid and fundsChange.isValid()
        return valid
    
    def __str__(self) -> str:
        return f"{self.dashboard.owner}'s Budget({self.month}/{self.year})"

class Funds(models.Model):
    budget = models.ForeignKey("MonthBudget",related_name="funds", on_delete=models.CASCADE)
    title = models.CharField(max_length=64)
    amount = models.DecimalField(decimal_places=2, max_digits=20)
    defaultOwner = models.ForeignKey("User", related_name="defaultFunds", on_delete=models.DO_NOTHING, default=None, null=True)

    def __str__(self) -> str:
        return f"{self.budget.dashboard.owner}'s {self.title}"
    
class FundsChange(models.Model):
    budget = models.ForeignKey("MonthBudget",related_name="fundsChanges", on_delete=models.CASCADE)
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=200, default="No Description")
    amount = models.DecimalField(decimal_places=2, max_digits=20)
    destination = models.ForeignKey("Funds", related_name="associatedFundsChanges", on_delete=models.CASCADE)
    reoccuring = models.BooleanField(default=False)
    dateTime = models.DateTimeField(auto_now_add=True)
    is_expense = models.BooleanField(default=False, blank=False)

    def isValid(self):
        if self.is_expense:
            return self.amount < 0
        else:
            return self.amount >= 0

    @property    
    def type(self):
        if self.is_expense:
            return "Expense"
        return "Income"
        
    def __str__(self) -> str:
        if self.is_expense:
            return f"{self.budget.dashboard.owner}'s Expense: {self.title}"
        return f"{self.budget.dashboard.owner}'s Income: {self.title}"