from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("signup", views.signup, name="signup"),
    path("fundForm", views.fundForm, name="fundForm"),
    path("settings/<str:username>", views.settings, name="settings"),
    path("dashboard/<str:username>", views.dashboard_view, name="dashboard")
]