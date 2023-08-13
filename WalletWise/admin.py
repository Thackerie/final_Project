from django.contrib import admin

# Register your models here.

from .models import User, Funds, FundsChange, Dashboard,MonthBudget

admin.site.register(User)
admin.site.register(Funds)
admin.site.register(FundsChange)
admin.site.register(Dashboard)
admin.site.register(MonthBudget)