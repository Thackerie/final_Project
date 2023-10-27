from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard_view, name="dashboard"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("signup", views.signup, name="signup"),
    path("fundForm", views.fundForm, name="fundForm"),
    path("transferFundsForm", views.transferFundsForm, name="transferFundsForm"),
    path("incomeForm", views.incomeForm, name="incomeForm"),
    path("expenseForm", views.expenseForm, name="expenseForm"),
    path("fundsChangeForm", views.fundsChangeForm, name="fundsChangeForm"),
    path("fundsChange/<int:id>", views.fundsChange, name="fundsChange"),
    path("settings", views.settings, name="settings"),
    path("balances", views.balances, name="balances"),
    path("balances/month/<str:date>", views.changeMonthBalance, name="changeMonthBalance"),
    path("balances/<int:id>/edit", views.editBalance, name="editBalance"),
    path("balances/<int:id>/", views.balance, name="balance"),
    path("balances/<int:id>/delete", views.deleteBalance, name="deleteBalance"),
    path("incomes", views.incomes, name="incomes"),
    path("incomes/<str:date>", views.changeMonthIncome, name="changeMonthIncome"),
    path("fundsChanges/<int:id>/edit", views.editFundsChange, name="editFundsChange"),
    path("expenses", views.expenses, name="expenses"),
    path("expenses/<str:date>", views.changeMonthExpense, name="changeMonthExpense"),
    path("dashboard", views.dashboard_view, name="dashboard"),
    path("dashboard/finished", views.dashboard_finished, name="dashboard_finished"),    
]