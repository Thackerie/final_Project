from django.db import models
from django.contrib.auth.models import AbstractUser

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
        return self.openned_before == False and self.months != None and self.month_dates_unique()

class MonthBudget(models.Model):
    dashboard = models.ForeignKey("Dashboard", on_delete=models.CASCADE, related_name="months")
    date = models.DateField(auto_now_add=True)

    @property
    def all_funds(self):
        total_amount = self.funds.aggregate(amount_sum=models.Sum('amount'))['amount__sum']
        return total_amount or 0  # Return 0 if no funds are associated

    @property
    def total_Funds(self):
        total_amount = self.all_funds + self.total_Income + self.total_Expenses
        return total_amount

    @property
    def total_Income(self):
        total_amount = self.filter(is_expense=True).aggregate(amount_sum=models.Sum('amount'))['amount_sum']
        return total_amount or 0  # Return 0 if no incomes are associated

    @property
    def total_Expenses(self):
        total_amount = self.expense.aggregate(amount_sum=models.Sum('amount'))['amount__sum']
        return total_amount or 0  # Return 0 if no expenses are associated

    @property
    def month(self):
        return self.date.month

    @property 
    def year(self):
        return self.date.year

class Funds(models.Model):
    budget = models.ForeignKey("MonthBudget",related_name="funds", on_delete=models.CASCADE)
    title = models.CharField(max_length=64)
    amount = models.FloatField()
    
class FundsChange(models.Model):
    budget = models.ForeignKey("MonthBudget",related_name="fundsChanges", on_delete=models.CASCADE)
    title = models.CharField(max_length=64)
    amount = models.FloatField()
    dateTime = models.DateTimeField(auto_now_add=True)
    is_expense = models.BooleanField(default=False)