from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("signup", views.signup, name="signup"),
    path("fundForm", views.fundForm, name="fundForm"),
    path("transferFundsForm", views.transferFundsForm, name="transferFundsForm"),
    path("incomeForm", views.incomeForm, name="incomeForm"),
    path("expenseForm", views.expenseForm, name="expenseForm"),
    path("fundsChangeForm", views.fundsChangeForm, name="fundsChangeForm"),
    path("settings", views.settings, name="settings"),
    path("dashboard", views.dashboard_view, name="dashboard"),
    path("dashboard/finished", views.dashboard_finished, name="dashboard_finished")
]